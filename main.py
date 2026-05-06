import re

def calculate_2d_ledger(input_text):
    lines = input_text.strip().split('\n')
    total_sales = 0
    
    lower_text = input_text.lower()
    percent = 0
    two_d_name = ""
    
    # "mega" ကို "me" ထက် အရင် စစ်ရမယ်
    if "mm" in lower_text:
        two_d_name, percent = "MM", 10
    elif any(x in lower_text for x in ["mega", "မီဂါ"]):
        two_d_name, percent = "Mega", 7
    elif "du" in lower_text:
        two_d_name, percent = "Du", 7
    elif "me" in lower_text:
        two_d_name, percent = "Me", 7
    
    if not two_d_name:
        return "📢 @admin1 @owner \n⚠️ 2D Name (Mega, Du, MM, Me) မပါရှိသဖြင့် စစ်ပေးပါရှင့်။"

    for line in lines:
        line = line.strip().lower()
        if not line: continue
        if two_d_name.lower() in line and not re.search(r'\d', line): continue

        # (A) Special Keywords
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

        # (B) အပီးအပူးပါ Logic
        if any(x in line for x in ["အပီးအပူးပါ", "အပြီးအပူးပါ", "အပီးပူးပါ"]):
            parts = re.split(r'အပီး|အပြီး', line)
            nums = re.findall(r'\d', parts[0])
            price_match = re.findall(r'\d+', parts[-1])
            if nums and price_match:
                n = len(nums)
                total_sales += (n * n) * int(price_match[0])
            continue

        # (C) ပုံမှန် R နှင့် ဒဲ့ - BUG FIX
        cleaned_line = re.sub(r'[*=,]', ' ', line)
        
        # R ပါမပါ စစ်ခြင်း
        is_r = bool(re.search(r'\br\b', cleaned_line))
        
        # ဈေးနှုန်း (နောက်ဆုံး ဂဏန်း)
        price_match = re.search(r'(\d+)\s*$', re.sub(r'\br\b', '', cleaned_line))
        if not price_match:
            continue
        price = int(price_match.group(1))
        
        # ဂဏန်းအတွဲများ ရှာဖွေခြင်း (ဈေးနှုန်းမပါဘဲ)
        number_section = cleaned_line[:price_match.start()]
        
        # "/" သို့ "-" ဖြင့် ပိုင်းထားတဲ့ combo စစ်ခြင်း
        # ဥပမာ: "124567/3890" → ဂဏန်း ၁၀ ခု
        # ဂဏန်းတစ်ခုချင်းစီ ပိုင်းထုတ်
        digit_groups = re.findall(r'\d+', number_section)
        
        slot_count = 0
        for grp in digit_groups:
            if len(grp) == 1:
                # တစ်လုံးချင်း ဆိုရင် ၁ slot
                slot_count += 1
            else:
                # ဂဏန်းစုံ (45, 124567) → နှစ်လုံးစီ ပိုင်းရမယ်
                slot_count += len(grp) // 2
        
        multiplier = 2 if is_r else 1
        total_sales += slot_count * multiplier * price

    cash_back_amount = (total_sales * percent) / 100
    net_total = total_sales - cash_back_amount
    
    return (f"✅ 2D Name: {two_d_name}\n"
            f"━━━━━━━━━━━━━━\n"
            f"💰 စုစုပေါင်း: {total_sales:,} ကျပ်\n"
            f"📉 {percent}% ချွေ: {int(cash_back_amount):,} ကျပ်\n"
            f"━━━━━━━━━━━━━━\n"
            f"💵 လက်ခံရမည့်ငွေ: {int(net_total):,} ကျပ်")
