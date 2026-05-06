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
    
    # 2D Name မပါရင် စာရင်းမတွက်ဘဲ Admin ခေါ်ရန်
    if not two_d_name:
        return "📢 @admin @owner \n⚠️ 2D Name (Mega, Du, MM, Me) မပါရှိသဖြင့် စစ်ပေးပါရှင့်။"

    for line in lines:
        line = line.strip().lower()
        if not line or any(x in line for x in ["mega", "mm", "du", "me", "မီဂါ"]):
            continue

        # --- ၁။ Special Keywords (အပူး၊ နက္ခတ်၊ ပါဝါ၊ ညီကို) ---
        special_map = {"အပူး": 10, "နက္ခတ်": 10, "ပါဝါ": 10, "ညီကို": 20}
        found_sp = False
        for kw, slots in special_map.items():
            if kw in line:
                price = re.findall(r'\d+', line)
                if price:
                    total_sales += slots * int(price[-1])
                    found_sp = True
                    break
        if found_sp: continue

        # --- ၂။ n x n Logic (အပီးအပူးပါ) ---
        if "အပီးအပူးပါ" in line or "အပြီးအပူးပါ" in line:
            parts = re.split(r'အပီး|အပြီး', line)
            nums = re.findall(r'\d', parts[0])
            price = re.findall(r'\d+', parts[1])
            if nums and price:
                n = len(nums)
                total_sales += (n * n) * int(price[0])
            continue

        # --- ၃။ ပုံမှန် Parsing (R ပါရင် ၂ ဆ၊ မပါရင် ဒဲ့) ---
        # "50/30=100r50" ကဲ့သို့သော စာသားများကို / သို့မဟုတ် - ဖြင့်ခွဲမည်
        segments = re.split(r'/|-|,', line)
        for seg in segments:
            # ဈေးနှုန်းနှင့် R ကို ရှာဖွေခြင်း (ဥပမာ- 12 350r250)
            match = re.search(r'([\d\s]+)\s*(r)?\s*(\d+)', seg)
            if match:
                num_part = match.group(1).strip().split()
                is_r = match.group(2) is not None
                price = int(match.group(3))
                
                count = len(num_part)
                multiplier = 2 if is_r else 1
                total_sales += count * multiplier * price

    # --- ၄။ Final Calculation ---
    cash_back = (total_sales * percent) / 100
    net_total = total_sales - cash_back
    
    return f"✅ 2D Name: {two_d_name}\n" \
           f"----------------------\n" \
           f"💰 စုစုပေါင်း: {total_sales:,} ကျပ်\n" \
           f"📉 {percent}% ချွေ: {int(cash_back):,} ကျပ်\n" \
           f"💵 လက်ခံရမည့်ငွေ: {int(net_total):,} ကျပ်"

# စမ်းသပ်ရန်
# print(calculate_2d_ledger("12 350r250\n15 150r100\nMega"))
