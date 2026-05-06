import re

def calculate_2d_ledger(input_text):
    lines = input_text.strip().split('\n')
    total_sales = 0
    
    # --- ၁။ အုပ်စု (၇) စု သတ်မှတ်ခြင်း (Discount Mapping) ---
    lower_text = input_text.lower()
    percent = 0
    two_d_name = ""

    groups = {
        "Du": {"kw": ["du2d", "du", "ဒု", "ဒူ", "ဒူဘိူင်း", "ငဒူ", "dubai"], "p": 7},
        "Mega": {"kw": ["mega", "မီ", "me", "မီဂါ"], "p": 7},
        "MM": {"kw": ["mm"], "p": 10},
        "Maxi": {"kw": ["maxi", "မက်ဆီ", "မက်စီ", "စီစီ"], "p": 7},
        "Lao": {"kw": ["lao", "loa", "laos", "loas", "လာအို", "လာလာ", "la"], "p": 7},
        "Global": {"kw": ["glo", "ကလို", "ဂလို", "global"], "p": 3},
        "London": {"kw": ["ld", "landon", "london", "lan", "လန်ဒန်", "လန်လန်"], "p": 7}
    }

    # Name ရှာဖွေခြင်း
    for name, data in groups.items():
        if any(kw in lower_text for kw in data["kw"]):
            two_d_name, percent = name, data["p"]
            break
    
    if not two_d_name:
        return "📢 @admin1 @owner \n⚠️ 2D Name မပါရှိသဖြင့် စစ်ပေးပါရှင့်။"

    # --- ၂။ စာရင်းတွက်ချက်ခြင်း Logic ---
    for line in lines:
        line = line.strip().lower()
        if not line: continue
        
        # Name ပါတဲ့လိုင်းတွေကို ကျော်ရန်
        is_name_line = any(kw in line for name in groups for kw in groups[name]["kw"])
        if is_name_line and len(line) < 15: continue

        # Symbols များကို Space ပြောင်းခြင်း ( - , * , / , . )
        line = re.sub(r'[-\*/\.]', ' ', line)

        # (A) ပတ်သီး / အပါ (၁၉ ကွက်)
        if any(x in line for x in ["ပတ်", "အပါ", "ပါ"]) and not any(x in line for x in ["ပတ်ပူး", "ပူးပို"]):
            price = re.findall(r'\d+', line)
            if price: total_sales += 19 * int(price[-1]); continue

        # (B) ပတ်ပူး / ပူးပို / ပတ်အကွက်20 (၂၀ ကွက်)
        if any(x in line for x in ["ပတ်ပူး", "ပူးပို", "ထန", "ထပ", "ထိပ်ပိတ်", "ထိပ်နောက်"]):
            price = re.findall(r'\d+', line)
            if price: total_sales += 20 * int(price[-1]); continue

        # (C) ထိပ် / ထ / ဘရိတ် / ဆယ်ပြည့် / အပူး / ပူး (၁၀ ကွက်)
        if any(x in line for x in ["ထိပ်", "ထ", "ဘရိတ်", "ဆယ်ပြည့်", "အပူး", "ပူး"]) and not any(x in line for x in ["စုံပူး", "မပူး", "စုံဘရိတ်", "မဘရိတ်"]):
            price = re.findall(r'\d+', line)
            if price: total_sales += 10 * int(price[-1]); continue

        # (D) စုံပူး / မပူး (၅ ကွက်)
        if any(x in line for x in ["စုံပူး", "မပူး"]):
            price = re.findall(r'\d+', line)
            if price: total_sales += 5 * int(price[-1]); continue

        # (E) စစ / မမ / စမ / မစ (၂၅ ကွက် / R ပါရင် ၅၀)
        if any(x in line for x in ["စစ", "မမ", "စမ", "မစ", "စုံစုံ", "စုံမ", "မစုံ"]):
            is_r = "r" in line
            price = re.findall(r'\d+', line)
            if price:
                slots = 50 if is_r else 25
                total_sales += slots * int(price[-1]); continue

        # (F) စုံဘရိတ် / မဘရိတ် (၅၀ ကွက်)
        if any(x in line for x in ["စုံဘရိတ်", "စုံbk", "မbk", "မဘရိတ်", "စဘရိတ်"]):
            price = re.findall(r'\d+', line)
            if price: total_sales += 50 * int(price[-1]); continue

        # (G) ကပ် / အကပ် / ကို (ရှေ့လုံး x နောက်လုံး)
        if any(x in line for x in ["ကပ်", "အကပ်", "ကို"]):
            # Keyword ဖြင့် ခွဲပြီး ဂဏန်းအရေအတွက် ရှာသည်
            parts = re.split(r'ကပ်|အကပ်|ကို', line)
            if len(parts) >= 2:
                n1 = len(re.findall(r'\d', parts[0]))
                n2 = len(re.findall(r'\d', parts[1].split()[0]))
                price = re.findall(r'\d+', line)
                if n1 and n2 and price:
                    total_sales += (n1 * n2) * int(price[-1]); continue

        # (H) ခွေ / အပူးပါခွေ
        if "ခွေ" in line:
            parts = line.split("ခွေ")
            n = len(re.findall(r'\d', parts[0]))
            price = re.findall(r'\d+', line)
            if n and price:
                if "ပူး" in line or "အပူးပါ" in line:
                    slots = (n * (n - 1)) + n # ခွေ + အပူး
                else:
                    slots = (n * (n - 1)) # ခွေသီးသန့်
                total_sales += slots * int(price[-1]); continue

        # (I) n x n (အပီး / အပြီး)
        if any(x in line for x in ["အပီး", "အပြီး"]):
            parts = re.split(r'အပီး|အပြီး', line)
            n = len(re.findall(r'\d', parts[0]))
            price = re.findall(r'\d+', line)
            if n and price:
                total_sales += (n * n) * int(price[-1]); continue

        # (J) ပုံမှန် R နှင့် ဒဲ့ (ဂဏန်းအမျိုးမျိုး)
        cleaned_line = re.sub(r'[*\/=\-,]', ' ', line)
        match = re.search(r'(.+?)\s*(r)?\s*(\d+)$', cleaned_line)
        if match:
            is_r = match.group(2) is not None
            price = int(match.group(3))
            all_numbers = re.findall(r'\d+', match.group(1))
            for num in all_numbers:
                multiplier = 2 if is_r else 1
                total_sales += 1 * multiplier * price

    # --- ၃။ Summary ထုတ်ပြန်ခြင်း ---
    cash_back = (total_sales * percent) / 100
    net_total = total_sales - cash_back
    
    return (f"✅ 2D Name: {two_d_name}\n"
            f"━━━━━━━━━━━━━━\n"
            f"💰 စုစုပေါင်း: {total_sales:,} ကျပ်\n"
            f"📉 {percent}% ချွေ: {int(cash_back):,} ကျပ်\n"
            f"━━━━━━━━━━━━━━\n"
            f"💵 လက်ခံရမည့်ငွေ: {int(net_total):,} ကျပ်")
