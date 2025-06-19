# bot_ocr.py
import os
import logging
import re
import io
import threading

from telegram import Update, Bot
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    ContextTypes,
    CommandHandler,
)
from fastapi import FastAPI
import uvicorn
from PIL import Image
import pytesseract

# --- Configuración desde env vars ---
TOKEN = os.environ["BOT_TOKEN"]
TARGET_GROUP_ID = int(os.environ.get("TARGET_GROUP_ID", "-1002565451607"))
PORT = int(os.environ.get("PORT", "8000"))

# --- Health check HTTP con FastAPI ---
health_app = FastAPI()

@health_app.get("/")
async def health_check():
    return {"status": "ok", "service": "Telegram OCR Bot"}

def start_health_server():
    uvicorn.run(health_app, host="0.0.0.0", port=PORT, log_level="warning")

# --- Funciones del bot ---
def clear_telegram_state(token: str):
    # En python-telegram-bot v22 delete_webhook es síncrono
    bot = Bot(token=token)
    bot.delete_webhook(drop_pending_updates=True)
    logging.info("✅ Webhook eliminado y pendientes descartados")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = await update.message.photo[-1].get_file()
        data = await photo.download_as_bytearray()
        img = Image.open(io.BytesIO(data))
        text = pytesseract.image_to_string(img, lang="eng+spa")

        if not re.search(r"\b(duolingo|dwolingo)\b", text, re.IGNORECASE):
            return

        filtered = re.sub(r"\b(duolingo|dwolingo)\b", "", text, flags=re.IGNORECASE)
        lines = [l.strip() for l in filtered.splitlines() if l.strip()]
        cleaned = "\n".join(lines)
        if not cleaned:
            return

        eng, esp = "", ""
        m = re.search(r"^(.+?[.!?])", cleaned, re.DOTALL)
        if m:
            eng = m.group(1).strip()
            rest = cleaned[m.end():].strip()
            m2 = re.search(r"^([¿¡]?.+?[.!?]?)$", rest, re.DOTALL)
            esp = m2.group(1).strip() if m2 else ""
        else:
            parts = cleaned.split("\n")
            if len(parts) >= 2:
                eng, esp = parts[0], parts[1]
            else:
                return

        resp = (
            "🇬🇧 *Frase en inglés:*\n" f"{eng}\n\n"
            "🇪🇸 *Frase en español:*\n" f"{esp}"
        )
        await update.message.reply_text(resp, parse_mode="Markdown")
        if TARGET_GROUP_ID:
            await context.bot.send_message(chat_id=TARGET_GROUP_ID, text=resp, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Error en handle_image: {e}")

async def set_target_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TARGET_GROUP_ID
    TARGET_GROUP_ID = update.effective_chat.id
    await update.message.reply_text(
        f"✅ Grupo destino configurado: `{TARGET_GROUP_ID}`",
        parse_mode="Markdown"
    )
    logging.info(f"Grupo destino actualizado: {TARGET_GROUP_ID}")

def main():
    # Logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    # 1) Limpiar estado de Telegram
    clear_telegram_state(TOKEN)

    # 2) Arrancar servidor de health check en un hilo demonio
    t = threading.Thread(target=start_health_server, daemon=True)
    t.start()
    logging.info(f"Health server escuchando en puerto {PORT}")

    # 3) Crear y arrancar bot en polling (bloqueante)
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.add_handler(CommandHandler("setgroup", set_target_group))

    logging.info("Bot iniciado en polling sin conflictos")
    app.run_polling()

if __name__ == "__main__":
    main()
