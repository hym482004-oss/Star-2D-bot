import telebot
import re
import os
from dotenv import load_dotenv

# .env file ကနေ Token ယူမယ် (Security)
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN', "8669202237:AAGAU29lQRSlT4sRwvG6YIxsmlJsnGSd-Tc")
bot = telebot.TeleBot(TOKEN)

def calculate_shwethoon_master(input_text):
    """2D ထိုးကွက် တွက်ချက်ရန် Main Function"""
    lines = input_text.strip().split('\n')
    total_sales = 0
    is_ledger = False
    
    lower_full_text = input_text.lower()
    
    # Brand Detection & Percent
    groups_config = {
        "Du": ["du2d", "du", "ဒု", "ဒူ", "dubai"],
        "Mega": ["mega", "မီ", "me", "မီဂါ"],
        "MM": ["mm", "ဗမာ"],
        "Maxi": ["maxi", "မက်ဆီ", "စီစီ"],
        "Lao": ["lao", "laos", "လာအို", "la"],
        "Global": ["glo", "ကလို", "ဂလို", "global"],
        "London": ["ld", "london", "လန်လန်"]
    }
    
    percent, two_d_name = 0, ""
    for name, keywords in groups_config.items():
        if any(kw in lower_full_text for kw in keywords):
            two_d_name = name
            percent = 10 if name == "MM" else (3 if name == "Global" else 7)
            break
    
    if not two_d_name: 
        return None

    # နှစ်လိုင်း လိုက် Process
    for line in lines:
        line = line.strip().lower()
        if not line or any(kw == line for k in groups_config.values() for kw in k): 
            continue
            
        # မြန်မာဂဏန်း -> English ပြောင်း
        line = line.translate(str.maketrans('၀၁၂၃၄၅၆၇၈၉', '0123456789'))
        
        # r, ခပ, ခွေပူး ဖယ်ရှား (Price ရှာဖို့)
        temp_line = line.replace('r', ' ').replace('ခပ', ' ').replace('ခွေပူး', ' ')
        all_numbers = re.findall(r'\d+', temp_line)
        
        if not all_numbers: 
            continue
        
        price = int(all_numbers[-1])
        bet_numbers = all_numbers[:-1]

        # ================================
        # 1. အကပ် / ကပ် Logic
        # ================================
        if any(x in line for x in ["/", "ကို", "ကပ်"]):
            parts = re.split(r'/|ကို|ကပ်', line)
            if len(parts) >= 2:
                left = re.findall(r'\d', parts[0])
                right = re.findall(r'\d', parts[1].split(' ')[0])
                if left and right:
                    count = len(left) * len(right)
                    total_sales += count * price * (2 if "r" in line else 1)
                    is_ledger = True
                    continue

        # ================================
        # 2. ထိပ် / ပိတ် / နပ / ဘရိတ်
        # ================================
        if any(x in line for x in ["ထိပ်", "ပိတ်", "နပ", "နောက်", "ဘရိတ်", "ဘ", "bk"]):
            nums_to_count = "".join(bet_numbers)
            if nums_to_count:
                total_sales += len(nums_to_count) * 10 * price
                is_ledger = True
                continue

        # ================================
        # 3. ခွေပူး / ခပ
        # ================================
        if any(x in line for x in ["ခွေပူး", "ခပ"]):
            nums_to_khway = "".join(bet_numbers)
            if nums_to_khway:
                n = len(nums_to_khway)
                total_sales += (n * n) * price
                is_ledger = True
                continue

        # ================================
        # 4. အခွေ (ခ)
        # ================================
        if "ခ" in line:
            nums_to_khway = "".join(bet_numbers)
            if nums_to_khway:
                n = len(nums_to_khway)
                total_sales += (n * (n - 1)) * price
                is_ledger = True
                continue

        # ================================
        # 5. ပတ်သီး / P / CH
        # ================================
        if any(x in line for x in ["ပတ်", "ပါ", "p", "ch"]):
            nums_to_patt = "".join(bet_numbers)
            if nums_to_patt:
                c = 20 if any(x in line for x in ["ပတ်ပူး", "ပူးပို", "ထိပ်ပိတ်","ထိပ်နောက်","ထန"]) else 19
                total_sales += len(nums_to_patt) * c * price
                is_ledger = True
                continue

        # ================================
        # 6. အုပ်စု အမျိုးမျိုး
        # ================================
        group_map = {
            "အပူး": 10, "ပူး": 10, "pu": 10,
            "ပါဝါ": 10, "pw": 10, "power": 10,
            "နက္ခတ်": 10, "နက": 10, "nk": 10,
            "မပူး": 5, "စုံပူး": 5,
            "ညီကို": 20, "ညီအကို": 20,
            "စုံစုံ": 25, "စစ": 25, "မမ": 25, "စုံမ": 25, "မစုံ": 25,
            "စုံဘရိတ်": 50, "မဘရိတ်": 50, "စဘ": 50, "မဘ": 50
        }
        
        found_g = False
        for k, v in group_map.items():
            if k in line:
                total_sales += v * price
                found_g = True
                is_ledger = True
                break
        if found_g: 
            continue

        # ================================
        # 7. ဒဲ့ (2 ဂဏန်း) + R Reverse
        # ================================
        two_digit_bets = re.findall(r'\d{2}', " ".join(map(str, bet_numbers)))
        if two_digit_bets:
            total_sales += len(two_digit_bets) * price * (2 if "r" in line else 1)
            is_ledger = True

    if not is_ledger: 
        return None
    
    # Cashback & Net Total
    cash_back = (total_sales * percent) / 100
    net_total = total_sales - cash_back
    
    return {
        "two_d_name": two_d_name,
        "total_sales": total_sales,
        "percent": percent,
        "cash_back": int(cash_back),
        "net_total": int(net_total)
    }

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Bot Start / Help Command"""
    welcome_msg = """
🎰 **2D ထိုးကွက် တွက်ချက်ရေး Bot**

📝 **အသုံးပြုနည်း:**
