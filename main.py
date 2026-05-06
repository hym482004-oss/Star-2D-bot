import telebot
import re

# Leo Bot Token
TOKEN = "8669202237:AAG9nQ7Bxp-qTkKnwaiyp6ls73Y8Bphm5n0"
bot = telebot.TeleBot(TOKEN)

def calculate_leo_ledger(input_text):
    lines = input_text.strip().split('\n')
    total_sales = 0
    percent = 0
    two_d_name = ""

    # --- ၁။ 2D Name 7 ခု နှင့် Percent များ ---
    lower_text = input_text.lower()
    group_7 = ["maxi", "du", "lao", "mega", "glo", "london", "dubai"]
    group_10 = ["mm"]

    for name in group_7:
        if name in lower_text:
            percent, two_d_name = 7, name.capitalize()
            break
    if not two_d_name:
        for name in group_10:
            if name in lower_text:
                percent, two_d_name = 10, name.upper()
                break
    
    # --- Name မပါရင် Mention ခေါ်စစ်ခိုင်းခြင်း ---
    if not two_d_name:
        return "📢 @owner @admin1 \n⚠️ 2D Name (ဥပမာ- Maxi, MM) မပါရှိသဖြင့် စစ်ပေးပါရှင့်။"

    # --- ၂။ တွက်ချက်ခြင်း Logic ---
    for line in lines:
        line = line.strip().lower()
        if not line or len(line) < 2: continue
        
        clean_line = re.sub(r'[-\*\.]', ' ', line)
        full_line_eng = clean_line.translate(str.maketrans('၀၁၂၃၄၅၆၇၈၉', '0123456789'))

        # (A) အကပ် Logic (123/456, ကို, ကပ်)
        if any(x in line for x in ["/", "ကို", "ကပ်"]):
            parts = re.split(r'/|ကို|ကပ်', line)
            if len(parts) >= 2:
                left = re.findall(r'\d+', parts[0])
                right = re.findall(r'\d+', parts[1])
                if left and right:
                    count = len(left[-1]) * len(right[0])
                    prices = re.findall(r'\d+', full_line_eng[full_line_eng.find(right[0]):])
                    if prices:
                        price = int(prices[0])
                        if "r" in line: count *= 2
                        total_sales += count * price
                        continue

        # (B) ခွေပူး (n x n)
        k_p_keys = ["ခွေပူး", "ခပ", "အခွေပူး", "ခွေအပူး", "အပီအပူး"]
        if any(x in line for x in k_p_keys):
            nums = re.findall(r'\d', line.split(next(x for x in k_p_keys if x in line))[0])
            if nums:
                price_match = re.findall(r'\d+', full_line_eng)
                if price_match:
                    total_sales += (len(nums)**2) * int(price_match[-1])
                    continue

        # (C) အကွက်ခွေ (n x n-1)
        if "ခ" in line and not any(x in line for x in ["ခပ", "ခွေပူး"]):
            parts = re.split(r'ခွေ|ခ', line)
            nums = re.findall(r'\d', parts[0])
            if len(nums) > 1:
                price_match = re.findall(r'\d+', full_line_eng)
                if price_match:
                    total_sales += (len(nums)*(len(nums)-1)) * int(price_match[-1])
                    continue

        # (D) ပတ်သီး / ပတ်ပူး (၁၉ / ၂၀ ကွက်)
        if any(x in line for x in ["ပတ်", "အပါ", "ပါ", "p"]):
            count = 20 if any(x in line for x in ["ပတ်ပူး", "ပူးပို"]) else 19
            nums = re.findall(r'\d', line.split(next(x for x in ["ပတ်", "အပါ", "ပါ", "p"] if x in line))[0])
            price_match = re.findall(r'\d+', full_line_eng)
            if nums and price_match:
                total_sales += (len(nums) * count) * int(price_match[-1])
                continue

        # (E) အုပ်စုလိုက် Logic (BK ပါဝင်လာသည်)
        groups = [
            {"keys": ["စစ", "စုံစုံ", "မမ", "စုံမ", "မစုံ", "စမ", "မစ"], "count": 25},
            {"keys": ["ညီကို", "ညီအကို", "ညီအစ်ကို"], "count": 20},
            {"keys": ["ထိပ်ပိတ်", "ထပ", "ထန", "ထိပ်နောက်"], "count": 20},
            {"keys": ["အပူး", "ပူး", "puu"], "count": 10},
            {"keys": ["ပါဝါ", "pw", "ပဝ"], "count": 10},
            {"keys": ["နက္ခတ်", "နက", "nk"], "count": 10},
            {"keys": ["ထိပ်", "ထ"], "count": 10},
            {"keys": ["ပိတ်", "ပ"], "count": 10},
            {"keys": ["bk", "ဘရိတ်", "ဘရိပ်", "break"], "count": 10}, # BK Logic
            {"keys": ["မပူး", "စုံပူး"], "count": 5}
        ]
        found = False
        for g in groups:
            if any(k in line for k in g["keys"]):
                prices = re.findall(r'\d+', full_line_eng)
                if prices:
                    total_sales += g["count"] * int(prices[-1])
                    found = True; break
        if found: continue

        # (F) ဒဲ့ နှင့် R (ရိုးရိုး)
        match = re.search(r'(\d+)?\s*(r)\s*(\d+)$', line)
        if match:
            nums = re.findall(r'\d+', line[:match.start()])
            if nums:
                d_p = int(match.group(1)) if match.group(1) else 0
                r_p = int(match.group(3))
                total_sales += len(nums) * (d_p + r_p if d_p > 0 else r_p * 2)
                continue
        
        # (G) ဒဲ့ သီးသန့်
        pure_nums = re.findall(r'\d+', full_line_eng)
        if len(pure_nums) >= 2:
            price = int(pure_nums[-1])
            for n in pure_nums[:-1]:
                if len(n) == 2: total_sales += price

    # --- ၃။ ပြန်ပို့မည့်စာ ---
    cash_back = (total_sales * percent) / 100
    net_total = total_sales - cash_back
    
    return (f"👤 らŤΛ尺\n\n"
            f"✅ {two_d_name} စုစုပေါင်း Total = {total_sales:,} ကျပ်\n\n"
            f"🎁 {percent}% Cash Back = {int(cash_back):,} ကျပ်\n\n"
            f"💵 Total = {int(net_total):,} ကျပ် ဘဲ လွဲပေးပါရှင့်\n\n"
            f"ကံကောင်းပါစေ")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, calculate_leo_ledger(message.text))

bot.infinity_polling()
