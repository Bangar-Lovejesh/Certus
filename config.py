"""
Configuration settings for the RBC Mortgage & Creditor Insurance Advisor Assistant
"""
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
VECTOR_DB_PATH = BASE_DIR / "vector_db"

# Create directories if they don't exist
os.makedirs(DOCS_DIR, exist_ok=True)

# API Keys (should be loaded from environment variables in production)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")

# Vector DB settings
COLLECTION_NAME = "documents"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# LLM settings
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_TEMPERATURE = 0.3
MAX_TOKENS = 1000
MAX_CONTEXT_LENGTH = 3000

# UI settings
APP_TITLE = "Certus"
APP_SUBTITLE = "Mortgage & Creditor Insurance Advisor Assistant"
APP_ICON = "logo.png"
PRIMARY_COLOR = "#0042B2"  # Primary Blue
SECONDARY_COLOR = "#FEDF01"  # Secondary Yellow
TEXT_COLOR = "#FFFFFF"
BACKGROUND_COLOR = "#0A0A0A"

# Product information
PRODUCT_TYPES = {
    "life": "Life Insurance",
    "disability": "Disability Insurance",
    "critical_illness": "Critical Illness Insurance",
    "job_loss": "Job Loss Insurance"
}

# Screen types for context-aware alerts
SCREEN_TYPES = {
    "client_profile": "Client Profile",
    "mortgage_application": "Mortgage Application",
    "product_recommendation": "Product Recommendation",
    "insurance_application": "Insurance Application",
    "payment_calculator": "Payment Calculator"
}

# Prompts
SYSTEM_PROMPT = """
You are an AI assistant for RBC Mortgage Specialists and Advisors. Your role is to help them provide better advice to clients about mortgages and creditor insurance products.

Answer questions based on the context provided. If the answer is not in the context, say "I don't have information on that specific topic, but I can help you find the right resources or connect you with a product specialist."

Be concise, professional, and helpful. Format your response in a way that's easy for advisors to explain to clients.
"""
