# 🚀 AI Business Audit & Lead Automation System

An end-to-end full-stack automation workflow that captures lead information, scrapes their company website, generates a highly personalized Business & Tech Audit Report using Google Gemini AI, and automatically emails a professionally formatted PDF to the client.

## ✨ Key Features

- **Automated Web Scraping:** Intelligently extracts company descriptions using `BeautifulSoup` with User-Agent spoofing to bypass basic bot-protection (e.g., Cloudflare).
- **AI-Powered Content Generation:** Integrates `google-genai` (Gemini 2.5 Flash) to analyze the scraped data and generate a comprehensive 3-section business audit: (1) Company Overview, (2) Value Proposition, and (3) Tech Integrations.
- **Smart Fallback Logic:** If scraping fails or is blocked (e.g., Amazon, Razorpay), the system seamlessly falls back to Gemini's internal knowledge base to ensure a report is always generated.
- **Premium PDF Generation:** Converts Markdown to HTML, injects it into a custom `Jinja2` template, and uses `WeasyPrint` to render a highly professional, visually appealing PDF report.
- **Automated Email Delivery:** Uses Python's `smtplib` to securely email the generated PDF report directly to the lead.
- **Modern User Interface:** A clean, responsive frontend built with HTML, JavaScript, and Tailwind CSS.

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python 3.12
- **Frontend:** HTML5, Tailwind CSS, Vanilla JavaScript
- **AI / LLM:** Google GenAI SDK (Gemini 2.5 Flash)
- **Document Rendering:** WeasyPrint, Jinja2, Markdown
- **Web Scraping:** Requests, BeautifulSoup4

## 📁 Project Structure

```text
├── main.py                  # Core FastAPI backend and automation logic
├── index.html               # Frontend UI for lead submission
├── report_template.html     # Jinja2 HTML template for the PDF layout
├── requirements.txt         # Python dependencies
├── .env.example             # Template for environment variables
├── .gitignore               # Ignored files (venv, pycache, .env, outputs)
└── README.md                # Project documentation
⚙️ Setup & Installation Instructions
Follow these steps to run the project locally:

1. Clone the repository

Bash
git clone [https://github.com/vanshika2818/Audit_report.git](https://github.com/vanshika2818/Audit_report.git)
cd Audit_report
2. Set up Environment Variables

Create a new file named .env in the root directory.

Copy the contents of .env.example into your new .env file.

Add your active API keys and Email App Password:

Code snippet
GEMINI_API_KEY=your_actual_gemini_api_key
SENDER_EMAIL=your_official_email@gmail.com
SENDER_PASSWORD=your_google_app_password
3. Install Dependencies
It is recommended to use a virtual environment.

Bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
4. Run the Application
Start the FastAPI server using Uvicorn:

Bash
uvicorn main:app --reload
5. Access the Platform
Open your web browser and navigate to: http://127.0.0.1:8000

🧠 Architectural Decisions & Problem Solving
Separation of Concerns: The PDF styling is decoupled from the Python code using Jinja2 and HTML/CSS, making future design changes effortless compared to rigid X/Y coordinate drawing in FPDF.

Error Handling: Implemented robust try-except blocks across API calls, scraping, and email functions to ensure the server never crashes due to third-party failures.

Security: Sensitive credentials are strictly managed via python-dotenv and ignored by Git to prevent API key leaks.


### Ise GitHub par kaise push karein?
Apne VS Code mein ek nayi file banaiye jiska naam `README.md` rakhein. Upar diya gaya poora content usme paste karke save karein. Phir terminal mein yeh commands chalayein:

```bash
git add README.md
git commit -m "Added comprehensive README for project evaluation"
git push origin main
