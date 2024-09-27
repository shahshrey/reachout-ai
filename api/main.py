from fastapi import FastAPI, HTTPException
from .models import EmailRequest, EmailResponse
from .email_generator import generate_email
from .email_sender import send_email
from .utils import save_email_data, update_email_data

app = FastAPI()

@app.post("/generate-email/", response_model=EmailResponse)
async def generate_email_endpoint(request: EmailRequest):
    try:
        email_content = generate_email(request.dict())
        save_email_data({
            'timestamp': email_content.timestamp,
            'user_email': request.sender_email,
            'recipient_email': '',
            'recipient_name': request.recipient_info.name,
            'recipient_company': request.recipient_info.company,
            'recipient_role': request.recipient_info.role,
            'email_type': request.email_type,
            'specific_details': request.specific_details,
            'generated_subject': email_content.subject,
            'generated_body': email_content.body,
            'sent': False
        })
        return EmailResponse(subject=email_content.subject, body=email_content.body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-email/")
async def send_email_endpoint(request: EmailRequest):
    try:
        email_content = generate_email(request.dict())
        if send_email(request.recipient_info.email, email_content):
            update_email_data(request.recipient_info.email, sent=True)
            return {"message": "Email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/email-stats/")
async def get_email_stats():
    # Implement the email stats logic here
    pass