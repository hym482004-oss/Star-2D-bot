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
        
    # --- ၃။ ရလဒ်ပြန်ထုတ်ပေးခြင်း (Summary) ---
    cash_back = (total_sales * percent) / 100
    net_total = total_sales - cash_back
    
    return (f"✅ 2D Name: {two_d_name}\n"
            f"━━━━━━━━━━━━━━\n"
            f"💰 စုစုပေါင်း: {total_sales:,} ကျပ်\n"
            f"📉 {percent}% ချွေ: {int(cash_back):,} ကျပ်\n"
            f"━━━━━━━━━━━━━━\n"
            f"💵 လက်ခံရမည့်ငွေ: {int(net_total):,} ကျပ်ဘဲ လွဲပါရှင့်")
