import streamlit as st
from datetime import datetime
import pymongo
import pandas as pd
import tensorflow as tf
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from tensorflow.keras.applications import vgg16
from tensorflow.keras.applications.vgg16 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np
from langchain_nvidia_ai_endpoints import ChatNVIDIA

# MongoDB setup
API_KEY = "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"  # Replace with your valid API key

client = pymongo.MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB URI
db = client["travel_planner"]
users_collection = db["users"]

# Initialize embeddings and LLM
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
llm = ChatNVIDIA(
    model="meta/llama-3.1-405b-instruct",
    api_key=API_KEY, 
    temperature=0.2,
    top_p=0.7,
    max_tokens=1024
)

# Dataset and embedding storage
embeddings = []
documents = []

def load_dataset(file_path):
    try:
        data = pd.read_csv(file_path)
        questions = data['QUESTIONS'].tolist()
        answers = data['ANSWERS'].tolist()
        return questions, answers
    except Exception as e:
        st.error(f"An error occurred while loading the dataset: {e}")
        return None, None

def index_documents(questions, answers):
    global embeddings, documents
    try:
        document_embeddings = embedding_model.encode(answers, convert_to_tensor=True)
        documents = [{"question": q, "answer": a} for q, a in zip(questions, answers)]
        embeddings = document_embeddings
    except Exception as e:
        st.error(f"An error occurred during indexing: {e}")

def search_documents(query, top_k=5):
    global embeddings, documents
    try:
        query_embedding = embedding_model.encode([query], convert_to_tensor=True)
        similarities = cosine_similarity(query_embedding, embeddings)[0]
        top_indices = similarities.argsort()[-top_k:][::-1]
        return [documents[i] for i in top_indices]
    except Exception as e:
        st.error(f"An error occurred during search: {e}")
        return []

def get_rag_response(query):
    retrieved_results = search_documents(query, top_k=5)
    if not retrieved_results:
        return "No relevant recommendations found. Please try a different query."

    context = "\n".join([f"- {res['answer']}" for res in retrieved_results])
    prompt = (
        f"You are a travel assistant. Based on the following information, "
        f"recommend the best destination:\n{context}\n"
        f"Provide a single concise recommendation."
    )
    response = llm.ask(prompt)
    return response

def analyze_image(uploaded_file):
    try:
        model = vgg16.VGG16(weights="imagenet")
        img = image.load_img(uploaded_file, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        predictions = model.predict(img_array)
        decoded_predictions = decode_predictions(predictions, top=3)
        return [f"{label}: {round(prob * 100, 2)}%" for _, label, prob in decoded_predictions[0]]
    except Exception as e:
        st.error(f"An error occurred during image analysis: {e}")
        return None

# Load dataset and index documents
dataset_path = "dataset (1).csv"  # Replace with your dataset path
questions, answers = load_dataset(dataset_path)
if questions and answers:
    index_documents(questions, answers)

# Streamlit app setup
st.title("Travel Planner App")
st.sidebar.header("User Information")

# User ID
user_id = st.sidebar.text_input("Enter your User ID", "")

# Destination Recommendations
# Dropdown menu for Indian states
indian_states = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", 
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", 
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", 
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", 
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", 
    "West Bengal", "Andaman and Nicobar Islands", "Chandigarh", 
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir", 
    "Ladakh", "Lakshadweep", "Puducherry"
]

# Destination selection with a dropdown
st.header("Choose Your Destination")
destination_query = st.selectbox("Select State", indian_states, index=0)

# Initialize session state
if "rec_index" not in st.session_state:
    st.session_state.rec_index = 0
    st.session_state.recommendations = []
    st.session_state.selected_recommendation = None

# Button to get initial recommendations
if st.button("Get Recommendations"):
    if destination_query:
        st.session_state.recommendations = search_documents(destination_query)
        st.session_state.rec_index = 0  # Reset index
        st.session_state.selected_recommendation = None  # Clear any previous selection
        if st.session_state.recommendations:
            rec = st.session_state.recommendations[st.session_state.rec_index]
            st.write(f"**Destination:** {rec['question']}")
            st.write(f"**Description:** {rec['answer']}")
            if st.button(f"Select Recommendation: {rec['question']}"):
                st.session_state.selected_recommendation = rec['question']
        else:
            st.warning("No recommendations found.")
    else:
        st.error("Please select a state.")

# Button to get more recommendations
if st.session_state.recommendations and st.session_state.rec_index < len(st.session_state.recommendations) - 1:
    if st.button("Show More Recommendations"):
        st.session_state.rec_index += 1
        rec = st.session_state.recommendations[st.session_state.rec_index]
        st.write(f"**Destination:** {rec['question']}")
        st.write(f"**Description:** {rec['answer']}")
        if st.button(f"Select Recommendation: {rec['question']}"):
            st.session_state.selected_recommendation = rec['question']
elif st.session_state.recommendations:
    st.info("No more recommendations available.")

# Display Save Destination button if a recommendation is selected
if st.session_state.selected_recommendation:
    st.success(f"You have selected: {st.session_state.selected_recommendation}")
    if st.button("Save Destination"):
        if user_id:
            users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"destination": st.session_state.selected_recommendation}},
                upsert=True
            )
            st.success("Destination saved successfully!")
        else:
            st.error("Please provide your User ID.")

# Additional sections (Dates, Trip Type, Interests, Image Analysis) remain unchanged

# Date selection
st.header("Select Your Dates")
start_date = st.date_input("Start Date", value=datetime.now())
end_date = st.date_input("End Date", value=datetime.now())
if st.button("Save Dates"):
    if user_id:
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "trip_dates": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d")
                }
            }},
            upsert=True
        )
        st.success("Dates saved successfully!")
    else:
        st.error("Please enter your User ID.")

# Trip type selection
st.header("Select Trip Type")
trip_type = st.radio("What type of trip are you planning?", ("Solo", "Partner", "Friends", "Family"))
if st.button("Save Trip Type"):
    if user_id:
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"trip_type": trip_type.lower()}},
            upsert=True
        )
        st.success("Trip type saved successfully!")
    else:
        st.error("Please enter your User ID.")

# Interests selection
st.header("Select Your Interests")
interests = st.multiselect("What are you interested in?", [
    "Pearl Harbor history tours",
    "Hawaiian Culture and History",
    "Great Food",
    "Hidden Gems",
    "Diamond Head hiking",
    "Luxury Shopping",
    "Nature and Wildlife",
    "Island flavors of Oahu",
    "Hawaiian Cuisine",
    "Surfing",
    "Nightlife and Entertainment"
])
if st.button("Save Interests"):
    if user_id:
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"interests": interests}},
            upsert=True
        )
        st.success("Interests saved successfully!")
    else:
        st.error("Please enter your User ID.")

# Image upload and analysis
st.header("Analyze Uploaded Image")
uploaded_file = st.file_uploader("Upload an image of a place you've visited:", type=["jpg", "jpeg", "png"])
if uploaded_file:
    predictions = analyze_image(uploaded_file)
    if predictions:
        st.write("Image Analysis Results:")
        for pred in predictions:
            st.write(f"- {pred}")
        # Save the image results to MongoDB for user preferences
        if user_id:
            users_collection.update_one(
                {"user_id": user_id},
                {"$addToSet": {"image_analysis": predictions}},
                upsert=True
            )
            st.success("Image analysis results saved!")
        else:
            st.warning("Please enter your User ID to save results.")

