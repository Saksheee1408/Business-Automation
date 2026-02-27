from pymongo import MongoClient
from app.config import MONGO_URI, MONGO_DB_NAME
from loguru import logger
from datetime import datetime

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
profiles_collection = db["profiles"]

def save_profile(url: str, data: dict):
    """Save or update the extracted data to database."""
    try:
        # Add timestamp
        data['scraped_at'] = datetime.utcnow()
        
        # Upsert: Update if the record exists, else Create
        result = profiles_collection.update_one(
            {"source_url": url},
            {"$set": data},
            upsert=True
        )
        if result.upserted_id:
            logger.success(f"Inserted new profile for {url}")
        else:
            logger.success(f"Updated existing profile for {url}")
    except Exception as e:
        logger.error(f"MongoDB save failed: {e}")
