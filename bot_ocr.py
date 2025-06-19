import os
import logging
import re
import io
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from fastapi import FastAPI
import uvicorn
from PIL import Image
import pytesseract

# --- Configuración ---
TOKEN = os.environ["BOT_TOKEN"]
TARGET_GROUP_ID = int(os.environ.get("TARGET_GROUP_ID", "-1002565451607"))
PORT = int(os.environ.get("PORT", 8000))  # Render asigna el puerto automáticamente

# Crear app FastAPI para health checks
health_app = FastAPI()

@health_app.get("/")
async def health_check():
    return {"status": "ok", "service": "Telegram OCR Bot"}

# --- Funciones del bot ---

async def clear_telegram_state(token: str):
    bot = Bot(token=token)
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("✅ Webhook eliminado y pendientes descartados")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Descargar imagen
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        image = Image.open(io.BytesIO(image_bytes))
        
        # OCR
        text = pytesseract.image_to_string(image, lang='eng+spa')
        
        # Verificar si es imagen de Duolingo
        if not re.search(r'\b(duolingo|dwolingo)\b', text, re.IGNORECASE):
            return
        
        # Filtrar "duolingo"
        filtered_text = re.sub(r'\b(duolingo|dwolingo)\b', '', text, flags=re.IGNORECASE)
        cleaned_lines = [line.strip() for line in filtered_text.splitlines() if line.strip()]
        cleaned_text = '\n'.join(cleaned_lines)
        
        if not cleaned_text.strip():
            return
        
        # Extraer frases
        english_phrase = ""
        spanish_phrase = ""
        
        # Intento 1: Buscar frase inglesa con puntuación final
        match_eng = re.search(r'^(.+?[.!?])', cleaned_text, re.DOTALL)
        if match_eng:
            english_phrase = match_eng.group(1).strip()
            rest_text = cleaned_text[match_eng.end():].strip()
            match_esp = re.search(r'^([¿¡]?.+?[.!?]?)$', rest_text, re.DOTALL)
            if match_esp:
                spanish_phrase = match_esp.group(1).strip()
        else:
            # Intento 2: Dividir por líneas
            lines = cleaned_text.split('\n')
            if len(lines) >= 2:
                english_phrase, spanish_phrase = lines[0], lines[1]
            else:
                return
        
        response = (
            "🇬🇧 *Frase en inglés:*\n"
            f"{english_phrase}\n\n"
            "🇪🇸 *Frase en español:*\n"
            f"{spanish_phrase}"
        )
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
        if TARGET_GROUP_ID:
            await context.bot.send_message(
                chat_id=TARGET_GROUP_ID,
                text=response,
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logging.error(f"Error procesando imagen: {e}")

async def set_target_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TARGET_GROUP_ID
    chat_id = update.message.chat_id
    TARGET_GROUP_ID = chat_id
    await update.message.reply_text(
        f"✅ Grupo destino configurado: `{chat_id}`",
        parse_mode='Markdown'
    )
    logging.info(f"Grupo destino actualizado: {chat_id}")

async def run_bot():
    """Inicia el bot de Telegram en modo polling."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    await clear_telegram_state(TOKEN)
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(CommandHandler("setgroup", set_target_group))
    
    logging.info("Bot de Telegram iniciado en modo polling")
    await application.run_polling()

async def run_health_server():
    """Inicia el servidor HTTP para health checks."""
    config = uvicorn.Config(
        app=health_app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
    server = uvicorn.Server(config)
    logging.info(f"Servidor de salud iniciado en puerto {PORT}")
    await server.serve()

async def main():
    """Función principal que ejecuta ambas tareas simultáneamente."""
    await asyncio.gather(
        run_health_server(),
        run_bot()
    )

if __name__ == "__main__":
    asyncio.run(main())