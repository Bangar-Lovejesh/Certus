# Certus

Certus is an AI-powered virtual assistant designed to assist mortgage specialists and advisors in providing personalized mortgage and creditor insurance advice to clients. Built with Streamlit, the application combines a modern UI with powerful backend services including ChromaDB for vector search and OpenAI for natural language processing.

## Overview

Certus empowers financial advisors to:
- Provide AI-powered mortgage and insurance advice through an intelligent chatbot interface
- Manage comprehensive client profiles with an intuitive, streamlined interface
- Calculate and visualize mortgage scenarios with the interactive WIPT (What If Payment Tool)
- Generate data-driven insurance recommendations based on client risk profiles
- Model financial impacts of critical life events (job loss, disability, illness, death)
- Receive context-aware alerts for timely cross-selling opportunities
- Track mortgage application journeys with visual timeline representations
- Access product information through semantic search powered by ChromaDB
- Manage and search product documentation with advanced AI capabilities

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
   cd certus
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
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

5. The vector database directory will be created automatically on first run

## Getting Started

1. Start the application:
   ```bash
   streamlit run app.py
   ```

2. The app will open in your default web browser at `http://localhost:8501`

3. Navigate through the sidebar to access the following features:
   - **AI Advisor Assistant**: Get AI-powered answers to mortgage and insurance questions
   - **Client Profile**: Create and manage client information
   - **Mortgage Journey Tracker**: Track application progress and identify protection opportunities
   - **WIPT Calculator**: Calculate and visualize mortgage payment scenarios
   - **Insurance Recommendations**: View personalized coverage suggestions
   - **Scenario Simulator**: Model financial impacts of life events
   - **Document Management**: Upload and search product documentation

4. Begin by creating a client profile, then use other tools to provide comprehensive financial advice

## Technical Architecture

Certus follows a modular architecture with clear separation of concerns:

### Frontend Layer
- **Streamlit UI**: Interactive web interface built with Streamlit 1.25.0
- **Plotly Charts**: Dynamic data visualizations for financial simulations and journey tracking

### Core Services Layer
- **Client Profile Management**: Client data handling with Pydantic models
- **Mortgage Journey Tracking**: State machine for tracking application progress
- **WIPT Calculator Engine**: Mortgage calculation engine with multiple payment scenarios
- **Scenario Simulation Engine**: Financial impact modeling for life events
- **Insurance Recommendation System**: Data-driven coverage suggestions based on risk profiles
- **Context-aware Alert System**: Targeted advisor prompts based on client state

### AI and Knowledge Layer
- **Vector Database**: ChromaDB for efficient storage and retrieval of document embeddings
- **Sentence Transformers**: Text embedding generation using all-MiniLM-L6-v2 model
- **OpenAI Integration**: GPT models for natural language understanding and generation
- **Document Processing**: PDF text extraction and chunking with PyPDF2

### Data Flow
1. Client data collected through UI and stored in Streamlit session state
2. Data processed by calculation and simulation engines
3. Results presented as interactive visualizations and recommendations
4. Advisor queries processed by vector search and AI response system

## Features

### Client Profile Management
Comprehensive client information collection with integrated risk assessment:
- Personal details (name, age, contact information)
- Financial information (income, employment stability, savings)
- Mortgage details (principal, term, interest rate, amortization period)
- Family composition and dependent information
- Health factors and risk tolerance evaluation

### Mortgage Journey Tracker
Interactive visualization and management of the mortgage application process:
- Visual timeline from initial inquiry through post-funding stages
- Protection discussion status tracking with automated reminders
- Algorithmic identification of optimal insurance conversation opportunities
- Dynamic conversation guides tailored to current journey stage
- Life event logging with automatic protection need reassessment

### WIPT Calculator (What If Payment Tool)
Advanced mortgage payment simulation and visualization tool:
- Multi-frequency payment calculations (weekly, biweekly, monthly, semi-monthly)
- Side-by-side comparison of multiple interest rate scenarios
- Interactive payment breakdown charts showing principal vs. interest
- Amortization analysis with dynamic visualization
- Comprehensive interest cost projections over various terms

### Scenario Simulator
Comprehensive financial impact modeling for critical life events:
- **Job Loss**: EI benefit integration, savings depletion timeline, and monthly shortfall analysis
- **Disability**: Income reduction modeling, medical expense impacts, and recovery timeline
- **Critical Illness**: Financial impact projections with treatment cost analysis
- **Death**: Surviving family financial gap analysis and support requirement calculations
- All scenarios include side-by-side comparisons with and without insurance protection

### Insurance Recommendation Engine
Intelligent insurance product recommendation system:
- Data-driven coverage calculations based on client risk profile
- Personalized premium estimates using demographic and health factors
- Clear recommendation rationales with client-specific benefits
- Smart prioritization of coverage types based on vulnerability analysis
- Interactive protection gap visualization and comparison

### AI Advisor Assistant
Sophisticated AI-powered knowledge assistant:
- ChromaDB-powered semantic search across product documentation
- Natural language processing for complex mortgage and insurance queries
- Detailed product comparison and feature explanation capabilities
- Context-aware responses incorporating client profile information
- Comprehensive objection handling with evidence-based counterpoints

### Document Management System
Integrated document processing and knowledge management platform:
- Streamlined PDF document uploading and processing
- Intelligent text extraction with automatic chunking
- Vector embedding generation for semantic search functionality
- Built-in document viewer with navigation controls
- Expandable knowledge base through continuous document additions

## Usage Guide

### Recommended Workflow
The application is designed with an intuitive workflow that guides advisors through the client consultation process:

1. **Client Profile** → 2. **Mortgage Journey Tracker** → 3. **WIPT Calculator** → 4. **Insurance Recommendations** → 5. **Scenario Simulator**

### Client Profile

1. Complete the client information form with relevant details:
   - Personal information (name, age, contact details)
   - Employment information (occupation, income, job stability)
   - Mortgage details (current balance, property value)
   - Family composition (marital status, dependents)
   - Health factors (smoker status, medical conditions)
   - Risk tolerance assessment

2. Sample client profile:
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

3. Click 'Save Profile' to store the information in the session state for use across all application modules

### Mortgage Journey Tracker

1. Configure the mortgage journey parameters:
   - Select mortgage type (New Purchase, Refinance, Renewal, Transfer, Investment Property)
   - Set the current application stage
   - Update protection discussion status (Not Discussed, Briefly Mentioned, Detailed Discussion, etc.)
   - Record relevant life events that may impact protection needs

2. View the interactive timeline visualization showing the client's progress through the mortgage process

3. Identify optimal protection discussion opportunities (highlighted with a star icon)

4. Add stage-specific notes to document client conversations and decisions

### WIPT Calculator

1. Input the mortgage parameters:
   - Principal amount (loan value)
   - Annual interest rate (percentage)
   - Term length (1-10 years)
   - Amortization period (5-30 years)
   - Payment frequency (weekly, biweekly, monthly, semi-monthly)

2. Create multiple interest rate scenarios for comparison:
   - Use the "Add Scenario" button to create alternative rate scenarios
   - Typical scenarios include current rate, +1%, +2%, and stress test rates
   - Each scenario will be color-coded in the visualization

3. Review the interactive visualization results:
   - Payment amount comparison across all scenarios
   - Principal vs. interest breakdown charts
   - Amortization timeline visualization
   - Total interest cost calculation over the term and amortization period

### Scenario Simulator

1. Choose from four life event scenarios to simulate:
   - **Job Loss**: Temporary unemployment impact analysis
   - **Disability**: Short or long-term disability financial modeling
   - **Critical Illness**: Serious health condition financial impact
   - **Death of Primary Earner**: Family financial sustainability analysis

2. Configure the scenario parameters based on client circumstances:

   **Job Loss Scenario:**
   - Expected unemployment duration (months)
   - Estimated monthly Employment Insurance benefits
   - Available emergency savings
   - Essential monthly expenses (mortgage, utilities, food, etc.)

   **Disability Scenario:**
   - Projected disability duration
   - Income replacement from existing disability coverage
   - Available emergency savings
   - Essential expenses plus anticipated medical costs

   **Critical Illness Scenario:**
   - Estimated recovery period
   - Income reduction during recovery
   - Available emergency savings
   - Regular expenses plus treatment costs

   **Death Scenario:**
   - Existing life insurance coverage
   - Remaining household income
   - Available emergency savings
   - Ongoing family expenses

3. Analyze the comprehensive simulation results:
   - Monthly cash flow shortfall calculation
   - Cumulative financial impact over time
   - Emergency savings depletion timeline
   - Side-by-side comparison with and without insurance protection

4. Use the interactive visualizations to demonstrate the value of appropriate coverage

### Insurance Recommendations

1. Access the personalized insurance recommendations generated from the client profile data

2. Review comprehensive coverage recommendations across protection types:
   - Life insurance (mortgage balance and additional family needs)
   - Disability insurance (income replacement during inability to work)
   - Critical illness coverage (lump sum for treatment and recovery costs)
   - Job loss protection (mortgage payment coverage during unemployment)

3. Each recommendation provides detailed information:
   - Data-driven coverage amount with calculation methodology
   - Estimated monthly premium based on client demographics
   - Priority classification (Essential, Recommended, Optional)
   - Client-specific benefit explanation and value proposition

4. Leverage the provided conversation guides and objection handling tips during client discussions

### AI Advisor Assistant

1. Access the AI Advisor Assistant from the sidebar navigation

2. Enter specific questions about mortgage products, insurance policies, or advisory best practices

3. The system will perform semantic search across the knowledge base and generate comprehensive responses

4. Example questions the assistant can answer:
   ```
   "What is the difference between term and whole life insurance?"
   "How does HomeProtector insurance work with mortgage renewals?"
   "What happens to mortgage insurance if a client sells their home?"
   "What are the eligibility requirements for disability coverage?"
   "How are premiums calculated for critical illness insurance?"
   "What exclusions apply to disability coverage?"
   "Can clients have both individual life insurance and mortgage insurance?"
   ```

5. Use the AI-generated responses to enhance client conversations and provide accurate information

### Document Management

1. Navigate to the Document Management section in the sidebar

2. Add new documents to the knowledge base:
   - Click the "Upload Document" button
   - Select a PDF file containing product information or policies
   - The system will automatically extract text, create chunks, and generate embeddings
   - New information is immediately available for search via the AI Assistant

3. Access and view existing documents:
   - Select any document from the dropdown menu
   - View the PDF directly within the application interface
   - All document content is searchable through the AI Assistant's semantic search

## Advanced Usage

### CRM Integration

Certus can be integrated with external client management systems:

1. Modify the `profile.json` structure to align with your CRM data schema
2. Implement API connectors in `utils.py` to synchronize client data
3. Update the `client_profile_form()` function in `app.py` to handle external data sources
4. Add authentication handlers if required for your CRM system

### Knowledge Base Expansion

Extend the AI Assistant's knowledge with additional documents:

1. Prepare PDF documents containing product information, policies, or guidelines
2. Use the Document Management interface to upload and process these files
3. The system automatically handles text extraction, chunking, and embedding generation
4. All new information becomes immediately searchable through the AI Assistant
5. Consider organizing documents by product type for better search results

### Custom Scenario Development

Create additional financial simulation scenarios:

1. Add new scenario types to the `scenario_simulator()` function in `app.py`
2. Define scenario-specific input parameters and calculation logic
3. Develop interactive visualizations using the Plotly library
4. Create explanation templates with HTML formatting for consistent presentation
5. Add corresponding recommendation logic in the insurance recommendation engine

## Development Guide

### Project Structure

```
├── app.py                 # Main Streamlit application with UI components
├── backend/               # Backend service modules
│   ├── __init__.py
│   ├── conversation_guides.py      # Advisor conversation templates
│   ├── early_journey_integration.py # Protection opportunity detection
│   ├── journey_visualization.py    # Timeline visualization components
│   └── mortgage_journey.py         # Mortgage journey state machine
├── config.py              # Application settings and constants
├── docs/                  # Document storage directory
│   └── home_protector_creditor.pdf # Sample product documentation
├── logo.png               # Certus application logo
├── models.py              # Pydantic data models and type definitions
├── profile.json           # Sample client profile template
├── requirements.txt       # Python dependencies
├── utils.py               # Shared utility functions
└── vector_db/            # ChromaDB vector database (created at runtime)
```

### Adding New Features

1. Define data models in `models.py` using Pydantic with proper validation
2. Implement core business logic in the appropriate backend module
3. Create UI components in `app.py` using Streamlit widgets
4. Add any new configuration parameters to `config.py`
5. Update tests to cover new functionality

### Code Style Guidelines

- Follow PEP 8 conventions for Python code style
- Organize imports alphabetically by standard, third-party, and local modules
- Document all functions with descriptive docstrings including parameters and return values
- Use type hints consistently throughout the codebase
- Maintain separation between UI components and business logic
- Use consistent naming conventions for variables and functions

## Data Privacy

- All client information is processed locally within the Streamlit session state
- No client data is persisted between sessions or stored in external databases
- OpenAI API calls contain only anonymized queries with no personally identifiable information
- Vector database stores only product documentation, never client details
- All session data is automatically cleared when the application is closed
- No tracking or analytics code is included in the application

## Troubleshooting

### Common Issues and Solutions

- **Application Startup Problems**: 
  - Ensure all dependencies are installed with `pip install -r requirements.txt`
  - Verify Python version is 3.8 or higher (use `python --version` to check)
  - Look for detailed error messages in the console output
  - Check that port 8501 is not in use by another application

- **Vector Search Functionality**: 
  - Verify the vector_db directory has appropriate write permissions
  - Confirm ChromaDB installation is complete with all dependencies
  - Try uploading a new document to reinitialize the database
  - Check for any ChromaDB version compatibility issues

- **OpenAI Integration**: 
  - Ensure your API key is correctly configured in config.py or as an environment variable
  - Monitor for API rate limits or quota exhaustion in the OpenAI dashboard
  - Verify you have access permissions for the models being used
  - Check network connectivity to OpenAI's API endpoints

- **Visualization Issues**: 
  - Confirm Plotly and Pandas are properly installed and compatible
  - Ensure client data inputs are within expected numerical ranges
  - Check that all numeric fields have consistent data types (float or int)
  - Clear browser cache if visualizations appear corrupted

- **Document Processing**: 
  - Verify PDF files are not password-protected or encrypted
  - Ensure PyPDF2 is properly installed with `pip install PyPDF2==3.0.0`
  - Check that the docs directory exists with appropriate permissions
  - Limit PDF size to under 10MB for optimal processing
