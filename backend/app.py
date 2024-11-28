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


# Load Documents Once (Cached)
@st.cache_data
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


# Add Documents to DB (Run Once)
@st.cache_resource
def initialize_db(documents):
    existing_docs = collection.count()
    if existing_docs == 0:
        for i, doc in enumerate(documents):
            collection.add(
                documents=[doc["content"]],
                metadatas=[doc["metadata"]],
                ids=[f"doc_{i}"]
            )
    return collection


# Retrieve Relevant Chunks
@st.cache_data
def retrieve_relevant_chunks(query, top_k=5):
    results = collection.query(query_texts=[query], n_results=top_k)
    return results["documents"][0]


# Generate Response
def generate_response_with_chunking(query, relevant_docs, model="gpt-3.5-turbo", max_tokens=3000):
    chunks = []
    for doc in relevant_docs:
        chunks.extend(split_text_into_chunks(doc, max_tokens))
    
    context = "\n".join(f"- {chunk}" for chunk in chunks[:5])
    
    # Include instruction for concise answers
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer with as few unnecessary words as possible and ONLY in bullet point format:"
    
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()  # Strip any extra whitespace
    except openai.OpenAIError as e:
        print(f"Error with OpenAI API: {e}")
        return "An error occurred."



# Streamlit Display PDF
def display_pdf(file_path):
    with open(file_path, "rb") as file:
        base64_pdf = base64.b64encode(file.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def chatbot_moment():
    # Initialize chat history if not already done
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Function to display chat with some styling improvements
    def display_chat():
        for user_message, bot_response in st.session_state.chat_history[-10:]:
            # Display user message with a bubble-like styling
            st.markdown(f'<div style="background-color:#214b59; padding: 10px; border-radius: 10px; margin: 5px;">'
                        f'**You**: {user_message}</div>', unsafe_allow_html=True)
            
            # Display bot response with another bubble style
            st.markdown(f'<div style="background-color:#212f59; padding: 10px; border-radius: 10px; margin: 5px;">'
                        f'**Helper**: {bot_response}</div>', unsafe_allow_html=True)

    with st.form(key="chat_form", clear_on_submit=True):
        # User input field with a more polished label
        user_query = st.text_input("Ask a question:", key="user_input", placeholder="Type something...", label_visibility="collapsed")
        
        submit_button = st.form_submit_button(label="Submit")
        # If there's a user query, immediately show the user's message and simulate a delay for the bot's response
        if submit_button and user_query:
            # Display the user's message instantly
            st.session_state.chat_history.append((user_query, ""))
            # display_chat()

            # Process the query and generate a response asynchronously
            relevant_docs = retrieve_relevant_chunks(user_query)
            response = generate_response_with_chunking(user_query, relevant_docs)
            
            if response:
                # Simulate a "typing..." effect and then show the bot's response after a slight delay
                with st.spinner("Helper is typing..."):
                    time.sleep(2)  # Simulate the bot's typing delay

                # Update chat history with the bot's response
                st.session_state.chat_history[-1] = (user_query, response)
                display_chat()
            else:
                # Fallback in case there is no response
                st.session_state.chat_history[-1] = (user_query, "Sorry, I couldn't find an answer.")
                display_chat()
    
    if st.button("Clear Chat"):
        st.session_state.chat_history = []  # Reset chat history
        # st.experimental_rerun()  # Optionally rerun the app to reset the UI


# App Initialization
DOCS_PATH = "docs"
documents = load_docs(DOCS_PATH)
collection = initialize_db(documents)


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

# st.title("NUMBA1 APP")
st.markdown("<h1 style='text-align: center; color: white; '>ADVISOR AI</h1>",unsafe_allow_html=True)

st.subheader("Home & Auto", divider="blue")
if button("Leland Car Insurance.pdf", key="button1"):
    display_pdf("docs/Leland Car Insurance.pdf")

st.subheader("Life & Health", divider="blue")
if button("RBC Visa Cert of Insurance.pdf", key="button2"):
    display_pdf("docs/RBC Visa Cert of Insurance.pdf")

with st.sidebar:
    st.title("ADVISOR AI Chatbot")
    chatbot_moment()
