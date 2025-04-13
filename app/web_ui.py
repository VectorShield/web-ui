import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Base directory = /workspaces/web-ui/app
BASE_DIR = Path(__file__).resolve().parent

# If your main API is at a different URL/port, set it here:
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")

# Create the FastAPI app for the UI
app = FastAPI(title="VectorShield Web UI", version="1.0.0")

# Set up logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "[%(asctime)s] %(levelname)s %(name)s - %(message)s"
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger("web_ui")
logger.setLevel(logging.INFO)

# Mount static directory
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(BASE_DIR / "static" / "favicon.ico")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"api_base_url": API_BASE_URL}
    )

