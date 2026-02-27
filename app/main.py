from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Website Data Extraction API",
    description="A powerful AI pipeline extracting highly structured branding and contact blueprints from any URL.",
    version="1.0.0"
)

# Connect all the routes
app.include_router(router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Scraper API is running!"}

if __name__ == "__main__":
    import uvicorn
    # Can run this file directly to boot the server
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
