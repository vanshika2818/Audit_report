from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import requests
from bs4 import BeautifulSoup
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from google import genai
import markdown
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import datetime

load_dotenv()

app = FastAPI(title="Lead Automation Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Serve the frontend HTML file."""
    return FileResponse("index.html")

class LeadSubmitRequest(BaseModel):
    name: str
    email: EmailStr
    company_domain: str

def enrich_company_data(domain: str) -> str:
    """
    Fetches a short description of the company based on its domain, 
    then uses Gemini API to generate a comprehensive audit report.
    """
    scraped_desc = "Information not currently available"
    
    if not domain.startswith("http"):
        url = f"https://{domain}"
    else:
        url = domain
        
    print(f"Starting scraping for domain: {domain}")
    try:
        # User-Agent header helps avoid basic bot blocking
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try to find meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            scraped_desc = meta_desc["content"].strip()
        else:
            # Fallback to OpenGraph description
            og_desc = soup.find("meta", attrs={"property": "og:description"})
            if og_desc and og_desc.get("content"):
                scraped_desc = og_desc["content"].strip()
            elif soup.title and soup.title.string:
                scraped_desc = f"Company Title: {soup.title.string.strip()}"
        print(f"Scraped Description: {scraped_desc}")
    except Exception as e:
        print(f"Failed to scrape domain {domain}: {e}")
        
    # Generate LLM Report
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("Warning: Valid GEMINI_API_KEY not found. Returning basic scraped data.")
        return scraped_desc
        
    print("Calling Gemini API...")
    try:
        # Using the new google-genai SDK
        client = genai.Client(api_key=api_key)
        
        if scraped_desc == "Information not currently available":
            prompt = f"The website description could not be scraped. However, based on your general knowledge of the domain {domain}, please write a comprehensive 3-section B2B audit report: (1) Company Overview, (2) Value Proposition, (3) Recommended AI/Tech Integrations."
            print("Using fallback prompt based on internal LLM knowledge.")
        else:
            prompt = f"You are an expert B2B consultant. Based on the following company domain ({domain}) and short description ({scraped_desc}), write a professional, 3-section audit report: (1) Company Overview, (2) Value Proposition, (3) Recommended AI/Tech Integrations for their domain. Keep the tone professional and concise."
            print("Using standard prompt with scraped description.")
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        print("GEMINI RESPONSE:", response.text)
        
        if response.text:
            return response.text
    except Exception as e:
        print(f"EXPLICIT LLM ERROR - LLM generation failed: {e}")
        import traceback
        traceback.print_exc()
        
    return scraped_desc

def generate_audit_report(name: str, company_domain: str, company_info: str) -> str:
    """
    Generates a professional-looking PDF document containing the lead's audit report using WeasyPrint.
    Returns the file path of the generated PDF.
    """
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse Markdown to HTML
    company_info_html = markdown.markdown(company_info)
    
    # Set up Jinja2 Environment (loads templates from current directory)
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('report_template.html')
    
    # Render HTML Template with context variables
    html_out = template.render(
        name=name,
        company_domain=company_domain,
        date=datetime.now().strftime("%B %d, %Y"),
        company_info_html=company_info_html
    )
    
    # Save the PDF file using WeasyPrint
    file_path = os.path.join(output_dir, f"{company_domain}_audit_report.pdf")
    HTML(string=html_out).write_pdf(file_path)
    
    return file_path

def send_email_with_report(recipient_name: str, recipient_email: str, pdf_file_path: str):
    """
    Sends an email with the generated PDF report attached.
    """
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    if not sender_email or not sender_password:
        print("Warning: Email credentials not found in .env file. Skipping email delivery.")
        return
        
    msg = EmailMessage()
    msg['Subject'] = 'Your Custom Tech Audit Report'
    msg['From'] = sender_email
    msg['To'] = recipient_email
    
    # Email Body
    body = f"Hello {recipient_name},\n\nThank you for your interest! We have performed a preliminary audit based on your company domain.\nPlease find your custom Tech Audit Report attached to this email.\n\nBest regards,\nThe Lead Automation Team\n"
    msg.set_content(body)
    
    # Attach PDF
    try:
        with open(pdf_file_path, 'rb') as f:
            pdf_data = f.read()
            pdf_name = os.path.basename(pdf_file_path)
            msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=pdf_name)
    except Exception as e:
        print(f"Failed to read PDF file for attachment: {e}")
        return
        
    # Send Email
    try:
        # Using Gmail's SMTP server as a common default
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print(f"Email successfully sent to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.post("/submit-lead")
def submit_lead(lead: LeadSubmitRequest):
    """
    Accepts a lead submission. 
    Validation for required fields and valid email format is handled automatically by Pydantic.
    """
    # Enrich company data
    company_info = enrich_company_data(lead.company_domain)
    
    # Generate Audit Report
    report_path = generate_audit_report(lead.name, lead.company_domain, company_info)
    
    # Send Email
    send_email_with_report(lead.name, lead.email, report_path)
    
    # Add enriched data and report path to response
    lead_data = lead.model_dump()
    lead_data["company_info"] = company_info
    lead_data["report_path"] = report_path
    
    return {
        "message": "Lead submitted successfully, report generated and email sent (if configured).",
        "data": lead_data
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
