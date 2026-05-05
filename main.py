import telebot
import re
import os
from threading import Thread
from flask import Flask

# ==============================================
# 1. Web Server (Render Keep Alive)
# ==============================================
server = Flask(__name__)

@server.route("/")
def home():
    return "Bot is running", 200


def run_web():
    port = int(os.environ.get("PORT", 8080))
    server.run(host="0.0.0.0", port=port)


# ==============================================
# 2. Bot Config
# ==============================================
BOT_TOKEN = "8663479446:AAEHOXsSBCxpwh7fK3AbtEbbIAouBMFM9R4"
ADMIN_USERNAME = "@livia308"

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)


# ==============================================
# 3. Type Alias Mapping
# ==============================================
type_map = {
    "Du": {
        "aliases": [
            "du2d", "du", "ဒု", "ဒူ", "ဒူဘိုင်း",
            "ငဒူ", "dubai"
        ],
        "discount": 0.07
    },

    "Mega": {
        "aliases": [
            "mega", "မီ", "me"
        ],
        "discount": 0.07
    },

    "MM": {
        "aliases": [
            "mm"
        ],
        "discount": 0.10
    },

    "Maxi": {
        "aliases": [
            "maxi", "မက်ဆီ", "မက်စီ", "စီစီ"
        ],
        "discount": 0.07
    },

    "Lao": {
        "aliases": [
            "lao", "loa", "laos", "loas",
            "လာအို", "လာလာ", "la"
        ],
        "discount": 0.07
    },

    "Glo": {
        "aliases": [
            "glo", "global", "ကလို", "ဂလို"
        ],
        "discount": 0.03
    },

    "LD": {
        "aliases": [
            "ld", "landon", "london",
            "lan", "လန်ဒန်", "လန်လန်"
        ],
        "discount": 0.07
    }
}


# ==============================================
# 4. Start Command
# ==============================================
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(
        message,
        "✅ 2D Bot စတင်ပါပြီ\n\nစာရင်းပို့ပြီး တွက်ချက်နိုင်ပါပြီ။"
    )


# ==============================================
# 5. Main Calculation Handler
# ==============================================
@bot.message_handler(func=lambda m: True)
def calculate(message):
    text = message.text.lower().strip()
    user_name = message.from_user.first_name or "User"

    type_name = None
    discount = 0

    # Type Detect
    for name, config in type_map.items():
        if any(alias in text for alias in config["aliases"]):
            type_name = name
            discount = config["discount"]
            break

    # Type မပါရင် Admin Mention
    if not type_name:
        bot.reply_to(
            message,
            f"📢 {ADMIN_USERNAME}\n"
            f"🔎 {user_name} ရဲ့စာရင်းမှာ အမျိုးအစားမပါသေးပါ။\n"
            f"ကျေးဇူးပြု၍ စစ်ဆေးပေးပါ။"
        )
        return

    lines = [x.strip() for x in text.splitlines() if x.strip()]

    total_money = 0
    total_count = 0
    temp_numbers = []

    for line in lines:

        # type line skip
        if any(alias in line for t in type_map.values() for alias in t["aliases"]):
            continue

        # --------------------------
        # Group R Price
        # Example: 27-22-77-r200
        # --------------------------
        r_price = re.search(r'r(\d+)$', line)

        if r_price:
            price = int(r_price.group(1))

            nums = []
            for x in temp_numbers:
                nums.extend(re.findall(r'\d+', x))

            nums.extend(re.findall(r'\d+', line.replace(f"r{price}", "")))

            count = len(nums) * 2

            total_count += count
            total_money += count * price

            temp_numbers = []
            continue

        # --------------------------
        # ခပ Logic
        # Example: 170953ခပ100
        # --------------------------
        if "ခပ" in line:
            nums = re.findall(r'\d+', line)

            if nums:
                num = nums[0]
                price = int(nums[-1])

                n = len(num)
                count = (n * (n - 1)) + n

                total_count += count
                total_money += count * price

            continue

        # --------------------------
        # Mixed Price
        # Example: 34.35.94.95.55.25-600R400
        # --------------------------
        mixed = re.search(r'(\d+)r(\d+)$', line)

        if mixed:
            normal_price = int(mixed.group(1))
            rprice = int(mixed.group(2))

            body = line[:mixed.start()]
            nums = re.findall(r'\d+', body)

            normal_total = len(nums) * normal_price
            r_total = len(nums) * rprice

            total_count += len(nums) * 2
            total_money += normal_total + r_total

            continue

        # normal lines store
        temp_numbers.append(line)

    cashback = int(total_money * discount)
    final_amt = total_money - cashback

    result = (
        f"👤 {user_name}\n\n"
        f"✅ {type_name} စုစုပေါင်း Total = {total_money:,} ကျပ်\n\n"
        f"🎁 {int(discount * 100)}% Cash Back = {cashback:,} ကျပ်\n\n"
        f"💵 Total = {final_amt:,} ကျပ်"
    )

    bot.reply_to(message, result)


# ==============================================
# 6. Run Bot
# ==============================================
if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling()
