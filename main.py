import telebot
import re
import itertools
import os
from threading import Thread
from flask import Flask

# ==============================================
# 🔴 ၁။ Web Server ပိုင်း (Render Free Tier အတွက်)
# ==============================================
server = Flask(__name__)

@server.route("/")
def webhook():
    return "Bot is running", 200

def run_web():
    # Render ကပေးတဲ့ PORT ကိုသုံးမယ်၊ မရှိရင် 8080 သုံးမယ်
    port = int(os.environ.get("PORT", 8080))
    server.run(host="0.0.0.0", port=port)

# ==============================================
# 🔴 ၂။ သတ်မှတ်ချက်များ (Token နှင့် ID များ)
# ==============================================
BOT_TOKEN = '8663479446:AAEHOXsSBCxpwh7fK3AbtEbbIAouBMFM9R4'
OWNER_ID = -6023513934 

bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=10)

# ==============================================
# 🛠️ ၃။ ဖော်မြူလာ Logic များ
# ==============================================
def get_one(num): return [num]
def get_reverse(num): return [num, num[::-1]] if len(num) == 2 and num[0] != num[1] else [num]
def get_round(num): return [f"{i:02d}" for i in range(100) if str(num) in f"{i:02d}"]
def get_top(num): return [f"{num}{i:01d}" for i in range(10)]
def get_break_sum(total):
    return [f"{i:02d}" for i in range(100) if (int(f"{i:02d}"[0]) + int(f"{i:02d}"[1])) % 10 == int(total)]
def get_cycle(num):
    u = list(dict.fromkeys(num))
    return [a+b for a, b in itertools.permutations(u, 2)] if len(u) >= 2 else []
def get_double_cycle(num):
    res = get_cycle(num)
    res.extend([d+d for d in set(num)])
    return list(set(res))
def get_ten_full(): return [f"{i}0" for i in range(10)]
def get_all_double(): return [f"{i}{i}" for i in range(10)]
def get_special_pattern(p_type):
    e, o = ['0','2','4','6','8'], ['1','3','5','7','9']
    if p_type == 'စစ်': return [a+b for a in e for b in e]
    if p_type == 'မမ': return [a+b for a in o for b in o]
    if p_type == 'စမ': return [a+b for a in e for b in o]
    if p_type == 'မစုံ': return [a+b for a in o for b in e]
    return []
def get_kap(text):
    parts = re.split(r'ကို|ကပ်', text)
    nums = [''.join(re.findall(r'\d+', p)) for p in parts if re.search(r'\d+', p)]
    return [a+b for a in list(nums[0]) for b in list(nums[1])] if len(nums) >= 2 else []
def get_break_type(b_type):
    res = []
    for i in range(100):
        s = f"{i:02d}"
        t = int(s[0]) + int(s[1])
        if 'စုံ' in b_type and t % 2 == 0: res.append(s)
        elif 'မ' in b_type and t % 2 != 0: res.append(s)
    return res

def get_admin_mentions(chat_id):
    try:
        admins = bot.get_chat_administrators(chat_id)
        mentions = ""
        for a in admins:
            if a.user.username: mentions += f"@{a.user.username} "
            else: mentions += f"[{a.user.first_name}](tg://user?id={a.user.id}) "
        return mentions
    except: return "Admin များ"

# ==============================================
# 🤖 ၄။ Bot Message Handlers
# ==============================================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = "✅ **Shwethoon 2D Bot စတင်ပါပြီ**\n\nစာရင်းများကို ပုံစံတကျ ပို့ပေးပါ။\nအမျိုးအစားမပါရင် Admin များကို Tag ခေါ်ပေးပါမည်။"
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def calculate_all(message):
    Thread(target=process_msg, args=(message,)).start()

def process_msg(message):
    text = message.text.strip()
    lower_text = text.lower()
    
    config = {
        'du': (0.07, 7, "Du"), 'mega': (0.07, 7, "Mega"), 'mm': (0.10, 10, "mm"),
        'maxi': (0.07, 7, "Maxi"), 'lao': (0.07, 7, "လာအို"), 'glo': (0.03, 3, "Glo"),
        'ld': (0.07, 7, "Ld")
    }
    
    used_percent, percent_num, type_text = 0, 0, ""
    found = False
    
    keywords_map = {
        'du': ['ဒူ', 'ဒု', 'dubai', 'du'],
        'mega': ['မီ', 'me', 'mega'],
        'maxi': ['စီစီ', 'maxi'],
        'lao': ['လာလာ', 'lao', 'လာအို'],
        'glo': ['ကလို', 'glo', 'global'],
        'ld': ['လန်လန်', 'လန်ဒန်', 'ld', 'london']
    }
    
    for key, words in keywords_map.items():
        if any(w in lower_text for w in words):
            used_percent, percent_num, type_text = config[key]
            found = True; break
    
    if not found:
        if re.search(r'\d+', text):
            mentions = get_admin_mentions(message.chat.id)
            bot.send_message(message.chat.id, f"⚠️ **အမျိုးအစား မပါဝင်ပါ!**\n{mentions}\nလာစစ်ပေးပါဦး။", parse_mode="Markdown")
        return

    price_match = re.search(r'(\d+)\s*$', text)
    price = int(price_match.group(1)) if price_match else 0
    nums_all = re.findall(r'\d+', text)
    if price_match and nums_all: nums_all = nums_all[:-1]
    
    main_num = nums_all[0] if nums_all else ""
    result_list = []
    is_reverse = 'r' in lower_text or 'အာ' in lower_text

    if any(k in text for k in ['စုံဘရိတ်', 'မဘရိတ်', 'စုံbk', 'မbk']):
        result_list = get_break_type('စုံ' if 'စုံ' in text else 'မ')
    elif 'ကပ်' in text or 'ကို' in text:
        result_list = get_kap(text)
    elif any(k in text for k in ['စစ်', 'မမ', 'စမ', 'မစုံ']):
        p = 'စစ်' if 'စစ်' in text else 'မမ' if 'မမ' in text else 'စမ' if 'စမ' in text else 'မစုံ'
        result_list = get_special_pattern(p)
    elif not main_num: return
    else:
        if any(k in text for k in ['ပတ်', 'အပါ', 'ပါ']): result_list = get_round(main_num)
        elif any(k in text for k in ['ထိပ်', 'ထ']): result_list = get_top(main_num)
        elif 'ဘရိတ်' in text: result_list = get_break_sum(main_num)
        elif 'ခွေ' in text and 'ပူး' not in text: result_list = get_cycle(main_num)
        elif any(k in text for k in ['ပူး', 'ခပ်']): result_list = get_double_cycle(main_num)
        elif 'ဆယ်ပြည့်' in text: result_list = get_ten_full()
        elif 'အပူးစုံ' in text: result_list = get_all_double()
        else: result_list = get_one(main_num)

    if is_reverse and result_list:
        rev = [n[::-1] for n in result_list if len(n) == 2 and n[0] != n[1]]
        result_list = list(set(result_list + rev))

    if not result_list or price == 0:
        mentions = get_admin_mentions(message.chat.id)
        bot.send_message(message.chat.id, f"⚠️ **စျေးနှုန်း သို့မဟုတ် ပုံစံ မှားယွင်းနေပါသည်!**\n{mentions}", parse_mode="Markdown")
        return

    total_original = len(result_list) * price
    discount = total_original * used_percent
    total_final = total_original - discount

    display = (f"{type_text} Total={int(total_original):,}ကျပ်\n\n"
               f"{percent_num}% cash back={int(discount):,}ကျပ်\n\n"
               f"Total={int(total_final):,}ကျပ် ဘဲ လွဲပါရှင့်")

    bot.reply_to(message, display)

# ==============================================
# 🔴 ၅။ Main Execution
# ==============================================
if __name__ == "__main__":
    # Web Server ကို Thread နဲ့ run မယ်
    Thread(target=run_web).start()
    print("✅ Web Server started!")
    
    # Bot ကို run မယ်
    print("✅ Bot is running...")
    bot.infinity_polling()
