import re

def calculate_2d_ledger(input_text):
    # စာရင်းကို တစ်ကြောင်းချင်းစီ ခွဲထုတ်ခြင်း
    lines = input_text.strip().split('\n')
    total_sales = 0
    
    # --- ၁။ 2D Name & Percent Setup (အကြီးအသေးမရွေး စစ်ဆေးခြင်း) ---
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
    
    # 2D Name လုံးဝမတွေ့မှသာ Admin ခေါ်မည်
    if not two_d_name:
        return "📢 @admin1 @owner \n⚠️ 2D Name (Mega, Du, MM, Me) မပါရှိသဖြင့် စစ်ပေးပါရှင့်။"

    # --- ၂။ တစ်ကြောင်းချင်းစီကို စတင်တွက်ချက်ခြင်း ---
    for line in lines:
        line = line.strip().lower()
        
        # နာမည်ပါတဲ့လိုင်း သို့မဟုတ် blank line ကို ကျော်မည်
        if not line or any(x == two_d_name.lower() or x in line for x in ["mega", "mm", "du", "me", "မီဂါ"]):
            if len(line) < 5: # "Mm", "Me" ကဲ့သို့သော နာမည်သီးသန့်လိုင်းများကို ကျော်ရန်
                continue

        # (A) Special Keywords (ညီကို=20, အပူး/နက္ခတ်/ပါဝါ=10)
        special_map = {"အပူး": 10, "နက္ခတ်": 10, "ပါဝါ": 10, "ညီကို": 20}
        found_sp = False
        for kw, slots in special_map.items():
            if kw in line:
                price_match = re.findall(r'\d+', line)
                if price_match:
                    total_sales += slots * int(price_match[-1])
                    found_sp = True
                    break
        if found_sp: continue

        # (B) n x n Logic (အပီးအပူးပါ)
        if any(x in line for x in ["အပီးအပူးပါ", "အပြီးအပူးပါ", "အပီးပူးပါ"]):
            parts = re.split(r'အပီး|အပြီး', line)
            nums = re.findall(r'\d', parts[0])
            price_match = re.findall(r'\d+', parts[-1])
            if nums and price_match:
                n = len(nums)
                total_sales += (n * n) * int(price_match[0])
            continue

        # (C) ပုံမှန် R နှင့် ဒဲ့ (Special handling for * and other symbols)
        # သင်္ကေတများ (*, /, =, -) ကို space ဖြင့် အစားထိုးသည်
        cleaned_line = re.sub(r'[*\/=\-,]', ' ', line)
        
        # စာကြောင်းအဆုံးမှ 'r' နှင့် ဈေးနှုန်းကို ရှာဖွေသည်
        main_match = re.search(r'(.+?)\s*(r)?\s*(\d+)$', cleaned_line)
        
        if main_match:
            number_part = main_match.group(1)
            is_r = main_match.group(2) is not None
            price = int(main_match.group(3))
            
            # ဂဏန်းအတွဲများကို ရှာဖွေခြင်း
            all_numbers = re.findall(r'\d+', number_part)
            count = len(all_numbers)
            
            multiplier = 2 if is_r else 1
            total_sales += count * multiplier * price

    # --- ၃။ Summary ထုတ်ပြန်ခြင်း ---
    cash_back_amount = (total_sales * percent) / 100
    net_total = total_sales - cash_back_amount
    
    summary = (
        f"✅ 2D Name: {two_d_name}\n"
        f"━━━━━━━━━━━━━━\n"
        f"💰 စုစုပေါင်း: {total_sales:,} ကျပ်\n"
        f"📉 {percent}% ချွေ: {int(cash_back_amount):,} ကျပ်\n"
        f"━━━━━━━━━━━━━━\n"
        f"💵 လက်ခံရမည့်ငွေ: {int(net_total):,} ကျပ်"
    )
    return summary
