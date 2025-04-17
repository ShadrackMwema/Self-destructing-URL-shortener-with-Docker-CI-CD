from fastapi import FastAPI, Request, Body
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime, timedelta
import os

app = FastAPI()

# Configure templates
templates = Jinja2Templates(directory="templates")

# Serve static files if they exist
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    # No static directory, continue without it
    pass

# Temporary storage (replace with database later)
url_db = {}

class URLRequest(BaseModel):
    url: str
    expires_in: int = 24

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "OK"}

@app.post("/shorten")
async def shorten_url(url_data: URLRequest):
    key = f"short_{len(url_db)}"
    expires_at = datetime.now() + timedelta(hours=url_data.expires_in)
    url_db[key] = {"url": url_data.url, "expires_at": expires_at}
    base_url = os.getenv('VERCEL_URL', '')
    # Use https:// prefix if not localhost
    if base_url and not base_url.startswith('localhost'):
        base_url = f"https://{base_url}"
    else:
        base_url = "http://localhost:8000"
    return {
        "short_url": f"{base_url}/{key}",
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