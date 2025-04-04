
import os
import openai
import PyPDF2
import tiktoken
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
import streamlit as st
import base64
import json
import time

# Load environment variables
load_dotenv()

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Persistent Chroma DB Client
DB_PATH = "vector_db"
chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection = chroma_client.get_or_create_collection("document_embeddings")

if collection is None:
    raise Exception("Failed to create or retrieve the collection from ChromaDB.")

# Choose Embedding Function
USE_LOCAL_EMBEDDINGS = True
if USE_LOCAL_EMBEDDINGS:
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
else:
    embedding_function = embedding_functions.OpenAIEmbeddingFunction(api_key=os.getenv("OPENAI_API_KEY"), model_name="text-embedding-3-small")

# RBC styling
def apply_rbc_styling():
    # RBC colors: blue (#005DAA), dark blue (#00335A), gold (#FEDF01)
    st.markdown("""
    <style>
        /* Global Styles */
        @import url('[https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');](https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');)
        
        html, body, [class*="css"] {
            font-family: 'Nunito', sans-serif;
        }
        
        /* Header Styles */
        .main .block-container {
            padding-top: 1rem;
        }
        
        h1, h2, h3 {
            color: #005DAA !important;
            font-weight: 700 !important;
        }
        
        /* Sidebar Styles */
        .css-1d391kg {
            background-color: #005DAA;
        }
        
        .sidebar .sidebar-content {
            background-color: #005DAA;
        }
        
        /* Button Styles */
        .stButton>button {
            background-color: #005DAA;
            color: white;
            border-radius: 4px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        
        .stButton>button:hover {
            background-color: #00335A;
        }
        
        /* Form Styles */
        .stForm {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Tab Styles */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: #f1f1f1;
            border-radius: 4px 4px 0 0;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #005DAA !important;
            color: white !important;
        }
        
        /* Chat Styles */
        .user-message {
            background-color: #E1F5FE;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
            border-left: 4px solid #005DAA;
        }
        
        .bot-message {
            background-color: #f1f1f1;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
            border-left: 4px solid #FEDF01;
        }
        
        /* Card Styles */
        .rbc-card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        
        /* Logo Styles */
        .rbc-logo {
            max-width: 150px;
            margin-bottom: 20px;
        }
        
        /* Footer Styles */
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid #e1e1e1;
            font-size: 12px;
            color: #666;
        }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def count_tokens(text, model="gpt-3.5"):
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def split_text_into_chunks(text, max_tokens=3000):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    chunks = []
    while len(tokens) > 0:
        chunk = tokens[:max_tokens]
        chunks.append(encoding.decode(chunk))
        tokens = tokens[max_tokens:]
    return chunks

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

def initialize_db(documents):
    try:
        existing_ids = collection.get()["ids"]
        if existing_ids:
            collection.delete(ids=existing_ids)
            print(f"Deleted existing IDs: {existing_ids}")
    except Exception as e:
        print(f"Error retrieving or deleting existing documents: {e}")

    for i, doc in enumerate(documents):
        chunks = split_text_into_chunks(doc["content"])
        chunk_ids = [f"doc_{i}_chunk_{j}" for j in range(len(chunks))]
        existing_ids = collection.get()["ids"]
        new_ids = [id for id in chunk_ids if id not in existing_ids]
        if new_ids:
            collection.add(
                documents=[chunks[j] for j, id in enumerate(chunk_ids) if id in new_ids],
                metadatas=[doc["metadata"]] * len(new_ids),
                ids=new_ids
            )
            print(f"Added new IDs: {new_ids}")
        else:
            print(f"No new IDs to add for {doc['metadata']['source']}")

@st.cache_data
def retrieve_relevant_chunks(query, top_k=5):
    results = collection.query(query_texts=[query], n_results=top_k)
    return results["documents"][0] if results["documents"] else []

def generate_response_with_chunking(query, relevant_docs, model="gpt-3.5-turbo", max_tokens=3000):
    chunks = []
    for doc in relevant_docs:
        chunks.extend(split_text_into_chunks(doc, max_tokens))
    context = "\n".join(f"- {chunk}" for chunk in chunks[:5])
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer with as few unnecessary words as possible and ONLY in bullet point format:"
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        print(f"Error with OpenAI API: {e}")
        return "An error occurred."

def display_pdf(file_path):
    with open(file_path, "rb") as file:
        base64_pdf = base64.b64encode(file.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" style="border: none;"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def upload_and_overwrite_file(uploaded_file, folder_path="../docs"):
    if uploaded_file is not None:
        file_path = os.path.join(folder_path, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File '{uploaded_file.name}' has been uploaded and overwritten.")
        documents = load_docs(folder_path)
        initialize_db(documents)
        print("processing done")
    else:
        st.warning("No file uploaded.")

def chatbot_moment():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    def display_chat():
        for user_message, bot_response in st.session_state.chat_history[-10:]:
            st.markdown(f'<div class="user-message"><strong>You:</strong> {user_message}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bot-message"><strong>RBC Advisor:</strong> {bot_response}</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="rbc-card">', unsafe_allow_html=True)
        display_chat()
        st.markdown('</div>', unsafe_allow_html=True)

    with st.form(key="chat_form", clear_on_submit=True):
        user_query = st.text_input("Ask a question:", key="user_input", placeholder="How can I help with your mortgage needs today?", label_visibility="collapsed")
        col1, col2 = st.columns([4, 1])
        with col2:
            submit_button = st.form_submit_button(label="Send")

    if submit_button and user_query:
        st.session_state.chat_history.append((user_query, ""))
        relevant_docs = retrieve_relevant_chunks(user_query)
        response = generate_response_with_chunking(user_query, relevant_docs)
        if response:
            with st.spinner("RBC Advisor is typing..."):
                time.sleep(1)
            st.session_state.chat_history[-1] = (user_query, response)
            st.experimental_rerun()
        else:
            st.session_state.chat_history[-1] = (user_query, "I'm sorry, I couldn't find information on that. Please try rephrasing your question or speak with an RBC mortgage specialist for more assistance.")
            st.experimental_rerun()

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.experimental_rerun()

def generate_scenarios_with_docs(customer_data):
    # First, retrieve relevant document chunks based on customer data
    search_query = f"mortgage scenarios for income {customer_data['income']} credit score {customer_data['credit_score']} mortgage amount {customer_data['mortgage_amount']}"
    relevant_docs = retrieve_relevant_chunks(search_query, top_k=5)
    
    # Combine the relevant document chunks into a context
    context = "\n".join(relevant_docs) if relevant_docs else "No specific information found in documents."
    
    # Create a prompt that includes both customer data and document context
    prompt = f"""Based on the following customer data:
Name: {customer_data['name']}
Age: {customer_data['age']}
Annual Income: ${customer_data['income']}
Mortgage Amount: ${customer_data['mortgage_amount']}
Credit Score: {customer_data['credit_score']}

And considering this information from RBC mortgage documents:
{context}

Generate three possible scenarios related to their mortgage situation and financial standing. 
Use specific details from RBC documents where relevant.
Provide advice for each scenario. Format your response as follows:

Scenario 1:
[Description]
Advice:
- [Bullet point 1]
- [Bullet point 2]

Scenario 2:
[Description]
Advice:
- [Bullet point 1]
- [Bullet point 2]

Scenario 3:
[Description]
Advice:
- [Bullet point 1]
- [Bullet point 2]
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        print(f"Error with OpenAI API: {e}")
        return "An error occurred while generating scenarios."

def customer_data_form():
    st.markdown('<div class="rbc-card">', unsafe_allow_html=True)
    st.markdown("### Personalized Mortgage Assessment")
    st.markdown("Fill in your details below to receive personalized mortgage scenarios and advice based on RBC's mortgage products and services.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="rbc-card">', unsafe_allow_html=True)
    with st.form("customer_data_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=18, max_value=100, value=30)
            income = st.number_input("Annual Income ($)", min_value=0, value=75000, step=5000)
        
        with col2:
            mortgage_amount = st.number_input("Desired Mortgage Amount ($)", min_value=0, value=400000, step=25000)
            credit_score = st.slider("Credit Score", min_value=300, max_value=850, value=700)
            use_docs = st.checkbox("Include RBC product information", value=True)
        
        submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
        with submit_col2:
            submitted = st.form_submit_button("Generate Personalized Scenarios")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    if submitted:
        customer_data = {
            "name": name,
            "age": age,
            "income": income,
            "mortgage_amount": mortgage_amount,
            "credit_score": credit_score
        }
        
        with st.spinner("Analyzing your financial profile..."):
            time.sleep(2)
            
            st.markdown('<div class="rbc-card">', unsafe_allow_html=True)
        st.markdown("### Your Personalized Mortgage Scenarios")
        
        if use_docs:
            scenarios = generate_scenarios_with_docs(customer_data)
        else:
            scenarios = generate_scenarios(customer_data)
        
        # Format the scenarios with better styling
        formatted_scenarios = scenarios.replace("Scenario 1:", "<h4 style='color: #005DAA;'>Scenario 1:</h4>")
        formatted_scenarios = formatted_scenarios.replace("Scenario 2:", "<h4 style='color: #005DAA;'>Scenario 2:</h4>")
        formatted_scenarios = formatted_scenarios.replace("Scenario 3:", "<h4 style='color: #005DAA;'>Scenario 3:</h4>")
        formatted_scenarios = formatted_scenarios.replace("Advice:", "<strong style='color: #00335A;'>Advice:</strong>")
        
        st.markdown(formatted_scenarios, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: #E1F5FE; padding: 15px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #FEDF01;">
            <strong>Next Steps:</strong> To discuss these scenarios in more detail or to begin your mortgage application, 
            please contact an RBC mortgage specialist at 1-800-769-2511 or visit your nearest RBC branch.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def generate_scenarios(customer_data):
    prompt = f"""Based on the following customer data:
Name: {customer_data['name']}
Age: {customer_data['age']}
Annual Income: ${customer_data['income']}
Mortgage Amount: ${customer_data['mortgage_amount']}
Credit Score: {customer_data['credit_score']}

Generate three possible scenarios related to their mortgage situation and financial standing with RBC. 
Format your response as follows:

Scenario 1:
[Description]
Advice:
- [Bullet point 1]
- [Bullet point 2]

Scenario 2:
[Description]
Advice:
- [Bullet point 1]
- [Bullet point 2]

Scenario 3:
[Description]
Advice:
- [Bullet point 1]
- [Bullet point 2]
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        print(f"Error with OpenAI API: {e}")
        return "An error occurred while generating scenarios."
    
def simulate(query, user_info):
    """
    Generate a simulation based on user query and personal information.
    
    Args:
        query (str): The user's question or scenario request
        user_info (dict): User profile information
    
    Returns:
        str: Generated simulation response in markdown format
    """
    # Get relevant document chunks for context
    relevant_chunks = retrieve_relevant_chunks(query)
    context = "\n\n".join(relevant_chunks)
    
    # Format user info
    user_info_str = json.dumps(user_info, indent=2)
    
    # Create prompt for the simulation
    prompt = f"""
You are a helpful mortgage advisor at RBC Royal Bank. Create a detailed simulation based on the following query:

Query: {query}

User Profile:
{user_info_str}

Use the following mortgage insurance information as context:
{context}

Create a realistic simulation that addresses the query and incorporates the user's financial situation. Format your response in markdown with clear sections and bullet points where appropriate.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful mortgage advisor at RBC Royal Bank."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        print(f"Error with OpenAI API: {e}")
        return "An error occurred."

def load_user_profile(file_path="../profile.json"):
    """Load user profile from JSON file"""
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading profile: {e}")
        return None

def simulation_tab():
    """Create a simulation tab interface"""
    st.markdown("## Mortgage Scenario Simulator")
    st.markdown("Explore how different life events might affect your mortgage situation.")
    
    # Load user profile
    profile_data = load_user_profile()
    if not profile_data:
        st.error("Could not load user profile data. Please check your profile.json file.")
        return
    
    # Display user profile
    st.markdown("### Your Profile")
    selected_applicant = st.selectbox(
        "Select Applicant",
        options=range(len(profile_data["applicants"])),
        format_func=lambda i: f"{profile_data['applicants'][i]['first_name']} {profile_data['applicants'][i]['last_name']}"
    )
    
    user_info = profile_data["applicants"][selected_applicant]
    
    # Display user info in columns
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Name:** {user_info['first_name']} {user_info['last_name']}")
        st.markdown(f"**Age:** {user_info['age']}")
        st.markdown(f"**Marital Status:** {user_info['marital_status']}")
        st.markdown(f"**Employment:** {user_info['employment']}")
        st.markdown(f"**Income:** ${user_info['income']:,}")
    
    with col2:
        st.markdown(f"**Household Income:** ${user_info['household_income']:,}")
        st.markdown(f"**Number of Kids:** {user_info['number_of_kids']}")
        st.markdown("**Current Assets:**")
        for asset in user_info['current_assets']:
            st.markdown(f"- {asset}")
        st.markdown("**Liabilities:**")
        for liability in user_info['liabilities']:
            st.markdown(f"- {liability}")
    
    # Simulation scenarios
    st.markdown("### Simulation Scenarios")
    
    # Predefined scenarios
    scenarios = [
        "Create a scenario where the client has to deal with job loss",
        "Simulate how a new child would affect mortgage affordability",
        "Create a simulation of how critical illness would impact mortgage payments",
        "Simulate the impact of interest rate increases on the mortgage",
        "Custom scenario (specify below)"
    ]
    
    selected_scenario = st.selectbox("Choose a scenario to simulate", scenarios)
    
    if selected_scenario == "Custom scenario (specify below)":
        custom_query = st.text_area("Describe your custom scenario:", height=100)
        query = custom_query if custom_query else "Create a general mortgage scenario"
    else:
        query = selected_scenario
    
    if st.button("Generate Simulation"):
        with st.spinner("Generating simulation..."):
            simulation_result = simulate(query, user_info)
            st.markdown(simulation_result)

def main():
    st.set_page_config(page_title="RBC Mortgage Advisor", layout="wide", page_icon="🏦")
    apply_rbc_styling()
    
    # Header with RBC logo
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("https://www.rbcroyalbank.com/dvl/v1.0/assets/images/logos/rbc-logo-shield.svg", width=80)
    with col2:
        st.title("RBC Mortgage Advisor")
        st.markdown("<p style='color: #666;'>Powered by AI to help you make informed mortgage decisions</p>", unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Sidebar for file upload and processing
    with st.sidebar:
        st.image("https://www.rbcroyalbank.com/dvl/v1.0/assets/images/logos/rbc-logo-shield.svg",width=50)
        st.markdown("<h3 style='color: white;'>Document Management</h3>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload PDF Document", type=["pdf"])
        if st.button("Process Document") and uploaded_file is not None:
            upload_and_overwrite_file(uploaded_file)
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Mortgage Assistant", "📝 Personalized Assessment", "📄 Document Library", "🔮 Scenario Simulator"])
    
    with tab1:
        chatbot_moment()
    
    with tab2:
        customer_data_form()
    
    with tab3:
        st.markdown("## Document Library")
        st.markdown("View and search through mortgage-related documents.")
        
        doc_folder = "../docs"
        if os.path.exists(doc_folder):
            docs = [f for f in os.listdir(doc_folder) if f.endswith(".pdf")]
            
            if not docs:
                st.info("No documents found. Please upload documents using the sidebar.")
            else:
                selected_doc = st.selectbox("Select a document to view:", docs)
                if selected_doc:
                    display_pdf(os.path.join(doc_folder, selected_doc))
        else:
            st.error(f"Document folder '{doc_folder}' not found.")
    
    with tab4:
        simulation_tab()
    # Footer
    st.markdown("""
    <div class="footer">
        <p>© Royal Bank of Canada 2023. All rights reserved.</p>
        <p>This is a demonstration project for RBC hackathon purposes only.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()