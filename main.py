import telebot
import re

TOKEN = "8669202237:AAEPCaS8x4jEsUaP6BQ-8-PM-b6_PN4hk5w"
bot = telebot.TeleBot(TOKEN)

def calculate_shwethoon_master(input_text):
    lines = input_text.strip().split('\n')
    total_sales = 0
    
    # --- ၁။ 2D Name & Percent သတ်မှတ်ချက် ---
    lower_full_text = input_text.lower()
    percent = 0
    two_d_name = ""

    # Brand စာရင်း
    groups_config = {
        "Du": {"kw": ["du2d", "du", "ဒု", "ဒူ", "ဒူဘိူင်း", "ငဒူ", "dubai"], "p": 7},
        "Mega": {"kw": ["mega", "မီ", "me", "မီဂါ"], "p": 7},
        "MM": {"kw": ["mm", "ဗမာ"], "p": 10},
        "Maxi": {"kw": ["maxi", "မက်ဆီ", "မက်စီ", "စီစီ"], "p": 7},
        "Lao": {"kw": ["lao", "loa", "laos", "loas", "လာအို", "လာလာ", "la"], "p": 7},
        "Global": {"kw": ["glo", "ကလို", "ဂလို", "global"], "p": 3},
        "London": {"kw": ["ld", "landon", "london", "lan", "လန်ဒန်", "လန်လန်"], "p": 7}
    }

    for name, data in groups_config.items():
        if any(kw in lower_full_text for kw in data["kw"]):
            two_d_name, percent = name, data["p"]
            break
    
    if not two_d_name:
        return "📢 @admin1 @owner \n⚠️ 2D Name မပါရှိသဖြင့် စစ်ပေးပါရှင့်။"

    # --- ၂။ စာရင်းတွက်ချက်ခြင်း Logic ---
    for line in lines:
        line = line.strip().lower()
        if not line: continue
        
        # နာမည်ပါတဲ့လိုင်းကို ကျော်မယ် (စာရင်းထဲမတွက်ဖို့)
        is_name_line = False
        for name in groups_config:
            if any(kw == line for kw in groups_config[name]["kw"]):
                is_name_line = True
                break
        if is_name_line: continue

        # ဗမာဂဏန်းကို အင်္ဂလိပ်ပြောင်း
        line = line.translate(str.maketrans('၀၁၂၃၄၅၆၇၈၉', '0123456789'))

        # (A) ပတ်သီး (၁၉ ကွက်)
        pats_keywords = ["ပတ်", "အပါ", "ပါ", "p", "ch"]
        if any(x in line for x in pats_keywords) and not any(x in line for x in ["ပတ်ပူး", "ပူးပို"]):
            parts = re.split(r'ပတ်|အပါ|ပါ|p|ch', line)
            nums = re.findall(r'\d', parts[0])
            price_match = re.findall(r'\d+', line)
            if nums and price_match:
                price = int(price_match[-1])
                total_sales += (len(nums) * 19) * price
                continue

        # (B) ပတ်ပူး / ထိပ်ပိတ် (၂၀ ကွက်)
        p20_keywords = ["ပတ်ပူး", "ပတ်သီးအပူးပို", "ပတ်သီးပူးပို", "ပတ်ပူးပို", "ထိပ်ပိတ်", "ထပ", "ထန", "ထိပ်နောက်"]
        if any(x in line for x in p20_keywords):
            pattern = '|'.join(p20_keywords)
            parts = re.split(pattern, line)
            nums = re.findall(r'\d', parts[0])
            price_match = re.findall(r'\d+', line)
            if nums and price_match:
                price = int(price_match[-1])
                total_sales += (len(nums) * 20) * price
                continue

        # (C) အကပ် Logic
        if any(x in line for x in ["/", "ကို", "ကပ်"]):
            parts = re.split(r'/|ကို|ကပ်', line)
            if len(parts) >= 2:
                left_nums = re.findall(r'\d', parts[0])
                right_nums = re.findall(r'\d', re.split(r'\s|r', parts[1])[0])
                price_match = re.findall(r'\d+', line)
                if left_nums and right_nums and price_match:
                    price = int(price_match[-1])
                    count = len(left_nums) * len(right_nums)
                    total_sales += count * price
                    if "r" in line: total_sales += count * price
                    continue

        # (D) အခွေ (n * n-1)
        if "ခ" in line and "ခွေပူး" not in line and "ခပ" not in line:
            parts = re.split(r'ခွေ|ခ', line)
            nums = re.findall(r'\d', parts[0])
            price_match = re.findall(r'\d+', line)
            if nums and price_match:
                n = len(nums)
                price = int(price_match[-1])
                total_sales += (n * (n - 1)) * price
                continue

        # (E) အုပ်စုလိုက်တွက်နည်းများ
        groups_list = [
            {"keys": ["ခွေပူး", "အပြီအပူး", "ခပ", "အခွေပူး"], "type": "kp"},
            {"keys": ["အပူး", "ပူး", "puu", "pu"], "count": 10},
            {"keys": ["စုံစုံ", "စစ", "မမ", "စုံမ", "မစုံ", "စမ", "မစ"], "count": 25},
            {"keys": ["မပူး", "စုံပူး"], "count": 5},
            {"keys": ["ပါဝါ", "pw", "power"], "count": 10},
            {"keys": ["နက္ခတ်", "နက", "nk"], "count": 10},
            {"keys": ["ညီကို", "ညီအကို", "ညီအစ်ကို"], "count": 20},
            {"keys": ["စုံဘရိတ်", "စဘရိတ်", "စဘ", "မဘရိတ်", "မဘ"], "count": 50}
        ]

        found_grp = False
        for g in groups_list:
            if any(k in line for k in g["keys"]):
                price_match = re.findall(r'\d+', line)
                if price_match:
                    price = int(price_match[-1])
                    if g.get("type") == "kp":
                        nums = re.findall(r'\d', line.split(g["keys"][0])[0])
                        total_sales += (len(nums) * len(nums)) * price
                    else:
                        total_sales += g["count"] * price
                    found_grp = True
                    break
        if found_grp: continue

        # (F) ဒဲ့ နှင့် R (ပုံမှန်)
        nums = re.findall(r'\d{2}', line)
        if nums:
            price_match = re.findall(r'\d+', line)
            if price_match:
                price = int(price_match[-1])
                total_sales += len(nums) * price
                if "r" in line: total_sales += len(nums) * price

    # --- ၃။ ရလဒ်ထုတ်ပေးခြင်း ---
    cash_back = (total_sales * percent) / 100
    net_total = total_sales - cash_back
    
    return (f"✅ 2D Name: {two_d_name}\n"
            f"━━━━━━━━━━━━━━\n"
            f"💰 စုစုပေါင်း: {total_sales:,} ကျပ်\n"
            f"📉 {percent}% cash bock= {int(cash_back):,} ကျပ်\n"
            f"━━━━━━━━━━━━━━\n"
            f"💵 လက်ခံရမည့်ငွေ: {int(net_total):,} ကျပ်ဘဲ လွဲပါရှင့်")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, calculate_shwethoon_master(message.text))

bot.infinity_polling()
