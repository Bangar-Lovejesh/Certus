# RBC Mortgage & Creditor Insurance Advisor Assistant

A comprehensive AI-powered virtual assistant designed to assist RBC financial advisors in providing personalized mortgage and creditor insurance advice to clients. The application uses a Streamlit interface with ChromaDB vector search capabilities to deliver context-aware recommendations and intelligent alerts.

## Overview

This tool helps RBC advisors:
- Access AI-powered assistance for mortgage and insurance advice through a chatbot interface
- Collect and manage client information through an intuitive interface
- Get context-aware recommendations based on the current screen
- Receive intelligent alerts for cross-selling opportunities
- Simulate financial impacts of life events on clients
- Calculate mortgage payments and insurance premiums
- Access RBC product information through vector search

## Table of Contents

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Features](#features)
- [Usage Guide](#usage-guide)
- [Data Privacy](#data-privacy)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the FastAPI server:
   ```bash
   cd backend
   uvicorn api:app --reload
   ```

3. Access the application:
   Open your browser and navigate to `http://localhost:8000`

### API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
   ```

## Getting Started

1. Start the application:
   ```bash
   streamlit run backend/app.py
   ```

2. The app will open in your default web browser at `http://localhost:8501`

## Features

### Client Profile
Collect and store client information to generate personalized advice:
- Personal details
- Financial information
- Risk tolerance
- Family composition

### WIPT Calculator (What If Payment Tool)
Calculate how different interest rates affect mortgage payments:
- Compare current vs. potential future rates
- Visualize payment breakdowns
- Analyze amortization scenarios

### Scenario Simulator
Model the financial impact of life events:
- Job loss
- Critical illness
- Disability
- Death of a family member

### Insurance Options
Recommend appropriate insurance products based on client profile:
- Life insurance
- Disability coverage
- Critical illness protection
- Job loss protection

### Advisor Assistant
AI-powered chatbot providing:
- Product information
- Policy details
- Recommendation rationales
- Client-friendly explanations

## Usage Guide

### Navigation
Use the sidebar to navigate between different sections of the app.

### Client Profile

1. Enter the client's personal information:
   - Name, age, contact information
   - Occupation and income details
   - Current mortgage information
   - Family situation

2. Example input:
   ```
   Full Name: Sarah Johnson
   Age: 35
   Email: sarah.johnson@example.com
   Phone: 416-555-7890
   Occupation: Software Developer
   Annual Income: $95,000
   Current Mortgage Balance: $450,000
   Property Value: $650,000
   Dependents: 2
   Risk Tolerance: Moderate
   ```

### WIPT Calculator

1. Enter mortgage details:
   - Principal amount
   - Amortization period
   - Term length
   - Current interest rate
   - Payment frequency

2. Add alternative rate scenarios to compare payments

3. Example input:
   ```
   Mortgage Amount: $450,000
   Amortization Period: 25 years
   Term: 5 years
   Current Interest Rate: 4.5%
   Payment Frequency: Monthly
   Alternative Rate Scenario: 5.5%
   ```

### Scenario Simulator

1. Select life events to simulate:
   - Duration of potential job loss
   - Probability of critical illness
   - Potential disability period
   - Impact of primary earner's death

2. View the financial impact analysis and recommended protection options

### Insurance Options

1. Select the types of insurance coverage to explore:
   - Life insurance
   - Disability insurance
   - Critical illness coverage
   - Job loss protection

2. Review personalized recommendations based on the client profile

### Advisor Assistant

1. Type questions about RBC products or policies in the chat interface
2. Receive detailed, client-friendly responses you can share directly
3. Example questions:
   ```
   "What is the difference between term and whole life insurance?"
   "How does the RBC HomeProtector insurance work?"
   "What happens to mortgage insurance if my client sells their home?"
   "What are the eligibility requirements for disability coverage?"
   ```

## Data Privacy

- All client data is processed locally and not stored permanently
- No personal information is transmitted to external servers
- Session data is cleared when the application is closed

## Troubleshooting

### Common Issues

- **Application won't start**: Ensure all dependencies are installed and Python version is compatible
- **Visualization errors**: Check that input data is in the correct format
- **Rerun errors**: If you encounter `st.experimental_rerun()` errors, update to `st.rerun()` in the code
