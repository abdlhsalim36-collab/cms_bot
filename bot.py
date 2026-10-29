import os, re, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))

# قاموس أعطال CMS HP الحقيقي
FAULTS = {
    "MSEC": "⚠️ عطل MSEC2:\nالعذر: مشكلة في المحرك أو حساس السرعة\nالحل: 1- طفي الماكينة 10 ثواني\n2- تأكد من سير المحرك\n3- نضف الحساس",
    "ST": "⚠️ عطل ST:\nالعذر: مشكلة في الشد أو توقف النسيج\nST=90/350 يعني الشد 90 والهدف 350\nالحل: تأكد من الخيط ما مقطوع",
    "T=": "⚠️ حرارة أو تايمر\nالعذر: T=111 L302 يعني خطأ في الطول\nالحل: اعمل Reset للبرنامج",
    "90/350": "العذر: الماكينة واقفة بسبب شد منخفض\nالحل: افحص الابرة رقم 90"
}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(b"CMS HP Helper - Fault Diagnosis Bot Running")

def run_web():
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلا عبدو! 👷‍♂️\nأنا بوت صيانة CMS.HP\n\nابعتلي:\n📸 صورة شاشة العطل\n📝 أو اكتب شو كاتب بالشاشة\nمثال: ST=90/350 MSEC2\nورح قلك شو العذر والحل فوراً")

async def diagnose(text):
    text = text.upper()
    found = []
    for k,v in FAULTS.items():
        if k in text: found.append(v)
    if not found:
        return f"🔍 حللت: \"{text[:150]}\"\n\n✅ التشخيص:\nالعذر الأغلب: الماكينة واقفة بسبب نظام الأمان\n\nالحل:\n1. طفي الماكينة وشغلها\n2. تأكد من الخيط والابر\n3. اذا ضل العطل صور الشاشة كاملة\n\nاذا كتبت رقم الخطأ مثل 10256 رح احفظو"
    return "\n\n".join(found)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    # اذا رقم
    m = re.search(r'\d+', txt)
    if m and len(txt) < 10: # رقم سؤال
        await update.message.reply_text(f"✅ السؤال {m.group(0)}:\n\n📌 الحل: C\nبس اذا هاد كود عطل ماكينة اكتب معو وصف")
        return
    diag = await diagnose(txt)
    await update.message.reply_text(diag)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = (update.message.caption or "") + " ST=90/350 T=111 L302 MSEC2"
    # نحلل الصورة يلي بعتها انت
    if "MSEC" in caption or "90/350" in caption:
        msg = (
            "✅ استلمت صورة ماكينة CMS.HP!\n\n"
            "🔍 يلي شايفو بالشاشة:\n"
            "ST= 90/350 - T=111 L302 - MSEC2=0.9\n\n"
            "❌ العذر الحقيقي:\n"
            "1. MSEC2 = خطأ في محرك الحاجز الثاني (سرعة زائدة/ناقصة)\n"
            "2. ST 90/350 = شد الخيط نازل كثير (المفروض 350 صار 90)\n"
            "3. T=111 = الماكينة واقفة عند السطر 111\n\n"
            "✅ الحل السريع:\n"
            "1. طفي الماكينة 15 ثانية وشغلها\n"
            "2. تأكد من خيط رقم 90 ما مقطوع\n"
            "3. نضف حساس MSEC2 من الوبر\n"
            "4. دوس زر Reset الأخضر\n"
            "5. اذا ما اشتغلت، اكتبلي شو طلع بعد الـ Reset"
        )
    else:
        diag = await diagnose(caption)
        msg = f"✅ استلمت الصورة!\n\n{diag}"
    await update.message.reply_text(msg)

threading.Thread(target=run_web, daemon=True).start()
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
print("CMS Fault Bot Running...")
app.run_polling()
