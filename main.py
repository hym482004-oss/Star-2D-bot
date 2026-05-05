import telebot
import re
import itertools
import sqlite3
from datetime import datetime

BOT_TOKEN = '8626110758:AAFMD05N-DRmxxWrZeXTLsmBT5UsciPlCvw'
OWNER_ID = 6023513934

bot = telebot.TeleBot(BOT_TOKEN)

conn = sqlite3.connect('bot_control.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS groups_list
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              group_id INTEGER UNIQUE,
              status TEXT)''')
conn.commit()

def is_owner(user_id):
    return user_id == OWNER_ID

@bot.message_handler(commands=['start'])
def add_group(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "⚠️ Owner တစ်ယောက်တည်းသာ သုံးလို့ရပါတယ်!")
        return
    
    if 't.me/' in message.text or '+' in message.text:
        bot.reply_to(message, "✅ **Ok Start...**\nGroup ကို အောင်မြင်စွာ ဖွင့်ပေးလိုက်ပါပြီ!\n⚠️ Group ထဲကို Bot ကို Add ထည့်ပေးပါ။", parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ ပုံစံမှားနေပါတယ်!\n/start t.me/xxxxxx\nဒီလိုမျိုး Link တွဲပြီးပို့ပါ။")

@bot.message_handler(commands=['close'])
def remove_group(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "⚠️ Owner တစ်ယောက်တည်းသာ သုံးလို့ရပါတယ်!")
        return
    
    bot.reply_to(message, "✅ **Ok Close...**\nGroup ကို အောင်မြင်စွာ ပိတ်ပေးလိုက်ပါပြီ!", parse_mode="Markdown")

def is_group_active(chat_id):
    c.execute("SELECT status FROM groups_list WHERE group_id=?", (chat_id,))
    result = c.fetchone()
    return result and result[0] == 'active'

@bot.message_handler(func=lambda m: True)
def calculate_all(message):
    if not is_group_active(message.chat.id):
        return

    text = message.text.strip()
    lower_text = text.lower()
    
    used_percent = 0
    percent_num = 0
    type_text = ""
    valid = True
    
    # --- Company Type Check ---
    if any(k in lower_text for k in ['du2d', 'du', 'ဒု', 'ဒူ', 'ဒူဘိုင်း', 'ငဒူ', 'dubai']):
        used_percent = 0.07
        percent_num = 7
        type_text = "Du"
    elif any(k in lower_text for k in ['mega', 'မီ', 'me']):
        used_percent = 0.07
        percent_num = 7
        type_text = "Mega"
    elif any(k in lower_text for k in ['mm']):
        used_percent = 0.10
        percent_num = 10
        type_text = "mm"
    elif any(k in lower_text for k in ['maxi', 'မက်ဆီ', 'မက်စီ', 'စီစီ']):
        used_percent = 0.07
        percent_num = 7
        type_text = "Maxi"
    elif any(k in lower_text for k in ['လာအို', 'lao', 'loa', 'laos', 'loas', 'လာလာ', 'la']):
        used_percent = 0.07
        percent_num = 7
        type_text = "လာအို"
    elif any(k in lower_text for k in ['glo', 'ကလို', 'ဂလို', 'global']):
        used_percent = 0.03
        percent_num = 3
        type_text = "Glo"
    elif any(k in lower_text for k in ['ld', 'landon', 'london', 'lan', 'လန်ဒန်', 'လန်လန်']):
        used_percent = 0.07
        percent_num = 7
        type_text = "Ld"
    else:
        valid = False

    if not valid:
        display = f"⚠️ အမည်မသိ ဖောက်သည် တစ်ယောက် ဝင်လာပြီ!\n"
        display += f"👑 Owner [ID:{OWNER_ID}]\n"
        display += "👉 လာစစ်ဆေးပါရှင့်!"
        bot.reply_to(message, display)
        return

    # --- Price Extraction ---
    # Find price pattern (supports X=Y, X-Y, X Y)
    price_match = re.search(r'(\d+)\s*[=-]?\s*(\d+)$', text)
    if price_match:
        # If format like 25=300R200 or 25-300R200
        if 'r' in lower_text and lower_text.endswith('r'+price_match.group(2)):
             price_normal = int(price_match.group(1))
             price_reverse = int(price_match.group(2))
        else:
             price_normal = int(price_match.group(2))
             price_reverse = int(price_match.group(2))
    else:
        # Simple case
        price_match_simple = re.search(r'(\d+)\s*$', text)
        price_normal = int(price_match_simple.group(1)) if price_match_simple else 0
        price_reverse = price_normal

    # --- Number Extraction ---
    numbers_all = re.findall(r'\d+', text)
    if price_match and numbers_all:
        numbers_all = numbers_all[:-2] if len(numbers_all)>=2 else numbers_all[:-1]
    
    main_num = numbers_all[0] if numbers_all else ""
    result_list = []
    is_reverse_mode = False # True if R is at the end of line (apply to all)
    
    # --- Reverse Check ---
    if 'r' in lower_text and any(k in lower_text for k in ['r', 'အာ']):
        # If R is written at the end like "r150" or "R400"
        if re.search(r'r\s*\d+', lower_text):
            is_reverse_mode = True

    # --- Calculation Logic ---
    if any(k in text for k in ['စုံဘရိတ်', 'စုံbk', 'စBk', 'မဘရိတ်', 'မbk', 'မBk']):
        result_list = get_break_type('စုံဘရိတ်' if 'စုံ' in text else 'မဘရိတ်')
        
    elif 'ကပ်' in text or 'ကို' in text:
        result_list = get_kap(text)
        
    elif any(k in text for k in ['စစ်', 'စုံစုံ', 'မမ', 'စမ', 'စုံမ', 'မစ်', 'မစုံ']):
        if 'စစ်' in text or 'စုံစုံ' in text: p='စစ်'
        elif 'မမ' in text: p='မမ'
        elif 'စမ' in text or 'စုံမ' in text: p='စမ'
        else: p='မစ်'
        result_list = get_special_pattern(p)
        
    elif not main_num:
        bot.reply_to(message, "⚠️ နံပါတ်ထည့်ပေးပါ ဗျာ!")
        return
    else:
        if any(k in text for k in ['ပတ်ပူးပို', 'ပူးပို', 'ထန်', 'ထပ်', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
            result_list = get_round_full(main_num)
        elif 'ပတ်' in text or 'အပါ' in text or 'ပါ' in text:
            result_list = get_round(main_num)
        elif any(k in text for k in ['ထိပ်', 'ထ']):
            result_list = get_top(main_num)
        elif 'ဘရိတ်' in text:
            result_list = get_break_sum(main_num)
        elif 'ခွေ' in text and 'ပူး' not in text:
            result_list = get_cycle(main_num)
        elif 'ပူး' in text or 'အပူးပါ' in text or 'အေခွေပူး' in text or 'ခပ်' in text:
            result_list = get_double_cycle(main_num)
        elif 'ဆယ်ပြည့်' in text:
            result_list = get_ten_full()
        elif 'အပူးစုံ' in text:
            result_list = get_all_double()
        elif 'စုံပူး' in text:
            result_list = get_even_odd_double(True)
        elif 'မပူး' in text:
            result_list = get_even_odd_double(False)
        else:
            # Default: Single number
            result_list = get_one(main_num)

    # --- Apply Reverse Logic ---
    final_list = []
    if is_reverse_mode:
        # R is at end: Apply to ALL numbers
        for num in result_list:
            final_list.append(num)
            if len(num) == 2 and num[0] != num[1]:
                final_list.append(num[::-1])
        
        # Calculate price: All numbers use price_reverse (the R price)
        count = len(final_list)
        total_original = count * price_reverse
        
    else:
        # Normal mode or specific R
        final_list = result_list
        count = len(final_list)
        total_original = count * price_normal

    # Remove duplicates
    final_list = list(dict.fromkeys(final_list))
    count = len(final_list)
    
    if not final_list:
        bot.reply_to(message, "⚠️ တွက်လို့မရတဲ့ပုံစံပါဗျာ")
        return

    # --- Final Calculation ---
    # Recalculate total after dedup
    if is_reverse_mode:
        total_original = count * price_reverse
    else:
        total_original = count * price_normal
        
    discount_amount = total_original * used_percent
    total_final = total_original - discount_amount

    user_name = message.from_user.first_name if message.from_user.first_name else "User"
    
    display = f"👤 {user_name}\n"
    display += f"{type_text} Total = {int(total_original):,} ကျပ်\n"
    display += f"{percent_num}% Cash Back = {int(discount_amount):,} ကျပ်\n"
    display += f"Total = {int(total_final):,} ကျပ်ဘဲ လွဲပေးပါရှင့်"

    bot.reply_to(message, display)

# --- FUNCTION DEFINITIONS ---

def get_one(num):
    return [num]

def get_reverse(num):
    return [num, num[::-1]]

def get_round(num):
    num = int(num)
    nums = []
    for i in range(100):
        if str(num) in f"{i:02d}":
            nums.append(f"{i:02d}")
    return nums

def get_round_full(num):
    num = int(num)
    nums = []
    for i in range(100):
        if str(num) in f"{i:02d}":
            nums.append(f"{i:02d}")
    return nums

def get_top(num):
    num = int(num)
    return [f"{num}{i:01d}" for i in range(10)]

def get_break_sum(total):
    total = int(total)
    nums = []
    for i in range(100):
        s = f"{i:02d}"
        if int(s[0]) + int(s[1]) == total:
            nums.append(s)
    return nums

def get_cycle(num):
    unique = list(dict.fromkeys(num))
    if len(unique) < 2:
        return []
    cycles = []
    for a, b in itertools.permutations(unique, 2):
        cycles.append(a+b)
    return cycles

def get_double_cycle(num):
    cycles = get_cycle(num)
    doubles = [d+d for d in set(num)]
    cycles.extend(doubles)
    return list(set(cycles))

def get_ten_full():
    return [f"{i}0" for i in range(10)]

def get_all_double():
    return [f"{i}{i}" for i in range(10)]

def get_even_odd_double(is_even):
    res = []
    start = 0 if is_even else 1
    for i in range(start, 10, 2):
        res.append(f"{i}{i}")
    return res

def get_special_pattern(p_type):
    even = ['0','2','4','6','8']
    odd = ['1','3','5','7','9']
    res = []
    if p_type == 'စစ်' or p_type == 'စုံစုံ':
        for a in even:
            for b in even:
                res.append(a+b)
    elif p_type == 'မမ':
        for a in odd:
            for b in odd:
                res.append(a+b)
    elif p_type == 'စမ' or p_type == 'စုံမ':
        for a in even:
            for b in odd:
                res.append(a+b)
    elif p_type == 'မစ်' or p_type == 'မစုံ':
        for a in odd:
            for b in even:
                res.append(a+b)
    return res

def get_kap(text):
    parts = re.split(r'ကို|ကပ်', text)
    nums = [''.join(re.findall(r'\d+', p)) for p in parts if re.search(r'\d+', p)]
    if len(nums) >= 2:
        left = list(nums[0])
        right = list(nums[1])
        return [a+b for a in left for b in right]
    return []

def get_break_type(b_type):
    res = []
    if 'စုံ' in b_type:
        for i in range(100):
            s = f"{i:02d}"
            total = int(s[0]) + int(s[1])
            if total % 2 == 0:
                res.append(s)
    elif 'မ' in b_type:
        for i in range(100):
            s = f"{i:02d}"
            total = int(s[0]) + int(s[1])
            if total % 2 != 0:
                res.append(s)
    return res

print("✅ Star စာရင်းကိုင်လေး Bot အလုပ်လုပ်နေပြီ...")
print("✅ Owner က /start နဲ့ /close နဲ့ Control လုပ်လို့ရပြီ")
print("✅ သတ်မှတ်ထားတဲ့ Group မှာသာ အလုပ်လုပ်မယ်")
bot.polling()
