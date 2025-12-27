# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
# Note: PORT is automatically provided by Cloud Run, no need to set it here
ENV PYTHONUNBUFFERED=1

# Expose port (Cloud Run will use the PORT env var it provides)
EXPOSE 8080

# Run the application with uvicorn for production
# Cloud Run will provide the PORT environment variable automatically
CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
