import telebot
import re
import os
from threading import Thread
from flask import Flask

# =========================
# WEB SERVER
# =========================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running", 200

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


# =========================
# BOT CONFIG
# =========================
BOT_TOKEN = "YOUR_BOT_TOKEN"
ADMIN_USERNAME = "@your_admin_username"

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)


# =========================
# NORMALIZE
# =========================
def normalize(text):
    text = text.lower()
    text = text.replace("=", "\n")
    text = text.replace("-", "\n")
    text = text.replace("/", " ")
    text = text.replace(".", " ")
    return text


# =========================
# TYPE DETECT (UNCHANGED)
# =========================
type_map = {
    "Mega": {"aliases": ["mega", "မီ"], "discount": 0.07},
    "Du": {"aliases": ["du2d", "du", "ဒု"], "discount": 0.07},
    "MM": {"aliases": ["mm"], "discount": 0.10},
}

def detect_type(text):
    for name, cfg in type_map.items():
        for alias in cfg["aliases"]:
            if alias in text:
                return name, cfg["discount"]
    return None, 0


# =========================
# ✔ FIXED CALC ONLY
# =========================
def calculate(text):

    total = 0
    lines = [l.strip() for l in normalize(text).split("\n") if l.strip()]

    for line in lines:

        # ======================
        # KHWE (FIXED)
        # ======================
        if "ခွေ" in line:

            nums = re.findall(r'\d+', line)

            if not nums:
                continue

            n = len(nums)

            base = n * (n - 1)

            if "ပူး" in line:
                pair = sum(1 for x in nums if len(x) == 2 and x[0] == x[1])
                total += base + pair
            else:
                total += base

            continue

        # ======================
        # TOP / BRAKET
        # ======================
        if "ထိပ်" in line or "ဘရိတ်" in line:
            nums = re.findall(r'\d+', line)
            if nums:
                total += 10 * len(nums)
            continue

        # ======================
        # EVEN / ODD
        # ======================
        if any(x in line for x in ["စမ", "စစ", "မမ"]):
            total += 25
            continue

        # ======================
        # PAIR SYSTEM
        # ======================
        if "ကပ်" in line:
            nums = re.findall(r'\d+', line)
            total += len(nums) * len(nums)
            continue

        # ======================
        # DEFAULT
        # ======================
        nums = re.findall(r'\d+', line)
        total += len(nums)

    return total


# =========================
# START
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Bot စတင်ပါပြီ\nစာရင်းပို့ပြီးတွက်နိုင်ပါပြီ။")


# =========================
# MAIN HANDLER (UNCHANGED)
# =========================
@bot.message_handler(func=lambda m: True)
def handler(message):

    text = message.text
    user = message.from_user.first_name or "User"

    try:
        type_name, discount = detect_type(text)

        if not type_name:
            bot.reply_to(message, f"📢 {ADMIN_USERNAME}\nType မတွေ့ပါ")
            return

        total = calculate(text)

        cashback = int(total * discount)
        final = total - cashback

        result = (
            f"👤 {user}\n\n"
            f"📊 {type_name} Total = {total:,} ကျပ်\n"
            f"🎁 Cash Back = {cashback:,} ကျပ်\n"
            f"💵 Total = {final:,} ကျပ်"
        )

        bot.reply_to(message, result)

    except Exception:
        bot.reply_to(message, "❌ Error")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling()
