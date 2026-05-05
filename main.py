import telebot
import re
import os
from threading import Thread
from flask import Flask

# =========================
# Web Server
# =========================
server = Flask(__name__)

@server.route("/")
def home():
    return "Bot is running", 200


def run_web():
    port = int(os.environ.get("PORT", 8080))
    server.run(host="0.0.0.0", port=port)


# =========================
# Bot Config
# =========================
BOT_TOKEN = "YOUR_BOT_TOKEN"
ADMIN_USERNAME = "@your_admin_username"

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)


# =========================
# Type Map
# =========================
type_map = {
    "Du": {"aliases": ["du2d", "ဒု", "dubai"], "discount": 0.07},
    "Mega": {"aliases": ["mega", "မီ"], "discount": 0.07},
    "MM": {"aliases": ["mm"], "discount": 0.10},
    "Maxi": {"aliases": ["maxi", "မက်ဆီ"], "discount": 0.07},
    "Lao": {"aliases": ["lao", "လာအို"], "discount": 0.07},
    "Glo": {"aliases": ["glo", "global"], "discount": 0.03},
    "LD": {"aliases": ["ld", "london", "လန်ဒန်"], "discount": 0.07}
}


# =========================
# Start
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Bot စတင်ပါပြီ\nစာရင်းပို့ပြီးတွက်နိုင်ပါပြီ။")


# =========================
# Main Handler
# =========================
@bot.message_handler(func=lambda m: True)
def calculate(message):

    text = message.text.lower().strip()
    user_name = message.from_user.first_name or "User"

    type_name = None
    discount = 0

    # -------------------------
    # Type Detect (SAFE MATCH)
    # -------------------------
    for name, config in type_map.items():
        for alias in config["aliases"]:
            if re.search(rf'\b{re.escape(alias)}\b', text):
                type_name = name
                discount = config["discount"]
                break
        if type_name:
            break

    if not type_name:
        bot.reply_to(message, f"📢 {ADMIN_USERNAME}\nType မတွေ့ပါ")
        return

    lines = [x.strip() for x in text.splitlines() if x.strip()]

    total_money = 0
    total_count = 0

    for line in lines:

        # skip type line
        if any(re.search(rf'\b{re.escape(a)}\b', line)
               for t in type_map.values()
               for a in t["aliases"]):
            continue

        # =========================
        # R Price Format
        # =========================
        r_match = re.search(r'(.+)-(\d+)r(\d+)$', line)

        if r_match:
            body = r_match.group(1)
            normal_price = int(r_match.group(2))
            rprice = int(r_match.group(3))

            nums = re.findall(r'\d+', body)
            count = len(nums)

            total_money += (count * normal_price) + (count * rprice)
            total_count += count * 2
            continue

        # =========================
        # ခပ Logic
        # =========================
        if "ခပ" in line:
            nums = re.findall(r'\d+', line)

            if len(nums) >= 2:
                num = nums[0]
                price = int(nums[-1])

                n = len(num)
                count = (n * (n - 1)) + n

                total_money += count * price
                total_count += count
            continue

        # =========================
        # Mixed Price (FIXED)
        # =========================
        mixed = re.search(r'(.+)-(\d+)r(\d+)$', line)

        if mixed:
            body = mixed.group(1)
            normal_price = int(mixed.group(2))
            rprice = int(mixed.group(3))

            nums = re.findall(r'\d+', body)
            count = len(nums)

            total_money += (count * normal_price) + (count * rprice)
            total_count += count * 2
            continue

    # =========================
    # Final Calc
    # =========================
    cashback = int(total_money * discount)
    final_amt = total_money - cashback

    result = (
        f"👤 {user_name}\n\n"
        f"📊 Type = {type_name}\n"
        f"💰 Total = {total_money:,}\n"
        f"🎁 Cashback = {cashback:,}\n"
        f"💵 Final = {final_amt:,}"
    )

    bot.reply_to(message, result)


# =========================
# Run
# =========================
if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling()
