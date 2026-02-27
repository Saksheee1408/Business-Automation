import json
from openai import OpenAI
from loguru import logger
from app.config import GROQ_API_KEY

client = None
if GROQ_API_KEY:
    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )
else:
    logger.warning("No GROQ_API_KEY found. AI functions will fail.")

def analyze_business_profile(title: str, description: str, raw_text: str) -> dict:
    """Uses Gemini to clean, summarize, classify text, and extract services."""
    logger.info("Sending raw text to Groq for intelligent extraction...")
    
    if not client:
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
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        logger.success("Successfully processed unstructured data through Groq!")
        return result
        
    except Exception as e:
        logger.error(f"Failed to process via Groq: {e}")
        return {
            "industry": None,
            "business_type": None,
            "about": raw_text[:300].strip() + "..." if raw_text else None, # Fallback to raw text
            "services": [],
            "keywords": []
        }
