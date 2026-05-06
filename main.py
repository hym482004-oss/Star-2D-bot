import telebot
import re
import os
from threading import Thread
from flask import Flask

# =========================
# KEEP ALIVE SERVER
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
BOT_TOKEN = "8663479446:AAEHOXsSBCxpwh7fK3AbtEbbIAouBMFM9R4"
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

ADMINS = ["@admin1", "@owner"]


# =========================
# NORMALIZE (FIXED)
# =========================
def normalize(text):
    text = text.lower()
    text = text.replace("=", "\n")
    text = text.replace("-", "\n")
    text = text.replace("/", " ")
    text = text.replace(".", " ")
    text = re.sub(r'\s+', ' ', text)
    return text


# =========================
# COUNT ENGINE
# =========================
def calculate_count(line):

    nums = re.findall(r'\d+', line)
    if not nums:
        return 0, False

    is_reverse = 'r' in line or 'အာ' in line

    # KHWE
    if "ခွေ" in line:
        n = len(nums)
        return n * (n - 1), is_reverse

    # POWER TYPE
    elif any(x in line for x in ['pw', 'ပါဝါ', 'nk', 'နက္ခတ်', 'အပူး']):
        return 10, is_reverse

    # BK
    elif "bk" in line or "ဘရိတ်" in line:
        return 10, is_reverse

    # TOP
    elif "ထိပ်" in line:
        return 10, is_reverse

    # PATTERN
    elif any(x in line for x in ["စမ", "စစ", "မမ"]):
        return 25, is_reverse

    # KAP
    elif "ကပ်" in line:
        return len(nums) * len(nums), is_reverse

    # DEFAULT
    return len(nums), is_reverse


# =========================
# START
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ စာရင်းစတွက်ပေးပါမယ်ရှင့်")


# =========================
# MAIN HANDLER (FIXED 0 BUG)
# =========================
@bot.message_handler(func=lambda m: True)
def handle(message):

    user = message.from_user.first_name or "User"

    try:
        text = message.text
        if not text:
            return

        raw_text = text
        lower_text = text.lower()

        # =========================
        # FILTER
        # =========================
        trigger_words = [
            'ခွေ','ပူး','ထိပ်','bk','ကပ်','စမ','မမ','pw','nk','r','အပူး',
       'ခပ' ]

        has_digits = bool(re.search(r'\d', text))
        has_trigger = any(w in lower_text for w in trigger_words)

        if not has_digits and not has_trigger:
            return

        # =========================
        # PRICE DETECT (FIXED)
        # =========================
        price_match = re.search(r'(\d+)\s*[rR]\s*(\d+)', raw_text)
        price_match2 = re.search(r'(\d+)\s*$', raw_text)

        if price_match:
            price_norm = int(price_match.group(1))
            price_rev = int(price_match.group(2))
        elif price_match2:
            price_norm = int(price_match2.group(1))
            price_rev = price_norm
        else:
            price_norm = 0
            price_rev = 0

        # =========================
        # SPLIT (FIXED)
        # =========================
        lines = [l.strip() for l in normalize(text).split("\n") if l.strip()]

        total_amount = 0

        for line in lines:

            count, is_reverse = calculate_count(line)

            if count == 0:
                continue

            if is_reverse:
                total_amount += (count * price_norm) + (count * price_rev)
            else:
                total_amount += count * price_norm

        # =========================
        # ADMIN ALERT
        # =========================
        if total_amount == 0 and has_digits:
            bot.reply_to(
                message,
                f"📢 {' '.join(ADMINS)}\n⚠️ {user} ရဲ့စာရင်းစစ်ပေးပါ"
            )
            return

        # =========================
        # % SYSTEM
        # =========================
        percent = 7
        comp_name = "Company"

        if "mega" in lower_text or "မီ" in lower_text:
            comp_name = "Mega"
            percent = 7
        elif "du" in lower_text:
            comp_name = "Du"
            percent = 7
        elif "mm" in lower_text:
            comp_name = "MM"
            percent = 10

        discount = total_amount * (percent / 100)
        final = total_amount - discount

        # =========================
        # REPLY
        # =========================
        reply = (
            f"👤 {user}\n"
            f"{comp_name} Total = {int(total_amount):,} ကျပ်\n"
            f"{percent}% Cash Back = {int(discount):,} ကျပ်\n"
            f"Total = {int(final):,} ကျပ်"
        )

        bot.reply_to(message, reply)

    except Exception as e:
        print("ERROR:", e)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling()
