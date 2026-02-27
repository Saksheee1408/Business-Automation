import io
import re
import requests
from colorthief import ColorThief
from bs4 import BeautifulSoup
from loguru import logger

def enhance_branding(html: str, logo_url: str = None) -> dict:
    """Extracts fonts from HTML and color palette from a given logo image URL."""
    branding = {
        "primary_color": None,
        "color_palette": [],
        "fonts": [],
        "layout_style": "modern-minimal" # Default fallback placeholder
    }

    # 1. Extract Fonts from HTML
    soup = BeautifulSoup(html, "lxml")
    fonts_found = []
    
    # Try getting fonts from Google Fonts links
    for link in soup.find_all("link", href=True):
        href = link.get("href")
        if "fonts.googleapis.com/css" in href:
            # Example: ...family=Roboto:wght@400&family=Open+Sans...
            matches = re.findall(r'family=([^&:]+)', href)
            for m in matches:
                clean_name = m.replace("+", " ")
                if clean_name not in fonts_found:
                    fonts_found.append(clean_name)
                    
    # Also extract from inline/embedded CSS simply using regex
    inline_fonts = re.findall(r'font-family:\s*([^;\}]+)', html, re.IGNORECASE)
    for f in inline_fonts:
        parts = f.split(",")
        if parts:
            first_font = parts[0].strip().strip("'").strip('"')
            # very basic filter to avoid CSS junk
            if len(first_font) < 25 and "{" not in first_font:
                fonts_found.append(first_font)
                
    # Deduplicate and keep the top 3 core fonts
    fonts_found = list(dict.fromkeys(fonts_found))[:3]
    branding["fonts"] = fonts_found

    # 2. Extract Colors from Logo Image using ColorThief
    if logo_url:
        try:
            logger.info(f"Extracting color palette from logo image: {logo_url}")
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(logo_url, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            
            # Load into ColorThief
            image_stream = io.BytesIO(response.content)
            color_thief = ColorThief(image_stream)
            
            # Get dominant (primary) brand color
            dominant_color_rgb = color_thief.get_color(quality=1)
            branding["primary_color"] = '#%02x%02x%02x' % dominant_color_rgb
            
            # Get complementary color palette
            palette_rgb = color_thief.get_palette(color_count=5, quality=1)
            branding["color_palette"] = ['#%02x%02x%02x' % rgb for rgb in palette_rgb]
            
            logger.success("Brand colors extracted successfully!")
            
        except Exception as e:
            logger.error(f"Failed to extract colors from logo: {e}")

    return branding
