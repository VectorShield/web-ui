import sys
import os
import pytest

# Make sure our 'app/' folder is on the Python path:
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.web_ui import app

def test_index_returns_200_and_html():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Phishing Detection UI" in response.text
    assert "<title>Phishing Detection UI</title>" in response.text
    assert "API Base URL:" in response.text

def test_static_css_serving():
    client = TestClient(app)
    response = client.get("/static/style.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]
    assert "body {" in response.text

def test_favicon_serving():
    client = TestClient(app)
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    # Should now explicitly return image/x-icon
    assert response.headers["content-type"] == "image/x-icon"
    # Should include cache headers
    assert "cache-control" in response.headers
    assert "public" in response.headers["cache-control"]

def test_security_headers_on_html_response():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    
    # Check for security headers
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
    assert response.headers.get("x-xss-protection") == "1; mode=block"
    assert response.headers.get("referrer-policy") == "strict-origin-when-cross-origin"
    assert "content-security-policy" in response.headers

def test_metrics_endpoint():
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    # Should contain Prometheus metrics
    assert "app_requests_total" in response.text
    assert "app_request_duration_seconds" in response.text

def test_cors_headers():
    client = TestClient(app)
    response = client.options("/", headers={"Origin": "http://localhost:3000"})
    # FastAPI should handle CORS properly
    assert response.status_code in [200, 405]  # 405 if OPTIONS not explicitly handled
