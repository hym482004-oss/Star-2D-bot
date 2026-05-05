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
BOT_TOKEN = "YOUR_BOT_TOKEN"
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

# =========================
# ADMIN LIST
# =========================
ADMINS = ["@admin1", "@owner"]


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
# COUNT ENGINE (YOUR LOGIC)
# =========================
def calculate_count(line):

    nums = re.findall(r'\d+', line)
    if not nums:
        return 0, False

    is_reverse = 'r' in line or 'အာ' in line

    if "ခွေ" in line:
        n = len(nums)
        return n * (n - 1), is_reverse

    elif "bk" in line or "ဘရိတ်" in line:
        return 10, is_reverse

    elif "ထိပ်" in line:
        return 10, is_reverse

    elif any(x in line for x in ['pw', 'ပါဝါ', 'nk', 'နက္ခတ်', 'အပူး']):
        return 10, is_reverse

    elif any(x in line for x in ["စမ", "စစ", "မမ"]):
        return 25, is_reverse

    elif "ကပ်" in line:
        return len(nums) * len(nums), is_reverse

    else:
        return len(nums), is_reverse


# =========================
# START
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Bot စတင်ပါပြီ")


# =========================
# MAIN HANDLER
# =========================
@bot.message_handler(func=lambda m: True)
def handle(message):

    user = message.from_user.first_name or "User"

    try:
        text = message.text
        if not text:
            return

        lower_text = text.lower()

        # =========================
        # FILTER (GP SAFE)
        # =========================
        trigger_words = [
            'ခွေ','ပူး','ထိပ်','bk','ကပ်','စမ','မမ','pw','nk','r','အပူး'
        ]

        has_digits = bool(re.search(r'\d', text))
        has_trigger = any(w in lower_text for w in trigger_words)

        if not has_digits and not has_trigger:
            return

        # =========================
        # PRICE DETECT
        # =========================
        price_match = re.search(r'(\d+)\s*r\s*(\d+)', lower_text)
        price_match2 = re.search(r'(\d+)\s*[-=]\s*(\d+)', lower_text)
        price_simple = re.search(r'(\d+)\s*$', lower_text)

        if price_match:
            price_norm = int(price_match.group(1))
            price_rev = int(price_match.group(2))
        elif price_match2:
            price_norm = int(price_match2.group(1))
            price_rev = int(price_match2.group(2))
        elif price_simple:
            price_norm = int(price_simple.group(1))
            price_rev = price_norm
        else:
            price_norm = 0
            price_rev = 0

        # =========================
        # CALCULATION
        # =========================
        lines = [l.strip() for l in normalize(text).split("\n") if l.strip()]

        total_amount = 0

        for line in lines:
            count, is_reverse = calculate_count(line)

            if count <= 0:
                continue

            if is_reverse:
                total_amount += (count * price_norm) + (count * price_rev)
            else:
                total_amount += count * price_norm

        # =========================
        # ADMIN ALERT (NO VALID DATA)
        # =========================
        if total_amount == 0 and has_digits:
            admin_text = " ".join(ADMINS)
            bot.reply_to(
                message,
                f"📢 {admin_text}\n⚠️ {user} ရဲ့စာရင်းကို စစ်ဆေးပေးပါရှင့်"
            )
            return

        # =========================
        # % SYSTEM
        # =========================
        percent = 7
        comp_name = "Company"

        if any(k in lower_text for k in ['du', 'ဒု', 'dubai']):
            percent = 7
            comp_name = "Du"
        elif any(k in lower_text for k in ['me', 'mega', 'မီ']):
            percent = 7
            comp_name = "Mega"
        elif any(k in lower_text for k in ['mm']):
            percent = 10
            comp_name = "MM"
        elif any(k in lower_text for k in ['lao', 'လာအို']):
            percent = 7
            comp_name = "Lao"
        elif any(k in lower_text for k in ['ld', 'london']):
            percent = 7
            comp_name = "LD"

        discount = total_amount * (percent / 100)
        final_total = total_amount - discount

        # =========================
        # REPLY
        # =========================
        reply = (
            f"👤 {user}\n"
            f"{comp_name} Total = {int(total_amount):,} ကျပ်\n"
            f"{percent}% Cash Back = {int(discount):,} ကျပ်\n"
            f"Total = {int(final_total):,} ကျပ်"
        )

        bot.reply_to(message, reply)

    except Exception as e:
        print(e)


# =========================
# RUN BOT
# =========================
if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling()
