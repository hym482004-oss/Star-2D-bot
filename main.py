import re

def calculate_2d_ledger(input_text):
    lines = input_text.strip().split('\n')
    total_sales = 0
    
    # --- ၁။ အုပ်စု (၇) စု သတ်မှတ်ခြင်း ---
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

    # Name စစ်ဆေးခြင်း
    for name, data in groups.items():
        if any(kw in lower_text for kw in data["kw"]):
            two_d_name = name
            percent = data["p"]
            break
    
    if not two_d_name:
        return "📢 @admin1 @owner \n⚠️ 2D Name မပါရှိသဖြင့် စစ်ပေးပါရှင့်။"

    # --- ၂။ စာရင်းတွက်ချက်ခြင်း Logic ---
    for line in lines:
        line = line.strip().lower()
        if not line or any(kw in line for name in groups for kw in groups[name]["kw"]):
            if len(line) < 10: continue # Name လိုင်းတွေကို ကျော်ရန်

        # (A) Special: ညီကို=20, အပူး/နက္ခတ်/ပါဝါ=10
        sp_map = {"အပူး": 10, "နက္ခတ်": 10, "ပါဝါ": 10, "ညီကို": 20}
        found_sp = False
        for kw, slots in sp_map.items():
            if kw in line:
                price = re.findall(r'\d+', line)
                if price:
                    total_sales += slots * int(price[-1])
                    found_sp = True; break
        if found_sp: continue

        # (B) n x n Rule (အပီးအပူးပါ)
        if any(x in line for x in ["အပီးအပူးပါ", "အပြီးအပူးပါ", "အပီးပူးပါ"]):
            parts = re.split(r'အပီး|အပြီး', line)
            nums = re.findall(r'\d', parts[0])
            price = re.findall(r'\d+', parts[-1])
            if nums and price:
                n = len(nums)
                total_sales += (n * n) * int(price[0])
            continue

        # (C) ပုံမှန် R နှင့် ဒဲ့ (Symbols အားလုံး ရှင်းထုတ်သည်)
        cleaned = re.sub(r'[*\/=\-,]', ' ', line)
        match = re.search(r'(.+?)\s*(r)?\s*(\d+)$', cleaned)
        if match:
            is_r = match.group(2) is not None
            price = int(match.group(3))
            all_nums = re.findall(r'\d+', match.group(1))
            for num in all_nums:
                total_sales += (2 if is_r else 1) * price

    # --- ၃။ Final Result ---
    cash_back = (total_sales * percent) / 100
    net_total = total_sales - cash_back
    
    return (f"✅ 2D Name: {two_d_name}\n"
            f"━━━━━━━━━━━━━━\n"
            f"💰 စုစုပေါင်း: {total_sales:,} ကျပ်\n"
            f"📉 {percent}% ချွေ: {int(cash_back):,} ကျပ်\n"
            f"━━━━━━━━━━━━━━\n"
            f"💵 လက်ခံရမည့်ငွေ: {int(net_total):,} ကျပ်")
