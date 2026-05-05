import telebot
import re
import os
from threading import Thread
from flask import Flask

# =========================
# WEB SERVER (Keep Alive)
# =========================
server = Flask(__name__)

@server.route("/")
def home():
    return "Bot is running", 200

def run_web():
    port = int(os.environ.get("PORT", 8080))
    server.run(host="0.0.0.0", port=port)


# =========================
# BOT CONFIG
# =========================
BOT_TOKEN = "YOUR_BOT_TOKEN"
ADMIN_USERNAME = "@your_admin_username"

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)


# =========================
# TYPE CONFIG
# =========================
type_map = {
    "Mega": {"aliases": ["mega", "မီ"], "discount": 0.07},
    "Du": {"aliases": ["du2d", "du", "ဒု"], "discount": 0.07},
    "MM": {"aliases": ["mm"], "discount": 0.10},
}


# =========================
# NORMALIZE INPUT
# =========================
def normalize(text):
    text = text.lower()
    text = text.replace("=", "\n")   # critical fix
    text = re.sub(r'\s+', ' ', text)
    return text


# =========================
# TYPE DETECT
# =========================
def detect_type(text):
    for name, cfg in type_map.items():
        for alias in cfg["aliases"]:
            if re.search(rf'\b{re.escape(alias)}\b', text):
                return name, cfg["discount"]
    return None, 0


# =========================
# CORE PARSER (SAFE ENGINE)
# =========================
def parse_blocks(text):

    total_money = 0
    total_count = 0

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    for line in lines:

        # skip type line
        if any(a in line for t in type_map.values() for a in t["aliases"]):
            continue

        # =========================
        # R FORMAT BLOCK
        # =========================
        match = re.search(r'(\d+)r(\d+)', line)

        if match:

            normal_price = int(match.group(1))
            r_price = int(match.group(2))

            # remove R part before number counting
            clean = re.sub(r'\d+r\d+', '', line)

            nums = re.findall(r'\d+', clean)
            count = len(nums)

            total_money += count * (normal_price + r_price)
            total_count += count * 2

            continue

        # ignore other garbage lines safely
        continue

    return total_money, total_count


# =========================
# START COMMAND
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Bot စတင်ပါပြီ\nစာရင်းပို့ပြီးတွက်နိုင်ပါပြီ။")


# =========================
# MAIN HANDLER
# =========================
@bot.message_handler(func=lambda m: True)
def handler(message):

    text = normalize(message.text)
    user = message.from_user.first_name or "User"

    type_name, discount = detect_type(text)

    if not type_name:
        bot.reply_to(message, f"📢 {ADMIN_USERNAME}\nType မတွေ့ပါ")
        return

    total_money, total_count = parse_blocks(text)

    cashback = int(total_money * discount)
    final = total_money - cashback

    result = (
        f"👤 {user}\n\n"
        f"📊 {type_name} Total = {total_money:,} ကျပ်\n\n"
        f"🎁 Cashback = {cashback:,} ကျပ်\n\n"
        f"💵 Final = {final:,} ကျပ်ဘဲလွဲပါရှင့်"
    )

    bot.reply_to(message, result)


# =========================
# RUN BOT
# =========================
if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling()
