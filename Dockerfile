FROM python:3.11-slim-bullseye
WORKDIR /app

# Instalar Tesseract y dependencias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      tesseract-ocr \
      tesseract-ocr-eng \
      tesseract-ocr-spa \
      libtesseract-dev \
      ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Verificar instalación
RUN tesseract --version && tesseract --list-langs

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["python", "bot_ocr.py"]