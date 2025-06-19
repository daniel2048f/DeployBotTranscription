FROM python:3.11-slim-bullseye
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      tesseract-ocr \
      tesseract-ocr-eng \
      tesseract-ocr-spa \
      libtesseract-dev \
      ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Verificación de Tesseract (para debug)
RUN which tesseract && tesseract --version

CMD ["python", "bot_ocr.py"]