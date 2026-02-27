from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
import urllib.parse

from app.modules.orchestrator import process_url
from app.database.mongo import db

router = APIRouter()

class ScrapeRequest(BaseModel):
    url: str

@router.post("/scrape", status_code=202)
async def trigger_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Triggers a background data extraction job.
    Returns 202 Accepted immediately. Check GET /profile later.
    """
    background_tasks.add_task(process_url, request.url)
    return {
        "status": "Accepted", 
        "message": "Scrape task initiated in the background.", 
        "url": request.url
    }

@router.get("/profile/{url:path}")
async def get_profile(url: str):
    """
    Fetch the scraped, structured JSON given a source URL.
    Pass URL like: /profile/https://example.com
    """
    # Quick fix for potential fastAPI path parsing quirks
    decoded_url = urllib.parse.unquote(url)
    
    # query MongoDB
    profile = db["profiles"].find_one({"source_url": decoded_url})
    
    if not profile:
        # Fallback check stripping trailing slash
        profile = db["profiles"].find_one({"source_url": decoded_url.rstrip('/')})
        
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Is it still processing or was the URL invalid?")
        
    # Remove MongoDB internal ObjectId before dumping to JSON
    if "_id" in profile:
        profile["_id"] = str(profile["_id"])
        
    return profile
