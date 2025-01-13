import assemblyai as aai
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
from pydub import AudioSegment
import speech_recognition as sr
import requests
from urllib.parse import quote_plus

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY", "e0d4f9ff6644425a82307b882181edfa")

def load_dataset(file_path):
    try:
        df = pd.read_csv(file_path)
        questions = df['QUESTIONS'].tolist()
        answers = df['ANSWERS'].tolist()
        return questions, answers
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return [], []

questions, answers = load_dataset(r'C:\Users\samee\Documents\projects\TRAVEL-NAVIGATOR\TRAVEL-NAVIGATOR\travelnavigator\dataset (1).csv')

retriever = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
generator = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")

question_embeddings = retriever.encode(questions, convert_to_tensor=True).cpu().numpy()
embedding_dim = question_embeddings.shape[1]
index = faiss.IndexFlatL2(embedding_dim)
index.add(question_embeddings)

def filter_answers_by_keywords(query, answers, top_k=3):
    keywords = ['kerala', 'karnataka', 'trip', 'days', 'vacation']
    query = query.lower()
    filtered_answers = [answer for answer in answers if any(keyword in answer.lower() for keyword in keywords)]
    return filtered_answers[:top_k] if filtered_answers else answers[:top_k]

def retrieve_answers(query, top_k=3):
    query_embedding = retriever.encode([query], convert_to_tensor=True).cpu().numpy()
    distances, indices = index.search(query_embedding, top_k)
    return [answers[idx] for idx in indices[0]]

def generate_response(query, context_answers):
    context = " ".join(context_answers)
    input_text = f"Context: {context} Question: {query}"
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
    outputs = generator.generate(**inputs, max_length=100, num_return_sequences=1)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def search_images_unsplash(query, num_images=3):
    # unsplash_access_key = os.getenv('PsTPz9S5OTm2rCzKwInEfUNuzQAWgM8CjrG9U9hKcwk')
    unsplash_access_key = "PsTPz9S5OTm2rCzKwInEfUNuzQAWgM8CjrG9U9hKcwk"
    query = quote_plus(query)
    search_url = f"https://api.unsplash.com/search/photos?query={query}&client_id={unsplash_access_key}&per_page={num_images}"
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        search_results = response.json()
        return [image['urls']['regular'] for image in search_results['results']]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching images: {e}")
        return []

def upload_and_transcribe_audio():
    try:
        wav_file = "converted_audio.wav"
        audio = AudioSegment.from_file(r'C:\Users\samee\Documents\projects\TRAVEL-NAVIGATOR\TRAVEL-NAVIGATOR\audio.opus')
        audio.export(wav_file, format="wav")
        print(f"File converted to WAV format: {wav_file}")

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_file) as source:
            print("Listening to the audio file...")
            audio_data = recognizer.record(source)
            print("Transcribing audio...")
            return recognizer.recognize_google(audio_data)
    except Exception as e:
        print(f"Error processing audio: {e}")
        return None

def rag_chatbot(query):
    context_answers = retrieve_answers(query, top_k=3)
    response = generate_response(query, context_answers)
    image_urls = search_images_unsplash(query)
    return response, image_urls

def chat():
    print("Chatbot: Hello! You can talk to me via text or voice input. Type 'exit' to quit.")
    while True:
        query = input("You (type 'voice' to upload a voice file or type your question): ")
        if query.lower() in ["exit", "quit", "bye"]:
            print("Chatbot: Goodbye! Feel free to come back anytime.")
            break

        if query.lower() == "voice":
            query = upload_and_transcribe_audio()
            if query:
                print(f"Transcribed query: {query}")
            else:
                continue

        response, image_urls = rag_chatbot(query)
        print("Chatbot:", response)

        if image_urls:
            print("Here are some related images:")
            for url in image_urls:
                print(url)
chat()