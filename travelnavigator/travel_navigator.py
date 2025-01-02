import streamlit as st
import os
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from dotenv import load_dotenv
import pandas as pd  # for CSV processing
import filetype  # for file type detection

load_dotenv()

# Initialize Hugging Face models for embeddings and language model
def initialize_hugging_face_models():
    # Embedding model
    st.session_state.embeddings = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    # Language model (choose an appropriate model here)
    st.session_state.llm_pipeline = pipeline("text-generation", model="gpt2", tokenizer="gpt2", device=0)

initialize_hugging_face_models()

def process_file(file_path, mime_type):
    if mime_type == 'application/pdf':
        loader = PyPDFLoader(file_path)
        return loader.load()
    elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        loader = UnstructuredWordDocumentLoader(file_path)
        return loader.load()
    elif mime_type == 'text/csv':
        # Process CSV file
        data = pd.read_csv("sample2.csv")
        documents = data.apply(lambda row: ' '.join(row.values.astype(str)), axis=1).tolist()
        return [{'page_content': doc} for doc in documents]
    else:
        st.error("Unsupported file type: " + mime_type)
        return []

def vector_embedding(uploaded_file):
    file_path = os.path.join("uploaded_files", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Reopen the file to read its content
    file_bytes = uploaded_file.read()
    kind = filetype.guess(file_bytes)
    if kind is None:
        st.error("Unsupported file type")
        return
    
    mime_type = kind.mime
    documents = process_file(file_path, mime_type)
    
    st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=50)
    st.session_state.final_documents = st.session_state.text_splitter.split_documents(documents)
    # Generate embeddings using SentenceTransformer
    doc_embeddings = [st.session_state.embeddings.encode(doc['page_content']) for doc in st.session_state.final_documents]
    st.session_state.vectors = FAISS.from_embeddings(doc_embeddings)

st.title("Hugging Face Model for Document Summarization")
prompt_template = ChatPromptTemplate.from_template(
"""
You are an advanced AI assistant that provides accurate and detailed answers based on the given context. Please follow these guidelines when answering the questions:

1. Answer the questions based on the provided context only.
2. Provide the most accurate response based on the question.
3. Structure the answer in a clear and concise manner.
4. If applicable, break down the answer into bullet points or numbered lists for clarity.
5. Mention the source of the information if relevant.
6. Include any quotes or specific parts of the document that support your answer.
7. Use a formal tone and technical language appropriate for the topic.
8. Use the recent document as the context.
9. If questions are not part of the context, please respond like I am not trained for it.

<context>
{context}
<context>
Questions: {input}

Answer:
"""
)

uploaded_file = st.file_uploader("Upload Document", type=["pdf", "txt", "docx", "csv"])

if st.button("CLICK HERE TO PROCEED."):
    if uploaded_file:
        os.makedirs("uploaded_files", exist_ok=True)
        vector_embedding(uploaded_file)
        st.session_state.file_processed = True
        st.write("Your document is ready to be processed!")
    else:
        st.error("Please upload a document before proceeding.")

if st.session_state.get("file_processed", False):
    prompt1 = st.text_input("Enter Your Question From Document")

    if prompt1:
        # Create the document chain
        document_chain = create_stuff_documents_chain(
            lambda context: st.session_state.llm_pipeline(prompt_template.format(context=context, input=prompt1), max_length=300)[0]["generated_text"],
            prompt_template
        )
        
        retriever = st.session_state.vectors.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        start = time.process_time()
        response = retrieval_chain.invoke({'input': prompt1})
        st.write("Response time: ", time.process_time() - start)
        answer = response['answer']
        st.write(answer)
        
        if st.button("Clear Response"):
            if "vectors" in st.session_state:
                del st.session_state["vectors"]
            if "file_processed" in st.session_state:
                del st.session_state["file_processed"]
            st.rerun()