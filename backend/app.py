import os
import openai
import PyPDF2
import tiktoken
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
import streamlit as st
import base64
from streamlit_extras.stateful_button import button
import time

# Load environment variables
load_dotenv()

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Persistent Chroma DB Client
DB_PATH = "vector_db"
chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection = chroma_client.get_or_create_collection("document_embeddings")

if collection is None:
    raise Exception("Failed to create or retrieve the collection from ChromaDB.")

# Choose Embedding Function
USE_LOCAL_EMBEDDINGS = True
if USE_LOCAL_EMBEDDINGS:
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
else:
    embedding_function = embedding_functions.OpenAIEmbeddingFunction(api_key=os.getenv("OPENAI_API_KEY"), model_name="text-embedding-3-small")

# Token Counting (Cached)
@st.cache_data
def count_tokens(text, model="gpt-3.5"):
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

# Text Splitting (Optimized)
def split_text_into_chunks(text, max_tokens=3000):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    chunks = []
    while len(tokens) > 0:
        chunk = tokens[:max_tokens]
        chunks.append(encoding.decode(chunk))
        tokens = tokens[max_tokens:]
    return chunks

# Load Documents Once (No Caching for Realtime Updates)
def load_docs(folder_path):
    documents = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            try:
                if filename.endswith(".pdf"):
                    with open(file_path, "rb") as file:
                        reader = PyPDF2.PdfReader(file)
                        content = "".join([page.extract_text() for page in reader.pages])
                    documents.append({"content": content, "metadata": {"source": filename}})
                elif filename.endswith((".txt", ".md")):
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                        content = file.read()
                    documents.append({"content": content, "metadata": {"source": filename}})
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    return documents

# Add Documents to DB (Overwrite Chunks)
def initialize_db(documents):
    try:
        existing_ids = collection.get()["ids"]
        if existing_ids:
            collection.delete(ids=existing_ids)
            print(f"Deleted existing IDs: {existing_ids}")
    except Exception as e:
        print(f"Error retrieving or deleting existing documents: {e}")

    for i, doc in enumerate(documents):
        chunks = split_text_into_chunks(doc["content"])
        chunk_ids = [f"doc_{i}_chunk_{j}" for j in range(len(chunks))]
        existing_ids = collection.get()["ids"]
        new_ids = [id for id in chunk_ids if id not in existing_ids]
        if new_ids:
            collection.add(
                documents=[chunks[j] for j, id in enumerate(chunk_ids) if id in new_ids],
                metadatas=[doc["metadata"]] * len(new_ids),
                ids=new_ids
            )
            print(f"Added new IDs: {new_ids}")
        else:
            print(f"No new IDs to add for {doc['metadata']['source']}")

# Retrieve Relevant Chunks
@st.cache_data
def retrieve_relevant_chunks(query, top_k=5):
    results = collection.query(query_texts=[query], n_results=top_k)
    return results["documents"][0] if results["documents"] else []

# Generate Response
def generate_response_with_chunking(query, relevant_docs, model="gpt-3.5-turbo", max_tokens=3000):
    chunks = []
    for doc in relevant_docs:
        chunks.extend(split_text_into_chunks(doc, max_tokens))
    context = "\n".join(f"- {chunk}" for chunk in chunks[:5])
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer with as few unnecessary words as possible and ONLY in bullet point format:"
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        print(f"Error with OpenAI API: {e}")
        return "An error occurred."

# Streamlit Display PDF
def display_pdf(file_path):
    with open(file_path, "rb") as file:
        base64_pdf = base64.b64encode(file.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def upload_and_overwrite_file(uploaded_file, folder_path="docs"):
    if uploaded_file is not None:
        file_path = os.path.join(folder_path, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File '{uploaded_file.name}' has been uploaded and overwritten.")
        documents = load_docs(folder_path)
        initialize_db(documents)
        print("processing done")
    else:
        st.warning("No file uploaded.")

# App Initialization
DOCS_PATH = "docs"

# Use session state to control database initialization
if "db_initialized" not in st.session_state:
    st.session_state.db_initialized = False

if not st.session_state.db_initialized:
    documents = load_docs(DOCS_PATH)
    initialize_db(documents)
    st.session_state.db_initialized = True

def chatbot_moment():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    def display_chat():
        for user_message, bot_response in st.session_state.chat_history[-10:]:
            st.markdown(f'<div style="background-color:#214b59; padding: 10px; border-radius: 10px; margin: 5px;">'
                        f'**You**: {user_message}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="background-color:#212f59; padding: 10px; border-radius: 10px; margin: 5px;">'
                        f'**Helper**: {bot_response}</div>', unsafe_allow_html=True)

    with st.form(key="chat_form", clear_on_submit=True):
        user_query = st.text_input("Ask a question:", key="user_input", placeholder="Type something...", label_visibility="collapsed")
        submit_button = st.form_submit_button(label="Submit")

    if submit_button and user_query:
        st.session_state.chat_history.append((user_query, ""))
        relevant_docs = retrieve_relevant_chunks(user_query)
        response = generate_response_with_chunking(user_query, relevant_docs)
        if response:
            with st.spinner("Helper is typing..."):
                time.sleep(2)
            st.session_state.chat_history[-1] = (user_query, response)
            display_chat()
        else:
            st.session_state.chat_history[-1] = (user_query, "Sorry, I couldn't find an answer.")
            display_chat()

    if st.button("Clear Chat"):
        st.session_state.chat_history = []

with open("logo.png", "rb") as f:
    data = base64.b64encode(f.read()).decode('utf-8')

st.markdown(
    f"""
    <div style="display:table;margin-top:-0%;margin-left:-22%;">
    <img src="data:image/png;base64,{data}" width="77" height="100">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 style='text-align: center; color: white; '>ADVISOR AI</h1>", unsafe_allow_html=True)
st.subheader("Home & Auto", divider="blue")
if button("Leland Car Insurance.pdf", key="button1"):
    display_pdf("docs/Leland Car Insurance.pdf")

st.subheader("Life & Health", divider="blue")
if button("RBC Visa Cert of Insurance.pdf", key="button2"):
    display_pdf("docs/RBC Visa Cert of Insurance.pdf")

uploaded_file = st.file_uploader("Upload a file", type=["pdf", "txt", "md"])
if st.button("Upload"):
    upload_and_overwrite_file(uploaded_file)

with st.sidebar:
    st.title("ADVISOR AI Chatbot")
    chatbot_moment()
