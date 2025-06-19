FROM python:3.11-slim-bullseye
WORKDIR /app

# 1. Actualiza índices e instala Tesseract + idiomas y dependencias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      tesseract-ocr \
      tesseract-ocr-spa \
      tesseract-ocr-eng \
      libtesseract-dev \
      ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# 2. Copia y instala dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copia tu código y arranca el bot
COPY . .
CMD ["python", "bot_ocr.py"]
