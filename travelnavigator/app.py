import streamlit as st
from datetime import datetime
import pymongo
import faiss
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_nvidia_ai_endpoints import ChatNVIDIA,NVIDIAEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain_community.docstore.in_memory import InMemoryDocstore

# MongoDB setup
API_KEY = "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"  # Replace with your valid API key

client = pymongo.MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB URI
db = client["travel_planner"]
users_collection = db["users"]

# Initialize FAISS index and embeddings
embedding_model = NVIDIAEmbeddings(
  model="nvidia/llama-3.2-nv-embedqa-1b-v2", 
  api_key=API_KEY, 
  truncate="NONE", 
  )

llm = ChatNVIDIA(
  model="meta/llama-3.1-405b-instruct",
  api_key=API_KEY, 
  temperature=0.2,
  top_p=0.7,
  max_tokens=1024,)

dimension = 1024  # Change this to match your embedding size
index = faiss.IndexFlatL2(dimension)
docstore = InMemoryDocstore({}) 
index_to_docstore_id = {}
faiss_index = FAISS(embedding_model, index, docstore, index_to_docstore_id)

def load_dataset(file_path, chunk_size=1000):
    try:
        st.info("Loading dataset...")
        chunks = pd.read_csv(file_path, chunksize=chunk_size)
        data = pd.concat(chunks, ignore_index=True)
        return data
    except Exception as e:
        st.error(f"An error occurred while loading the dataset: {e}")
        return None

# Load dataset and populate FAISS index
def load_dataset_to_faiss(file_path):
    # Load dataset (CSV with columns 'QUESTIONS' and 'ANSWERS')
    # Load dataset (CSV with columns 'QUESTIONS' and 'ANSWERS')
    try:
        data = pd.read_csv(file_path)
        destinations = data['QUESTIONS'].tolist()
        descriptions = data['ANSWERS'].tolist()
    except Exception as e:
        raise ValueError(f"Error reading the dataset: {e}")

    # Generate embeddings for descriptions
    try:
        embeddings = [embedding_model.embed_query(desc) for desc in descriptions]
        if not embeddings or len(embeddings[0]) == 0:
            raise ValueError("Embeddings generation failed or produced empty results.")
    except Exception as e:
        raise ValueError(f"Error generating embeddings: {e}")

    # Validate FAISS index dimensions
    dimension = len(embeddings[0])
    if not hasattr(faiss_index, "index"):
        try:
            faiss_index.index = faiss.IndexFlatL2(dimension)
        except Exception as e:
            raise ValueError(f"Error initializing FAISS index: {e}")

    # Prepare documents for FAISS
    documents = [
        {"page_content": desc, "metadata": {"destination": dest}}
        for desc, dest in zip(descriptions, destinations)
    ]

    # Add embeddings and destinations to FAISS
    try:
        faiss_index.add_documents(documents)
        st.title("hi")
    except Exception as e:
        raise ValueError(f"Error adding texts to FAISS index: {e}")

    return destinations

   

# Load your dataset (provide the correct file path)
dataset_path = "data.csv"  # Replace with your dataset path
stored_destinations = load_dataset_to_faiss(dataset_path)

# Initialize retriever and QA chain
retriever = faiss_index.as_retriever()
qa_chain = RetrievalQA.from_chain_type(
    retriever=retriever,
    llm=llm,
    chain_type="stuff"
)

# Initialize RAG components
retriever = faiss_index.as_retriever()
llm = ChatNVIDIA(temperature=0.7)  # Replace with your preferred LLM
qa_chain = RetrievalQA(llm=llm, retriever=retriever)

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
        response = qa_chain.run(destination_query)
        st.write("Top Recommendations:")
        st.write(response)
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
