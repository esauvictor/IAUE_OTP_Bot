import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get token with fallback for local testing
TOKEN = os.getenv('8461109289:AAGf5bE6uDLmu31IZeowBlpZwcevYxEMQyw')
if not TOKEN:
    logger.error("❌ No TELEGRAM_TOKEN found in environment variables")
    # Don't raise error - let the app start but log the issue
    application = None
else:
    try:
        application = Application.builder().token(TOKEN).build()
        logger.info("✅ Bot initialized successfully")
    except Exception as e:
        logger.error(f"❌ Bot initialization failed: {e}")
        application = None

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if application:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🚀 Bot is working!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if application:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Echo: {update.message.text}")

if application:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@app.route('/webhook', methods=['POST'])
async def webhook():
    if not application:
        return "Bot not configured", 503
    try:
        update = Update.de_json(await request.get_json(), application.bot)
        await application.process_update(update)
        return ''
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "Error", 400

@app.route('/')
def home():
    status = "running" if application else "misconfigured - check logs"
    return f"🤖 Bot status: {status}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
