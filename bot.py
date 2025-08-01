import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

app = Flask(__name__)
TOKEN = os.getenv('8461109289:AAGf5bE6uDLmu31IZeowBlpZwcevYxEMQyw')
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

# Command Handlers
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="🚀 Bot is alive!")

def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"You said: {update.message.text}")

# Add handlers
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

@app.route('/')
def home():
    return "🤖 Bot is running on Railway!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
