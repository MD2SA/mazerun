FROM python:3.11-slim

WORKDIR /app

# Install dependencies and wine
RUN apt-get update && apt-get install -y wine && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1

# Run persistence app
CMD ["python", "app.py"]
