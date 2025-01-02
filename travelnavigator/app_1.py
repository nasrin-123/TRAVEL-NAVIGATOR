import streamlit as st
from datetime import datetime
import pymongo
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from langchain.chains import RetrievalQA
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_community.docstore.in_memory import InMemoryDocstore

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

# In-memory document store
docstore = InMemoryDocstore({})

# Dataset and embedding storage
embeddings = []
documents = []

def load_dataset(file_path):
    try:
        st.info("Loading dataset...")
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
        st.info("Indexing documents...")
        document_embeddings = embedding_model.encode(answers, convert_to_tensor=True)
        documents = [{"question": q, "answer": a} for q, a in zip(questions, answers)]
        embeddings = document_embeddings
        st.success("Documents indexed successfully!")
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

# Load dataset and index documents
dataset_path = "data.csv"  # Replace with your dataset path
questions, answers = load_dataset(dataset_path)
if questions and answers:
    index_documents(questions, answers)

# Streamlit app setup
st.title("Travel Planner App")
st.sidebar.header("User Information")

# User ID
user_id = st.sidebar.text_input("Enter your User ID", "")

# Destination selection
st.header("Choose Your Destination")
destination_query = st.text_input("Search for a destination (or enter manually):", "")
if st.button("Search Destination"):
    if destination_query:
        results = search_documents(destination_query)
        if results:
            st.write("Top Recommendations:")
            for res in results:
                st.write(f"**Destination:** {res['question']}")
                st.write(f"**Description:** {res['answer']}")
        else:
            st.warning("No results found.")
    else:
        st.error("Please enter a search query.")

destination = st.text_input("Or enter your destination manually:", "")
if st.button("Save Destination"):
    if user_id and destination:
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"destination": destination}},
            upsert=True
        )
        st.success("Destination saved successfully!")
    else:
        st.error("Please enter both User ID and Destination.")

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
