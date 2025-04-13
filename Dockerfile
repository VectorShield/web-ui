FROM python:3.13-alpine

WORKDIR /app

# Copy only requirements first (for caching)
COPY app/requirements.txt .

# Install dependencies (without cache for smaller image)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY app/ .

# Create a non-root user for security
USER nobody

# Expose port for API
EXPOSE 8000

# Use Gunicorn for better performance (adjust workers as needed)
ENTRYPOINT ["uvicorn", "web_ui:app", "--host", "0.0.0.0", "--port", "8000"]
# uvicorn app.web_ui:app --host 0.0.0.0 --port 8000
