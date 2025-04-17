from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
import secrets

app = FastAPI()
links = {}  # Temporary "database" (replace with Redis later)

@app.post("/shorten")
async def shorten_url(url: str, expires_in: int = 24):  # Expires in 24h by default
    key = secrets.token_urlsafe(4) 
    expires_at = datetime.now() + timedelta(hours=expires_in)
    links[key] = {"url": url, "expires_at": expires_at.isoformat()}
    return {"short_url": f"/{key}", "expires_at": expires_at}

@app.get("/{key}")
async def redirect(key: str):
    if key not in links:
        raise HTTPException(status_code=404, detail="Link expired or invalid!")
    if datetime.now() > datetime.fromisoformat(links[key]["expires_at"]):
        del links[key]  # Auto-delete expired links
        raise HTTPException(status_code=410, detail="Link self-destructed! 💥")
    return {"original_url": links[key]["url"]}