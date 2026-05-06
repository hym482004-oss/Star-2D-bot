import re

def calculate_2d_ledger(input_text):
    lines = input_text.strip().split('\n')
    total_sales = 0
    
    # --- ၁။ 2D Name & Percent သတ်မှတ်ချက် ---
    lower_text = input_text.lower()
    percent = 0
    two_d_name = ""

    groups_config = {
        "Du": {"kw": ["du2d", "du", "ဒု", "ဒူ", "ဒူဘိူင်း", "ငဒူ", "dubai"], "p": 7},
        "Mega": {"kw": ["mega", "မီ", "me", "မီဂါ"], "p": 7},
        "MM": {"kw": ["mm"], "p": 10},
        "Maxi": {"kw": ["maxi", "မက်ဆီ", "မက်စီ", "စီစီ"], "p": 7},
        "Lao": {"kw": ["lao", "loa", "laos", "loas", "လာအို", "လာလာ", "la"], "p": 7},
        "Global": {"kw": ["glo", "ကလို", "ဂလို", "global"], "p": 3},
        "London": {"kw": ["ld", "landon", "london", "lan", "လန်ဒန်", "လန်လန်"], "p": 7}
    }

    for name, data in groups_config.items():
        if any(kw in lower_text for kw in data["kw"]):
            two_d_name, percent = name, data["p"]
            break
    
    if not two_d_name:
        return "📢 @admin1 @owner \n⚠️ 2D Name မပါရှိသဖြင့် စစ်ပေးပါရှင့်။"

    # --- ၂။ စာရင်းတွက်ချက်ခြင်း Logic ---
    for line in lines:
        line = line.strip().lower()
        if not line or len(line) < 2: continue
        
        # Symbols တွေကို space ပြောင်းမယ်
        line = re.sub(r'[-\*/\.]', ' ', line)
        full_line_eng = line.translate(str.maketrans('၀၁၂၃၄၅၆၇၈၉', '0123456789'))

        # (A) ခွေပူး (n x n)
        k_p_keys = ["ခွေပူး", "အပြီအပူး", "အပီအပူး", "ခပ", "အခွေပူး", "ခွေအပူး"]
        if any(x in line for x in k_p_keys):
            pattern = '|'.join(k_p_keys)
            parts = re.split(pattern, line)
            if parts:
                nums = re.findall(r'\d', parts[0])
                if nums:
                    num_count = len(nums) * len(nums)
                    price_match = re.findall(r'\d+', full_line_eng)
                    if price_match:
                        price = int(price_match[-1])
                        total_sales += num_count * price
                        continue

        # (B) အကွက်ခွေ (n x n-1)
        if "ခ" in line:
            parts = re.split(r'ခွေ|ခ', line)
            if parts:
                nums = re.findall(r'\d', parts[0])
                n = len(nums)
                if n > 1:
                    price_match = re.findall(r'\d+', full_line_eng)
                    if price_match:
                        price = int(price_match[-1])
                        total_sales += (n * (n - 1)) * price
                        continue

        # (C) ပတ်သီး (၁၉/၂၀ ကွက်)
        if any(x in line for x in ["ပတ်", "အပါ", "ပါ", "p", "ch", "ထိပ်ပိတ်", "ထပ"]):
            is_p20 = any(x in line for x in ["ပတ်ပူး", "ပူးပို", "ထိပ်ပိတ်", "ထပ", "ထန"])
            parts = re.split(r'ပတ်|အပါ|ပါ|p|ch|ထိပ်ပိတ်|ထပ', line)
            if parts:
                nums = re.findall(r'\d', parts[0])
                price_match = re.findall(r'\d+', full_line_eng)
                if price_match and nums:
                    price = int(price_match[-1])
                    total_sales += (len(nums) * (20 if is_p20 else 19)) * price
                    continue

        # (D) ဒဲ့ နှင့် R
        match = re.search(r'(\d+)?\s*(r)\s*(\d+)$', line, re.IGNORECASE)
        if match:
            number_part = line[:match.start()]
            d_price_str = match.group(1)
            r_price = int(match.group(3))
            all_numbers = re.findall(r'\d+', number_part)
            if all_numbers:
                for _ in all_numbers:
                    total_sales += (int(d_price_str) + r_price) if d_price_str else (r_price * 2)
                continue

        # (E) အုပ်စုလိုက် (စုံမ၊ ဘရိတ်၊ ညီကို၊ အပူး၊ ထိပ်/ပိတ်)
        groups_list = [
            {"keys": ["စုံဘရိတ်", "မဘရိတ်"], "count": 50},
            {"keys": ["စုံစုံ", "စူံစူံ", "စူံစုံ", "စုံစူံ", "မမ", "စုံမ", "မစုံ", "စမ", "မစ", "စစ"], "count": 25},
            {"keys": ["ညီကို", "ညီအကို", "ညီအစ်ကို"], "count": 20},
            {"keys": ["အပူး", "ပူး", "puu", "pu"], "count": 10},
            {"keys": ["ပါဝါ", "pw", "ပဝ", "power"], "count": 10},
            {"keys": ["နက္ခတ်", "နက", "nk", "နကွတ်"], "count": 10},
            {"keys": ["ထိပ်", "ထ", "အထိပ်", "ထိတ်"], "count": 10},
            {"keys": ["ပိတ်", "ပ", "အပိတ်", "ပိက်"], "count": 10},
            {"keys": ["မပူး", "စုံပူး"], "count": 5}
        ]
        
        found_group = False
        for g in groups_list:
            if any(k in line for k in g["keys"]):
                price_match = re.findall(r'\d+', full_line_eng)
                if price_match:
                    price = int(price_match[-1])
                    total_sales += g["count"] * price
                    found_group = True
                    break
        if found_group: continue

    # --- ၃။ Summary ---
    cash_back = (total_sales * percent) / 100
    net_total = total_sales - cash_back
    
    return (f"✅ 2D Name: {two_d_name}\n"
            f"━━━━━━━━━━━━━━\n"
            f"💰 စုစုပေါင်း: {total_sales:,} ကျပ်\n"
            f"📉 {percent}% ချွေ: {int(cash_back):,} ကျပ်\n"
            f"━━━━━━━━━━━━━━\n"
            f"💵 လက်ခံရမည့်ငွေ: {int(net_total):,} ကျပ်ဘဲ လွဲပါရှင့်")
