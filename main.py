import re

def calculate_2d_ledger(input_text):
    lines = input_text.strip().split('\n')
    total_sales = 0
    
    # 2D Name & Percent Setup
    lower_text = input_text.lower()
    percent = 0
    two_d_name = ""
    
    if "mm" in lower_text:
        two_d_name, percent = "MM", 10
    elif "mega" in lower_text or "မီဂါ" in lower_text:
        two_d_name, percent = "Mega", 7
    elif "du" in lower_text:
        two_d_name, percent = "Du", 7
    elif "me" in lower_text:
        two_d_name, percent = "Me", 7
    
    import re

def calculate_2d_ledger(input_text):
    lines = input_text.strip().split('\n')
    total_sales = 0
    
    # --- ၁။ 2D Name & Percent Setup ---
    lower_text = input_text.lower()
    percent = 0
    two_d_name = ""
    
    if "mm" in lower_text:
        two_d_name, percent = "MM", 10
    elif any(x in lower_text for x in ["mega", "မီဂါ"]):
        two_d_name, percent = "Mega", 7
    elif "du" in lower_text:
        two_d_name, percent = "Du", 7
    elif "me" in lower_text:
        two_d_name, percent = "Me", 7
    
    # 2D Name မပါရင် Admin ခေါ်ပြီး ရပ်မည်
    if not two_d_name:
        return "📢 @admin @owner \n⚠️ 2D Name (Mega, Du, MM, Me) မပါရှိသဖြင့် စစ်ပေးပါရှင့်။"

    # --- ၂။ စာရင်းများကို တစ်ကြောင်းချင်းစီ တွက်ချက်ခြင်း ---
    for line in lines:
        line = line.strip().lower()
        # Header သို့မဟုတ် blank line များကို ကျော်မည်
        if not line or any(x in line for x in ["mega", "mm", "du", "me", "မီဂါ"]):
            continue

        # (A) Special Keywords Rule (ညီကို = 20၊ နက္ခတ်/အပူး/ပါဝါ = 10)
        special_map = {"အပူး": 10, "နက္ခတ်": 10, "ပါဝါ": 10, "ညီကို": 20}
        found_sp = False
        for kw, slots in special_map.items():
            if kw in line:
                price_match = re.findall(r'\d+', line)
                if price_match:
                    # စာကြောင်းအဆုံးက ကိန်းဂဏန်းကို ဈေးနှုန်းအဖြစ် ယူသည်
                    total_sales += slots * int(price_match[-1])
                    found_sp = True
                    break
        if found_sp: continue

        # (B) n x n Rule (အပီးအပူးပါ / အပီးပူးပါ)
        if any(x in line for x in ["အပီးအပူးပါ", "အပြီးအပူးပါ", "အပီးပူးပါ"]):
            # 'အပီး' စကားလုံးရဲ့ ရှေ့က ဂဏန်းတွေကို ရေတွက်သည်
            parts = re.split(r'အပီး|အပြီး', line)
            nums = re.findall(r'\d', parts[0])
            price_match = re.findall(r'\d+', parts[-1])
            if nums and price_match:
                n = len(nums)
                total_sales += (n * n) * int(price_match[0])
            continue

        # (C) ပုံမှန် R (အာ) နှင့် ဒဲ့ (ဥပမာ- 12 350r250 သို့မဟုတ် 18-16-70R600)
        # စာကြောင်းအဆုံးမှ r/R နှင့် ဈေးနှုန်းကို အရင်ရှာသည်
        main_match = re.search(r'(.+?)\s*(r)?\s*(\d+)$', line)
        if main_match:
            number_part = main_match.group(1)
            is_r = main_match.group(2) is not None
            price = int(main_match.group(3))
            
            # ဂဏန်းအတွဲများကို ခွဲထုတ်သည် (space, dash, slash အကုန်ရသည်)
            all_numbers = re.findall(r'\d+', number_part)
            
            # ဂဏန်း ၅ လုံးထက်ပိုသော "အပီး" ပုံစံမဟုတ်သော အတွဲများအတွက်လည်း အလုပ်လုပ်သည်
            count = len(all_numbers)
            multiplier = 2 if is_r else 1
            total_sales += count * multiplier * price

    # --- ၃။ Final Summary Calculation ---
    cash_back_amount = (total_sales * percent) / 100
    net_total = total_sales - cash_back_amount
    
    # ရလဒ် ထုတ်ပြန်ခြင်း (Rich Format ဖြင့်)
    summary = (
        f"✅ 2D Name: {two_d_name}\n"
        f"━━━━━━━━━━━━━━\n"
        f"💰 စုစုပေါင်း: {total_sales:,} ကျပ်\n"
        f"📉 {percent}% ချွေ: {int(cash_back_amount):,} ကျပ်\n"
        f"━━━━━━━━━━━━━━\n"
        f"💵 လက်ခံရမည့်ငွေ: {int(net_total):,} ကျပ်"
    )
    return summary
