import os
import openai
import PyPDF2
import tiktoken
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
import shutil

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI API client
openai.api_key = os.getenv("OPEN-API-KEY")

# Initialize Chroma client for the vector database
db_path = "W:/Projects/python/RBC/NUMBA1/vector_db"  # Ensure this path is persistent
chroma_client = chromadb.PersistentClient(path=db_path)  # Use PersistentClient for persistent DB

# Create or get the collection in the vector database
collection = chroma_client.get_or_create_collection("document_embeddings")  # Ensure the same collection name is used

# Function to calculate the number of tokens in a text
def count_tokens(text, model="gpt-3.5"):
    encoding = tiktoken.get_encoding("cl100k_base")  # Get the encoding for the model
    tokens = encoding.encode(text)
    return len(tokens)

# Function to split text into smaller chunks based on token limit
def split_text_into_chunks(text, model="gpt-3.5-turbo", max_tokens=3000):
    chunks = []
    current_chunk = ""
    
    # Split the text into sentences and check token limit
    for sentence in text.split(". "):  # Split by sentences
        # Check if adding this sentence would exceed the token limit
        if count_tokens(current_chunk + sentence) <= max_tokens:
            current_chunk += sentence + ". "
        else:
            # If current chunk is full, add it to the list and start a new chunk
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    # Add the last chunk if there's any remaining text
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

# Function to load documents (PDF, text, and markdown)
def load_docs(folder_path):
    documents = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            if filename.endswith(".pdf"):  # Process PDFs
                try:
                    with open(file_path, "rb") as file:
                        reader = PyPDF2.PdfReader(file)
                        content = ""
                        for page in reader.pages:
                            content += page.extract_text()
                        documents.append({"content": content, "metadata": {"source": filename}})
                except Exception as e:
                    print(f"Failed to read PDF {filename}: {e}")
            elif filename.endswith((".txt", ".md")):  # Process text files
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                        content = file.read()
                        documents.append({"content": content, "metadata": {"source": filename}})
                except Exception as e:
                    print(f"Failed to read text file {filename}: {e}")
    return documents

# Function to add documents to the vector database
def add_documents_to_db(documents):
    for i, doc in enumerate(documents):
        collection.add(
            documents=[doc["content"]],
            metadatas=[doc["metadata"]],
            ids=[f"doc_{i}"]
        )
    print(f"Added {len(documents)} documents to the vector database.")

# Choose embedding function (you can switch between OpenAI or local embeddings)
use_local_embeddings = True  # Set to False to use OpenAI API

if use_local_embeddings:
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
else:
    embedding_function = embedding_functions.OpenAIEmbeddingFunction(api_key=os.getenv("OPEN-API-KEY"), model_name="text-embedding-3-small")

# Define document folder path
doc_path = "W:/Projects/python/RBC/NUMBA1/docs"

# Load documents from folder
documents = load_docs(doc_path)
print(f"Loaded {len(documents)} documents.")

# Add the documents to the vector database
add_documents_to_db(documents)

# Function to retrieve relevant chunks based on user query
def retrieve_relevant_chunks(query, top_k=5):
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    return results['documents'][0]

# Function to generate response from OpenAI based on query and relevant docs
def generate_response_with_chunking(query, relevant_docs, model="gpt-3.5-turbo", max_tokens=3000):
    # Split the relevant documents into chunks
    chunks = []
    for doc in relevant_docs:
        chunks.extend(split_text_into_chunks(doc, model, max_tokens))
    
    # Create the prompt with the chunks (limit the number of chunks to avoid too many tokens)
    context = "\n".join(f"- {chunk}" for chunk in chunks[:3])  # Limit to 3 chunks as an example
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    
    try:
        # Request OpenAI for the answer using the chat-completions endpoint
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Return the response text
        return response.choices[0].message.content
    
    except openai.OpenAIError as e:
        print(f"Error with OpenAI request: {e}")
        return None

# Option to clear vector database (use only if you want to reset the DB)
def clear_vector_db():
    print("Clearing vector database...")
    collection.clear()  # Clears all documents from the collection

# Main loop for user interaction
while True:
    user_query = input("Please enter your question (or 'quit' to exit): ")
    if user_query.lower() == 'quit':
        break

    # Retrieve relevant documents based on the user query
    relevant_docs = retrieve_relevant_chunks(user_query)
    
    # Generate and print the response from OpenAI based on the relevant documents
    response = generate_response_with_chunking(user_query, relevant_docs)
    
    if response:
        print("Response from GPT:")
        print(response)
    print("\n" + "-"*50 + "\n")

print("Thank you for using the system. Goodbye!")
