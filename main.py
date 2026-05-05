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
        n = len(nums[0])
        if "ပူး" in line:
            return (n * (n - 1)) + n, is_reverse
        else:
            return n * (n - 1), is_reverse

    # --- Break Rule (bk / ဘရိတ်) ---
    if "bk" in line or "ဘရိတ်" in line:
        bk_digits = re.findall(r'(\d+)bk', line)
        return len(bk_digits) * 10, is_reverse

    # --- Top Rule (ထိပ်) ---
    if "ထိပ်" in line or "ထ" in line:
        return 10, is_reverse

    # --- Power / Nk / နက္ခတ် / အပူး / PH ---
    if any(x in line for x in ['pw', 'ပါဝါ', 'nk', 'နက္ခတ်', 'အပူး', 'ph']):
        return 10, is_reverse

    # --- Special Pattern ---
    if any(x in line for x in ["စမ", "စစ", "မမ", "စုံစုံ", "စုံမ", "မစ်"]):
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
        text = message.text
        lower_text = text.lower()

        if not text:
            return

        # 🛑 RULE:
        # 1. ဂဏန်း အနည်းဆုံး 2 လုံးတွဲ (xx) ပါရမည်
        # 2. ဒါမှမဟုတ် စာရင်းစစ်စကားလုံး ပါရမည်
        # ဖုန်းနံပါတ် ရှည်ကြီးတွေကို ကျော်သွားမည်
        
        has_number_pair = re.search(r'\d{2}', text)
        trigger_words = ['ခွေ', 'ပူး', 'ထိပ်', 'bk', 'ဘရိတ်', 'ကပ်', 'ကို', 'စမ', 'စစ', 'မမ', 'pw', 'ပါဝါ', 'nk', 'နက္ခတ်', 'အပူး', 'ph', 'r', 'အာ']
        
        if not has_number_pair and not any(word in lower_text for word in trigger_words):
            return

        # --- Company Check & Percentage ---
        percent = 0
        comp_name = ""
        if any(k in lower_text for k in ['du', 'ဒု', 'ဒူ', 'dubai']):
            percent = 7
            comp_name = "Du"
        elif any(k in lower_text for k in ['me', 'mega', 'မီ']):
            percent = 7
            comp_name = "Me"
        elif any(k in lower_text for k in ['mm']):
            percent = 10
            comp_name = "MM"
        elif any(k in lower_text for k in ['laos', 'လာအို', 'la']):
            percent = 7
            comp_name = "Laos"
        elif any(k in lower_text for k in ['ld', 'london', 'လန်ဒန်']):
            percent = 7
            comp_name = "LD"
        else:
            percent = 7
            comp_name = "Company"

        # --- Price Extraction ---
        # Pattern: X R Y
        price_match = re.search(r'(\d+)\s*r\s*(\d+)', lower_text)
        # Pattern: X-Y or X=Y
        price_match2 = re.search(r'(\d+)\s*[-=]\s*(\d+)', lower_text)
        # Pattern: only price at end
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

        # --- Split Lines ---
        lines = [l.strip() for l in normalize(text).split("\n") if l.strip()]

        total_amount = 0

        for line in lines:
            count, is_reverse_mode = calculate_count(line)

            if count <= 0:
                continue

            if is_reverse_mode:
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
        pass


# =========================
# RUN BOT
# =========================
if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling()
