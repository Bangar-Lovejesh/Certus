# RBC Mortgage & Creditor Insurance Advisor Assistant

An AI-powered virtual assistant designed to assist RBC mortgage specialists and advisors in providing personalized mortgage and creditor insurance advice to clients. The application uses Streamlit for the UI and ChromaDB for vector search capabilities.

## Overview

This tool helps RBC advisors:
- Access AI-powered assistance for mortgage and insurance advice through a chatbot interface
- Collect and manage client information through an intuitive interface
- Calculate mortgage payments with the WIPT (What If Payment Tool) calculator
- Get personalized insurance recommendations based on client profiles
- Simulate financial impacts of life events on clients (job loss, disability, critical illness, death)
- Receive context-aware advisor alerts for cross-selling opportunities
- Access RBC product information through vector search

## Table of Contents

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Features](#features)
- [Usage Guide](#usage-guide)
- [Data Privacy](#data-privacy)
- [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository or download the source code

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Make sure you have an OpenAI API key and set it in the config.py file or as an environment variable named OPENAI_API_KEY

## Getting Started

1. Start the application:
   ```bash
   streamlit run app.py
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

### Document Management
Manage and search through RBC product documentation:
- Upload PDF documents
- Vector search for relevant information
- View document content within the app

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

### Scenario Simulator

1. Select life events to simulate:
   - Duration of potential job loss
   - Probability of critical illness
   - Potential disability period
   - Impact of primary earner's death

2. View the financial impact analysis and recommended protection options

### Insurance Options

1. Review personalized recommendations based on the client profile for:
   - Life insurance
   - Disability insurance
   - Critical illness coverage
   - Job loss protection

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
- **Vector search errors**: Make sure the vector database directory exists and has proper permissions
- **OpenAI API errors**: Verify your API key is correctly set in config.py or as an environment variable
