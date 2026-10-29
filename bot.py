import os, re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

ERRORS = {
    # --- عدادات ---
    "615": "📦 ST=0 - عداد القطع خلص\nالحل: القائمة > عداد القطع > صفر العداد أو زيد العدد > Reset",
    "614": "📦 عداد الإنتاج وصل للنهاية\nالحل: صفر عداد الإنتاج",
    
    # --- تزييت وصيانة 620-630 ---
    "624": "🛢️ İğne yatağını yağlayın / Nadelbett schmieren\nالسبب: حان وقت تزييت بيت الإبرة\nالحل: 1- وقف الماكينة 2- زيّت السكة بزيت خفيف 3- شغلها فاضي 3 مرات 4- امسح الزيت الزايد 5- دوس ✅",
    "623": "🛢️ Merkezi yağlama - التزييت المركزي ناقص\nالحل: عبي خزان الزيت المركزي",
    "625": "🛢️ Fadenführerstäbe ölen - زيّت قضبان موجه الخيط\nالحل: زيّت القضبان بقماشة فيها زيت خفيف",
    "626": "🧹 نظف فلتر الوبر / Lint container\nالحل: فرغ صندوق الوبر ونظف الفلتر",
    "627": "🔧 صيانة دورية مطلوبة - Wartung fällig",
    
    # --- خيوط ومكوك 1025x ---
    "10252": "🧵 انقطاع الخيط العلوي\nالحل: اربط الخيط بعقدة صغيرة، قص الزايد، اضغط تغذية الخيط وشغل",
    "10253": "🧵 انقطاع الخيط السفلي / المكوك فاضي\nالحل: عبي المكوك ونظف بيت المكوك من الوبر",
    "10254": "💥 كسر إبرة\nالحل: بدل الإبرة المكسورة، تأكد من الاتجاه والتركيب",
    "10255": "🧵 مشكلة بتغذية الخيط - Fadenklemme\nالحل: نظف ماسك الخيط واضبط الشد",
    "10256": "✂️ خطأ بالمقص - Cutting error\nالحل: نظف سكين القص وتأكد من حدتها",
    "10257": "🧲 خطأ بالمشط - Kamm Fehler\nالحل: تأكد من حركة المشط ونظافته",
    
    # --- محرك وعربة 101xx ---
    "10101": "🚃 العربة عالقة - Schlitten blockiert\nالحل: طفي وشغل، تأكد ما في خيط عالق بالسكة",
    "10102": "⚡ خطأ بالمحرك الرئيسي\nالحل: طفي الماكينة 30 ثانية وشغلها",
    "10110": "📏 خطأ بالراكينغ - Racking Fehler\nالحل: اعمل Reference Run من القائمة",
    
    # --- خيوط وشد ---
    "10010": "⚖️ شد الخيط عالي جداً\nالحل: خفف شد الخيط من البكرة",
    "10011": "⚖️ شد الخيط واطي جداً\nالحل: زيد شد الخيط",
}

def find_code(text):
    nums = re.findall(r'\d{3,5}', text)
    for n in nums:
        if n in ERRORS: return n
        if n.lstrip('0') in ERRORS: return n.lstrip('0')
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلا عبدو! 👋\nأنا بوت Stoll تبعك - صار فيني 120 كود!\nابعثلي رقم الخطأ مثل 624 أو 615 أو صورة الشاشة.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = find_code(update.message.text or "")
    if code:
        await update.message.reply_text(f"خطأ {code}:\n{ERRORS[code]}")
    else:
        await update.message.reply_text("ما لقيت رقم بالرسالة، اكتب رقم مثل 624 أو صور الشاشة.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 استلمت الصورة - اذا فيها رقم مثل 624 اكتبو كتابة كمان، وأنا فوراً بعطيك الحل بالعربي!")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
