import telebot
import re
import itertools
import os
from threading import Thread
from flask import Flask

# ==============================================
# 🔴 ၁။ Web Server (Render အတွက်)
# ==============================================
server = Flask(__name__)
@server.route("/")
def webhook(): return "Bot is running", 200

def run_web():
    port = int(os.environ.get("PORT", 8080))
    server.run(host="0.0.0.0", port=port)

# ==============================================
# 🔴 ၂။ Bot Configuration
# ==============================================
BOT_TOKEN = '8663479446:AAEHOXsSBCxpwh7fK3AbtEbbIAouBMFM9R4'
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

# ==============================================
# 🛠️ ၃။ စာကြောင်းအရှည်ကြီးကို ခွဲထုတ်တွက်ချက်သည့် Logic
# ==============================================

def process_line(line):
    line = line.lower().replace(' ', '')
    # ဈေးနှုန်းခွဲထုတ်ခြင်း
    match = re.search(r'(\d+)([ra]?)$', line)
    if not match: return 0, 0
    
    price = int(match.group(1))
    suffix = match.group(2)
    
    # ရှေ့က ဂဏန်းအတွဲများကို ခွဲထုတ်ခြင်း (ဥပမာ- 12.34.56)
    prefix = line[:match.start()]
    nums_in_line = re.findall(r'\d+', prefix)
    
    count = 0
    if any(x in line for x in ['ပတ်', 'အပါ', 'ပါ']):
        count = 19 if 'ပူးပို' not in line else 20
    elif any(x in line for x in ['ထိပ်', 'ထ', 'ဘရိတ်', 'bk']):
        count = 10
    elif 'ခွေ' in line:
        n = len(nums_in_line[0]) if nums_in_line else 0
        count = n * (n-1) // 2
    elif 'ကို' in line or 'ကပ်' in line:
        parts = re.split(r'ကို|ကပ်', line)
        n1, n2 = len(re.findall(r'\d', parts[0])), len(re.findall(r'\d', parts[1]))
        count = n1 * n2
    else:
        # ဒဲ့ဂဏန်းများ
        count = len(nums_in_line)

    # R (အာ) ပါလျှင် ၂ ဆတွက်ခြင်း (အပူးမပါသော အကွက်များအတွက်)
    if 'r' in line or 'အာ' in line:
        count = count * 2
        
    return count, price

# ==============================================
# 🤖 ၄။ Bot Handlers
# ==============================================

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "✅ **Shwethoon 2D Bot စတင်ပါပြီ**\n\nစာရင်းများကို ပုံစံတကျ ပို့ပေးပါ။ အမျိုးအစားမပါရင် Admin များကို Tag ခေါ်ပေးပါမည်။", parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def calculate(message):
    text = message.text.lower()
    
    # အမျိုးအစားသတ်မှတ်ချက်
    type_name = ""
    discount = 0.07
    
    if any(x in text for x in ['ဒူ', 'du']): type_name = "Du"
    elif any(x in text for x in ['မီ', 'mega', 'me']): type_name = "Mega"
    elif any(x in text for x in ['လာ', 'lao']): type_name = "Lao"
    elif any(x in text for x in ['ကလို', 'glo']): type_name = "Glo"; discount = 0.03

    if not type_name:
        # Admin Mention Logic (Optional)
        return

    # စာကြောင်း တစ်ကြောင်းချင်းစီ ခွဲတွက်ခြင်း
    lines = re.split(r'[\n\s,-]+', text)
    total_count = 0
    total_money = 0
    
    for line in lines:
        if re.search(r'\d+', line):
            c, p = process_line(line)
            total_count += c
            total_money += (c * p)

    if total_count == 0: return

    cash_back = total_money * discount
    final_amt = total_money - cash_back
    
    res_text = (f"✅ {type_name} အတွက် တွက်ချက်မှု\n"
                f"🔢 အကွက်အရေအတွက်: {total_count} ကွက်\n"
                f"💰 စုစုပေါင်း: {int(total_money):,} ကျပ်\n"
                f"🎁 Cash Back ({int(discount*100)}%): {int(cash_back):,} ကျပ်\n"
                f"💵 လွှဲရမည့်ငွေ: {int(final_amt):,} ကျပ်")
    
    bot.reply_to(message, res_text)

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling()
