from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Simple "database"
url_db = {}

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/shorten")
async def shorten_url(url: str, expires_in: int = 24):
    key = f"short_{len(url_db)}"
    expires_at = datetime.now() + timedelta(hours=expires_in)
    url_db[key] = {"url": url, "expires_at": expires_at.isoformat()}
    return {
        "short_url": f"https://your-domain.vercel.app/{key}",
        "expires_at": expires_at.isoformat()
    }

@app.get("/{key}")
async def redirect(key: str):
    if key not in url_db:
        return {"error": "Not found"}
    return RedirectResponse(url_db[key]["url"])