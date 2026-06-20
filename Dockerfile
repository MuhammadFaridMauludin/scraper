FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget curl gnupg unzip \
    libnss3 libxss1 libgbm1 libasound2 \
    libatk-bridge2.0-0 libgtk-3-0 \
    libglib2.0-0 libx11-6 libxcb1 \
    fonts-liberation xdg-utils \
    chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "scraper.py"]