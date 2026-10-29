import os
import re
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

ERRORS = {
 "10252": "🔴 10252 - قطع الخيط أو عقدة\nالسبب: الخيط انقطع او في عقدة كبيرة\nالحل: شوف رقم ST، اربط الخيط بعقدة صغيرة، قص العقدة الكبيرة، اضغط زر تغذية الخيط وشغل",
 "10254": "🔴 10254 - خطأ تغذية الخيط اليسار\nالسبب: موتور التغذية اليسار عليه وبر او الخيط لافف عليه\nالحل: وقف الماكينة، نظف الموتور من الوبر، تأكد الخيط مو مشدود، نظف الحساس بضربة هوا، اعمل Reset",
 "10250": "🔴 10250 - خطأ تغذية خيط عام\nالحل: تأكد من البكرات ونظف المغذيات"
}

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "أهلا بك! 👋 أنا خبير ماكينات CMS 530 HP\n\nأرسل لي صورة شاشة الخطأ أو اكتب رقم الخطأ مثل 10252")

@bot.message_handler(content_types=['photo'])
def on_photo(m):
    bot.send_message(m.chat.id, "📸 استلمت الصورة!\nاكتب رقم الخطأ الظاهر على الشاشة مثل 10252 حتى أعطيك الحل الدقيق بالعربي")

@bot.message_handler(func=lambda m: True)
def on_text(m):
    nums = re.findall(r'10\d{3}', m.text)
    if nums:
        for code in nums:
            if code in ERRORS:
                bot.send_message(m.chat.id, ERRORS[code])
                return
        bot.send_message(m.chat.id, f"الخطأ {nums[0]} لسا ما عندي، ابعتلي صورة واضحة للخطأ مشان أضيفو")
    else:
        bot.send_message(m.chat.id, "اكتب رقم الخطأ مثل 10252 أو ابعت صورة الشاشة")

bot.infinity_polling()
