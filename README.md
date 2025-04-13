# VectorShield Web UI

This repository contains a **FastAPI** application that provides a minimal web-based UI for phishing detection workflows. It includes the following key features:

- A **FastAPI** server (`web_ui.py`) that:
  - Serves static files (CSS, favicon).
  - Renders an HTML UI for sending requests (insert, analyze, and report phishing emails).
  - Exposes **Prometheus** metrics on the `/metrics` endpoint.
- A series of **Pytest tests** (`tests/test_web_ui.py`) verifying key routes and assets.
- A **Dockerfile** for containerizing and distributing the application.

---

## Table of Contents
1. [Prerequisites](#prerequisites)  
2. [Local Development](#local-development)  
3. [Running Tests](#running-tests)  
4. [Prometheus Metrics](#prometheus-metrics)  
5. [Docker Build & Run](#docker-build--run)  
6. [Configuration](#configuration)  
7. [Contributing](#contributing)  
8. [License](#license)

---

## Prerequisites
- **Python 3.8+** (For local dev and testing)
- **pip** or **pipenv** for installing dependencies
- **Docker** (optional, for container builds)
- **Prometheus** (optional, if you want to scrape the provided metrics)

---

## Local Development

1. **Clone** the repository:
   ```bash
   git clone https://github.com/your-repo/vectorshield-web-ui.git
   cd vectorshield-web-ui
   ```

2. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r app/requirements.txt
   ```

3. **Run the server**:
   ```bash
   uvicorn app.web_ui:app --host 0.0.0.0 --port 8000 --reload
   ```
   - The UI is served at [http://localhost:8000/](http://localhost:8000/).

4. **Navigate to** the UI:
   - Open a browser at [http://localhost:8000/](http://localhost:8000/).
   - Use the form fields (Subject, Body, etc.) to test the UI.

---

## Running Tests

This project uses **Pytest** for testing. The test suite (`test_web_ui.py`) does the following checks:
- Ensures the **index page** (`/`) returns HTTP 200 and includes expected HTML elements.
- Verifies the **static CSS** route is served properly.
- Verifies the **favicon** route responds with the correct icon mime-type.

To run tests:

```bash
pytest -v tests
```

---

## Prometheus Metrics

A middleware in `web_ui.py` captures:
- **Request counts** by method, endpoint, and HTTP status.
- **Request durations** (in seconds).

The metrics are exposed on **`/metrics`** in Prometheus format. To scrape from Prometheus, add an entry like:

```yaml
scrape_configs:
  - job_name: "vectorshield-webui"
    static_configs:
      - targets: ["localhost:8000"]
```

Then you can see stats such as:
- `app_requests_total{method="GET",endpoint="/",http_status="200"}`  
- `app_request_duration_seconds_sum{method="GET",endpoint="/",}`

---

## Docker Build & Run

A sample Docker image is published to **`ghcr.io/vectorshield/web-ui:latest`**.  
You can **build** it locally:

```bash
docker build -t ghcr.io/vectorshield/web-ui:latest -f Dockerfile .
```

Then **run** it:

```bash
docker run -it --rm -p 8000:8000 ghcr.io/vectorshield/web-ui:latest
```

The service is now accessible at [http://localhost:8000/](http://localhost:8000/).

---

## Configuration

### Environment Variables

| Variable       | Default                  | Description                                       |
|----------------|--------------------------|---------------------------------------------------|
| `API_BASE_URL` | `http://localhost:5000` | The base URL that the UI uses for API calls       |

Set an environment variable before starting the server, for example:

```bash
export API_BASE_URL="https://my-production-api.example.com"
uvicorn app.web_ui:app --port 8000
```

---

## Contributing

1. **Fork** the repo and create a new branch for your feature or bugfix.
2. Commit and push your changes to your branch.
3. Create a Pull Request on the main repository describing your changes.

---

## License

This project is licensed under the terms of the **MIT License** (or whichever license you choose). See [LICENSE](LICENSE) for details.

---

## Contact

For questions or feedback, please open a GitHub Issue or contact the maintainers directly.