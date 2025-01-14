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
import streamlit as st
from tempfile import NamedTemporaryFile

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

questions, answers = load_dataset(r'C:\Users\himaj\OneDrive\Desktop\TRAVEL-NAVIGATOR\travelnavigator\dataset (1).csv')

retriever = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
generator = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")

question_embeddings = retriever.encode(questions, convert_to_tensor=True).cpu().numpy()
embedding_dim = question_embeddings.shape[1]
index = faiss.IndexFlatL2(embedding_dim)
index.add(question_embeddings)

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

def upload_and_transcribe_audio(file_path):
    try:
        wav_file = "converted_audio.wav"
        audio = AudioSegment.from_file(file_path)
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

st.title("Travel Navigator Chatbot")
st.markdown("""
This chatbot helps you plan trips, answer travel-related queries, and even provides image suggestions!
You can either type your question or upload a voice file for transcription and response.
""")


input_method = st.radio(
    "Choose input method:",
    options=["Text Input", "Voice Input"]
)

query = None

if input_method == "Text Input":
    query = st.text_input("Type your question here:")
elif input_method == "Voice Input":
    uploaded_file = st.file_uploader("Upload your voice file (e.g., .wav, .opus):")
    if uploaded_file is not None:
        with NamedTemporaryFile(delete=False, suffix=".opus") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name
        st.write("Processing uploaded file...")
        query = upload_and_transcribe_audio(temp_file_path)  # Use your existing function
        if query:
            st.success(f"Transcribed Query: {query}")
        else:
            st.error("Could not process the uploaded file.")

if query:
    if st.button("Get Response"):
        with st.spinner("Generating response..."):
            response, image_urls = rag_chatbot(query)
            st.subheader("Chatbot Response:")
            st.write(response)

            if image_urls:
                st.subheader("Related Images:")
                for url in image_urls:
                    st.image(url, use_column_width=True)


st.markdown("---")
st.caption("Powered by Streamlit, AssemblyAI, and Unsplash API.")