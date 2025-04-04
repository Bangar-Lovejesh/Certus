"""
Utility functions for the RBC Mortgage & Creditor Insurance Advisor Assistant
"""
import os
import re
import base64
# Temporarily removed tiktoken due to installation issues
import PyPDF2
from sentence_transformers import SentenceTransformer
import chromadb
import openai
from config import (
    VECTOR_DB_PATH, 
    COLLECTION_NAME, 
    EMBEDDING_MODEL, 
    OPENAI_API_KEY,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    MAX_TOKENS,
    SYSTEM_PROMPT
)

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

# Initialize embedding model
model = SentenceTransformer(EMBEDDING_MODEL)

# Initialize ChromaDB client
try:
    # Try the newer API first
    client = chromadb.Client(chromadb.Settings(persist_directory=str(VECTOR_DB_PATH)))
except Exception as e:
    try:
        # Fall back to older API if available
        client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH))
    except Exception as e2:
        print(f"Error initializing ChromaDB: {e2}")
        # Create a minimal client that won't crash but won't work either
        # At least the app will start
        class DummyClient:
            def get_collection(self, name):
                raise Exception("ChromaDB not properly initialized")
            def create_collection(self, name):
                raise Exception("ChromaDB not properly initialized")
        client = DummyClient()

def count_tokens(text):
    """Count the number of tokens in a text
    
    This is a simplified version that doesn't require tiktoken.
    It uses a simple approximation based on whitespace and punctuation.
    """
    # Simple approximation: 1 token ~= 4 characters in English
    return len(text) // 4

def split_text_into_chunks(text, max_tokens=500):
    """Split text into chunks of max_tokens"""
    # Clean and normalize text
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        # If adding this paragraph would exceed max_tokens, add current chunk to chunks and start a new one
        if count_tokens(current_chunk + " " + paragraph) > max_tokens and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph
        else:
            current_chunk += " " + paragraph if current_chunk else paragraph
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # If any chunk is still too large, split by sentences
    final_chunks = []
    for chunk in chunks:
        if count_tokens(chunk) > max_tokens:
            sentences = re.split(r'(?<=[.!?])\s+', chunk)
            temp_chunk = ""
            for sentence in sentences:
                if count_tokens(temp_chunk + " " + sentence) > max_tokens and temp_chunk:
                    final_chunks.append(temp_chunk.strip())
                    temp_chunk = sentence
                else:
                    temp_chunk += " " + sentence if temp_chunk else sentence
            if temp_chunk:
                final_chunks.append(temp_chunk.strip())
        else:
            final_chunks.append(chunk)
    
    return final_chunks

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file"""
    with open(pdf_path, "rb") as f:
        pdf_reader = PyPDF2.PdfReader(f)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def initialize_db(documents):
    """Initialize or update the vector database with documents"""
    try:
        # Create collection or get existing one
        try:
            collection = client.get_collection(COLLECTION_NAME)
            print(f"Found existing collection: {COLLECTION_NAME}")
        except:
            collection = client.create_collection(COLLECTION_NAME)
            print(f"Created new collection: {COLLECTION_NAME}")
        
        # Prepare documents, embeddings, and IDs for the collection
        ids = [doc["id"] for doc in documents]
        texts = [doc["content"] for doc in documents]
        metadatas = [{"source": doc["source"]} for doc in documents]
        
        # Generate embeddings for all texts
        embeddings = [model.encode(text).tolist() for text in texts]
        
        # Add documents to collection
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
        print(f"Added {len(documents)} documents to the collection")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

def retrieve_relevant_chunks(query, top_k=5):
    """Retrieve relevant chunks from vector database based on query"""
    try:
        # Check if collection exists, if not create it with default data
        try:
            collection = client.get_collection(COLLECTION_NAME)
        except Exception as collection_error:
            print(f"Collection not found, initializing with default data: {collection_error}")
            # Create a new collection
            collection = client.create_collection(COLLECTION_NAME)
            
            # Add some default documents
            default_docs = [
                {
                    "id": "default-mortgage-1",
                    "content": "HomeProtector mortgage life insurance provides coverage for your mortgage in case of death. The premium is based on your age, mortgage amount, and whether you choose single or joint coverage.",
                    "source": "default"
                },
                {
                    "id": "default-mortgage-2",
                    "content": "If you become disabled and are unable to work, HomeProtector disability insurance can help cover your mortgage payments for up to 24 months per disability.",
                    "source": "default"
                },
                {
                    "id": "default-mortgage-3",
                    "content": "Critical illness insurance provides a lump sum payment that is applied directly to your mortgage if you're diagnosed with a covered condition like cancer, heart attack, or stroke.",
                    "source": "default"
                },
                {
                    "id": "default-insurance-1",
                    "content": "RBC HomeProtector Insurance offers three types of coverage: life, disability, and critical illness. Life insurance covers your mortgage balance, disability helps with monthly payments if you can't work, and critical illness provides a lump sum for covered conditions.",
                    "source": "default"
                },
                {
                    "id": "default-insurance-2",
                    "content": "Premium rates for HomeProtector life insurance range from $0.10 to $1.63 per $1,000 of the initial insured mortgage balance, depending on age. Joint coverage rates are higher.",
                    "source": "default"
                },
                {
                    "id": "default-insurance-3",
                    "content": "To be eligible for HomeProtector insurance, you must be a Canadian resident, between 18-69 years of age for life insurance, 18-65 for disability, and 18-55 for critical illness insurance.",
                    "source": "default"
                },
                {
                    "id": "default-general-1",
                    "content": "RBC offers various mortgage terms from 6 months to 10 years, with both fixed and variable rate options. The most popular term is 5 years.",
                    "source": "default"
                },
                {
                    "id": "default-general-2",
                    "content": "When interest rates increase, your mortgage payments will also increase if you have a variable rate mortgage. With a fixed rate, your payments remain the same until the end of your term.",
                    "source": "default"
                }
            ]
            
            # Initialize the database with default documents
            initialize_db(default_docs)
            
            # Try to get the collection again
            collection = client.get_collection(COLLECTION_NAME)
        
        # Generate embedding for the query
        query_embedding = model.encode(query).tolist()
        
        # Query the collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Extract the documents from results
        if results and 'documents' in results and results['documents']:
            chunks = results['documents'][0]
            return chunks
        else:
            # Fallback to keyword-based responses if no results
            if "mortgage" in query.lower():
                return [
                    "HomeProtector mortgage life insurance provides coverage for your mortgage in case of death. The premium is based on your age, mortgage amount, and whether you choose single or joint coverage.",
                    "If you become disabled and are unable to work, HomeProtector disability insurance can help cover your mortgage payments for up to 24 months per disability.",
                    "Critical illness insurance provides a lump sum payment that is applied directly to your mortgage if you're diagnosed with a covered condition like cancer, heart attack, or stroke."
                ]
            elif "insurance" in query.lower():
                return [
                    "RBC HomeProtector Insurance offers three types of coverage: life, disability, and critical illness. Life insurance covers your mortgage balance, disability helps with monthly payments if you can't work, and critical illness provides a lump sum for covered conditions.",
                    "Premium rates for HomeProtector life insurance range from $0.10 to $1.63 per $1,000 of the initial insured mortgage balance, depending on age. Joint coverage rates are higher.",
                    "To be eligible for HomeProtector insurance, you must be a Canadian resident, between 18-69 years of age for life insurance, 18-65 for disability, and 18-55 for critical illness insurance."
                ]
            else:
                return [
                    "RBC offers various mortgage terms from 6 months to 10 years, with both fixed and variable rate options. The most popular term is 5 years.",
                    "When interest rates increase, your mortgage payments will also increase if you have a variable rate mortgage. With a fixed rate, your payments remain the same until the end of your term."
                ]
    except Exception as e:
        print(f"Error retrieving chunks: {e}")
        # Return a more user-friendly message instead of the error
        return [
            "I'm currently having trouble accessing my knowledge base. Here's some general information that might help:",
            "RBC HomeProtector Insurance offers protection for your mortgage with life, disability, and critical illness coverage options.",
            "You can ask me about mortgage terms, insurance eligibility, or payment calculations, and I'll do my best to assist you."
        ]

def generate_response(query, relevant_docs, max_context_length=3000):
    """Generate a response using OpenAI"""
    if not relevant_docs:
        return "I don't have enough information to answer that question. Please provide more context."
    
    # Combine relevant docs into context
    context = "\n\n".join(relevant_docs)
    
    # If context is too long, truncate it
    if count_tokens(context) > max_context_length:
        # Split into chunks and use the most relevant ones
        chunks = split_text_into_chunks(context, max_tokens=max_context_length // 2)
        context = "\n\n".join(chunks[:2])  # Use the first two chunks
    
    prompt = f"""
Context:
{context}

Question: {query}
"""

    try:
        # Try with OpenAI < 1.0.0 API format first
        try:
            response = openai.ChatCompletion.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            return response.choices[0].message.content.strip()
        except (AttributeError, TypeError):
            # Fall back to OpenAI >= 1.0.0 API format
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return "I'm having trouble generating a response right now. Please try again later."

def calculate_mortgage_payment(principal, annual_rate, years, payment_frequency="monthly"):
    """Calculate mortgage payment based on principal, rate, and term"""
    # Convert annual rate to decimal
    rate = annual_rate / 100
    
    # Determine number of payments based on frequency
    payments_per_year = {
        "weekly": 52,
        "biweekly": 26,
        "monthly": 12,
        "semi_monthly": 24
    }.get(payment_frequency, 12)
    
    # Calculate total number of payments
    n_payments = years * payments_per_year
    
    # Calculate periodic interest rate
    periodic_rate = rate / payments_per_year
    
    # Calculate payment using the mortgage payment formula
    if periodic_rate == 0:
        payment = principal / n_payments
    else:
        payment = principal * (periodic_rate * (1 + periodic_rate) ** n_payments) / ((1 + periodic_rate) ** n_payments - 1)
    
    return payment

def get_base64_encoded_image(image_path):
    """Get base64 encoded image for embedding in HTML"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def get_base64_pdf(pdf_path):
    """Get base64 encoded PDF for embedding in HTML"""
    with open(pdf_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode('utf-8')

def assess_risk_level(client_data):
    """Assess client's risk level based on their profile"""
    # Initialize risk score
    risk_score = 0
    
    # Age factor (younger = higher risk)
    age = client_data.get("age", 35)
    if age < 30:
        risk_score += 3
    elif age < 40:
        risk_score += 2
    elif age < 50:
        risk_score += 1
    
    # Dependents factor
    dependents = client_data.get("dependents", 0)
    risk_score += min(dependents, 3)  # Cap at 3
    
    # Income stability factor
    income = client_data.get("annual_income", 0)
    years_at_job = client_data.get("years_at_current_job", 0)
    
    if income < 50000:
        risk_score += 2
    elif income < 80000:
        risk_score += 1
    
    if years_at_job < 1:
        risk_score += 2
    elif years_at_job < 3:
        risk_score += 1
    
    # Mortgage to income ratio
    mortgage_amount = client_data.get("mortgage_amount", 0)
    if income > 0:
        mortgage_to_income = mortgage_amount / income
        if mortgage_to_income > 5:
            risk_score += 3
        elif mortgage_to_income > 3:
            risk_score += 2
        elif mortgage_to_income > 2:
            risk_score += 1
    
    # Health factors
    if client_data.get("smoker", False):
        risk_score += 2
    
    if client_data.get("pre_existing_conditions", False):
        risk_score += 2
    
    # Map score to risk level
    if risk_score >= 10:
        return "High"
    elif risk_score >= 6:
        return "Medium"
    else:
        return "Low"

def calculate_insurance_premium(age, coverage_amount, coverage_type, joint=False, risk_level="Medium"):
    """Calculate insurance premium based on age, coverage amount, and coverage type"""
    # Base rates per $1,000 of coverage
    base_rates = {
        "life": {
            "18-30": 0.10,
            "31-35": 0.15,
            "36-40": 0.21,
            "41-45": 0.31,
            "46-50": 0.44,
            "51-55": 0.59,
            "56-60": 0.79,
            "61-65": 1.06,
            "66-69": 1.63
        },
        "disability": {
            "18-30": 0.15,
            "31-35": 0.22,
            "36-40": 0.33,
            "41-45": 0.43,
            "46-50": 0.64,
            "51-55": 0.95,
            "56-60": 1.45,
            "61-65": 2.20
        },
        "critical_illness": {
            "18-30": 0.20,
            "31-35": 0.27,
            "36-40": 0.40,
            "41-45": 0.61,
            "46-50": 0.95,
            "51-55": 1.80
        }
    }
    
    # Determine age bracket
    age_bracket = ""
    if 18 <= age <= 30:
        age_bracket = "18-30"
    elif 31 <= age <= 35:
        age_bracket = "31-35"
    elif 36 <= age <= 40:
        age_bracket = "36-40"
    elif 41 <= age <= 45:
        age_bracket = "41-45"
    elif 46 <= age <= 50:
        age_bracket = "46-50"
    elif 51 <= age <= 55:
        age_bracket = "51-55"
    elif 56 <= age <= 60:
        age_bracket = "56-60"
    elif 61 <= age <= 65:
        age_bracket = "61-65"
    elif 66 <= age <= 69:
        age_bracket = "66-69"
    else:
        return None  # Age outside eligible range
    
    # Check if coverage type and age bracket are valid
    if coverage_type not in base_rates or age_bracket not in base_rates[coverage_type]:
        return None
    
    # Get base rate
    rate = base_rates[coverage_type][age_bracket]
    
    # Apply joint coverage multiplier if applicable
    if joint:
        rate *= 1.75
    
    # Apply risk level adjustment
    risk_multipliers = {
        "Low": 0.9,
        "Medium": 1.0,
        "High": 1.2
    }
    rate *= risk_multipliers.get(risk_level, 1.0)
    
    # Calculate premium
    premium = (coverage_amount / 1000) * rate
    
    return round(premium, 2)
