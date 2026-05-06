import telebot
import re
import os
from threading import Thread
from flask import Flask
def calculate_2d_ledger(input_text):
    # --- ၁။ 2D Name စစ်ဆေးခြင်း ---
    lower_text = input_text.lower()
    two_d_names = {
        'mega': 7, 'မီ': 7, 
        'du': 7, 
        'mm': 10, 
        'me': 7
    }
    
    # "me 10", "du 7" စတဲ့ နာရီစာသားတွေကို ဖယ်ထုတ်ဖို့ logic
    # 2D Name အစစ်အမှန် ပါ/မပါ စစ်ဆေးခြင်း
    found_name = None
    cash_back_percent = 0
    
    # စာရင်းထဲမှာ ပါတဲ့ name တွေကို ရှာဖွေခြင်း
    for name, percent in two_d_names.items():
        if name in lower_text:
            found_name = name
            cash_back_percent = percent
            break

    # 2D Name လုံးဝမပါရင် စာရင်းမတွက်ဘဲ Admin ကို Mention ခေါ်မည်
    if not found_name:
        return "📢 @admin @owner \n⚠️ 2D Name (Mega, Du, MM, Me) မပါရှိသဖြင့် စစ်ပေးပါရှင့်။"

    # --- ၂။ စာရင်းတွက်ချက်ခြင်း ---
    total_amount = 0
    lines = input_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or any(name in line.lower() for name in two_d_names):
            continue
            
        # အထူး Rule များ (အပူး၊ နက္ခတ်၊ ပါဝါ = 10 ကွက်၊ ညီကို = 20 ကွက်)
        special_keywords = {
            'အပူး': 10, 'နက္ခတ်': 10, 'ပါဝါ': 10, 'ညီကို': 20
        }
        
        found_special = False
        for kw, slots in special_keywords.items():
            if kw in line:
                price_match = re.search(r'\d+$', line)
                if price_match:
                    price = int(price_match.group())
                    total_amount += slots * price
                    found_special = True
                    break
        
        if found_special: continue

        # n x n Rule (အပီးအပူးပါ / အပြီးအပူးပါ)
        if "အပီးအပူးပါ" in line or "အပြီးအပူးပါ" in line:
            nums = re.findall(r'\d', line.split('အပီး')[0])
            price_match = re.search(r'\d+$', line)
            if nums and price_match:
                n = len(nums)
                total_amount += (n * n) * int(price_match.group())
            continue

        # ပုံမှန် R (အာ) နှင့် ဒဲ့ တွက်နည်း
        # (ဒီနေရာမှာ Regex သုံးပြီး ဂဏန်းအရေအတွက်နဲ့ ဈေးနှုန်းကို ခွဲထုတ်တွက်ချက်ပါမယ်)
        # ... (ကျန်ရှိသော parsing logic များ) ...

    # --- ၃။ ရလဒ် ထုတ်ပြန်ခြင်း ---
    cash_back_amount = (total_amount * cash_back_percent) / 100
    net_total = total_amount - cash_back_amount
    
    return f"✅ 2D Name: {found_name.upper()}\n" \
           f"💰 စုစုပေါင်း: {total_amount:,} ကျပ်\n" \
           f"📉 {cash_back_percent}% ချွေ: {int(cash_back_amount):,} ကျပ်\n" \
           f"💵 လက်ခံရမည့်ငွေ: {int(net_total):,} ကျပ်ဘဲ လွဲပေးပါရှင့် "
except Exception as e:
bot.reply_to(message, reply)
        print("ERROR:", e)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling()
