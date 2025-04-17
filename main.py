from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
import os

app = FastAPI()

# Temporary storage (replace with database later)
url_db = {}

@app.get("/")
async def health_check():
    return {"status": "OK"}

@app.post("/shorten")
async def shorten_url(url: str, expires_in: int = 24):
    key = f"short_{len(url_db)}"
    expires_at = datetime.now() + timedelta(hours=expires_in)
    url_db[key] = {"url": url, "expires_at": expires_at}
    return {
        "short_url": f"{os.getenv('VERCEL_URL', '')}/{key}",
        "expires_at": expires_at.isoformat()
    }

@app.get("/{key}")
async def redirect(key: str):
    if key not in url_db or datetime.now() > url_db[key]["expires_at"]:
        return {"error": "URL expired or invalid"}
    return RedirectResponse(url_db[key]["url"])

# Vercel-specific ASGI handler
async def app_handler(scope, receive, send):
    await app(scope, receive, send)

# Compatibility layer for Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)