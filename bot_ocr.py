import logging
import re
import os
import sys
from telegram import Update, Bot
from telegram.error import Conflict
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from PIL import Image
import pytesseract
import io


# SOLO PARA WINDOWS: Descomenta la siguiente línea si usas Windows
#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Obtener el token de una variable de entorno
TOKEN = os.environ.get("TOKEN", "7894095577:AAFH9VOmINKWsv_Z57tcgVrhHw--Y4pLovU")

# Variable para almacenar el ID del grupo destino
TARGET_GROUP_ID = -1002565451607

# ----- SOLUCIÓN PARA CONFLICTOS -----
def clear_webhook(token):
    try:
        bot = Bot(token=token)
        bot.delete_webhook(drop_pending_updates=True)
        logging.info("✅ Webhook eliminado y actualizaciones pendientes descartadas")
    except Exception as e:
        logging.error(f"⚠️ Error al eliminar webhook: {e}")

def handle_conflict(update, context):
    if isinstance(context.error, Conflict):
        logging.critical("🔴 CONFLICTO: Otra instancia del bot está ejecutándose. Cerrando...")
        sys.exit(1)
# -----------------------------------

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Descargar la imagen
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        
        # Convertir bytes a imagen
        image = Image.open(io.BytesIO(image_bytes))
        
        # Aplicar OCR (español e inglés)
        text = pytesseract.image_to_string(image, lang='eng+spa')
        
        # Verificar si el texto contiene "duolingo" o "dwolingo"
        if not re.search(r'\b(duolingo|dwolingo)\b', text, re.IGNORECASE):
            return
        
        # Filtrar "duolingo" y "dwolingo"
        filtered_text = re.sub(
            r'\b(duolingo|dwolingo)\b', 
            '', 
            text, 
            flags=re.IGNORECASE
        )
        
        # Limpiar espacios extras y líneas vacías
        cleaned_lines = [line.strip() for line in filtered_text.splitlines() if line.strip()]
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Verificar si queda texto después del filtrado
        if not cleaned_text.strip():
            return
        
        # Dividir en frases inglés y español
        english_phrase = ""
        spanish_phrase = ""
        
        # Buscar la primera frase (inglés)
        english_match = re.search(r'^(.+?[.!?])', cleaned_text, re.DOTALL)
        if english_match:
            english_phrase = english_match.group(1).strip()
            spanish_text = cleaned_text[english_match.end():].strip()
            spanish_match = re.search(r'^([¿¡]?.+?[.!?]?)$', spanish_text, re.DOTALL)
            if spanish_match:
                spanish_phrase = spanish_match.group(1).strip()
        else:
            lines = cleaned_text.split('\n')
            if len(lines) >= 2:
                english_phrase = lines[0]
                spanish_phrase = lines[1]
            else:
                return
        
        # Formatear la respuesta
        response = (
            "🇬🇧 *Frase en inglés:*\n"
            f"{english_phrase}\n\n"
            "🇪🇸 *Frase en español:*\n"
            f"{spanish_phrase}"
        )
        
        # 1. Responder en el grupo original
        await update.message.reply_text(response, parse_mode='Markdown')
        
        # 2. Enviar la misma respuesta al grupo adicional SI está configurado
        if TARGET_GROUP_ID:
            await context.bot.send_message(
                chat_id=TARGET_GROUP_ID,
                text=response,
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logging.error(f"Error: {e}")
        return

# Nuevo comando para obtener y configurar el ID del grupo
async def set_target_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TARGET_GROUP_ID
    chat_id = update.message.chat_id
    
    # Guardar el ID del grupo actual
    TARGET_GROUP_ID = chat_id
    
    # Confirmar al usuario
    await update.message.reply_text(
        f"✅ ¡Grupo destino configurado correctamente!\n"
        f"ID del grupo: `{chat_id}`\n\n"
        "Ahora todas las transcripciones se enviarán también a este grupo.",
        parse_mode='Markdown'
    )
    
    # Mostrar en consola para que puedas copiarlo
    print("\n" + "="*50)
    print(f"ID DEL GRUPO DESTINO: {chat_id}")
    print("="*50 + "\n")
    
    # Sugerencia para configurar permanente
    await update.message.reply_text(
        "💡 **Para hacer esta configuración permanente:**\n"
        "1. Copia el ID mostrado arriba\n"
        "2. Ábre tu código Python\n"
        "3. Busca la línea: `TARGET_GROUP_ID = None`\n"
        "4. Cámbiala por: `TARGET_GROUP_ID = TU_ID_AQUI`\n"
        "5. Guarda y reinicia el bot",
        parse_mode='Markdown'
    )

def main():
    # 1. Eliminar webhooks previos
    clear_webhook(TOKEN)
    
    # Configurar logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    
    # Crear la aplicación
    application = Application.builder().token(TOKEN).build()
    
    # 4. Manejador de errores para conflictos
    application.add_error_handler(handle_conflict)
    
    # Manejador para imágenes
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    # Manejador para el comando /setgroup
    application.add_handler(CommandHandler("setgroup", set_target_group))
    
    # Iniciar el bot en modo polling
    logging.info("Bot iniciado...")
    application.run_polling()

if __name__ == "__main__":
    main()