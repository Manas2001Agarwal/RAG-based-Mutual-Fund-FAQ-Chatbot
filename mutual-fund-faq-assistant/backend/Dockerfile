# Use official lightweight Python image
FROM python:3.10-slim

# Ensure Python output is unbuffered
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies required by Chroma & PDF processing
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire backend code
COPY . /app/

# Create chroma directory if missing (Railway volume will mount onto it)
RUN mkdir -p /app/chroma_db

# Expose the port used by Uvicorn
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
