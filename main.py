import telebot
import re

TOKEN = "8669202237:AAEPCaS8x4jEsUaP6BQ-8-PM-b6_PN4hk5w"
bot = telebot.TeleBot(TOKEN)

def calculate_shwethoon_master(input_text):
    lines = input_text.strip().split('\n')
    total_sales = 0
    percent = 7 
    brand_name = "LAO"

    for line in lines:
        line = line.strip().lower()
        if not line: continue
        
        # နာမည်စစ်ဆေးခြင်း
        if any(x in line for x in ["lao", "laos", "လာအို", "la"]):
            percent, brand_name = 7, "LAO"
            continue
        if any(x in line for x in ["mm", "ဗမာ"]):
            percent, brand_name = 10, "MM"
            continue

        line = line.translate(str.maketrans('၀၁၂၃၄၅၆၇၈၉', '0123456789'))

        # (1) အခွေ / ခွေပူး / ခပ (ဥပမာ- 135790ခပ 300)
        if "ခ" in line:
            nums_part = line.split('ခ')[0]
            nums = re.findall(r'\d', nums_part)
            price_match = re.findall(r'\d+', line[line.find('ခ'):])
            if nums and price_match:
                price = int(price_match[0])
                if any(x in line for x in ["ခပ", "ခွေပူး", "ပူး"]):
                    count = len(nums) * len(nums)
                else:
                    count = len(nums) * (len(nums) - 1)
                total_sales += count * price
                continue

        # (2) အကပ် / ပါဝါ / ဘရိတ် / ကို (ဥပမာ- 1/2469ကပ် r50)
        if any(x in line for x in ["/", "ကို", "ကပ်", "ပါ", "bk", "ဘရိတ်"]):
            parts = re.split(r'/|ကို|ကပ်|ပါ|bk|ဘရိတ်', line)
            if len(parts) >= 2:
                left_nums = re.findall(r'\d', parts[0])
                right_part = parts[1]
                right_nums = re.findall(r'\d', re.split(r'\s|r|ဒဲ့', right_part)[0])
                
                if left_nums and right_nums:
                    count = len(left_nums) * len(right_nums)
                    prices = re.findall(r'\d+', right_part[len(right_nums):] if right_nums else right_part)
                    if not prices: prices = re.findall(r'\d+', line)
                    
                    if prices:
                        p1 = int(prices[0])
                        total_sales += count * p1
                        if "r" in line:
                            p2 = int(prices[1]) if len(prices) > 1 else p1
                            total_sales += count * p2
                    continue

        # (3) အုပ်စုလိုက် (စုံမ, မစုံ, အပူး, ညီကို)
        groups = [
            {"keys": ["စုံစုံ", "စစ", "မမ", "မမ", "စုံမ", "စမ", "မစုံ", "မစ"], "count": 25},
            {"keys": ["ညီကို", "ညီအကို", "ညီအစ်ကို"], "count": 20},
            {"keys": ["အပူး", "ပူး", "puu"], "count": 10},
            {"keys": ["ပါဝါ", "pw"], "count": 10},
            {"keys": ["နက္ခတ်", "nk"], "count": 10}
        ]
        found_group = False
        for g in groups:
            if any(k in line for k in g["keys"]):
                prices = re.findall(r'\d+', line)
                if prices:
                    total_sales += g["count"] * int(prices[-1])
                    found_group = True; break
        if found_group: continue

        # (4) ဒဲ့ နှင့် အပြန် (72R200, 81.90.68... R 100)
        pure_nums = re.findall(r'\d{2}', line)
        if pure_nums:
            # တခါတလေ T1200 ဆိုတာမျိုးပါရင် ဖယ်ထုတ်ဖို့
            pure_nums = [n for n in pure_nums if not line[line.find(n)-1:line.find(n)].isalpha() or line[line.find(n)-1:line.find(n)] == ' ']
            if pure_nums:
                price_part = line[line.rfind(pure_nums[-1])+2:]
                prices = re.findall(r'\d+', price_part)
                if not prices: prices = re.findall(r'\d+', line.split('r')[-1]) if 'r' in line else []
                
                if prices:
                    d_p = int(prices[0])
                    total_sales += len(pure_nums) * d_p
                    if "r" in line:
                        total_sales += len(pure_nums) * d_p 
                continue

    cash_back = (total_sales * percent) / 100
    net_total = total_sales - cash_back
    
    return (f"👤 らŤΛ尺\n\n"
            f"✅ {brand_name} စုစုပေါင်း Total = {int(total_sales):,} ကျပ်\n\n"
            f"🎁 {percent}% Cash Back = {int(cash_back):,} ကျပ်\n\n"
            f"💵 Total = {int(net_total):,} ကျပ် ဘဲ လွဲပေးပါရှင့်\n\n"
            f"ကံကောင်းပါစေ ✨")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, calculate_shwethoon_master(message.text))

bot.infinity_polling()
