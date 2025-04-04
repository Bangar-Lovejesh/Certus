# RBC Mortgage & Creditor Insurance Advisor Assistant

An AI-powered virtual assistant designed to assist RBC mortgage specialists and advisors in providing personalized mortgage and creditor insurance advice to clients. The application combines a modern Streamlit UI with powerful backend services including ChromaDB for vector search and OpenAI for natural language processing.

## Overview

This tool helps RBC advisors:
- Access AI-powered assistance for mortgage and insurance advice through a sophisticated chatbot interface
- Collect and manage client profile information through an intuitive, streamlined interface
- Calculate and visualize mortgage payments with the interactive WIPT (What If Payment Tool) calculator
- Generate personalized insurance recommendations based on client profiles and risk assessments
- Simulate the financial impacts of life events on clients (job loss, disability, critical illness, death)
- Receive context-aware advisor alerts for timely cross-selling opportunities
- Track client mortgage journeys with visual timeline representations
- Access RBC product information through vector search powered by ChromaDB and sentence transformers
- Manage and search product documentation with semantic search capabilities

## Table of Contents

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Technical Architecture](#technical-architecture)
- [Features](#features)
- [Usage Guide](#usage-guide)
- [Advanced Usage](#advanced-usage)
- [Development Guide](#development-guide)
- [Data Privacy](#data-privacy)
- [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- OpenAI API key (for AI chatbot functionality)

### Setup

1. Clone the repository or download the source code:
   ```bash
   git clone <repository-url>
   cd NUMBA1
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your OpenAI API key:
   - Option 1: Set it in the config.py file:
     ```python
     OPENAI_API_KEY = "your-api-key-here"
     ```
   - Option 2: Set it as an environment variable:
     ```bash
     # On Windows
     set OPENAI_API_KEY=your-api-key-here
     # On macOS/Linux
     export OPENAI_API_KEY=your-api-key-here
     ```

5. Ensure the vector database directory is properly set up (will be created automatically on first run if it doesn't exist)

## Getting Started

1. Start the application:
   ```bash
   streamlit run app.py
   ```

2. The app will open in your default web browser at `http://localhost:8501`

3. Navigate through the sidebar to access different features:
   - AI Advisor Assistant (chatbot)
   - Client Profile
   - Mortgage Journey Tracker
   - WIPT Calculator
   - Insurance Recommendations
   - Scenario Simulator
   - Document Management

4. Start by creating a client profile, then explore the mortgage journey tracker, payment calculator, and scenario simulators to provide comprehensive advice to clients

## Technical Architecture

The application follows a modular architecture with clear separation of concerns:

### Frontend Layer
- **Streamlit UI**: Provides an interactive web interface built using Streamlit 1.25.0
- **Plotly Charts**: Generates interactive data visualizations for financial simulations and journey tracking

### Core Services Layer
- **Client Profile Management**: Stores and manages client information using Pydantic models
- **Mortgage Journey Tracking**: Implements a state machine to track mortgage application progress
- **WIPT Calculator Engine**: Performs complex mortgage calculations with various payment scenarios
- **Scenario Simulation Engine**: Models financial impacts of different life events
- **Insurance Recommendation System**: Generates personalized coverage recommendations based on client risk profile
- **Context-aware Alert System**: Delivers targeted advisor prompts based on client state and journey stage

### AI and Knowledge Layer
- **Vector Database**: ChromaDB for efficient storage and retrieval of embeddings
- **Sentence Transformers**: Creates embeddings from text using the all-MiniLM-L6-v2 model
- **OpenAI Integration**: Leverages GPT models to generate natural language responses
- **Document Processing**: Extracts and chunks text from PDF documents using PyPDF2

### Data Flow
1. Client data is collected through the UI and stored in session state
2. Data is processed by various calculation and simulation engines
3. Results are presented as visualizations and recommendations
4. Advisor queries are processed by the vector search and AI response system

## Features

### Client Profile Management
Comprehensive client information collection and risk assessment:
- Personal details (name, age, contact information)
- Financial information (income, job stability, savings)
- Mortgage details (principal, term, rate, amortization)
- Family composition and dependent information
- Health factors and risk tolerance assessment

### Mortgage Journey Tracker
Visualize and manage the client's progress through the mortgage process:
- Track journey stages from initial inquiry to post-funding
- Record and monitor protection discussion status
- Identify optimal opportunities for creditor insurance discussions
- Generate stage-specific conversation guides and talking points
- Log important life events that may influence protection needs

### WIPT Calculator (What If Payment Tool)
Sophisticated mortgage payment simulation tool:
- Calculate payments across different frequencies (weekly, biweekly, monthly)
- Compare multiple interest rate scenarios side-by-side
- Visualize payment breakdowns (principal vs. interest)
- Analyze amortization scenarios with interactive charts
- Project total interest costs over the mortgage term

### Scenario Simulator
Robust financial impact modeling for major life events:
- Job loss simulator with EI benefit calculations and savings depletion projections
- Disability scenario modeling with income reduction and medical expense impacts
- Critical illness financial impact projections with recovery period analysis
- Death scenario financial planning with family support gap calculations
- Side-by-side comparison of scenarios with and without insurance protection

### Insurance Recommendation Engine
Data-driven insurance product recommendations:
- Risk-based coverage amount calculations
- Premium estimates based on client demographics and coverage amounts
- Personalized recommendation rationales
- Coverage prioritization based on identified financial vulnerabilities
- Visual protection gap analysis

### AI Advisor Assistant
Advanced AI-powered chatbot with specialized knowledge:
- Semantic search across RBC product documentation
- Natural language answers to complex insurance and mortgage questions
- Product comparison and explanation capabilities
- Context-aware responses that consider client profile information
- Objection handling assistance with templated responses

### Document Management System
Comprehensive document processing and knowledge management:
- PDF document uploading and processing
- Automatic text extraction and chunking
- Vector embedding for semantic search capabilities
- In-app document viewing and navigation
- Knowledge base expansion through new document additions

## Usage Guide

### Navigation
Use the sidebar to navigate between different sections of the app. The main navigation flow typically follows:

1. Client Profile → 2. Mortgage Journey Tracker → 3. WIPT Calculator → 4. Insurance Recommendations → 5. Scenario Simulator

### Client Profile

1. Enter the client's personal and financial information:
   - Name, age, contact information
   - Occupation and income details
   - Current mortgage information and property value
   - Family situation and number of dependents
   - Health factors (smoker status, pre-existing conditions)
   - Risk tolerance assessment

2. Example input:
   ```
   Full Name: Sarah Johnson
   Age: 35
   Email: sarah.johnson@example.com
   Phone: 416-555-7890
   Occupation: Software Developer
   Annual Income: $95,000
   Years at Current Job: 3
   Current Mortgage Balance: $450,000
   Property Value: $650,000
   Dependents: 2
   Smoker: No
   Pre-existing Conditions: No
   Risk Tolerance: Moderate
   ```

3. Save the profile to make it available throughout the application

### Mortgage Journey Tracker

1. Set up the mortgage journey:
   - Select the mortgage type (New Purchase, Refinance, Renewal, etc.)
   - Select the current stage of the journey
   - Update protection discussion status
   - Add relevant life events (marriage, new child, etc.)

2. Use the interactive timeline visualization to track progress

3. Note the optimal protection discussion stage highlighted with a star icon

4. Add notes for the current stage to document important details

### WIPT Calculator

1. Enter detailed mortgage parameters:
   - Principal amount
   - Annual interest rate
   - Term length (years)
   - Amortization period (years)
   - Payment frequency (weekly, biweekly, monthly, semi-monthly)

2. Add alternative rate scenarios to compare payments:
   - Click "Add Scenario" to create multiple interest rate scenarios
   - For example, add +1% and +2% scenarios to show impact of rate increases

3. Analyze the interactive payment breakdown charts:
   - Monthly payment amounts across scenarios
   - Principal vs. interest breakdown
   - Total interest over the term

### Scenario Simulator

1. Select the scenario type to simulate:
   - Job Loss
   - Disability
   - Critical Illness
   - Death of Primary Earner

2. Configure scenario-specific parameters:

   **Job Loss Scenario:**
   - Months unemployed
   - Monthly EI benefit
   - Emergency savings
   - Essential monthly expenses

   **Disability Scenario:**
   - Months unable to work
   - Disability benefits from other sources
   - Emergency savings
   - Essential expenses and medical costs

   **Critical Illness Scenario:**
   - Recovery period
   - Income reduction percentage
   - Emergency savings
   - Medical expenses

   **Death Scenario:**
   - Other life insurance coverage
   - Surviving household income
   - Emergency savings
   - Essential monthly expenses

3. Review the simulation results showing:
   - Monthly shortfall amount
   - Total financial impact
   - Savings depletion projection
   - Protection benefit comparison

4. Use the interactive charts to visualize the financial impact with and without protection

### Insurance Recommendations

1. Access personalized recommendations after completing the client profile

2. Review the calculated recommendations for:
   - Life insurance coverage and premium
   - Disability insurance coverage and premium
   - Critical illness coverage and premium
   - Job loss protection options

3. Each recommendation includes:
   - Coverage amount calculation rationale
   - Premium estimate based on client profile
   - Priority level (Essential, Recommended, Optional)
   - Client benefit explanation

4. Use the provided talking points in client discussions

### AI Advisor Assistant

1. Navigate to the AI Advisor Assistant section

2. Type specific questions about RBC products or policies in the chat interface

3. The AI will search the knowledge base and provide detailed responses

4. Example questions to ask:
   ```
   "What is the difference between term and whole life insurance?"
   "How does the RBC HomeProtector insurance work?"
   "What happens to mortgage insurance if my client sells their home?"
   "What are the eligibility requirements for disability coverage?"
   "How is the premium calculated for critical illness insurance?"
   "What exclusions apply to disability coverage?"
   "Can a client have both individual life insurance and mortgage life insurance?"
   ```

5. Each response can be used directly in client communications

### Document Management

1. Navigate to the Document Management section

2. Upload new PDF documents about RBC products:
   - Click "Upload Document"
   - Select a PDF file from your computer
   - The document will be processed, chunked, and added to the vector database

3. View existing documents:
   - Select a document from the dropdown menu
   - The PDF will be displayed directly in the application
   - Information from all documents becomes searchable via the AI Assistant

## Advanced Usage

### Integrating with Client Management Systems

The application can be extended to integrate with external client management systems:

1. Modify the `profile.json` structure to match your CRM data format
2. Implement API connectors in the utils.py file to fetch and synchronize client data
3. Update the client_profile_form function in app.py to handle external data sources

### Extending the Vector Database

To enhance the AI Assistant's knowledge:

1. Prepare additional PDF documents with RBC product information
2. Use the Document Management interface to upload and process these documents
3. The system will automatically extract text, create chunks, and generate embeddings
4. New knowledge will be immediately available through the AI Assistant interface

### Custom Scenario Development

To create additional simulation scenarios:

1. Add new scenario types to the scenario_simulator function in app.py
2. Define scenario-specific input parameters and calculations
3. Create appropriate visualizations using the Plotly library
4. Add explanation templates in the HTML sections

## Development Guide

### Project Structure

```
├── app.py                 # Main Streamlit application
├── backend/               # Backend modules
│   ├── __init__.py
│   ├── conversation_guides.py      # Templates for advisor conversations
│   ├── early_journey_integration.py # Protection opportunity identification
│   ├── journey_visualization.py    # Timeline and visualization tools
│   └── mortgage_journey.py         # Journey tracking system
├── config.py              # Application configuration
├── docs/                  # Document storage
│   └── home_protector_creditor.pdf # Sample document
├── logo.png               # Application logo
├── models.py              # Data models using Pydantic
├── profile.json           # Sample client profile
├── requirements.txt       # Dependencies
├── utils.py               # Utility functions
└── vector_db/            # Vector database storage (created at runtime)
```

### Adding New Features

1. Define any new data models in models.py
2. Implement business logic in the appropriate backend module
3. Add UI components to app.py using Streamlit widgets
4. Update configuration parameters in config.py if needed

### Code Styling Conventions

- Use PEP 8 for Python code style
- Organize imports alphabetically
- Document functions with docstrings
- Use type hints for function parameters and return values
- Keep UI code separated from business logic

## Data Privacy

- All client data is processed locally within the Streamlit session
- Client information is stored in-memory and not persisted between sessions
- OpenAI API calls include only anonymized queries, never personal client data
- Vector database stores only product information, not client details
- Session data is completely cleared when the application is closed

## Troubleshooting

### Common Issues

- **Application won't start**: 
  - Ensure all dependencies are installed via `pip install -r requirements.txt`
  - Verify Python version is 3.8 or higher
  - Check for console errors during startup

- **Vector search errors**: 
  - Make sure the vector_db directory exists and has proper write permissions
  - Check ChromaDB installation is complete with all dependencies
  - Try reinitializing the database by uploading a document

- **OpenAI API errors**: 
  - Verify your API key is correctly set in config.py or as an environment variable
  - Check for API rate limits or quota exhaustion
  - Ensure you have proper API permission for the models being used

- **Visualization errors**: 
  - Ensure Plotly and Pandas are properly installed
  - Check that client data inputs are within expected ranges
  - Verify that all numeric input fields have consistent types (float or int)

- **PDF processing issues**: 
  - Ensure PDF files are not password-protected
  - Check that PyPDF2 is properly installed
  - Verify the docs directory exists and has proper permissions
