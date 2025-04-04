"""
Certus - Mortgage & Creditor Insurance Advisor Assistant
Main Streamlit Application
"""
import os
import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import base64
from datetime import datetime
import uuid

# Import local modules
from config import (
    APP_TITLE,
    APP_SUBTITLE,
    APP_ICON, 
    PRIMARY_COLOR, 
    SECONDARY_COLOR, 
    TEXT_COLOR, 
    BACKGROUND_COLOR,
    DOCS_DIR
)
from utils import (
    retrieve_relevant_chunks,
    generate_response,
    calculate_mortgage_payment,
    get_base64_encoded_image,
    get_base64_pdf,
    extract_text_from_pdf,
    split_text_into_chunks,
    initialize_db,
    assess_risk_level,
    calculate_insurance_premium
)
from models import (
    ClientProfile,
    MortgageDetails,
    InsuranceCoverage,
    CoverageType,
    PaymentFrequency,
    RiskLevel,
    ScreenType,
    AdvisorAlert,
    ChatMessage,
    InsuranceRecommendation
)
from backend.mortgage_journey import (
    MortgageJourney,
    MortgageJourneyStage,
    MortgageType,
    ProtectionDiscussionStatus,
    LifeEvent,
    get_journey_stage_description
)
from backend.conversation_guides import (
    create_personalized_guide,
    get_discovery_conversation_template,
    get_protection_benefits_template,
    get_what_if_scenario_template,
    get_objection_handling_tips
)
from backend.early_journey_integration import (
    identify_protection_opportunities,
    generate_protection_discussion_guide,
    ProtectionDiscussionTracker
)
from backend.journey_visualization import (
    create_journey_timeline,
    create_protection_opportunity_gauge,
    create_protection_impact_chart
)
# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if "client_data" not in st.session_state:
    st.session_state.client_data = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_screen" not in st.session_state:
    st.session_state.current_screen = ScreenType.CLIENT_PROFILE
if "alerts" not in st.session_state:
    st.session_state.alerts = []
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Initialize mortgage journey state variables
if "mortgage_journey" not in st.session_state:
    # Create default journey
    st.session_state.mortgage_journey = MortgageJourney(
        client_id=st.session_state.session_id,
        mortgage_type=MortgageType.NEW_PURCHASE,
        current_stage=MortgageJourneyStage.INITIAL_INQUIRY,
        started_at=datetime.now(),
        protection_discussion=ProtectionDiscussionStatus.NOT_DISCUSSED
    )
if "protection_discussion_tracker" not in st.session_state:
    st.session_state.protection_discussion_tracker = ProtectionDiscussionTracker(
        client_id=st.session_state.session_id
    )
if "conversation_guide" not in st.session_state:
    st.session_state.conversation_guide = None

def apply_certus_styling():
    """Apply Certus brand styling to the Streamlit app"""
    # Custom CSS for RBC styling
    st.markdown(f"""
    <style>
        /* RBC Colors */
        :root {{
            --primary-color: {PRIMARY_COLOR};
            --secondary-color: {SECONDARY_COLOR};
            --text-color: {TEXT_COLOR};
            --background-color: {BACKGROUND_COLOR};
        }}
        
        /* Base styling */
        .stApp {{
            background-color: var(--background-color);
            color: var(--text-color);
        }}
        
        /* Headers */
        h1, h2, h3 {{
            color: var(--primary-color) !important;
            font-family: 'Arial', sans-serif;
        }}
        
        /* Buttons */
        .stButton>button {{
            background-color: var(--primary-color);
            color: white;
            border-radius: 5px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: bold;
        }}
        
        .stButton>button:hover {{
            background-color: #003399;
            color: var(--secondary-color);
        }}
        
        /* Sidebar */
        .css-1d391kg {{
            background-color: #1E1E1E;
        }}
        
        /* Input fields */
        .stTextInput>div>div>input, .stNumberInput>div>div>input {{
            background-color: #2A2A2A;
            color: white;
            border: 1px solid #444;
            border-radius: 5px;
        }}
        
        /* Chat messages */
        .user-message {{
            background-color: #2A2A2A;
            padding: 10px 15px;
            border-radius: 15px 15px 15px 0;
            margin: 5px 0;
            max-width: 80%;
            align-self: flex-start;
        }}
        
        .assistant-message {{
            background-color: var(--primary-color);
            padding: 10px 15px;
            border-radius: 15px 15px 0 15px;
            margin: 5px 0;
            max-width: 80%;
            align-self: flex-end;
            margin-left: auto;
        }}
        
        /* Alert boxes */
        .alert-box {{
            padding: 10px 15px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        
        .alert-high {{
            background-color: rgba(255, 0, 0, 0.2);
            border-left: 5px solid red;
        }}
        
        .alert-medium {{
            background-color: rgba(255, 165, 0, 0.2);
            border-left: 5px solid orange;
        }}
        
        .alert-low {{
            background-color: rgba(0, 128, 0, 0.2);
            border-left: 5px solid green;
        }}
        
        /* Cards */
        .info-card {{
            background-color: #2A2A2A;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            border: 1px solid #444;
        }}
        
        /* Tables */
        .dataframe {{
            background-color: #2A2A2A !important;
            color: white !important;
        }}
        
        .dataframe th {{
            background-color: var(--primary-color) !important;
            color: white !important;
        }}
        
        /* Custom Certus logo header */
        .rbc-header {{
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            padding: 10px;
            background-color: #0A0A0A;
            border-bottom: 2px solid var(--primary-color);
        }}
        
        .rbc-logo {{
            height: 40px;
            margin-right: 15px;
        }}
        
        .rbc-title {{
            color: white;
            font-size: 1.8rem;
            font-weight: bold;
        }}
        
        .rbc-subtitle {{
            color: #cccccc;
            font-size: 1rem;
            margin-left: 15px;
            align-self: flex-end;
        }}
    </style>
    """, unsafe_allow_html=True)

    # Create Certus header with logo
    if os.path.exists("logo.png"):
        logo_base64 = get_base64_encoded_image("logo.png")
        st.markdown(f"""
        <div class="rbc-header">
            <img src="data:image/png;base64,{logo_base64}" class="rbc-logo">
            <div class="rbc-title">{APP_TITLE}</div>
            <div class="rbc-subtitle">{APP_SUBTITLE}</div>
        </div>
        """, unsafe_allow_html=True)

def display_pdf(pdf_path):
    """Display a PDF file in the Streamlit app"""
    try:
        with open(pdf_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        
        pdf_display = f"""
        <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>
        """
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying PDF: {e}")

def upload_and_process_document():
    """Upload and process a document for the knowledge base"""
    st.subheader("Upload Document to Knowledge Base")
    
    uploaded_file = st.file_uploader("Upload PDF document", type=["pdf"])
    
    if uploaded_file is not None:
        # Create docs directory if it doesn't exist
        os.makedirs(DOCS_DIR, exist_ok=True)
        
        # Save the uploaded file
        file_path = os.path.join(DOCS_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.info(f"Processing {uploaded_file.name}...")
        
        # Extract text from PDF
        text = extract_text_from_pdf(file_path)
        
        # Split text into chunks
        chunks = split_text_into_chunks(text)
        
        # Prepare documents for vector database
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                "id": f"{uploaded_file.name}-chunk-{i}",
                "content": chunk,
                "source": uploaded_file.name
            })
        
        # Initialize database with documents
        success = initialize_db(documents)
        
        if success:
            st.success(f"Successfully processed {uploaded_file.name} and added to the knowledge base.")
        else:
            st.error("There was an error processing the document.")

def chatbot_interface():
    """Create a chatbot interface for advisor questions"""
    st.subheader("AI Advisor Assistant")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"<div class='user-message'><strong>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='assistant-message'><strong>AI Assistant:</strong> {message['content']}</div>", unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input("Ask a question about RBC mortgage or insurance products:", key="chat_input")
    send_button = st.button("Send")
    
    # Use a form to prevent rerun loops
    if send_button and user_input:
        # Check if this is a new message (not just a rerun with the same input)
        if "last_input" not in st.session_state or user_input != st.session_state.last_input:
            # Store this input to prevent duplicate processing
            st.session_state.last_input = user_input
            
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input, "timestamp": str(datetime.now())})
            
            # Get relevant documents
            relevant_docs = retrieve_relevant_chunks(user_input)
            
            # Generate response
            response = generate_response(user_input, relevant_docs)
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response, "timestamp": str(datetime.now())})
            
            # Rerun to update the chat display
            st.rerun()

def calculate_insurance_premiums(client_data):
    """Calculate insurance premiums based on client data"""
    age = client_data.get("age", 35)
    mortgage_amount = client_data.get("mortgage_amount", 300000)
    risk_level = client_data.get("risk_level", "Medium")
    
    premiums = {}
    
    # Life insurance premium
    if 18 <= age <= 69:
        premiums["life"] = calculate_insurance_premium(
            age, 
            mortgage_amount, 
            "life", 
            joint=client_data.get("joint_applicant", False),
            risk_level=risk_level
        )
    
    # Disability insurance premium
    if 18 <= age <= 65:
        monthly_payment = calculate_mortgage_payment(
            mortgage_amount,
            client_data.get("interest_rate", 4.5),
            client_data.get("amortization_years", 25)
        )
        
        premiums["disability"] = calculate_insurance_premium(
            age, 
            monthly_payment * 24,  # 24 months of coverage 
            "disability", 
            joint=client_data.get("joint_applicant", False),
            risk_level=risk_level
        )
    
    # Critical illness insurance premium
    if 18 <= age <= 55:
        premiums["critical_illness"] = calculate_insurance_premium(
            age, 
            min(mortgage_amount, 300000),  # Max coverage of $300,000
            "critical_illness", 
            joint=client_data.get("joint_applicant", False),
            risk_level=risk_level
        )
    
    return premiums

def client_profile_form():
    """Create a form to collect client data"""
    st.subheader("Client Profile")    
    st.markdown("<div class='info-card'>Enter client information to generate personalized recommendations</div>", unsafe_allow_html=True)
    
    with st.form("client_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name", value=st.session_state.client_data.get("full_name", ""))
            age = st.number_input("Age", min_value=18, max_value=100, value=st.session_state.client_data.get("age", 35))
            email = st.text_input("Email", value=st.session_state.client_data.get("email", ""))
            phone = st.text_input("Phone", value=st.session_state.client_data.get("phone", ""))
            occupation = st.text_input("Occupation", value=st.session_state.client_data.get("occupation", ""))
            annual_income = st.number_input("Annual Income ($)", min_value=0, value=st.session_state.client_data.get("annual_income", 75000))
            years_at_job = st.number_input("Years at Current Job", min_value=0.0, value=st.session_state.client_data.get("years_at_current_job", 3.0), step=0.5)
        
        with col2:
            mortgage_amount = st.number_input("Mortgage Amount ($)", min_value=0, value=st.session_state.client_data.get("mortgage_amount", 350000))
            property_value = st.number_input("Property Value ($)", min_value=0, value=st.session_state.client_data.get("property_value", 500000))
            interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, max_value=30.0, value=st.session_state.client_data.get("interest_rate", 4.5), step=0.1)
            amortization_years = st.number_input("Amortization Period (years)", min_value=5, max_value=30, value=st.session_state.client_data.get("amortization_years", 25))
            dependents = st.number_input("Number of Dependents", min_value=0, value=st.session_state.client_data.get("dependents", 0))
            joint_applicant = st.checkbox("Joint Applicant", value=st.session_state.client_data.get("joint_applicant", False))
            smoker = st.checkbox("Smoker", value=st.session_state.client_data.get("smoker", False))
            pre_existing_conditions = st.checkbox("Pre-existing Health Conditions", value=st.session_state.client_data.get("pre_existing_conditions", False))
        
        risk_tolerance = st.select_slider(
            "Risk Tolerance",
            options=["Low", "Medium", "High"],
            value=st.session_state.client_data.get("risk_tolerance", "Medium")
        )
        
        submitted = st.form_submit_button("Save Client Profile")
        
        if submitted:
            # Update client data in session state
            st.session_state.client_data = {
                "full_name": full_name,
                "age": age,
                "email": email,
                "phone": phone,
                "occupation": occupation,
                "annual_income": annual_income,
                "years_at_current_job": years_at_job,
                "mortgage_amount": mortgage_amount,
                "property_value": property_value,
                "interest_rate": interest_rate,
                "amortization_years": amortization_years,
                "dependents": dependents,
                "joint_applicant": joint_applicant,
                "smoker": smoker,
                "pre_existing_conditions": pre_existing_conditions,
                "risk_tolerance": risk_tolerance
            }
            
            # Calculate risk level
            risk_level = assess_risk_level(st.session_state.client_data)
            st.session_state.client_data["risk_level"] = risk_level
            
            # Generate insurance recommendations
            generate_insurance_recommendations(st.session_state.client_data)
            
            st.success("Client profile saved successfully!")
            st.rerun()
    
    # Display client risk level if available
    if "risk_level" in st.session_state.client_data:
        risk_level = st.session_state.client_data["risk_level"]
        risk_color = {
            "Low": "green",
            "Medium": "orange",
            "High": "red"
        }.get(risk_level, "orange")
        
        st.markdown(f"""
        <div class='alert-box alert-{risk_level.lower()}'>
            <h3>Client Risk Assessment</h3>
            <p>Based on the provided information, this client has a <strong style='color:{risk_color}'>{risk_level} risk level</strong>.</p>
            <p>This assessment considers factors such as age, dependents, income stability, mortgage-to-income ratio, and health factors.</p>
        </div>
        """, unsafe_allow_html=True)

def wipt_calculator():
    """What If Payment Tool (WIPT) calculator for mortgage payments"""
    st.subheader("What If Payment Tool (WIPT)")
    st.markdown("<div class='info-card'>Calculate how different interest rates affect mortgage payments</div>", unsafe_allow_html=True)
    
    # Use client data if available
    default_mortgage = st.session_state.client_data.get("mortgage_amount", 350000)
    default_rate = st.session_state.client_data.get("interest_rate", 4.5)
    default_amortization = st.session_state.client_data.get("amortization_years", 25)
    
    with st.form("wipt_calculator_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            mortgage_amount = st.number_input("Mortgage Amount ($)", min_value=10000, value=default_mortgage)
            current_rate = st.number_input("Current Interest Rate (%)", min_value=0.1, max_value=30.0, value=default_rate, step=0.1)
            amortization_years = st.number_input("Amortization Period (years)", min_value=5, max_value=30, value=default_amortization)
        
        with col2:
            payment_frequency = st.selectbox(
                "Payment Frequency",
                options=["monthly", "biweekly", "weekly", "semi_monthly"],
                format_func=lambda x: x.replace("_", "-").title(),
                index=0
            )
            alternative_rate = st.number_input("Alternative Interest Rate (%)", min_value=0.1, max_value=30.0, value=current_rate + 1.0, step=0.1)
            term_years = st.number_input("Term Length (years)", min_value=1, max_value=10, value=5)
        
        calculate_button = st.form_submit_button("Calculate Payments")
    
    if calculate_button or "wipt_results" in st.session_state:
        # Calculate current payment
        current_payment = calculate_mortgage_payment(mortgage_amount, current_rate, amortization_years, payment_frequency)
        
        # Calculate alternative payment
        alternative_payment = calculate_mortgage_payment(mortgage_amount, alternative_rate, amortization_years, payment_frequency)
        
        # Calculate difference
        payment_difference = alternative_payment - current_payment
        percentage_increase = (payment_difference / current_payment) * 100
        
        # Store results in session state
        st.session_state.wipt_results = {
            "current_payment": current_payment,
            "alternative_payment": alternative_payment,
            "payment_difference": payment_difference,
            "percentage_increase": percentage_increase,
            "mortgage_amount": mortgage_amount,
            "current_rate": current_rate,
            "alternative_rate": alternative_rate,
            "amortization_years": amortization_years,
            "payment_frequency": payment_frequency,
            "term_years": term_years
        }
        
        # Display results
        st.subheader("Payment Comparison")
        
        # Create comparison table
        comparison_data = {
            "Scenario": ["Current Rate", "Alternative Rate", "Difference"],
            "Interest Rate": [f"{current_rate:.2f}%", f"{alternative_rate:.2f}%", f"{alternative_rate - current_rate:.2f}%"],
            f"Payment ({payment_frequency.replace('_', '-').title()})": [
                f"${current_payment:.2f}",
                f"${alternative_payment:.2f}",
                f"${payment_difference:.2f}"
            ],
            "Monthly Equivalent": [
                f"${current_payment * (12 / {'monthly': 12, 'biweekly': 26, 'weekly': 52, 'semi_monthly': 24}[payment_frequency]):.2f}",
                f"${alternative_payment * (12 / {'monthly': 12, 'biweekly': 26, 'weekly': 52, 'semi_monthly': 24}[payment_frequency]):.2f}",
                f"${payment_difference * (12 / {'monthly': 12, 'biweekly': 26, 'weekly': 52, 'semi_monthly': 24}[payment_frequency]):.2f}"
            ],
            "Annual Equivalent": [
                f"${current_payment * {'monthly': 12, 'biweekly': 26, 'weekly': 52, 'semi_monthly': 24}[payment_frequency]:.2f}",
                f"${alternative_payment * {'monthly': 12, 'biweekly': 26, 'weekly': 52, 'semi_monthly': 24}[payment_frequency]:.2f}",
                f"${payment_difference * {'monthly': 12, 'biweekly': 26, 'weekly': 52, 'semi_monthly': 24}[payment_frequency]:.2f}"
            ]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        st.table(comparison_df)
        
        # Create payment breakdown chart
        st.subheader("Payment Breakdown Over Term")
        
        # Calculate total payments over term
        payments_per_year = {'monthly': 12, 'biweekly': 26, 'weekly': 52, 'semi_monthly': 24}[payment_frequency]
        total_payments = term_years * payments_per_year
        
        # Calculate interest and principal for current rate
        current_total = current_payment * total_payments
        current_principal = min(mortgage_amount, current_total)  # Can't pay more than the mortgage amount
        current_interest = current_total - current_principal
        
        # Calculate interest and principal for alternative rate
        alternative_total = alternative_payment * total_payments
        alternative_principal = min(mortgage_amount, alternative_total)  # Can't pay more than the mortgage amount
        alternative_interest = alternative_total - alternative_principal
        
        # Create the chart
        fig = go.Figure()
        
        # Current rate bar
        fig.add_trace(go.Bar(
            name=f'Principal (Current {current_rate}%)',
            x=['Current Rate'],
            y=[current_principal],
            marker_color='#0042B2'
        ))
        fig.add_trace(go.Bar(
            name=f'Interest (Current {current_rate}%)',
            x=['Current Rate'],
            y=[current_interest],
            marker_color='#0042B2',
            opacity=0.5
        ))
        
        # Alternative rate bar
        fig.add_trace(go.Bar(
            name=f'Principal (Alternative {alternative_rate}%)',
            x=['Alternative Rate'],
            y=[alternative_principal],
            marker_color='#FEDF01'
        ))
        fig.add_trace(go.Bar(
            name=f'Interest (Alternative {alternative_rate}%)',
            x=['Alternative Rate'],
            y=[alternative_interest],
            marker_color='#FEDF01',
            opacity=0.5
        ))
        
        # Update layout
        fig.update_layout(
            barmode='stack',
            title=f'Payment Breakdown Over {term_years} Year Term',
            xaxis_title='Scenario',
            yaxis_title='Amount ($)',
            legend_title='Components',
            template='plotly_dark',
            height=500,
            margin=dict(l=50, r=50, t=80, b=50),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display impact message
        if percentage_increase > 0:
            st.markdown(f"""
            <div class='alert-box alert-medium'>
                <h3>Payment Impact</h3>
                <p>If the interest rate increases from {current_rate:.2f}% to {alternative_rate:.2f}%, 
                your {payment_frequency.replace('_', '-')} payment will increase by <strong>${payment_difference:.2f}</strong> 
                (a {percentage_increase:.1f}% increase).</p>
                <p>This represents an additional <strong>${payment_difference * {'monthly': 12, 'biweekly': 26, 'weekly': 52, 'semi_monthly': 24}[payment_frequency]:.2f}</strong> per year.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add insurance recommendation if appropriate
            if percentage_increase > 10 and "recommendations" not in st.session_state:
                st.markdown(f"""
                <div class='alert-box alert-high'>
                    <h3>Recommendation</h3>
                    <p>This significant payment increase could impact your client's financial stability. 
                    Consider discussing HomeProtector insurance options to protect against potential financial hardship.</p>
                </div>
                """, unsafe_allow_html=True)

def generate_advisor_alert(client_data, current_screen):
    """Generate context-aware alerts for advisors based on client data and current screen"""
    alerts = []
    
    # Get client details
    age = client_data.get("age", 35)
    mortgage_amount = client_data.get("mortgage_amount", 0)
    property_value = client_data.get("property_value", 0)
    dependents = client_data.get("dependents", 0)
    risk_level = client_data.get("risk_level", "Medium")
    
    # Alert for high LTV ratio
    if property_value > 0 and mortgage_amount / property_value > 0.8:
        alerts.append({
            "alert_id": "high_ltv",
            "screen_type": ScreenType.MORTGAGE_APPLICATION,
            "title": "High Loan-to-Value Ratio",
            "message": "This mortgage has a high loan-to-value ratio. CMHC insurance is required and HomeProtector insurance is strongly recommended.",
            "action_required": True,
            "priority": "High"
        })
    
    # Alert for clients with dependents
    if dependents > 0 and current_screen == ScreenType.CLIENT_PROFILE:
        alerts.append({
            "alert_id": "dependents",
            "screen_type": ScreenType.CLIENT_PROFILE,
            "title": "Family Protection Opportunity",
            "message": f"Client has {dependents} dependents. Discuss how HomeProtector life insurance can protect their family's home in case of death.",
            "action_required": False,
            "priority": "Medium"
        })
    
    # Alert for clients approaching retirement
    if age > 50 and current_screen == ScreenType.CLIENT_PROFILE:
        alerts.append({
            "alert_id": "retirement_planning",
            "screen_type": ScreenType.CLIENT_PROFILE,
            "title": "Retirement Planning",
            "message": "Client is approaching retirement age. Discuss how HomeProtector disability insurance can protect their mortgage payments if they're unable to work before retirement.",
            "action_required": False,
            "priority": "Medium"
        })
    
    # Alert for high risk clients
    if risk_level == "High" and current_screen in [ScreenType.MORTGAGE_APPLICATION, ScreenType.PRODUCT_RECOMMENDATION]:
        alerts.append({
            "alert_id": "high_risk",
            "screen_type": current_screen,
            "title": "High Risk Client",
            "message": "This client has been assessed as high risk. Strongly recommend comprehensive HomeProtector coverage including life, disability, and critical illness protection.",
            "action_required": True,
            "priority": "High"
        })
    
    # Alert for payment calculator screen
    if current_screen == ScreenType.PAYMENT_CALCULATOR and "wipt_results" in st.session_state:
        wipt_results = st.session_state.wipt_results
        if wipt_results["percentage_increase"] > 15:
            alerts.append({
                "alert_id": "rate_increase_risk",
                "screen_type": ScreenType.PAYMENT_CALCULATOR,
                "title": "Significant Rate Increase Impact",
                "message": f"A {wipt_results['alternative_rate'] - wipt_results['current_rate']:.1f}% rate increase would significantly impact this client's payments. Discuss how HomeProtector disability insurance can provide payment protection.",
                "action_required": False,
                "priority": "Medium"
            })
    
    return alerts

def display_screen_alerts():
    """Display context-aware alerts for the current screen"""
    if not st.session_state.client_data:
        return
    
    # Generate alerts for current screen
    alerts = generate_advisor_alert(st.session_state.client_data, st.session_state.current_screen)
    
    # Display alerts
    if alerts:
        st.sidebar.subheader("Advisor Alerts")
        
        for alert in alerts:
            priority_class = {
                "High": "alert-high",
                "Medium": "alert-medium",
                "Low": "alert-low"
            }.get(alert["priority"], "alert-medium")
            
            st.sidebar.markdown(f"""
            <div class='alert-box {priority_class}'>
                <h4>{alert['title']}</h4>
                <p>{alert['message']}</p>
                {"<p><strong>Action Required</strong></p>" if alert['action_required'] else ""}
            </div>
            """, unsafe_allow_html=True)

def generate_insurance_recommendations(client_data):
    """Generate insurance recommendations based on client data"""
    recommendations = []
    
    # Get client details
    age = client_data.get("age", 35)
    mortgage_amount = client_data.get("mortgage_amount", 0)
    annual_income = client_data.get("annual_income", 0)
    dependents = client_data.get("dependents", 0)
    risk_level = client_data.get("risk_level", "Medium")
    joint_applicant = client_data.get("joint_applicant", False)
    
    # Calculate insurance premiums
    premiums = calculate_insurance_premiums(client_data)
    
    # Life insurance recommendation
    if 18 <= age <= 69 and mortgage_amount > 0:
        life_premium = premiums.get("life")
        if life_premium:
            priority = "Essential" if (dependents > 0 or risk_level == "High") else "Recommended"
            recommendations.append({
                "coverage_type": CoverageType.LIFE,
                "recommended_amount": mortgage_amount,
                "monthly_premium": life_premium / 12,  # Convert to monthly
                "rationale": f"Provides full mortgage protection in case of death. {'Especially important with dependents.' if dependents > 0 else ''}",
                "priority": priority
            })
    
    # Disability insurance recommendation
    if 18 <= age <= 65 and mortgage_amount > 0:
        disability_premium = premiums.get("disability")
        if disability_premium:
            # Calculate monthly mortgage payment
            monthly_payment = calculate_mortgage_payment(
                mortgage_amount,
                client_data.get("interest_rate", 4.5),
                client_data.get("amortization_years", 25)
            )
            
            priority = "Essential" if (annual_income > 0 and monthly_payment / annual_income * 12 > 0.3) else "Recommended"
            recommendations.append({
                "coverage_type": CoverageType.DISABILITY,
                "recommended_amount": monthly_payment * 24,  # 24 months of payments
                "monthly_premium": disability_premium / 12,  # Convert to monthly
                "rationale": f"Covers mortgage payments for up to 24 months if you're unable to work due to disability. {'Your mortgage payments are a significant portion of your income.' if priority == 'Essential' else ''}",
                "priority": priority
            })
    
    # Critical illness insurance recommendation
    if 18 <= age <= 55 and mortgage_amount > 0:
        ci_premium = premiums.get("critical_illness")
        if ci_premium:
            priority = "Recommended" if age > 40 or client_data.get("pre_existing_conditions", False) else "Optional"
            recommendations.append({
                "coverage_type": CoverageType.CRITICAL_ILLNESS,
                "recommended_amount": min(mortgage_amount, 300000),  # Max coverage of $300,000
                "monthly_premium": ci_premium / 12,  # Convert to monthly
                "rationale": "Provides a lump sum payment to help with your mortgage if you're diagnosed with a covered critical illness like cancer, heart attack, or stroke.",
                "priority": priority
            })
    
    # Job loss recommendation (not priced, just a recommendation)
    if annual_income > 0 and age < 55:
        monthly_payment = calculate_mortgage_payment(
            mortgage_amount,
            client_data.get("interest_rate", 4.5),
            client_data.get("amortization_years", 25)
        )
        
        # Only recommend if they've been at their job less than 5 years
        if client_data.get("years_at_current_job", 0) < 5:
            recommendations.append({
                "coverage_type": CoverageType.JOB_LOSS,
                "recommended_amount": monthly_payment * 6,  # 6 months of payments
                "monthly_premium": monthly_payment * 0.03,  # Rough estimate
                "rationale": "Helps cover mortgage payments for up to 6 months if you lose your job involuntarily. Recommended for those with less job security.",
                "priority": "Optional"
            })
    
    # Store recommendations in session state
    st.session_state.recommendations = recommendations
    
    return recommendations

def display_insurance_recommendations():
    """Display insurance recommendations to the advisor"""
    if not st.session_state.recommendations:
        st.info("Complete the client profile to see personalized insurance recommendations.")
        return
    
    st.subheader("Insurance Recommendations")
    st.markdown("<div class='info-card'>Personalized coverage recommendations based on client profile</div>", unsafe_allow_html=True)
    
    # Group recommendations by priority
    essential = [r for r in st.session_state.recommendations if r["priority"] == "Essential"]
    recommended = [r for r in st.session_state.recommendations if r["priority"] == "Recommended"]
    optional = [r for r in st.session_state.recommendations if r["priority"] == "Optional"]
    
    # Display essential recommendations
    if essential:
        st.markdown("### Essential Coverage")
        for rec in essential:
            coverage_type = rec["coverage_type"].value.replace("_", " ").title()
            st.markdown(f"""
            <div class='alert-box alert-high'>
                <h4>{coverage_type} Insurance</h4>
                <p><strong>Recommended Coverage:</strong> ${rec['recommended_amount']:,.2f}</p>
                <p><strong>Monthly Premium:</strong> ${rec['monthly_premium']:,.2f}</p>
                <p>{rec['rationale']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Display recommended coverage
    if recommended:
        st.markdown("### Recommended Coverage")
        for rec in recommended:
            coverage_type = rec["coverage_type"].value.replace("_", " ").title()
            st.markdown(f"""
            <div class='alert-box alert-medium'>
                <h4>{coverage_type} Insurance</h4>
                <p><strong>Recommended Coverage:</strong> ${rec['recommended_amount']:,.2f}</p>
                <p><strong>Monthly Premium:</strong> ${rec['monthly_premium']:,.2f}</p>
                <p>{rec['rationale']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Display optional coverage
    if optional:
        st.markdown("### Optional Coverage")
        for rec in optional:
            coverage_type = rec["coverage_type"].value.replace("_", " ").title()
            st.markdown(f"""
            <div class='alert-box alert-low'>
                <h4>{coverage_type} Insurance</h4>
                <p><strong>Recommended Coverage:</strong> ${rec['recommended_amount']:,.2f}</p>
                <p><strong>Monthly Premium:</strong> ${rec['monthly_premium']:,.2f}</p>
                <p>{rec['rationale']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Calculate total monthly premium
    total_monthly = sum(rec["monthly_premium"] for rec in st.session_state.recommendations)
    total_annual = total_monthly * 12
    
    # Display total cost
    st.markdown(f"""
    <div class='info-card'>
        <h4>Total Insurance Cost</h4>
        <p><strong>Monthly Premium:</strong> ${total_monthly:,.2f}</p>
        <p><strong>Annual Premium:</strong> ${total_annual:,.2f}</p>
        <p>This represents {total_annual / st.session_state.client_data.get('annual_income', 100000) * 100:.1f}% of the client's annual income.</p>
    </div>
    """, unsafe_allow_html=True)

def mortgage_journey_tracker():
    """Create a mortgage journey tracker interface"""
    st.header("Mortgage Journey Tracker")
    
    journey = st.session_state.mortgage_journey
    client_data = st.session_state.client_data
    
    # Journey configuration section
    with st.expander("Journey Configuration", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # Mortgage type selection
            mortgage_type = st.selectbox(
                "Mortgage Type",
                options=list(MortgageType),
                format_func=lambda x: x.value.replace('_', ' ').title(),
                index=list(MortgageType).index(journey.mortgage_type)
            )
            
            # Current stage selection
            current_stage = st.selectbox(
                "Current Journey Stage",
                options=list(MortgageJourneyStage),
                format_func=lambda x: get_journey_stage_description(x).get("name", x.value),
                index=list(MortgageJourneyStage).index(journey.current_stage)
            )
        
        with col2:
            # Protection discussion status
            protection_status = st.selectbox(
                "Protection Discussion Status",
                options=list(ProtectionDiscussionStatus),
                format_func=lambda x: x.value.replace('_', ' ').title(),
                index=list(ProtectionDiscussionStatus).index(journey.protection_discussion)
            )
            
            # Life events multi-select
            life_events = st.multiselect(
                "Recent Life Events",
                options=list(LifeEvent),
                default=journey.recent_life_events,
                format_func=lambda x: x.value.replace('_', ' ').title()
            )
        
        # Notes for the current stage
        stage_notes = st.text_area(
            "Notes for Current Stage",
            value=journey.notes.get(current_stage, ""),
            height=100
        )
        
        # Update button
        if st.button("Update Journey"):
            # Update journey in session state
            journey.mortgage_type = mortgage_type
            journey.update_stage(current_stage, stage_notes)
            journey.update_protection_discussion(protection_status)
            
            # Update life events
            journey.recent_life_events = life_events
            
            # Update protection discussion tracker
            st.session_state.protection_discussion_tracker.add_discussion(
                stage=current_stage,
                status=protection_status,
                notes=stage_notes
            )
            
            # Regenerate conversation guide
            st.session_state.conversation_guide = create_personalized_guide(
                client_data=client_data,
                journey_stage=current_stage,
                life_events=life_events
            )
            
            st.success("Journey updated successfully!")
            st.rerun()
    
    # Journey visualization
    st.subheader("Journey Timeline")
    timeline_fig = create_journey_timeline(journey)
    st.plotly_chart(timeline_fig, use_container_width=True)
    
    # Protection opportunity gauge
    col1, col2 = st.columns([1, 2])
    with col1:
        gauge_fig = create_protection_opportunity_gauge(journey, client_data)
        st.plotly_chart(gauge_fig, use_container_width=True)
    
    with col2:
        st.subheader("Optimal Protection Discussion")
        optimal_stage = journey.get_optimal_protection_discussion_stage()
        optimal_stage_info = get_journey_stage_description(optimal_stage)
        
        st.markdown(f"**Recommended Stage:** {optimal_stage_info.get('name', optimal_stage.value)}")
        st.markdown(f"**Current Status:** {journey.protection_discussion.value.replace('_', ' ').title()}")
        
        if journey.should_discuss_protection_now():
            st.success("✅ Now is an ideal time to discuss protection with this client.")
        else:
            st.info("ℹ️ Protection has been discussed or the optimal time has not yet arrived.")
    
    # Protection discussion guide
    st.subheader("Protection Discussion Guide")
    
    # Generate or retrieve conversation guide
    if not st.session_state.conversation_guide:
        st.session_state.conversation_guide = create_personalized_guide(
            client_data=client_data,
            journey_stage=journey.current_stage,
            life_events=journey.recent_life_events
        )
    
    guide = st.session_state.conversation_guide
    
    with st.expander("Conversation Template", expanded=True):
        st.markdown(f"**Title:** {guide.template.title}")
        st.markdown(f"**Objective:** {guide.template.objective}")
        
        st.markdown("**Key Questions:**")
        for question in guide.template.key_questions:
            st.markdown(f"- {question}")
        
        st.markdown("**General Talking Points:**")
        for point in guide.template.talking_points:
            st.markdown(f"- {point}")
    
    with st.expander("Client-Specific Guidance", expanded=True):
        st.markdown("**Personalized Talking Points:**")
        if guide.client_specific_points:
            for point in guide.client_specific_points:
                st.markdown(f"- {point}")
        else:
            st.info("Complete the client profile to see personalized talking points.")
        
        st.markdown(f"**Recommended Timing:** {guide.recommended_timing}")
        
        st.markdown("**Next Steps:**")
        for step in guide.next_steps:
            st.markdown(f"- {step}")
    
    with st.expander("Objection Handling", expanded=False):
        st.markdown("**Common Objections and Responses:**")
        for objection, response in guide.template.objection_responses.items():
            st.markdown(f"**If client says:** *{objection}*")
            st.markdown(f"**You can respond:** {response}")
    
    # Financial impact visualization
    st.subheader("Protection Impact Visualization")
    
    scenario_type = st.selectbox(
        "Select Scenario",
        options=["disability", "critical_illness", "job_loss", "death"],
        format_func=lambda x: x.title()
    )
    
    impact_fig = create_protection_impact_chart(client_data, scenario_type)
    st.plotly_chart(impact_fig, use_container_width=True)

def scenario_simulator():
    """Create a scenario simulator for exploring insurance benefits"""
    st.subheader("Scenario Simulator")
    st.markdown("<div class='info-card'>Simulate the financial impact of life events and see how insurance can help</div>", unsafe_allow_html=True)
    
    # Check if client data is available
    if not st.session_state.client_data:
        st.warning("Please complete the client profile first to use the scenario simulator.")
        return
    
    # Get client data
    mortgage_amount = st.session_state.client_data.get("mortgage_amount", 350000)
    annual_income = st.session_state.client_data.get("annual_income", 75000)
    monthly_income = annual_income / 12
    
    # Calculate monthly mortgage payment
    monthly_payment = calculate_mortgage_payment(
        mortgage_amount,
        st.session_state.client_data.get("interest_rate", 4.5),
        st.session_state.client_data.get("amortization_years", 25)
    )
    
    # Scenario selection
    scenario = st.selectbox(
        "Select a Scenario to Simulate",
        options=[
            "Job Loss",
            "Disability",
            "Critical Illness",
            "Death of Primary Earner"
        ]
    )
    
    # Job Loss scenario
    if scenario == "Job Loss":
        st.markdown("### Job Loss Scenario")
        
        col1, col2 = st.columns(2)
        
        with col1:
            months_unemployed = st.slider("Months Unemployed", min_value=1, max_value=12, value=3)
            ei_benefit = st.number_input("Monthly EI Benefit ($)", min_value=0.0, value=float(min(2000, monthly_income * 0.55)))
        
        with col2:
            savings = st.number_input("Emergency Savings ($)", min_value=0.0, value=float(monthly_income * 3))
            other_expenses = st.number_input("Monthly Essential Expenses (excluding mortgage)", min_value=0.0, value=float(monthly_income * 0.4))
        
        # Calculate financial impact
        monthly_shortfall = monthly_payment + other_expenses - ei_benefit
        total_shortfall = monthly_shortfall * months_unemployed
        savings_depletion = min(savings, total_shortfall)
        remaining_shortfall = max(0, total_shortfall - savings_depletion)
        
        # Display impact
        st.markdown("### Financial Impact")
        
        impact_data = {
            "Item": ["Monthly Mortgage Payment", "Other Monthly Expenses", "Monthly EI Benefit", "Monthly Shortfall", "Duration", "Total Shortfall", "Savings Used", "Remaining Shortfall"],
            "Amount": [
                f"${monthly_payment:.2f}",
                f"${other_expenses:.2f}",
                f"${ei_benefit:.2f}",
                f"${monthly_shortfall:.2f}",
                f"{months_unemployed} months",
                f"${total_shortfall:.2f}",
                f"${savings_depletion:.2f}",
                f"${remaining_shortfall:.2f}"
            ]
        }
        
        impact_df = pd.DataFrame(impact_data)
        st.table(impact_df)
        
        # Insurance recommendation
        if remaining_shortfall > 0:
            st.markdown(f"""
            <div class='alert-box alert-high'>
                <h4>Financial Gap Identified</h4>
                <p>After using all available savings, there would still be a shortfall of <strong>${remaining_shortfall:.2f}</strong>.</p>
                <p>HomeProtector Job Loss Insurance would cover your mortgage payments for up to 6 months, providing <strong>${monthly_payment * 6:.2f}</strong> in protection.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='alert-box alert-medium'>
                <h4>Adequate Protection</h4>
                <p>Your emergency savings of ${savings:.2f} would cover the projected shortfall of ${total_shortfall:.2f} during this job loss scenario.</p>
                <p>However, consider that your savings would be depleted by ${savings_depletion:.2f}, leaving you vulnerable to other emergencies.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Disability scenario
    elif scenario == "Disability":
        st.markdown("### Disability Scenario")
        
        col1, col2 = st.columns(2)
        
        with col1:
            months_disabled = st.slider("Months Unable to Work", min_value=1, max_value=24, value=6)
            disability_benefit = st.number_input("Monthly Disability Benefit from Other Sources ($)", min_value=0.0, value=float(monthly_income * 0.3))
        
        with col2:
            savings = st.number_input("Emergency Savings ($)", min_value=0.0, value=float(monthly_income * 3))
            other_expenses = st.number_input("Monthly Essential Expenses (excluding mortgage)", min_value=0.0, value=float(monthly_income * 0.4))
            medical_expenses = st.number_input("Additional Monthly Medical Expenses ($)", min_value=0.0, value=500.0)
        
        # Calculate financial impact
        monthly_shortfall = monthly_payment + other_expenses + medical_expenses - disability_benefit
        total_shortfall = monthly_shortfall * months_disabled
        savings_depletion = min(savings, total_shortfall)
        remaining_shortfall = max(0, total_shortfall - savings_depletion)
        
        # Display impact
        st.markdown("### Financial Impact")
        
        impact_data = {
            "Item": ["Monthly Mortgage Payment", "Other Monthly Expenses", "Medical Expenses", "Monthly Disability Benefit", "Monthly Shortfall", "Duration", "Total Shortfall", "Savings Used", "Remaining Shortfall"],
            "Amount": [
                f"${monthly_payment:.2f}",
                f"${other_expenses:.2f}",
                f"${medical_expenses:.2f}",
                f"${disability_benefit:.2f}",
                f"${monthly_shortfall:.2f}",
                f"{months_disabled} months",
                f"${total_shortfall:.2f}",
                f"${savings_depletion:.2f}",
                f"${remaining_shortfall:.2f}"
            ]
        }
        
        impact_df = pd.DataFrame(impact_data)
        st.table(impact_df)
        
        # Insurance recommendation
        homeprotector_benefit = min(months_disabled, 24) * monthly_payment
        
        if remaining_shortfall > 0:
            st.markdown(f"""
            <div class='alert-box alert-high'>
                <h4>Financial Gap Identified</h4>
                <p>After using all available savings, there would still be a shortfall of <strong>${remaining_shortfall:.2f}</strong>.</p>
                <p>HomeProtector Disability Insurance would cover your mortgage payments for up to 24 months, providing <strong>${homeprotector_benefit:.2f}</strong> in protection.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='alert-box alert-medium'>
                <h4>Adequate Protection</h4>
                <p>Your emergency savings of ${savings:.2f} would cover the projected shortfall of ${total_shortfall:.2f} during this disability scenario.</p>
                <p>However, consider that your savings would be depleted by ${savings_depletion:.2f}, leaving you vulnerable to other emergencies.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Critical Illness scenario
    elif scenario == "Critical Illness":
        st.markdown("### Critical Illness Scenario")
        
        col1, col2 = st.columns(2)
        
        with col1:
            months_recovery = st.slider("Months for Recovery", min_value=1, max_value=12, value=6)
            income_reduction = st.slider("Income Reduction During Recovery (%)", min_value=0, max_value=100, value=70)
        
        with col2:
            savings = st.number_input("Emergency Savings ($)", min_value=0.0, value=float(monthly_income * 3))
            other_expenses = st.number_input("Monthly Essential Expenses (excluding mortgage)", min_value=0.0, value=float(monthly_income * 0.4))
            medical_expenses = st.number_input("Additional Monthly Medical Expenses ($)", min_value=0.0, value=2000.0)
        
        # Calculate financial impact
        reduced_income = monthly_income * (1 - income_reduction / 100)
        monthly_shortfall = monthly_payment + other_expenses + medical_expenses - reduced_income
        total_shortfall = monthly_shortfall * months_recovery
        savings_depletion = min(savings, total_shortfall)
        remaining_shortfall = max(0, total_shortfall - savings_depletion)
        
        # Display impact
        st.markdown("### Financial Impact")
        
        impact_data = {
            "Item": ["Monthly Mortgage Payment", "Other Monthly Expenses", "Medical Expenses", "Reduced Monthly Income", "Monthly Shortfall", "Duration", "Total Shortfall", "Savings Used", "Remaining Shortfall"],
            "Amount": [
                f"${monthly_payment:.2f}",
                f"${other_expenses:.2f}",
                f"${medical_expenses:.2f}",
                f"${reduced_income:.2f}",
                f"${monthly_shortfall:.2f}",
                f"{months_recovery} months",
                f"${total_shortfall:.2f}",
                f"${savings_depletion:.2f}",
                f"${remaining_shortfall:.2f}"
            ]
        }
        
        impact_df = pd.DataFrame(impact_data)
        st.table(impact_df)
        
        # Insurance recommendation
        ci_benefit = min(mortgage_amount, 300000)  # Max coverage of $300,000
        
        st.markdown(f"""
        <div class='alert-box alert-high'>
            <h4>Critical Illness Impact</h4>
            <p>A critical illness diagnosis could result in a financial shortfall of <strong>${total_shortfall:.2f}</strong> over {months_recovery} months.</p>
            <p>HomeProtector Critical Illness Insurance would provide a lump sum payment of up to <strong>${ci_benefit:.2f}</strong> that could be applied directly to your mortgage, significantly reducing your financial burden during recovery.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Death scenario
    elif scenario == "Death of Primary Earner":
        st.markdown("### Death of Primary Earner Scenario")
        
        # Get dependents information
        dependents = st.session_state.client_data.get("dependents", 0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            life_insurance = st.number_input("Other Life Insurance Coverage ($)", min_value=0.0, value=float(annual_income))
            survivor_income = st.number_input("Surviving Household Monthly Income ($)", min_value=0.0, value=float(monthly_income * 0.3 if dependents > 0 else 0.0))
        
        with col2:
            savings = st.number_input("Emergency Savings ($)", min_value=0.0, value=float(monthly_income * 6))
            other_expenses = st.number_input("Monthly Essential Expenses (excluding mortgage)", min_value=0.0, value=float(monthly_income * 0.4))
        
        # Calculate financial impact
        monthly_shortfall = monthly_payment + other_expenses - survivor_income
        years_to_cover = 5 if dependents > 0 else 2
        total_shortfall = monthly_shortfall * 12 * years_to_cover
        resources_available = savings + life_insurance
        remaining_shortfall = max(0, total_shortfall - resources_available)
        mortgage_burden = mortgage_amount - life_insurance if life_insurance < mortgage_amount else 0
        
        # Display impact
        st.markdown("### Financial Impact")
        
        impact_data = {
            "Item": ["Outstanding Mortgage", "Monthly Mortgage Payment", "Other Monthly Expenses", "Survivor's Monthly Income", "Monthly Shortfall", "Years to Support", "Total Shortfall", "Available Resources", "Remaining Shortfall", "Mortgage Balance After Other Insurance"],
            "Amount": [
                f"${mortgage_amount:.2f}",
                f"${monthly_payment:.2f}",
                f"${other_expenses:.2f}",
                f"${survivor_income:.2f}",
                f"${monthly_shortfall:.2f}",
                f"{years_to_cover} years",
                f"${total_shortfall:.2f}",
                f"${resources_available:.2f}",
                f"${remaining_shortfall:.2f}",
                f"${mortgage_burden:.2f}"
            ]
        }
        
        impact_df = pd.DataFrame(impact_data)
        st.table(impact_df)
        
        # Insurance recommendation
        if mortgage_burden > 0:
            st.markdown(f"""
            <div class='alert-box alert-high'>
                <h4>Mortgage Protection Gap</h4>
                <p>After applying existing life insurance, there would still be a mortgage balance of <strong>${mortgage_burden:.2f}</strong>.</p>
                <p>HomeProtector Life Insurance would pay off the entire mortgage balance of <strong>${mortgage_amount:.2f}</strong>, ensuring the home remains secure for your family.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if dependents > 0:
                st.markdown(f"""
                <div class='alert-box alert-high'>
                    <h4>Family Support Gap</h4>
                    <p>With {dependents} dependent{'s' if dependents > 1 else ''}, there would be an ongoing financial shortfall of <strong>${monthly_shortfall:.2f}</strong> per month.</p>
                    <p>By eliminating the mortgage payment with HomeProtector Life Insurance, this shortfall would be reduced to <strong>${other_expenses - survivor_income:.2f}</strong> per month, making it more manageable for the surviving family members.</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='alert-box alert-medium'>
                <h4>Adequate Mortgage Protection</h4>
                <p>Your existing life insurance of ${life_insurance:.2f} would cover your mortgage balance of ${mortgage_amount:.2f}.</p>
                <p>However, HomeProtector Life Insurance can still be valuable as it's specifically designed to pay off your mortgage, leaving your other life insurance to support your family's ongoing expenses.</p>
            </div>
            """, unsafe_allow_html=True)

def main():
    """Main function to run the Streamlit app"""
    # Apply Certus styling
    apply_certus_styling()
    
    # Sidebar navigation
    st.sidebar.title("Certus Navigation")
    page = st.sidebar.radio(
        "Select a Page",
        options=[
            "AI Advisor Assistant",
            "Client Profile",
            "Mortgage Journey Tracker",
            "WIPT Calculator",
            "Insurance Recommendations",
            "Scenario Simulator",
            "Document Management"
        ]
    )
    
    # Update current screen in session state for alerts
    screen_mapping = {
        "AI Advisor Assistant": ScreenType.PRODUCT_RECOMMENDATION,
        "Client Profile": ScreenType.CLIENT_PROFILE,
        "Mortgage Journey Tracker": ScreenType.MORTGAGE_APPLICATION,
        "WIPT Calculator": ScreenType.PAYMENT_CALCULATOR,
        "Insurance Recommendations": ScreenType.PRODUCT_RECOMMENDATION,
        "Scenario Simulator": ScreenType.PRODUCT_RECOMMENDATION,
        "Document Management": ScreenType.CLIENT_PROFILE
    }
    st.session_state.current_screen = screen_mapping.get(page, ScreenType.CLIENT_PROFILE)
    
    # Display context-aware alerts in sidebar
    display_screen_alerts()
    
    # Main content based on selected page
    if page == "AI Advisor Assistant":
        chatbot_interface()
    
    elif page == "Client Profile":
        client_profile_form()
    
    elif page == "Mortgage Journey Tracker":
        if not st.session_state.client_data:
            st.warning("Please complete the client profile first to use the Mortgage Journey Tracker.")
            st.button("Go to Client Profile", on_click=lambda: st.session_state.update({"_radio": "Client Profile"}))
        else:
            mortgage_journey_tracker()
    
    elif page == "WIPT Calculator":
        wipt_calculator()
    
    elif page == "Insurance Recommendations":
        if not st.session_state.client_data:
            st.warning("Please complete the client profile first to see insurance recommendations.")
            st.button("Go to Client Profile", on_click=lambda: st.session_state.update({"_radio": "Client Profile"}))
        else:
            display_insurance_recommendations()
    
    elif page == "Scenario Simulator":
        scenario_simulator()
    
    elif page == "Document Management":
        upload_and_process_document()
        
        st.subheader("Available Documents")
        if os.path.exists(DOCS_DIR):
            docs = [f for f in os.listdir(DOCS_DIR) if f.endswith(".pdf")]
            if docs:
                selected_doc = st.selectbox("Select a document to view", options=docs)
                if selected_doc:
                    st.subheader(f"Viewing: {selected_doc}")
                    display_pdf(os.path.join(DOCS_DIR, selected_doc))
            else:
                st.info("No documents available. Upload a PDF document to add it to the knowledge base.")

if __name__ == "__main__":
    main()
