import re

def calculate_2d_ledger(input_text):
    lines = input_text.strip().split('\n')
    total_sales = 0
    
    # --- ၁။ 2D Name & Percent သတ်မှတ်ချက် (နင်ပေးထားတဲ့ ၇ အုပ်စု) ---
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

    # Name ကို စစ်ထုတ်ခြင်း
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
        
        # နာမည်ပါတဲ့လိုင်းကို ကျော်မယ်
        if any(kw in line for name in groups for kw in groups[name]["kw"]):
            if len(line) < 15: continue

        # Symbols တွေကို space ပြောင်းမယ် (-, *, /, .)
        line = re.sub(r'[-\*/\.]', ' ', line)

        # --- ဒီအောက်မှာ ငါတို့ တွက်နည်းတွေ တစ်ခုချင်းစီ ထည့်သွားကြမယ် ---
                # (A) ပတ်သီး / p / ch (ဂဏန်းတစ်လုံးချင်းစီကို ၁၉ ကွက်နှုန်းနဲ့ တွက်မယ်)
        pats_keywords = ["ပတ်", "အပါ", "ပါ", "p", "ch"]
        
        if any(x in line for x in pats_keywords) and not any(x in line for x in ["ပတ်ပူး", "ပူးပို"]):
            # Keyword တွေနဲ့ ခွဲပြီး ရှေ့က ဂဏန်းအပိုင်းကို ယူမယ်
            parts = re.split(r'ပတ်|အပါ|ပါ|p|ch', line)
            if parts:
                nums = re.findall(r'\d', parts[0]) 
                num_count = len(nums)
                price_match = re.findall(r'\d+', line)
                if price_match and num_count > 0:
                    price = int(price_match[-1])
                    total_sales += (num_count * 19) * price
                    continue
                    # (B) ပတ်ပူး / ထိပ်ပိတ် / အပူးပို (၂၀ ကွက်)
        # နင်ပေးထားတဲ့ ခေါ်ပုံခေါ်နည်း အသစ်တွေအကုန် ထည့်ထားတယ်
        p20_keywords = [
            "ပတ်ပူး", "ပတ်သီးအပူးပို", "ပတ်သီးပူးပို", "ပတ်ပူးပို", 
            "ပတ်အကွက်20", "ပတ်အပူးအပိုယူ", "ထိပ်ပိတ်", "ထပ", "ထန", "ထိပ်နောက်"
        ]
        
        if any(x in line for x in p20_keywords):
            # Keyword တွေနဲ့ ခွဲပြီး ရှေ့က ဂဏန်းကို ရှာမယ်
            # (regex split သုံးပြီး keyword နေရာကနေ ဖြတ်လိုက်တာပါ)
            pattern = '|'.join(p20_keywords)
            parts = re.split(pattern, line)
            
            if parts:
                # ရှေ့က ဂဏန်းအရေအတွက်ကို ရေမယ် (ဥပမာ "94" ဆိုရင် ၂ လုံး)
                nums = re.findall(r'\d', parts[0])
                num_count = len(nums)
                
                # စာကြောင်းရဲ့ နောက်ဆုံးဂဏန်းကို ဈေးနှုန်းအဖြစ် ယူမယ်
                price_match = re.findall(r'\d+', line)
                if price_match and num_count > 0:
                    price = int(price_match[-1])
                    # (ဂဏန်းအရေအတွက် * ၂၀ ကွက်) * ဈေးနှုန်း
                    total_sales += (num_count * 20) * price
                    continue
                    
        # (C) ဒဲ့ နှင့် R (ဈေးခွဲတွက်နည်း + ပုံမှန် R တွက်နည်း)
        # ဥပမာ - 300R200 (ဒဲ့+အာ) သို့မဟုတ် R200 (အာသီးသန့်)
        match = re.search(r'(\d+)?\s*(r)\s*(\d+)$', line, re.IGNORECASE)
        if match:
            number_part = line[:match.start()]
            d_price_str = match.group(1) # ဒဲ့ဈေး (ရှိချင်မှရှိမယ်)
            r_price = int(match.group(3)) # R ဈေး (အမြဲပါတယ်)
            
            all_numbers = re.findall(r'\d+', number_part)
            if all_numbers:
                for _ in all_numbers:
                    if d_price_str:
                        # (၁) ဒဲ့ဈေးပါလျှင်: တစ်လုံးကို (ဒဲ့ဈေး + Rဈေး) ပေါင်းတွက်မယ်
                        total_sales += int(d_price_str) + r_price
                    else:
                        # (၂) ဒဲ့ဈေးမပါလျှင်: ပုံမှန်အတိုင်း (Rဈေး x ၂ ကွက်) တွက်မယ်
                        total_sales += r_price * 2
                continue
                        # (D) အကွက်ခွေ (ဥပမာ - 1234ခ500 သို့မဟုတ် 2345ခ၅၀၀)
        if "ခ" in line:
            # "ခွေ" သို့မဟုတ် "ခ" ရဲ့ ရှေ့က ဂဏန်းတွေကို ယူမယ်
            parts = re.split(r'ခွေ|ခ', line)
            if parts:
                # ရှေ့က ဂဏန်းအရေအတွက်ကို ရှာမယ်
                nums = re.findall(r'\d', parts[0])
                n = len(nums)
                num_count = n * (n - 1)
                
                # စာကြောင်းတစ်ခုလုံးမှာရှိတဲ့ ဂဏန်းတွေထဲက နောက်ဆုံးဂဏန်းကို ဈေးနှုန်းအဖြစ် ယူမယ်
                # (မြန်မာဂဏန်းပါခဲ့ရင် အင်္ဂလိပ်ဂဏန်းကို ပြောင်းပြီးမှ တွက်မယ်)
                full_line_eng = line.translate(str.maketrans('၀၁၂၃၄၅၆၇၈၉', '0123456789'))
                price_match = re.findall(r'\d+', full_line_eng)
                
                if price_match and num_count > 0:
                    price = int(price_match[-1])
                    total_sales += num_count * price
                    continue
                    
        # (F) အုပ်စုလိုက် တွက်နည်း (Keywords အစုံဆုံး version)
        groups = [
            # အပူးအုပ်စု (၁၀ ကွက်): 00, 11, 22...99
            {
                "keys": ["အပူး", "ပူး", "puu", "pu"],
                "count": 10
            },
            
            # ပါဝါအုပ်စု (၁၀ ကွက်): 05, 16, 27, 38, 49 (အာ)
            {
                "keys": ["ပါဝါ", "pw", "ပဝ", "power"], 
                "count": 10
            },
            
            # နက္ခတ်အုပ်စု (၁၀ ကွက်): 07, 18, 29, 35, 46 (အာ)
            {
                "keys": ["နက္ခတ်", "နက", "nk","နကွတ်"], 
                "count": 10
            },
            
            # ညီကိုအုပ်စု (၂၀ ကွက်): 01, 12, 23... (အာ)
            {
                "keys": ["ညီကို", "ညီအကို", "ညီအစ်ကို"], 
                "count": 20
            }
        ]
        
        found_group = False
                # --- (၁) ခွေပူး (n x n) အရင်စစ်မယ် ---
        k_p_keys = ["ခွေပူး", "အပြီအပူး", "အပီအပူး", "ခပ", "အခွေပူး", "ခွေအပူး"]
        if any(x in line for x in k_p_keys):
            pattern = '|'.join(k_p_keys)
            parts = re.split(pattern, line)
            if parts:
                nums = re.findall(r'\d', parts[0])
                n = len(nums)
                num_count = n * n
                
                full_line_eng = line.translate(str.maketrans('၀၁၂၃၄၅၆၇၈၉', '0123456789'))
                price_match = re.findall(r'\d+', full_line_eng)
                if price_match and num_count > 0:
                    price = int(price_match[-1])
                    total_sales += num_count * price
                    continue

        # --- (၂) ကျန်တဲ့ အုပ်စုလိုက်တွက်နည်းများ ---
        groups_list = [
            {"keys": ["အပူး", "ပူး", "puu", "pu"], "count": 10},
            {"keys": ["စုံစုံ", "စူံစူံ", "စူံစုံ", "စုံစူံ", "မမ", "စုံမ", "မစုံ", "စမ", "မစ", "စစ"], "count": 25},
            {"keys": ["မပူး"], "count": 5},
            {"keys": ["စုံပူး"], "count": 5},
            {"keys": ["ပါဝါ", "pw", "ပဝ", "power"], "count": 10},
            {"keys": ["နက္ခတ်", "နက", "nk", "နကွတ်"], "count": 10},
            {"keys": ["ညီကို", "ညီအကို", "ညီအစ်ကို"], "count": 20}
        ]

        found_group = False
        full_line_eng = line.lower().translate(str.maketrans('၀၁၂၃၄၅၆၇၈၉', '0123456789'))
        
        for g in groups_list:
            if any(k in full_line_eng for k in g["keys"]):
                price_match = re.findall(r'\d+', full_line_eng)
                if price_match:
                    price = int(price_match[-1])
                    total_sales += g["count"] * price
                    found_group = True
                    break
        
        if found_group:
            continue





    # --- ၃။ ရလဒ်ပြန်ထုတ်ပေးခြင်း (Summary) ---
    cash_back = (total_sales * percent) / 100
    net_total = total_sales - cash_back
    
    return (f"✅ 2D Name: {two_d_name}\n"
            f"━━━━━━━━━━━━━━\n"
            f"💰 စုစုပေါင်း: {total_sales:,} ကျပ်\n"
            f"📉 {percent}% ချွေ: {int(cash_back):,} ကျပ်\n"
            f"━━━━━━━━━━━━━━\n"
            f"💵 လက်ခံရမည့်ငွေ: {int(net_total):,} ကျပ်ဘဲ လွဲပါရှင့်")
