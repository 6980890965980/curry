import asyncio
import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx

app = FastAPI()
SERVICE_URL = os.getenv("SERVICE_URL", "https://stephen-curry.onrender.com")

# set up Jinja2
templates = Jinja2Templates(directory="templates")


# ─── Scheduled external ping ─────────────────────────────────────────────────
@app.on_event("startup")
async def schedule_ping_task():
    async def ping_loop():
        async with httpx.AsyncClient(timeout=5) as client:
            while True:
                try:
                    resp = await client.get(f"{SERVICE_URL}/ping")
                    if resp.status_code != 200:
                        print(f"Health ping returned {resp.status_code}")
                except Exception as e:
                    print(f"External ping failed: {e!r}")
                await asyncio.sleep(10)
    asyncio.create_task(ping_loop())


# ─── HEALTHCHECK ───────────────────────────────────────────────────────────────
@app.get("/ping")
async def ping():
    return {"status": "alive"}


# ─── RENDER HOME PAGE ───────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Pass any data you need into the template context
    context = {
        "request": request,
        "app_name": "My FastAPI Service",
        "status": "All systems nominal"
    }
    return templates.TemplateResponse("index.html", context)
