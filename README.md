# DeployBotTranscription

Un bot de Telegram que utiliza OCR para detectar y transcribir frases bilingües en capturas de pantalla de Duolingo. Extrae texto en inglés y español usando Tesseract y responde con ambas traducciones en un formato limpio y legible. El bot también permite reenviar automáticamente el resultado a un grupo de Telegram y está completamente desplegado usando Docker y Render.

---

## 🚀 Funcionalidades

- 📸 Acepta imágenes (capturas de pantalla) de Duolingo enviadas por Telegram
- 🧠 Usa `pytesseract` para extraer texto mediante OCR
- 🇬🇧 Detecta frases en inglés y 🇪🇸 su equivalente en español
- 📤 Responde con la transcripción formateada
- 🔁 Reenvío automático al grupo de Telegram configurado
- ✅ Endpoint de salud disponible mediante FastAPI
- 🐳 Dockerizado para facilitar el despliegue
- ☁️ Desplegado en [Render](https://render.com)

---

## 🛠️ Tecnologías Utilizadas

- [Python 3](https://www.python.org/)
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Pillow (PIL)](https://pillow.readthedocs.io/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Docker](https://www.docker.com/)
- [Render](https://render.com/)

---

## 🧾 Requisitos

Librerías de Python utilizadas:

```
python-telegram-bot==20.3
Pillow==10.3.0
pytesseract==0.3.10
fastapi==0.115.12
uvicorn==0.34.2
```

Además, necesitas tener instalado Tesseract OCR en tu máquina o en el contenedor.

> ℹ️ Asegúrate de instalar los paquetes de idiomas para inglés y español:
>
> ```
> sudo apt-get install tesseract-ocr-eng tesseract-ocr-spa
> ```

---

## ⚙️ Variables de Entorno

Crea un archivo `.env` o define estas variables en el entorno de despliegue:

| Variable          | Descripción                     |
| ----------------- | ------------------------------- |
| `BOT_TOKEN`       | Token de tu bot de Telegram     |
| `TARGET_GROUP_ID` | ID del grupo destino (opcional) |
| `PORT`            | Puerto para el servidor FastAPI |

---

## 🐳 Despliegue con Docker

Compila y ejecuta localmente:

```bash
docker build -t duolingo-bot .
docker run -e BOT_TOKEN=tu_token_aqui -p 8000:8000 duolingo-bot
```

> No olvides agregar los paquetes de idioma de Tesseract en tu imagen Docker.

---

## 📦 Instalación de dependencias (para desarrollo local)

```bash
pip install -r requirements.txt
```

También debes instalar el binario de Tesseract (vía `apt`, `brew`, etc.).

---

## 🔁 Comandos del Bot

- Envía una **captura de pantalla de Duolingo**: el bot detectará frases bilingües y responderá con la transcripción.
- `/setgroup`: establece el grupo actual como destino para reenvíos automáticos.

---

## 🌐 Endpoint de Salud

El bot corre un servidor FastAPI en el `PORT` especificado con un endpoint de verificación:

```
GET /
Respuesta: {"status": "ok", "service": "Telegram OCR Bot"}
```

---

## 📁 Estructura del Proyecto

- `bot_ocr.py`: Script principal con la lógica del bot y el servidor FastAPI
- `Dockerfile`: Archivo para construir y desplegar la imagen del bot
- `requirements.txt`: Lista de dependencias necesarias

---

## 📌 Notas

- Este proyecto está diseñado con fines educativos o de demostración. No se almacena información.
- Asegúrate de que el bot tenga permisos para leer imágenes en los grupos.

---

## 🤖 Demo

El bot está desplegado y funcionando en Render:  
👉 [https://deploybottranscription.onrender.com](https://deploybottranscription.onrender.com)

---

## 📝 Licencia

Licencia MIT — puedes usarlo y modificarlo libremente.
