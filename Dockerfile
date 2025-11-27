# Dockerfile for ParknGo Multi-Agent Parking System

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including curl for healthchecks
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create secrets directory
RUN mkdir -p secrets

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_ENV=production
ENV PORT=5000
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
ENV PYTHONUNBUFFERED=1

# Health check using curl
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run the application
CMD ["python", "app.py"]
