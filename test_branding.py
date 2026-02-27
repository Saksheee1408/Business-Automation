import asyncio
import json
from app.modules.crawler import static_crawl, dynamic_crawl, has_js_framework
from app.modules.parser import parse_html
from app.modules.branding import enhance_branding
from loguru import logger

async def test_logo():
    url = "https://stripe.com"
    logger.info(f"Testing logo extraction & branding for {url}")
    
    # Static crawl to start
    crawl_result = static_crawl(url)
    html = crawl_result["html"]
    
    # Upgrade to dynamic if needed
    if has_js_framework(html):
        logger.info("JS framework detected, using Playwright...")
        dyn_result = await dynamic_crawl(url)
        html = dyn_result["html"]
        
    # Parse HTML
    parsed_data = parse_html(html, base_url=url)
    logo_url = parsed_data.get("logo_url")
    logger.info(f"Extracted Logo URL: {logo_url}")
    
    # Branding
    if logo_url:
        brand_data = enhance_branding(html, logo_url=logo_url)
        logger.info(f"Branding results:\n{json.dumps(brand_data, indent=2)}")
    else:
        logger.warning("No logo found!")
        
if __name__ == "__main__":
    asyncio.run(test_logo())
