import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from dotenv import load_dotenv
from pdf2docx import Converter
from prometheus_client import start_http_srver

start_http_srver(8000)

# Загрузка токена из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Папка для временных файлов
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Пришли мне PDF-файл, и я конвертирую его в DOCX.")

# Команда /help
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь PDF-файл, и я верну его в формате DOCX.")

# Обработка входящих файлов
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = None
    file_name = "file.pdf"

    if update.message.document:
        file = await update.message.document.get_file()
        file_name = update.message.document.file_name
    else:
        await update.message.reply_text("Пожалуйста, отправь именно PDF-документ.")
        return

    # Проверка на PDF
    if not file_name.lower().endswith(".pdf"):
        await update.message.reply_text("Я умею работать только с PDF-файлами.")
        return

    pdf_path = os.path.join(DOWNLOAD_DIR, file_name)
    docx_filename = file_name.replace(".pdf", ".docx")
    docx_path = os.path.join(DOWNLOAD_DIR, docx_filename)

    # Скачивание PDF
    await file.download_to_drive(pdf_path)

    try:
        # Конвертация
        converter = Converter(pdf_path)
        converter.convert(docx_path, start=0, end=None)
        converter.close()

        # Отправка пользователю
        await update.message.reply_text("Готово! Вот твой файл DOCX:")
        await update.message.reply_document(document=open(docx_path, "rb"))

    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при конвертации: {e}")
    finally:
        # Удаление исходного PDF и docx-файла
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        if os.path.exists(docx_path):
            os.remove(docx_path)

# Запуск приложения
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_file))

    print("✅ Бот запущен...")
    app.run_polling()