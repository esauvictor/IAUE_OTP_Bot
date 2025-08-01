from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler
import json, re, os
from datetime import datetime
from flask import Flask
import threading

# ===== CONFIG =====
TOKEN = "8461109289:AAGf5bE6uDLmu31IZeowBlpZwcevYxEMQyw"  # Replace with your bot token
ADMIN_ID = 5382044313  # Your Telegram user ID
OTP_FILE = "otps.json"
# ==================

# Keep-alive server for UptimeRobot
app = Flask('')


@app.route('/')
def home():
    return "I'm alive!"


def run():
    app.run(host='0.0.0.0', port=8080)


threading.Thread(target=run).start()


# Load & save OTPs
def load_otps():
    if not os.path.exists(OTP_FILE):
        return []
    with open(OTP_FILE, "r") as f:
        return json.load(f)


def save_otps(otps):
    with open(OTP_FILE, "w") as f:
        json.dump(otps, f, indent=2)


# Extract OTP from message
def extract_otp_data(text):
    name = re.search(r'Dear (.*?),', text)
    otp = re.search(r'OTP.*?: (\d+)', text)
    phone = re.search(r'Phone: (\d+)', text)
    if name and otp and phone:
        return {
            "name": name.group(1).strip(),
            "otp": otp.group(1).strip(),
            "phone": phone.group(1).strip(),
            "used": False,
            "telegram_id": None,
            "timestamp": str(datetime.now())
        }
    return None


# Handle user messages
def handle_text(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    user = update.effective_user

    # Student says they paid
    if text.lower() == "i have paid":
        update.message.reply_text("📷 Please send your payment screenshot.")
        return

    # Admin stores OTP from website
    if user.id == ADMIN_ID:
        data = extract_otp_data(text)
        if data:
            otps = load_otps()

            # Overwrite any old OTP for the same phone
            otps = [o for o in otps if o["phone"] != data["phone"]]
            otps.append(data)
            save_otps(otps)
            update.message.reply_text(f"✅ OTP stored for {data['name']}")
            return

        # Admin replies Approve
        if text.lower() == "approve":
            otps = load_otps()
            for otp in otps:
                if not otp["used"] and otp["telegram_id"]:
                    otp["used"] = True
                    save_otps(otps)
                    context.bot.send_message(
                        chat_id=otp["telegram_id"],
                        text=f"✅ Payment confirmed.\nYour OTP is: {otp['otp']}"
                    )
                    update.message.reply_text("✅ OTP sent to student.")
                    return
            update.message.reply_text(
                "❌ No pending OTP found or already used.")
            return


# Handle screenshot/photo
def handle_photo(update: Update, context: CallbackContext):
    user = update.effective_user
    telegram_id = user.id

    otps = load_otps()
    for otp in otps:
        if not otp["used"] and otp["telegram_id"] is None:
            otp["telegram_id"] = telegram_id
            save_otps(otps)
            context.bot.send_message(
                chat_id=ADMIN_ID,
                text=
                f"📥 Payment screenshot received for {otp['name']} ({otp['phone']})\nReply with: Approve"
            )
            update.message.reply_text(
                "✅ Payment received. Awaiting approval...")
            return

    update.message.reply_text(
        "❌ No pending OTP record found for your payment.")


# Welcome message
def start(update: Update, context: CallbackContext):
    welcome = (
        "🏠 *IAUE Hostel OTP Registration*\n\n"
        "*To complete your hostel bio-data submission, follow these simple steps:*\n\n"
        "💳 *Make Payment*\n"
        "• Amount: ₦500\n"
        "• Bank: VFD MICROFINANCE BANK\n"
        "• Account Number: `4600415696`\n"
        "• Account Name: *SHUGALITE GLOBAL SOLUTIONS*\n\n"
        "📲 *After Payment*\n"
        "1. Come back here\n"
        "2. Type: `I have paid`\n"
        "3. Send your payment screenshot\n"
        "4. Your OTP will be sent after confirmation ✅\n\n"
        "⚠️ *Do not pay twice.* Each student receives one OTP only.")
    update.message.reply_text(welcome, parse_mode="Markdown")


# Start bot
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command,
                                  handle_text))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    updater.start_polling()
    print("Telegram bot is running...")
    updater.idle()


if __name__ == "__main__":
    main()
