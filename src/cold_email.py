import os
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import PyPDF2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import BaseModel, Field
from typing import Optional
import csv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Configurable variables
AI_MODEL = ChatOpenAI(model_name="gpt-4o")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
EMAIL_DATA_FILE = './email_data.csv'
TEMP_EMAIL_DATA_FILE = './email_data.csv'

EMAIL_TEMPLATES = {
    "Sales Pitch": """
        Create a persuasive sales email that highlights the value proposition for the recipient's industry. 
        Focus on addressing pain points and offering solutions.
    """,
    "Networking Introduction": """
        Craft a friendly networking email that establishes common ground and suggests a mutually beneficial connection.
    """,
    "Job Enquiry": """
        Compose an engaging recruitment email that showcases the opportunity and appeals to the candidate's background and aspirations.
    """,
    "Event Invitation": """
        Create a compelling invitation email that highlights the value of attending the event and encourages participation.
    """,
    "Job Application": """
        Write a professional job application email that highlights the applicant's qualifications, experience, and enthusiasm for the role.
    """,
}

class EmailContent(BaseModel):
    """Structured email content."""
    subject: str = Field(description="The subject line of the email")
    body: str = Field(description="The main content of the email")
    greeting: str = Field(description="The greeting or salutation of the email")
    closing: str = Field(description="The closing or signature of the email")
    tone: Optional[str] = Field(default=None, description="The overall tone of the email")

EMAIL_GENERATION_INSTRUCTIONS = """
    You are ReachOut AI, an AI-powered email generator designed to craft personalized cold outreach emails.

    You will be provided with the following information:
    - Industry: {industry}
    - Recipient Role: {recipient_role}
    - Company/Personal Details: {details}
    - Email Purpose: {purpose}
    - Email Type: {email_type}
    - Tone: {tone}
    - Word Limit: {word_limit}
    - Previous conversation: {chat_history}
    - Uploaded Document Content: {uploaded_content}
    - Sender Name: {sender_name}
    - Sender Email: {sender_email}
    - Sender Company: {sender_company}
    - Sender Role: {sender_role}

    To generate the most effective email, follow these steps:

    1. Analyze the provided information, including the uploaded document content if available. make use of the uploaded content to make the email more personal if its a available.
    2. Choose the appropriate email structure.
    3. Craft the email content, incorporating relevant details from the uploaded document if provided.
    4. Refine the email.
    5. Perform final checks.

    Based on this process, craft the email content according to the following template:
    {template}
    
    Generate the email content without any explanations or additional suggestions.
    
    format the output in json format in the following format:
    {{
        "subject": "...",
        "body": "...",
        "greeting": "...",
        "closing": "...",
        "tone": "..."
    }}
"""

email_template = ChatPromptTemplate.from_messages([
    ("system", EMAIL_GENERATION_INSTRUCTIONS)
])

email_generation_chain = email_template | AI_MODEL.with_structured_output(EmailContent)

conversation_history = ChatMessageHistory()

email_generator_with_history = RunnableWithMessageHistory(
    email_generation_chain,
    lambda session_id: conversation_history,
    input_messages_key="user_input",
    history_messages_key="chat_history",
)

def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def generate_email(email_info, session_id="email_session"):
    return email_generator_with_history.invoke(
        {
            "industry": email_info["industry"],
            "recipient_role": email_info["recipient_role"],
            "details": email_info["details"],
            "purpose": email_info["purpose"],
            "email_type": email_info["email_type"],
            "tone": email_info["tone"],
            "word_limit": email_info["word_limit"] if email_info["word_limit"] else "No limit",
            "template": EMAIL_TEMPLATES.get(email_info["email_type"], ""),
            "uploaded_content": email_info.get("uploaded_content", "No uploaded content"),
            "sender_name": email_info["sender_name"],
            "sender_email": email_info["sender_email"],
            "sender_company": email_info["sender_company"],
            "sender_role": email_info["sender_role"],
            "user_input": f"Generate an email for {email_info['industry']} industry, {email_info['recipient_role']} role, with details: {email_info['details']}, purpose: {email_info['purpose']}, type: {email_info['email_type']}, tone: {email_info['tone']}, word limit: {email_info['word_limit'] if email_info['word_limit'] else 'No limit'}"
        },
        {"configurable": {"session_id": session_id}}
    )

def save_email_data(email_data):
    fieldnames = ['timestamp', 'user_email', 'recipient_email', 'recipient_name', 'recipient_company', 'recipient_role', 'email_type', 'specific_details', 'generated_subject', 'generated_body', 'sent']
    file_exists = os.path.isfile(EMAIL_DATA_FILE)
    
    with open(EMAIL_DATA_FILE, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(email_data)

def get_email_stats():
    emails_generated = 0
    emails_sent = 0
    
    if os.path.isfile(EMAIL_DATA_FILE):
        with open(EMAIL_DATA_FILE, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                emails_generated += 1
                if row['sent'] == 'True':
                    emails_sent += 1
    
    response_rate = (emails_sent / emails_generated * 100) if emails_generated > 0 else 0
    
    return emails_generated, emails_sent, f"{response_rate:.2f}%"

def main():
    st.set_page_config(page_title="ReachOut AI", page_icon="️", layout="wide")
    
    # Apply custom theme
    st.markdown("""
        <style>
        .stApp {
            background-color: #152515;
            color: #FFFFFF;
        }
        .stButton>button {
            background-color: #8bd858;
            color: #152515;
        }
        .stTextInput>div>div>input, .stSelectbox>div>div>select {
            background-color: #464c37;
            color: #FFFFFF;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state variables if they don't exist
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {}
    if 'recipient_info' not in st.session_state:
        st.session_state.recipient_info = {}
    if 'email_details' not in st.session_state:
        st.session_state.email_details = {}
    if 'current_step' not in st.session_state:
        st.session_state.current_step = "home"
    if 'uploaded_content' not in st.session_state:
        st.session_state.uploaded_content = None
    
    st.title("ReachOut AI")
    
    if st.session_state.current_step == "home":
        display_home_page()
    elif st.session_state.current_step == "registration":
        display_registration_page()
    elif st.session_state.current_step == "personalize":
        display_personalize_page()
    elif st.session_state.current_step == "generate":
        display_generate_page()
    elif st.session_state.current_step == "send":
        display_send_page()
    else:
        st.error(f"Unknown step: {st.session_state.current_step}")

def display_home_page():
    st.write("Welcome to ReachOut AI, your advanced solution for crafting personalized and impactful cold outreach emails.")
    
    st.info("Follow our streamlined process to create your tailored email.")
    
    # Add a dashboard or overview here
    st.subheader("Performance Metrics")
    emails_generated, emails_sent, response_rate = get_email_stats()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Emails Generated", emails_generated)
    with col2:
        st.metric("Emails Successfully Sent", emails_sent)
    with col3:
        st.metric("Current Response Rate", response_rate)
    
    if st.button("Start Email Creation"):
        st.session_state.current_step = "registration"
        st.rerun()

def display_registration_page():
    st.subheader("User Registration")
    
    with st.form("registration_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Professional Email Address")
        company = st.text_input("Company or Organization Name")
        industry = st.text_input("Industry Sector")
        role = st.text_input("Current Position")
        email_type = st.selectbox("Select Email Category", 
                                  list(EMAIL_TEMPLATES.keys()))
        
        submitted = st.form_submit_button("Complete Registration and Proceed")
        if submitted:
            st.session_state.user_info = {
                "name": name,
                "email": email,
                "company": company,
                "industry": industry,
                "role": role,
                "email_type": email_type
            }
            st.success("Registration completed successfully!")
            st.session_state.current_step = "personalize"
            st.rerun()

def display_personalize_page():
    st.subheader("Email Personalization")
    
    st.write("Provide detailed information about your recipient to enhance email personalization.")
    
    recipient_name = st.text_input("Recipient's Full Name")
    recipient_company = st.text_input("Recipient's Company or Organization")
    recipient_role = st.text_input("Recipient's Position or Title")
    
    st.subheader("Additional Information")
    specific_details = st.text_area("Enter any relevant details or key points you wish to incorporate in the email")
    
    st.subheader("Supporting Documentation")
    uploaded_file = st.file_uploader("Upload your resume or any pertinent document", type=["pdf", "docx"])
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            st.session_state.uploaded_content = read_pdf(uploaded_file)
        else:
            st.warning("Document processing for non-PDF files is currently not supported.")
    
    if st.button("Save and Continue"):
        st.session_state.recipient_info = {
            "name": recipient_name,
            "company": recipient_company,
            "role": recipient_role
        }
        st.session_state.email_details = {
            "specific_details": specific_details
        }
        st.success("Information saved successfully!")
        st.session_state.current_step = "generate"
        st.rerun()

def display_generate_page():
    st.subheader("Email Generation")
    
    st.write("Review the information below and generate your customized email.")
    recipient_name = st.session_state.recipient_info.get('name', '[Name]')
    recipient_company = st.session_state.recipient_info.get('company', '[Company]')
    recipient_role = st.session_state.recipient_info.get('role', '[Role]')
    email_type = st.session_state.user_info.get('email_type', '[Selected Type]')
    specific_details = st.session_state.email_details.get('specific_details', '[Summary of details]')
    
    st.write(f"Recipient: {recipient_name}, {recipient_company}, {recipient_role}")
    st.write(f"Email Category: {email_type}")
    st.write(f"Additional Information: {specific_details}")
    
    if st.button("Generate Email"):
        email_info = {
            "industry": st.session_state.user_info.get('industry', ''),
            "recipient_role": recipient_role,
            "details": f"Recipient: {recipient_name}, Company: {recipient_company}, Role: {recipient_role}. Additional details: {specific_details}",
            "purpose": email_type,
            "email_type": email_type,
            "tone": "professional",
            "word_limit": "",
            "uploaded_content": st.session_state.uploaded_content or "No uploaded content",
            "sender_name": st.session_state.user_info.get('name', ''),
            "sender_email": st.session_state.user_info.get('email', ''),
            "sender_company": st.session_state.user_info.get('company', ''),
            "sender_role": st.session_state.user_info.get('role', '')
        }
        try:
            generated_email = generate_email(email_info)
            st.session_state.generated_email = generated_email
            
            # Save email data
            email_data = {
                'timestamp': datetime.now().isoformat(),
                'user_email': st.session_state.user_info.get('email', ''),
                'recipient_email': '',  # This will be filled later
                'recipient_name': recipient_name,
                'recipient_company': recipient_company,
                'recipient_role': recipient_role,
                'email_type': email_type,
                'specific_details': specific_details,
                'generated_subject': generated_email.subject,
                'generated_body': generated_email.body,
                'sent': False
            }
            save_email_data(email_data)
            
            # Display the generated email content
            st.subheader("Generated Email Content")
            st.text_input("Email Subject", generated_email.subject, disabled=False)
            st.text_area("Email Body", f"{generated_email.body}", height=300, disabled=False)
        
        except Exception as e:
            st.error(f"An error occurred during email generation: {str(e)}")
            return
    
    if st.button("Proceed to Send Email"):
        st.session_state.current_step = "send"
        st.rerun()

def display_send_page():
    st.subheader("Send Email")
    
    recipient_email = st.text_input("Recipient's Email Address")
    
    st.subheader("Final Email Preview")
    email_content = st.session_state.get('generated_email')
    if email_content:
        st.text_input("Email Subject", email_content.subject, disabled=False)
        st.text_area("Email Body", f"{email_content.body}", height=300, disabled=False)
    else:
        st.warning("No email has been generated yet. Please return to the previous step and generate an email.")
    if st.button("Send Email"):
        if send_email(recipient_email, email_content):
            st.success("Email sent successfully!")
            # Update email data
            update_email_data(recipient_email, sent=True)
        else:
            st.error("Failed to send email. Please check your settings and try again.")
    
    if st.button("Start a New Email"):
        st.session_state.current_step = "home"
        st.rerun()

def send_email(to_email, email_content):
    try:
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = to_email
        message["Subject"] = email_content.subject
        body = f"{email_content.body}"
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def update_email_data(recipient_email, sent=False):
    fieldnames = ['timestamp', 'user_email', 'recipient_email', 'recipient_name', 'recipient_company', 'recipient_role', 'email_type', 'specific_details', 'generated_subject', 'generated_body', 'sent']
    
    with open(EMAIL_DATA_FILE, 'r') as csvfile, open(TEMP_EMAIL_DATA_FILE, 'w', newline='') as tempfile:
        reader = csv.DictReader(csvfile)
        writer = csv.DictWriter(tempfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            if row['recipient_email'] == '':
                row['recipient_email'] = recipient_email
                row['sent'] = str(sent)
            writer.writerow(row)
    
    os.replace(TEMP_EMAIL_DATA_FILE, EMAIL_DATA_FILE)

if __name__ == "__main__":
    main()