import json
from loguru import logger
from datetime import datetime

from app.modules.validator import validate_target
from app.modules.crawler import static_crawl, dynamic_crawl, has_js_framework
from app.modules.parser import parse_html
from app.modules.ai_processor import analyze_business_profile
from app.modules.branding import enhance_branding
from app.database.mongo import save_profile
from app.models.profile import ScrapedProfile

async def process_url(url: str) -> dict:
    """Core pipeline. Returns dict with success/error."""
    logger.info(f"=== Starting extraction for {url} ===")
    
    # 1. Validation
    validation_status = validate_target(url)
    if not validation_status["valid"]:
        logger.error(f"Validation failed: {validation_status['error']}")
        return {"success": False, "error": validation_status["error"]}
        
    normalized_url = validation_status["url"]
    
    # 2. Crawler (Initial fast static pass)
    crawl_result = static_crawl(normalized_url)
    if not crawl_result["success"]:
        return {"success": False, "error": f"Static crawl failed: {crawl_result.get('error')}"}
        
    html = crawl_result["html"]
    final_url = crawl_result.get("url", normalized_url)
    is_dynamic = has_js_framework(html)
    
    # 2.5 Promote to dynamic if JS framework detected
    if is_dynamic:
        logger.warning("Detected heavy JS framework (React/Vue/Next.js). Upgrading to dynamic background rendering via Playwright...")
        
        dyn_result = await dynamic_crawl(normalized_url)
        if dyn_result["success"]:
            html = dyn_result["html"]
            final_url = dyn_result.get("url", normalized_url)
        else:
            logger.error("Dynamic crawl failed. Falling back to static HTML.")
    else:
        logger.info("Static HTML detected. Proceeding instantly.")
        
    # 3. Parser
    parsed_data = parse_html(html, base_url=final_url)
    
    # 3.5 AI Processor (Gemini)
    ai_data = analyze_business_profile(
        title=parsed_data.get("title", ""),
        description=parsed_data.get("meta_description", ""),
        raw_text=parsed_data.get("about", "")
    )
    
    # 3.8 Branding Intelligence (Colors & Fonts)
    brand_data = enhance_branding(
        html=html,
        logo_url=parsed_data.get("logo_url")
    )
    
    # 4. Normalization and Structuring
    data = {
        "source_url": normalized_url,
        "scraped_at": datetime.utcnow().isoformat(),
        "crawl_status": "success",
        "confidence_score": 0.85,

        "business_profile": {
            "name": parsed_data.get("title") or parsed_data.get("h1"),
            "industry": ai_data.get("industry"),
            "business_type": ai_data.get("business_type"),
            "about": ai_data.get("about", parsed_data.get("about")),
            "services": ai_data.get("services", []),
            "keywords": ai_data.get("keywords", [])
        },

        "contact": {
            "email": parsed_data.get("emails", []),
            "phone": parsed_data.get("phones", []),
            "address": "",
            "social_links": {}
        },

        "branding": {
            "logo_url": parsed_data.get("logo_url"),
            "favicon_url": parsed_data.get("favicon_url"),
            "primary_color": brand_data.get("primary_color"),
            "color_palette": brand_data.get("color_palette", []),
            "fonts": brand_data.get("fonts", [])
        },

        "technical_metadata": {
            "is_dynamic": is_dynamic,
            "page_title": parsed_data.get("title"),
            "meta_description": parsed_data.get("meta_description"),
        }
    }

    # Validate against Pydantic schema
    try:
        profile = ScrapedProfile(**data)
        logger.success("Data successfully validated against Pydantic schema.")
    except Exception as e:
        logger.error(f"Pydantic Validation Error: {e}")
        return {"success": False, "error": str(e)}

    # Save to Database
    logger.info("Saving to database...")
    save_profile(url=normalized_url, data=profile.model_dump())
    
    logger.success(f"=== Extraction complete for {normalized_url} ===")
    
    # Return serializable dict
    return {"success": True, "data": json.loads(profile.model_dump_json())}
