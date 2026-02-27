import urllib.parse
import urllib.robotparser
import requests
from loguru import logger
from app.config import USER_AGENT

def normalize_url(url: str) -> str:
    """Ensure URL is properly formatted with https."""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    # Remove trailing slash
    return url.rstrip('/')

def is_valid_url(url: str) -> bool:
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def can_crawl_url(url: str) -> bool:
    """Check robots.txt if crawling is allowed for the USER_AGENT."""
    parsed_url = urllib.parse.urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    request_headers = {"User-Agent": USER_AGENT}
    
    try:
        response = requests.get(robots_url, headers=request_headers, timeout=5, verify=False)
        if response.status_code != 200:
            logger.debug(f"robots.txt not found or inaccessible at {robots_url}. Proceeding.")
            return True
            
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(response.text.splitlines())
        
        # Check against both "*" and our specific user agent
        return (rp.can_fetch("*", url) and 
                rp.can_fetch(USER_AGENT, url))
    except Exception as e:
        logger.warning(f"Error checking robots.txt: {e}. Defaulting to allowing crawl.")
        return True

def validate_target(url: str) -> dict:
    normalized = normalize_url(url)
    
    if not is_valid_url(normalized):
        return {"valid": False, "url": url, "error": "Invalid URL format"}
        
    if not can_crawl_url(normalized):
        return {"valid": False, "url": normalized, "error": "Blocked by robots.txt"}
        
    return {"valid": True, "url": normalized, "error": None}
