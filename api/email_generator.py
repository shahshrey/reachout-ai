from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from .models import EmailContent
from datetime import datetime
import os

AI_MODEL = ChatGroq(
    model="llama3-groq-70b-8192-tool-use-preview",
    temperature=0,
    base_url="https://api.groq.com/"
)

EMAIL_TEMPLATES = {
    "Sales Pitch": "Create a persuasive sales email...",
    "Networking Introduction": "Craft a friendly networking email...",
    "Job Enquiry": "Compose an engaging recruitment email...",
    "Event Invitation": "Create a compelling invitation email...",
    "Job Application": "Write a professional job application email...",
}

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

    1. Analyze the provided information, including the uploaded document content if available.
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

def generate_email(email_info, session_id="email_session"):
    result = email_generator_with_history.invoke(
        {
            "industry": email_info["industry"],
            "recipient_role": email_info["recipient_info"]["role"],
            "details": f"Recipient: {email_info['recipient_info']['name']}, Company: {email_info['recipient_info']['company']}, Role: {email_info['recipient_info']['role']}. Additional details: {email_info['specific_details']}",
            "purpose": email_info["email_type"],
            "email_type": email_info["email_type"],
            "tone": "professional",
            "word_limit": "No limit",
            "template": EMAIL_TEMPLATES.get(email_info["email_type"], ""),
            "uploaded_content": email_info.get("uploaded_content", "No uploaded content"),
            "sender_name": email_info["sender_name"],
            "sender_email": email_info["sender_email"],
            "sender_company": email_info["sender_company"],
            "sender_role": email_info["sender_role"],
            "user_input": f"Generate an email for {email_info['industry']} industry, {email_info['recipient_info']['role']} role, with details: {email_info['specific_details']}, purpose: {email_info['email_type']}, type: {email_info['email_type']}, tone: professional"
        },
        {"configurable": {"session_id": session_id}}
    )
    result.timestamp = datetime.now().isoformat()
    return result