import requests
from bs4 import BeautifulSoup
from loguru import logger
import time
from playwright.async_api import async_playwright
from app.config import CRAWL_DELAY, USER_AGENT, REQUEST_TIMEOUT, MAX_RETRIES

def ensure_delay():
    """Simple blocking delay to respect CRAWL_DELAY."""
    time.sleep(CRAWL_DELAY)

def static_crawl(url: str, retries: int = MAX_RETRIES) -> dict:
    """Fetch HTML content using static requests."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }
    
    for attempt in range(retries):
        ensure_delay()
        try:
            logger.info(f"Crawling {url} (Attempt {attempt+1}/{retries})...")
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, verify=False)
            
            # Raise exception for bad status codes
            response.raise_for_status()
            
            logger.success(f"Successfully fetched {url}")
            return {"success": True, "html": response.text, "status": response.status_code, "url": response.url}
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}. Status code: {e.response.status_code}")
            return {"success": False, "error": str(e), "status_code": e.response.status_code}
            
        except requests.exceptions.Timeout as e:
            logger.warning(f"Timeout occurred: {e}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {e}")
            break # Break on serious connection problems, don't retry endlessly

    logger.error(f"Failed to fetch {url} after {retries} attempts.")
    return {"success": False, "error": "Max retries exceeded", "status_code": None}

async def dynamic_crawl(url: str, retries: int = MAX_RETRIES) -> dict:
    """Fetch HTML content using Playwright headless browser for JS-rendered apps."""
    for attempt in range(retries):
        ensure_delay()
        try:
            logger.info(f"Dynamically crawling {url} JS app (Attempt {attempt+1}/{retries})...")
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                # Setting up a context that mimics a real user session to avoid blocks
                context = await browser.new_context(
                    user_agent=USER_AGENT,
                    viewport={"width": 1920, "height": 1080},
                    ignore_https_errors=True
                )
                
                page = await context.new_page()
                
                # We wait until the network is idle to ensure JS framework data finishes fetching
                response = await page.goto(url, wait_until="networkidle", timeout=REQUEST_TIMEOUT * 1000)
                
                if not response:
                    await browser.close()
                    continue
                    
                status = response.status
                
                if status >= 400:
                    logger.error(f"HTTP error {status} during dynamic crawl.")
                    await browser.close()
                    return {"success": False, "error": f"HTTP {status}", "status_code": status}
                
                # Fetching the final rendered HTML
                html = await page.content()
                final_url = page.url
                
                await browser.close()
                logger.success(f"Successfully dynamically fetched {final_url}")
                return {"success": True, "html": html, "status": status, "url": final_url}
                
        except Exception as e:
            logger.warning(f"Error dynamically rendering {url}: {e}")
            
    logger.error(f"Failed to dynamically render {url} after {retries} attempts.")
    return {"success": False, "error": "Max retries exceeded", "status_code": None}

def has_js_framework(html: str) -> bool:
    """Detect if the page heavily relies on JS (React, Vue, Next.js)."""
    if "id=\"__next\"" in html or "data-reactroot" in html:
        return True
    if "id=\"app\"" in html and "vue" in html.lower():
        return True
    return False
