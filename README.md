# RBC Financial Advisor

An AI-powered financial advisory application that helps RBC clients make informed decisions about mortgages, insurance, and other financial products through personalized simulations, document analysis, and conversational assistance.

![RBC Logo](https://www.rbcroyalbank.com/dvl/v1.0/assets/images/logos/rbc-logo-shield.svg)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technical Architecture](#technical-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Document Processing](#document-processing)
- [Simulation Engine](#simulation-engine)
- [API Integration](#api-integration)
- [Contributing](#contributing)
- [License](#license)

## Overview

The RBC Financial Advisor is a Streamlit-based web application that leverages AI to provide personalized financial guidance. It combines document analysis, natural language processing, and financial simulation to help users understand their options across mortgages, insurance products, and other financial services offered by RBC.

## Features

### 💬 Financial Assistant (Chatbot)

- **Conversational Interface**: Engage in natural dialogue about financial questions
- **Document-Grounded Responses**: Get accurate answers based on official RBC documentation
- **Context-Aware**: The assistant maintains conversation history to provide coherent responses
- **Semantic Search**: Uses vector embeddings to find the most relevant information across various financial products

### 📝 Personalized Assessment

- **Customer Data Collection**: Input personal and financial information through an intuitive form
- **Scenario Generation**: Receive tailored financial scenarios based on your profile
- **Risk Assessment**: Understand potential risks and benefits of different financial options
- **Recommendation Engine**: Get personalized recommendations across RBC's product offerings

### 📄 Document Library

- **PDF Viewer**: Browse and read financial documents directly in the application
- **Document Management**: Upload, view, and organize documents related to various financial products
- **Knowledge Base**: Access a collection of RBC resources covering mortgages, insurance, and other financial services
- **Search Functionality**: Find specific information across all uploaded documents

### 🔮 Scenario Simulator

- **Life Event Simulations**: Explore how major life events might affect your finances:
  - Job loss
  - Having children
  - Critical illness
  - Interest rate changes
  - Travel emergencies
- **Insurance Simulations**: Understand how different insurance products protect you in various scenarios:
  - HomeProtector mortgage insurance
  - Critical illness insurance
  - Life insurance
  - Travel insurance
- **Custom Scenarios**: Create and analyze your own "what-if" situations
- **Financial Impact Analysis**: See how different scenarios affect your payments and overall finances
- **Personalized Results**: All simulations are tailored to your specific financial profile

## Insurance Products

The application provides detailed information and simulations for various RBC insurance products:

### HomeProtector Insurance
- **Life Insurance**: Covers mortgage balance in case of death
- **Critical Illness Insurance**: Covers mortgage if diagnosed with covered illnesses
- **Disability Insurance**: Helps with mortgage payments during disability periods
- **Prior Coverage Recognition**: Information on transferring existing coverage

### Travel Insurance
- **Emergency Medical Coverage**: Information on coverage during travel
- **Trip Cancellation/Interruption**: Simulation of travel disruption scenarios
- **Coverage Limits**: Details on maximum coverage amounts
- **Eligibility Requirements**: Information on who qualifies for coverage

### Critical Illness Insurance
- **Covered Conditions**: Information on which illnesses are covered
- **Benefit Calculation**: How benefits are determined and paid
- **Premium Rates**: Age-based premium calculations
- **Exclusions**: Understanding what isn't covered

## Technical Architecture

The application is built on a robust technical foundation:

### Vector Database (ChromaDB)
- Stores document embeddings for semantic search
- Enables efficient retrieval of relevant information
- Maintains document metadata for traceability

### Embedding Engine
- Supports both local and cloud-based embeddings
- Uses SentenceTransformer for local processing
- OpenAI embedding API integration for cloud processing

### Document Processing Pipeline
1. PDF upload and storage
2. Text extraction using PyPDF2
3. Text chunking and tokenization
4. Vector embedding generation
5. Storage in ChromaDB

### AI Integration
- OpenAI GPT models for natural language generation
- Context window management for handling long documents
- Temperature and token control for appropriate responses

### User Interface
- Streamlit-based responsive web interface
- RBC-branded styling and layout
- Tab-based navigation for intuitive user experience

## Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/rbc-financial-advisor.git
cd rbc-financial-advisor

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your OpenAI API key
```

## Usage

```bash
# Run the Streamlit app
streamlit run backend/app.py
```

The application will be available at http://localhost:8501

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
USE_LOCAL_EMBEDDINGS=True  # Set to False to use OpenAI embeddings
```

### Vector Database Configuration

The application uses a persistent ChromaDB instance stored in the `vector_db` directory. You can modify the database path in `app.py`:

```python
DB_PATH = "vector_db"  # Change this to your preferred location
```

## Document Processing

### Supported Document Types
- PDF documents (.pdf)

### Document Chunking
Documents are automatically split into chunks of approximately 1024 tokens to optimize for retrieval and context window limitations.

### Adding New Documents
1. Use the file uploader in the sidebar
2. Click "Process Document"
3. The document will be processed, chunked, and added to the vector database

## Simulation Engine

The simulation engine creates personalized scenarios based on:

1. **User Profile**: Personal and financial information
2. **Selected Scenario**: Predefined or custom situation
3. **Document Context**: Relevant information from financial documents

### Simulation Types
- Job loss impact
- New child financial adjustments
- Critical illness scenarios
- Interest rate fluctuations
- Travel emergency situations
- Insurance claim scenarios
- Custom user-defined scenarios

### Profile Format
User profiles are stored in JSON format with the following structure:

```json
{
  "applicants": [
    {
      "first_name": "John",
      "last_name": "Doe",
      "age": 35,
      "marital_status": "Married",
      "employment": "Software Engineer",
      "income": 120000,
      "household_income": 180000,
      "number_of_kids": 2,
      "current_assets": ["Stocks: $50,000", "401(k): $100,000"],
      "liabilities": ["Car Loan: $20,000", "Student Loans: $30,000"]
    }
  ]
}
```

## API Integration

The application integrates with the following APIs:

### OpenAI API
- Used for text generation and embeddings
- Requires an API key set in the `.env` file
- Controls for temperature and max tokens

### SentenceTransformer
- Local embedding generation
- Uses the "all-MiniLM-L6-v2" model by default
- No API key required

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the MIT license.

---