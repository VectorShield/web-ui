import logging
import os
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# For Prometheus
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

BASE_DIR = Path(__file__).resolve().parent
API_BASE_URL = os.getenv("API_BASE_URL", "http://172.17.0.2:5000")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

app = FastAPI(
    title="VectorShield Web UI", 
    version="1.0.0",
    description="A web interface for phishing detection workflows"
)

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "[%(asctime)s] %(levelname)s %(name)s - %(message)s"
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger("web_ui")
logger.setLevel(logging.INFO)

# Security middleware
if ALLOWED_HOSTS != ["*"]:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)

# CORS middleware - configure based on environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if os.getenv("ENVIRONMENT") == "development" else [API_BASE_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Mount static
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Templates
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# ------------------------------------------------------------------------------
# 1. Define Prometheus metrics
# ------------------------------------------------------------------------------
REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total number of requests to this FastAPI app",
    labelnames=["method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    "app_request_duration_seconds",
    "Histogram of request processing durations (in seconds)",
    labelnames=["method", "endpoint"]
)

# ------------------------------------------------------------------------------
# 2. Middleware to measure each request and add security headers
# ------------------------------------------------------------------------------
@app.middleware("http")
async def prometheus_and_security_middleware(request: Request, call_next):
    start_time = time.time()
    method = request.method
    path = request.url.path

    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled error processing {method} {path}: {e}")
        # Still update metrics for failed requests
        REQUEST_COUNT.labels(
            method=method,
            endpoint=path,
            http_status=500
        ).inc()
        raise HTTPException(status_code=500, detail="Internal server error")

    # Measure how long the request took
    duration = time.time() - start_time

    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Add CSP for HTML responses
    if "text/html" in response.headers.get("content-type", ""):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            f"connect-src 'self' {API_BASE_URL}"
        )

    # Update metrics
    REQUEST_LATENCY.labels(method=method, endpoint=path).observe(duration)
    REQUEST_COUNT.labels(
        method=method,
        endpoint=path,
        http_status=response.status_code
    ).inc()

    return response

# ------------------------------------------------------------------------------
# 3. Provide /metrics endpoint
# ------------------------------------------------------------------------------
@app.get("/metrics")
def metrics():
    """Expose Prometheus metrics."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# ------------------------------------------------------------------------------
# 4. Existing endpoints
# ------------------------------------------------------------------------------
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    favicon_path = BASE_DIR / "static" / "favicon.ico"
    if not favicon_path.exists():
        raise HTTPException(status_code=404, detail="Favicon not found")
    return FileResponse(
        favicon_path,
        media_type="image/x-icon",
        headers={"Cache-Control": "public, max-age=86400"}  # Cache for 1 day
    )

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"api_base_url": API_BASE_URL}
    )
