import telebot

# Leo Bot Token
TOKEN = "8669202237:AAEPCaS8x4jEsUaP6BQ-8-PM-b6_PN4hk5w"
bot = telebot.TeleBot(TOKEN)

def check_2d_name(input_text):
    lower_text = input_text.lower()
    
    # --- ၂D Name ၇ ခု သတ်မှတ်ခြင်း ---
    group_7 = ["maxi", "du", "lao", "mega", "glo", "london", "dubai"]
    group_10 = ["mm"]
    
    two_d_name = ""
    percent = 0

    # နာမည် စစ်ဆေးခြင်း
    for name in group_7:
        if name in lower_text:
            two_d_name = name.capitalize()
            percent = 7
            break
            
    if not two_d_name:
        for name in group_10:
            if name in lower_text:
                two_d_name = name.upper()
                percent = 10
                break

    # --- အဆင့် (၁) ရလဒ် ထုတ်ပေးခြင်း ---
    if not two_d_name:
        return "📢 @owner @admin1 \n⚠️ 2D Name (ဥပမာ- Maxi, MM) မပါရှိသဖြင့် စစ်ပေးပါရှင့်။"
    else:
        return (f"👤 らŤΛ尺\n\n"
                f"✅ {two_d_name} နာမည် လက်ခံရရှိပါတယ်\n"
                f"🎁 {percent}% Cash Back သတ်မှတ်ထားပါတယ်\n\n"
                f"တစ်ဆင့်ချင်းသွားနေပါသည်... (တွက်ချက်မှု Logic မထည့်ရသေးပါ)")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, check_2d_name(message.text))

bot.infinity_polling()
