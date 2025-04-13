import logging
import os
import time
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# For Prometheus
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

BASE_DIR = Path(__file__).resolve().parent
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")

app = FastAPI(title="VectorShield Web UI", version="1.0.0")

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "[%(asctime)s] %(levelname)s %(name)s - %(message)s"
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger("web_ui")
logger.setLevel(logging.INFO)

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
# 2. Middleware to measure each request
# ------------------------------------------------------------------------------
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    method = request.method
    path = request.url.path

    response = await call_next(request)

    # Measure how long the request took
    duration = time.time() - start_time

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
    return FileResponse(BASE_DIR / "static" / "favicon.ico")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"api_base_url": API_BASE_URL}
    )
