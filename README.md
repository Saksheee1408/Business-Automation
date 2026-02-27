# Website Data Extraction API

A complete, production-ready AI pipeline for intelligently scraping and structuring website data to power reverse-engineering or website generation tools. Designed to support normal static sites AND single-page applications (React/Next/Vue) fully rendering in browsers before extraction.

## ✨ Features
* **Modular Engine**: Validation → Crawler (Static/Playwright) → Parser (BeautifulSoup) → AI (Google Gemini) → Branding Evaluator.
* **Smart Crawling Auto-escalation**: Will do a blazing fast Static Request first. If a JS-Framework is heavily detected, it securely upgrades the scrape process to an asynchronous headless Playwright environment to force-render JS.
* **Intelligent Data Output (JSON)**: Leverages Gemini 1.5 Flash to write grammatically perfect summaries mapping unstructured `<p>` tags into Business Categories, Services, and core Keywords fields.
* **Branding Recognition Engine**: Iterates 5 different strategy paths to detect the exact brand logo, downloads it into memory, and extracts its exact Hex `#ColorPalette` representing the business theme using `ColorThief`.
* **API Wrapper**: Accessible over a slick asynchronous FastAPI.

---

## 🛠 Setup

### Requirements:
* MongoDB Running locally on port `27017`
* Python 3.10+
* Playwright binaries 

```powershell
# 1. Create your environment & install Python packages
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Install Playwright browser engines
playwright install chromium

# 3. Insert your Gemini AI API Token
# Open the generated .env file and replace it:
# GEMINI_API_KEY="AI..."
```

---

## 🚀 Running the API Server

Launch the webserver with:
```powershell
uvicorn app.main:app --reload
```

* Swagger API documentation automatically available at: `http://127.0.0.1:8000/docs`

---

## 📖 Endpoints

### 1. Trigger A Scrape (Asynchronous)
`POST /scrape`
Starts a background task. Since headless chromium and AI analysis can take 10-25 seconds per URL depending on network sizes, it returns a `202 Accepted` instantly.

**Request:**
```json
{
    "url": "https://stripe.com"
}
```

### 2. Fetch the Stored Output Profile
`GET /profile/{encoded_url}`
E.g., `GET /profile/https://stripe.com`

**Response Example:**
```json
{
  "source_url": "https://stripe.com",
  "crawl_status": "success",
  "confidence_score": 0.85,
  "business_profile": {
    "name": "Stripe | Financial Infrastructure for the Internet",
    "industry": "Financial Technology",
    "business_type": "B2B SaaS platform",
    "about": "Stripe is a software platform that enables businesses of all sizes to accept payments and manage their finances online...",
    "services": [
      "Payment processing",
      "Billing and subscription management",
      "Invoicing"
    ],
    "keywords": [
      "payment processing",
      "financial infrastructure"
    ]
  },
  "contact": {
    "email": [],
    "phone": [],
    "social_links": {}
  },
  "branding": {
    "logo_url": "https://b.stripecdn.com/logo.png",
    "primary_color": "#635BFF",
    "color_palette": ["#4F566B", "#0A2540", "#ffffff"],
    "fonts": ["Inter", "Roboto"]
  }
}
```

# Business-Automation
