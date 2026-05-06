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
        if not line: continue
        
        # နာမည်သီးသန့်ပါတဲ့လိုင်းကို ကျော်မည်
        if line == two_d_name.lower(): continue

        # (A) Special Keywords Rule (ညီကို=20, နက္ခတ်/အပူး/ပါဝါ=10)
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

        # (B) n x n Rule (အပီးအပူးပါ / အပီးပူးပါ)
        if any(x in line for x in ["အပီးအပူးပါ", "အပြီးအပူးပါ", "အပီးပူးပါ"]):
            parts = re.split(r'အပီး|အပြီး', line)
            nums = re.findall(r'\d', parts[0])
            price_match = re.findall(r'\d+', parts[-1])
            if nums and price_match:
                n = len(nums)
                total_sales += (n * n) * int(price_match[0])
            continue

        # (C) ခွေတွက်နည်း (ဥပမာ- 123456 ခွေ ၂၅၀)
        if "ခွေ" in line:
            parts = line.split("ခွေ")
            nums = re.findall(r'\d', parts[0])
            price_match = re.findall(r'\d+', parts[1])
            if nums and price_match:
                n = len(nums)
                total_slots = (n * (n - 1)) # အပြန်အလှန် ခွေထားခြင်း
                total_sales += total_slots * int(price_match[0])
            continue

        # (D) ပုံမှန် R နှင့် ဒဲ့ (Parsing အသစ်)
        # *, /, =, -, , စတဲ့ သင်္ကေတတွေကို space ပြောင်းမည်
        cleaned_line = re.sub(r'[*\/=\-,]', ' ', line)
        main_match = re.search(r'(.+?)\s*(r)?\s*(\d+)$', cleaned_line)
        
        if main_match:
            number_part = main_match.group(1)
            is_r = main_match.group(2) is not None
            price = int(main_match.group(3))
            all_numbers = re.findall(r'\d+', number_part)
            
            for num in all_numbers:
                # ဂဏန်းအတွဲလိုက် (ဥပမာ 13-18-36-68) ဖြစ်စေ၊ တစ်လုံးချင်းဖြစ်စေ တွက်ပေးမည်
                multiplier = 2 if is_r else 1
                total_sales += 1 * multiplier * price

    # --- ၃။ Summary ထုတ်ပြန်ခြင်း ---
    cash_back_amount = (total_sales * percent) / 100
    net_total = total_sales - cash_back_amount
    
    return (f"✅ 2D Name: {two_d_name}\n"
            f"━━━━━━━━━━━━━━\n"
            f"💰 စုစုပေါင်း: {total_sales:,} ကျပ်\n"
            f"📉 {percent}% ချွေ: {int(cash_back_amount):,} ကျပ်\n"
            f"━━━━━━━━━━━━━━\n"
            f"💵 လက်ခံရမည့်ငွေ: {int(net_total):,} ကျပ်")
