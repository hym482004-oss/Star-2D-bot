import telebot
import re
import itertools
import os
from threading import Thread
from flask import Flask

# ==============================================
# 🔴 ၁။ Web Server (Render Free Tier အတွက်)
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
# 🛠️ ၃။ Mention Function (Admin Tag ခေါ်ရန်)
# ==============================================
def get_admin_mentions(chat_id):
    try:
        admins = bot.get_chat_administrators(chat_id)
        mentions = ""
        for a in admins:
            if a.user.username: 
                mentions += f"@{a.user.username} "
            else: 
                mentions += f"[{a.user.first_name}](tg://user?id={a.user.id}) "
        return mentions
    except: 
        return "Admin များ"

# ==============================================
# 🛠️ ၄။ လူကြီးမင်း၏ တွက်နည်း Logic များ
# ==============================================
def get_numbers(text):
    # စာသားထဲက ဂဏန်းနှင့် လိုအပ်သောစာသားများကိုသာ ယူရန်
    text = text.lower().replace(' ', '')
    
    # ဈေးနှုန်းခွဲထုတ်ခြင်း (နောက်ဆုံးဂဏန်း)
    price_match = re.search(r'(\d+)$', text)
    if not price_match: return [], 0
    price = int(price_match.group(1))
    
    # ရှေ့ဂဏန်းများ
    main_match = re.search(r'^(\d+)', text)
    main_num = main_match.group(1) if main_match else ""
    
    res = []
    is_reverse = 'r' in text or 'အာ' in text

    # ၁။ ပတ်သီး (၁၉ သို့မဟုတ် ၂၀ ကွက်)
    if any(x in text for x in ['ပတ်', 'အပါ', 'ပါ']):
        res = [f"{i:02d}" for i in range(100) if main_num in f"{i:02d}"]
        if any(x in text for x in ['ပူးပို', '၂၀ကွက်', '20ကွက်']):
            # 99 ကဲ့သို့ အပူးကိုပါ ၂ ခါတွက်စေရန် (၂၀ ကွက်ရရန်)
            res.append(main_num + main_num)
        else:
            res = list(set(res)) # ပုံမှန်ဆို ၁၉ ကွက်

    # ၂။ ထိပ်စီး (၁၀ ကွက်)
    elif any(x in text for x in ['ထိပ်', 'ထ']):
        res = [f"{main_num}{i}" for i in range(10)]

    # ၃။ ဘရိတ် (၁၀ သို့မဟုတ် ၅၀ ကွက်)
    elif 'ဘရိတ်' in text or 'bk' in text:
        if any(x in text for x in ['စုံဘရိတ်', 'စုံbk']):
            res = [f"{i:02d}" for i in range(100) if (int(f"{i:02d}"[0]) + int(f"{i:02d}"[1])) % 10 in [0,2,4,6,8]]
        elif any(x in text for x in ['မဘရိတ်', 'မbk']):
            res = [f"{i:02d}" for i in range(100) if (int(f"{i:02d}"[0]) + int(f"{i:02d}"[1])) % 10 in [1,3,5,7,9]]
        else:
            res = [f"{i:02d}" for i in range(100) if (int(f"{i:02d}"[0]) + int(f"{i:02d}"[1])) % 10 == int(main_num) % 10]

    # ၄။ ခွေဂဏန်း
    elif 'ခွေ' in text:
        digits = list(main_num)
        if is_reverse:
            res = [a+b for a, b in itertools.permutations(digits, 2)]
        else:
            res = [a+b for a, b in itertools.combinations(digits, 2)]
            is_reverse = True

    # ၅။ အပူးပါခွေ / အပူးစုံ
    elif any(x in text for x in ['ပူး', 'အပူးပါ']):
        if main_num == "": # အပူးစုံ
            res = [f"{i}{i}" for i in range(10)]
        else:
            digits = list(main_num)
            res = [a+b for a, b in itertools.combinations(digits, 2)]
            res.extend([d+d for d in digits])
            is_reverse = True

    # ၆။ စုံစုံ/မမ/စမ/မစ (၂၅ ကွက်)
    elif any(x in text for x in ['စစ','မမ','စမ','မစ','စုံစုံ','စုံမ','မစုံ']):
        e, o = ['0','2','4','6','8'], ['1','3','5','7','9']
        p1 = e if (text.startswith('စ') or 'စုံ' in text[:2]) else o
        p2 = e if ('စုံ' in text[1:] or 'စ' in text[1:]) else o
        res = [a+b for a in p1 for b in p2]

    # ၇။ ကပ်/ကို (n * n)
    elif 'ကို' in text or 'ကပ်' in text:
        parts = re.split(r'ကို|ကပ်', text)
        nums_only = [re.findall(r'\d+', p) for p in parts]
        if len(nums_only) >= 2 and nums_only[0] and nums_only[1]:
            n1, n2 = nums_only[0][0], nums_only[1][0]
            res = [a+b for a in list(n1) for b in list(n2)]

    # ၈။ ဆယ်ပြည့်
    elif 'ဆယ်ပြည့်' in text:
        res = [f"{i}0" for i in range(10)]

    # ၉။ ဒဲ့ (၁ ကွက်)
    else:
        res = [main_num]

    # R (အာ) ပါလျှင်
    if is_reverse:
        rev = [n[::-1] for n in res if len(n) == 2 and n[0] != n[1]]
        res = list(set(res + rev))
        
    return res, price

# ==============================================
# 🤖 ၅။ Bot Handlers
# ==============================================
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "✅ **Star 2D Bot အဆင်သင့်ဖြစ်ပါပြီ**\n\nMe/Mega အပါအဝင် တွက်နည်းစုံ ပါဝင်ပါသည်။", parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def calculate(message):
    text = message.text.lower()
    
    # အမျိုးအစားသတ်မှတ်ချက်
    type_name = ""
    discount_rate = 0.07 # Default 7%

    # Me နှင့် Mega ကို တူညီစွာ သတ်မှတ်ခြင်း
    if any(x in text for x in ['ဒူ', 'du']): type_name = "Du"
    elif any(x in text for x in ['မီ', 'mega', 'me']): type_name = "Mega"
    elif any(x in text for x in ['စီ', 'maxi']): type_name = "Maxi"
    elif any(x in text for x in ['လာ', 'lao']): type_name = "Lao"
    elif any(x in text for x in ['ကလို', 'glo']): type_name = "Glo"; discount_rate = 0.03
    elif any(x in text for x in ['လန်', 'ld']): type_name = "Ld"

    # အမျိုးအစားမပါရင် Admin ကို Tag ခေါ်မယ်
    if type_name == "":
        if re.search(r'\d+', text):
            mentions = get_admin_mentions(message.chat.id)
            bot.reply_to(message, f"⚠️ **အမျိုးအစား မပါဝင်ပါ!**\n{mentions}\nလာစစ်ပေးပါဦး။", parse_mode="Markdown")
        return

    nums, price = get_numbers(text)
    if not nums or price == 0: return

    total_amt = len(nums) * price
    cash_back = total_amt * discount_rate
    final_amt = total_amt - cash_back
    
    res_text = (f"✅ {type_name} အတွက် တွက်ချက်မှု\n"
                f"🔢 အကွက်အရေအတွက်: {len(nums)} ကွက်\n"
                f"💰 စုစုပေါင်း: {int(total_amt):,} ကျပ်\n"
                f"🎁 Cash Back ({int(discount_rate*100)}%): {int(cash_back):,} ကျပ်\n"
                f"💵 လွှဲရမည့်ငွေ: {int(final_amt):,} ကျပ်")
    
    bot.reply_to(message, res_text)

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling()
