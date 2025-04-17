from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta

app = FastAPI()

# Temporary storage (replace with database later)
url_db = {}

@app.get("/")
async def read_root():
    return {"status": "OK"}  # Simple health check

@app.post("/shorten")
async def shorten_url(url: str, expires_in: int = 24):
    key = f"short_{len(url_db)}"
    expires_at = datetime.now() + timedelta(hours=expires_in)
    url_db[key] = {"url": url, "expires_at": expires_at}
    return {
        "short_url": f"/{key}",  # Relative URL works better on Vercel
        "expires_at": expires_at.isoformat()
    }

@app.get("/{key}")
async def redirect(key: str):
    if key not in url_db or datetime.now() > url_db[key]["expires_at"]:
        return {"error": "URL expired or invalid"}
    return RedirectResponse(url_db[key]["url"])

# Required for Vercel
handler = app