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
# CALCULATE COUNT
# =========================
def calculate_count(line):
    nums = re.findall(r'\d+', line)
    if not nums:
        return 0, False

    # --- Check Reverse ---
    is_reverse = 'r' in line or 'အာ' in line

    # --- Khwe Rule ---
    if "ခွေ" in line:
        n = len(nums[0]) # Take first number length
        if "ပူး" in line:
            # ခွေပူး = n*(n-1) + n
            return (n * (n - 1)) + n, is_reverse
        else:
            # ခွေ = n*(n-1)
            return n * (n - 1), is_reverse

    # --- Break Rule (bk / ဘရိတ်) ---
    if "bk" in line or "ဘရိတ်" in line:
        # Any number bk = 10 ကွက်
        return 10, is_reverse

    # --- Top Rule (ထိပ်) ---
    if "ထိပ်" in line or "ထ" in line:
        return 10, is_reverse

    # --- Power / Nk / နက္ခတ် / အပူး ---
    if any(x in line for x in ['pw', 'ပါဝါ', 'nk', 'နက္ခတ်', 'အပူး']):
        return 10, is_reverse

    # --- Special Pattern ---
    if any(x in line for x in ["စမ", "စစ်", "မမ", "စုံစုံ", "စုံမ", "မစ်"]):
        return 25, is_reverse

    # --- Kap Rule (ကပ် / ကို) ---
    if "ကပ်" in line or "ကို" in line:
        if len(nums) >= 2:
            n1 = len(nums[0])
            n2 = len(nums[1])
            return n1 * n2, is_reverse
        else:
            return len(nums), is_reverse

    # --- Default: List of numbers ---
    return len(nums), is_reverse


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
def handle(message):

    user = message.from_user.first_name or "User"

    try:
        text = message.text.lower()
        original_text = message.text

        if not text:
            bot.reply_to(message, "❌ စာမရှိပါ")
            return

        # --- Company Check & Percentage ---
        percent = 0
        comp_name = ""
        if any(k in text for k in ['du', 'ဒု', 'ဒူ', 'dubai']):
            percent = 7
            comp_name = "Du"
        elif any(k in text for k in ['me', 'mega', 'မီ']):
            percent = 7
            comp_name = "Me"
        elif any(k in text for k in ['mm']):
            percent = 10
            comp_name = "MM"
        elif any(k in text for k in ['laos', 'လာအို', 'la']):
            percent = 7
            comp_name = "Laos"
        elif any(k in text for k in ['ld', 'london', 'လန်ဒန်']):
            percent = 7
            comp_name = "LD"
        else:
            percent = 7
            comp_name = "Company"

        # --- Price Extraction ---
        # Find X R Y pattern
        price_match = re.search(r'(\d+)\s*r\s*(\d+)', text)
        if price_match:
            price_norm = int(price_match.group(1))
            price_rev = int(price_match.group(2))
        else:
            # Find simple price at end
            price_simple = re.search(r'(\d+)\s*$', text)
            if price_simple:
                price_norm = int(price_simple.group(1))
                price_rev = price_norm
            else:
                price_norm = 0
                price_rev = 0

        # --- Split Lines ---
        lines = [l.strip() for l in normalize(original_text).split("\n") if l.strip()]

        total_amount = 0

        for line in lines:
            count, is_reverse_mode = calculate_count(line)

            if count <= 0:
                continue

            if is_reverse_mode:
                # R ပါရင်: ပုံမှန်ကွက် + ပြောင်းပြန်ကွက်
                # ပုံမှန်ဈေးနဲ့ ပြောင်းပြန်ဈေး မတူရင် သီးခြားတွက်
                # User logic: All original * price_norm + All reversed * price_rev
                total_amount += (count * price_norm) + (count * price_rev)
            else:
                total_amount += count * price_norm

        # --- Final Calculation ---
        discount = total_amount * (percent / 100)
        total_final = total_amount - discount

        # --- Reply ---
        reply = (
            f"👤 {user}\n"
            f"{comp_name} Total = {int(total_amount):,} ကျပ်\n"
            f"{percent}% Cash Back = {int(discount):,} ကျပ်\n"
            f"Total = {int(total_final):,} ကျပ်ဘဲ လွဲပေးပါရှင့်"
        )

        bot.reply_to(message, reply)

    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "❌ Error ဖြစ်နေပါသည်")


# =========================
# RUN BOT
# =========================
if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling()
