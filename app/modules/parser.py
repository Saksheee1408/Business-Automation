import re
import urllib.parse
from bs4 import BeautifulSoup
from loguru import logger
from typing import Dict, Any

def extract_meta_tag(soup: BeautifulSoup, name: str = None, property: str = None) -> str:
    """Helper to safely extract a meta tag's content."""
    try:
        if name:
            tag = soup.find("meta", attrs={"name": name})
        elif property:
            tag = soup.find("meta", attrs={"property": property})
        else:
            return ""
            
        if tag and tag.get("content"):
            return tag.get("content").strip()
    except Exception:
        pass
        
    return ""

def parse_html(html: str, base_url: str) -> Dict[str, Any]:
    """Parse raw HTML and extract relevant fields using BeautifulSoup."""
    logger.info("Parsing HTML content...")
    soup = BeautifulSoup(html, "lxml")
    
    # Remove script and style elements completely to avoid noise
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    # Get the raw text
    text = soup.get_text(separator=' ', strip=True)

    # Dictionary to structure the data for mapping later
    data = {
        "title": soup.title.string.strip() if soup.title and soup.title.string else "",
        "meta_description": extract_meta_tag(soup, name="description") or extract_meta_tag(soup, property="og:description"),
        "og_title": extract_meta_tag(soup, property="og:title"),
        "about": text[:1000], # Grab first 1000 characters for now; the AI layer will summarize this.
        "links": [],
        "emails": [],
        "phones": [],
        "logo_url": None,
        "favicon_url": None,
        "h1": "",
    }

    # Extract H1 heading
    h1 = soup.find('h1')
    if h1:
        data["h1"] = h1.get_text(strip=True)

    # Advanced Logo Extraction Logic
    def find_logo() -> str:
        # Strategy 1: Look for explicit OpenGraph logo/image (often used if no other logo found)
        meta_logo = extract_meta_tag(soup, property="og:logo") or extract_meta_tag(soup, property="og:image")
        if meta_logo and ('logo' in meta_logo.lower() or 'brand' in meta_logo.lower()):
            return meta_logo

        # Strategy 2: Look in Schema.org JSON-LD
        import json
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                schema = json.loads(script.string if script.string else "")
                if isinstance(schema, dict) and 'logo' in schema:
                    if isinstance(schema['logo'], str): return schema['logo']
                    if isinstance(schema['logo'], dict) and 'url' in schema['logo']: return schema['logo']['url']
            except Exception:
                pass

        # Strategy 3: Look for generic classes/IDs associated with logos
        # (Very common in modern frameworks like Tailwind, Bootstrap, React)
        logo_classes = ['logo', 'brand', 'header-logo', 'navbar-brand', 'site-logo']
        for cls in logo_classes:
            img = soup.find('img', class_=re.compile(cls, re.I)) or soup.find('img', id=re.compile(cls, re.I))
            if img and img.get('src'):
                return img['src']

        # Strategy 4: Fallback to alt text matching "logo" (The original method)
        img = soup.find("img", alt=re.compile(r"\blogo\b", re.I))
        if img and img.get("src"):
            return img.get("src")
            
        # Strategy 5: Any image inside an anchor tag in a header/nav (usually the home link logo)
        header = soup.find('header') or soup.find('nav')
        if header:
            img_in_header = header.find('img')
            if img_in_header and img_in_header.get('src'):
                return img_in_header.get('src')
                
        return None

    extracted_logo = find_logo()
    if extracted_logo:
        data["logo_url"] = urllib.parse.urljoin(base_url, extracted_logo)

    # Favicon
    favicon = soup.find("link", rel="icon") or soup.find("link", rel="shortcut icon")
    if favicon:
        data["favicon_url"] = urllib.parse.urljoin(base_url, favicon.get("href", ""))

    # Simple email and telephone detection using `a href` values
    for link in soup.find_all('a', href=True):
        href = link.get('href').replace(' ', '')
        
        # Absolute links
        if href.startswith(('http://', 'https://')):
            data["links"].append(href)
            
        # Emails
        if href.startswith("mailto:"):
            email = href.replace("mailto:", "").split('?')[0] # Remove query params
            data["emails"].append(email)
            
        # Phones
        if href.startswith("tel:"):
            phone = href.replace("tel:", "")
            data["phones"].append(phone)

    # Some Regex for emails and phone numbers in the text body
    email_regex = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
    found_emails = email_regex.findall(text)
    data["emails"].extend(found_emails)
    
    # De-duplicate lists
    data["emails"] = list(set(data["emails"]))
    data["phones"] = list(set(data["phones"]))
    data["links"] = list(set(data["links"]))

    return data
