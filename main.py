import telebot
import re

TOKEN = "8669202237:AAGAU29lQRSlT4sRwvG6YIxsmlJsnGSd-Tc"
bot = telebot.TeleBot(TOKEN)

def calculate_shwethoon_master(input_text):
    lines = input_text.strip().split('\n')
    total_sales = 0
    is_ledger = False # စာရင်းဟုတ်မဟုတ် စစ်မယ့် variable
    
    # --- ၁။ နာမည်စစ်ဆေးခြင်း ---
    lower_full_text = input_text.lower()
    percent, two_d_name = 0, ""
    groups_config = {
        "Du": ["du2d", "du", "ဒု", "ဒူ", "dubai"],
        "Mega": ["mega", "မီ", "me", "မီဂါ"],
        "MM": ["mm", "ဗမာ"],
        "Maxi": ["maxi", "မက်ဆီ", "စီစီ"],
        "Lao": ["lao", "laos", "လာအို", "la"],
        "Global": ["glo", "ဂလို", "global"],
        "London": ["ld", "london", "လန်လန်"]
    }

    for name, keywords in groups_config.items():
        if any(kw in lower_full_text for kw in keywords):
            two_d_name = name
            percent = 10 if name == "MM" else (3 if name == "Global" else 7)
            break
    
    # နာမည်မပါရင် စာရင်းမဟုတ်ဘူးလို့ ယူဆပြီး ဘာမှပြန်မလုပ်ဘူး
    if not two_d_name:
        return None

    # --- ၂။ စာရင်းတွက်ချက်ခြင်း ---
    for line in lines:
        line = line.strip().lower()
        if not line or any(kw == line for k in groups_config.values() for kw in k): continue
        line = line.translate(str.maketrans('၀၁၂၃၄၅၆၇၈၉', '0123456789'))

        # စာကြောင်းထဲမှာ ဂဏန်း (သို့) Keyword ပါမပါ စစ်မယ်
        keywords = ["ပတ်", "ပါ", "ခွေ", "ခပ", "ကို", "ကပ်", "/", "ပူး", "ညီကို", "ဘရိတ်", "r"]
        if not (re.search(r'\d', line) or any(k in line for k in keywords)):
            continue

        # (A) အကပ် Logic
        if any(x in line for x in ["/", "ကို", "ကပ်"]):
            parts = re.split(r'/|ကို|ကပ်', line)
            if len(parts) >= 2:
                left = re.findall(r'\d', parts[0])
                right = re.findall(r'\d', re.split(r'\s|r', parts[1])[0])
                price_match = re.findall(r'\d+', line)
                if left and right and price_match:
                    p = int(price_match[-1])
                    total_sales += (len(left) * len(right)) * p * (2 if "r" in line else 1)
                    is_ledger = True
                    continue

        # (B) ခွေပူး / ခပ Logic
        kh_pu_keys = ["ခွေပူး", "ခပ", "အခွေပူး"]
        if any(x in line for x in kh_pu_keys):
            price_match = re.findall(r'\d+', line)
            match_key = re.findall('|'.join(kh_pu_keys), line)
            if match_key:
                nums = re.findall(r'\d', line.split(match_key[0])[0])
                if nums and price_match:
                    total_sales += (len(nums) * len(nums)) * int(price_match[-1])
                    is_ledger = True
                    continue

        # (C) ခွေ (ရိုးရိုး) Logic
        if "ခ" in line:
            price_match = re.findall(r'\d+', line)
            nums = re.findall(r'\d', line.split('ခ')[0])
            if nums and price_match:
                n = len(nums)
                total_sales += (n * (n - 1)) * int(price_match[-1])
                is_ledger = True
                continue

        # (D) ပတ်သီး / ပတ်ပူး
        if any(x in line for x in ["ပတ်", "ပါ", "p", "ch"]):
            price_match = re.findall(r'\d+', line)
            parts = re.split(r'ပတ်|ပါ|p|ch', line)
            nums = re.findall(r'\d', parts[0])
            if nums and price_match:
                count = 20 if any(x in line for x in ["ပတ်ပူး", "ပူးပို", "ထိပ်ပိတ်"]) else 19
                total_sales += (len(nums) * count) * int(price_match[-1])
                is_ledger = True
                continue

        # (E) အုပ်စုလိုက် (အပူး, ညီကို, စုံမ, ဘရိတ်)
        group_map = {
            "အပူး": 10, "ပူး": 10, "pu": 10,
            "စုံစုံ": 25, "မမ": 25, "စုံမ": 25, "မစုံ": 25, "စမ": 25, "မစ": 25, "စစ": 25,
            "ညီကို": 20, "ညီအကို": 20,
            "စုံဘရိတ်": 50, "စဘရိတ်": 50, "စဘ": 50, "မဘရိတ်": 50, "မဘ": 50
        }
        found_g = False
        for k, v in group_map.items():
            if k in line:
                price_match = re.findall(r'\d+', line)
                if price_match:
                    total_sales += v * int(price_match[-1])
                    found_g = True
                    is_ledger = True
                    break
        if found_g: continue

        # (F) ဒဲ့ နှင့် R (ပုံမှန်)
        nums = re.findall(r'\d{2}', line)
        if nums:
            price_match = re.findall(r'\d+', line)
            if price_match:
                p = int(price_match[-1])
                total_sales += len(nums) * p * (2 if "r" in line else 1)
                is_ledger = True

    # စာရင်း အမှန်တကယ် တွက်ချက်ထားခြင်း မရှိရင် ဘာမှပြန်မဖြေဘူး
    if not is_ledger:
        return None

    # --- ၃။ Summary ---
    cash_back = (total_sales * percent) / 100
    net_total = total_sales - cash_back
    return (f"✅ 2D Name: {two_d_name}\n━━━━━━━━━━━━━━\n💰 စုစုပေါင်း: {total_sales:,} ကျပ်\n"
            f"📉 {percent}% ချွေ: {int(cash_back):,} ကျပ်\n━━━━━━━━━━━━━━\n"
            f"💵 လက်ခံရမည့်ငွေ: {int(net_total):,} ကျပ်ဘဲ လွဲပါရှင့်")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    response = calculate_shwethoon_master(message.text)
    if response: # response ရှိမှသာ (စာရင်းဖြစ်မှသာ) reply ပြန်မယ်
        bot.reply_to(message, response)

bot.infinity_polling()
