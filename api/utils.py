import csv
import os
from typing import Dict

EMAIL_DATA_FILE = './email_data.csv'
TEMP_EMAIL_DATA_FILE = './temp_email_data.csv'

def save_email_data(email_data: Dict):
    fieldnames = ['timestamp', 'user_email', 'recipient_email', 'recipient_name', 'recipient_company', 'recipient_role', 'email_type', 'specific_details', 'generated_subject', 'generated_body', 'sent']
    file_exists = os.path.isfile(EMAIL_DATA_FILE)
    
    with open(EMAIL_DATA_FILE, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(email_data)

def update_email_data(recipient_email: str, sent: bool = False):
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