from pydantic import BaseModel, EmailStr
from typing import Optional

class RecipientInfo(BaseModel):
    name: str
    company: str
    role: str
    email: EmailStr

class EmailRequest(BaseModel):
    industry: str
    recipient_info: RecipientInfo
    email_type: str
    specific_details: str
    uploaded_content: Optional[str] = None
    sender_name: str
    sender_email: EmailStr
    sender_company: str
    sender_role: str

class EmailResponse(BaseModel):
    subject: str
    body: str

class EmailContent(BaseModel):
    subject: str
    body: str
    greeting: str
    closing: str
    tone: Optional[str] = None
    timestamp: str