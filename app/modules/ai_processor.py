import json
import google.generativeai as genai
from loguru import logger
from app.config import GEMINI_API_KEY

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("No GEMINI_API_KEY found. AI functions will fail.")

def analyze_business_profile(title: str, description: str, raw_text: str) -> dict:
    """Uses Gemini to clean, summarize, classify text, and extract services."""
    logger.info("Sending raw text to Gemini for intelligent extraction...")
    
    if not GEMINI_API_KEY:
        logger.error("Skipping AI step — no API key provided.")
        return {}

    prompt = f"""
    You are an expert business analyst and data structurer.
    I have scraped a website. Below is the unformatted raw text, page title, and meta description from it.
    
    Target:
    Title: {title}
    Description: {description}
    
    Raw Text chunk (truncated for size):
    {raw_text[:4000]}
    
    Based on this data, extract and generate the following JSON strict structure:
    {{
        "industry": "A high-level industry category (e.g. Technology, Healthcare, E-commerce, Local Services)",
        "business_type": "A specific type (e.g. B2B SaaS, Dental Clinic, Online Store)",
        "about": "A clean, well-grammar 2-3 sentence summary of what this business does and who they are.",
        "services": ["List of exactly 3 to 5 core services they offer, extracted and cleaned from the text."],
        "keywords": ["5 to 7 relevant SEO keywords for this business"]
    }}
    
    Return ONLY valid JSON. Focus on accuracy over making things up.
    """
    
    try:
        # Use JSON mime type to guarantee valid JSON string
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        
        result = json.loads(response.text)
        logger.success("Successfully processed unstructured data through Gemini!")
        return result
        
    except Exception as e:
        logger.error(f"Failed to process via Gemini: {e}")
        return {
            "industry": None,
            "business_type": None,
            "about": raw_text[:300].strip() + "..." if raw_text else None, # Fallback to raw text
            "services": [],
            "keywords": []
        }
