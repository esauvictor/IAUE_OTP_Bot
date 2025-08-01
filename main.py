import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5382044313
otp_file = "otp_data.json"

def load_data():
    if not os.path.exists(otp_file):
        return {}
    with open(otp_file, "r") as f:
        return json.load(f)

def save_data(data):
    with open(otp_file, "w") as f:
        json.dump(data, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "🏠 *IAUE Hostel OTP Registration*\n\n"
        "To complete your hostel bio-data submission, follow these simple steps:\n\n"
        "💳 *Make Payment*\n"
        "• Amount: ₦500\n"
        "• Bank: VFD MICROFINANCE BANK\n"
        "• Account Number: 4600415696\n"
        "• Account Name: SHUGALITE GLOBAL SOLUTIONS\n\n"
        "📲 *After Payment*\n"
        "1. Come back here\n"
        "2. Type: `I have paid`\n"
        "3. Send your payment screenshot\n"
        "4. Your OTP will be sent after confirmation ✅\n\n"
        "⚠️ *Do not pay twice.* Each student receives one OTP only."
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()
    user_id = update.message.chat_id
    data = load_data()

    if "i have paid" in user_text:
        data[str(user_id)] = {"status": "pending"}
        save_data(data)
        await update.message.reply_text("📷 Please send your payment screenshot.")
    elif user_text == "approve" and user_id == ADMIN_ID:
        for uid, info in data.items():
            if info["status"] == "pending":
                otp = str(100000 + int(uid[-4:]))
                data[uid]["status"] = "approved"
                data[uid]["otp"] = otp
                await context.bot.send_message(chat_id=uid, text=f"✅ OTP confirmed. Your OTP is: {otp}")
        save_data(data)
    else:
        await update.message.reply_text("🤖 Please follow the instructions.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    data = load_data()
    if str(user_id) in data and data[str(user_id)]["status"] == "pending":
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"📥 Payment screenshot received for {update.message.from_user.full_name} ({user_id})")
        await update.message.reply_text("✅ Payment received. Awaiting approval...")
    else:
        await update.message.reply_text("❌ No pending OTP record found for your payment.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

if __name__ == "__main__":
    app.run_polling()