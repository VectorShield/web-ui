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
    # Different OS / MIME libraries can produce variations of the icon MIME type
    assert response.headers["content-type"] in [
        "image/x-icon",
        "image/vnd.microsoft.icon",
        "application/octet-stream"  # Some systems may report .ico as octet-stream
    ]
