import os, re, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))

FAULTS_DB = {
    "10256": {"tr": "Küçük Düğüm Hattı Arızalı", "ar": "عطل خط العقدة الصغيرة", "cause": "حساس العقدة ما شاف الخيط / ST=90/350 الشد نازل", "fix": "1- نضف حساس العقدة\n2- تأكد خيط 90 مو مقطوع\n3- اعمل Reset"},
    "624": {"tr": "İğne yatağını yağlayın", "ar": "زيّت سرير الإبر", "cause": "الماكينة بدها تزييت ST=62/100 T=95", "fix": "زيّت سرير الإبر بزيت Stoll"},
    "615": {"tr": "Parça sayacı ST=0", "ar": "عداد القطع ST=0", "cause": "الماكينة خلصت العدد المطلوب ST=0/109 T=219 L569\nالماكينة واقفة لأن العداد صفر", "fix": "1- دوس على عداد القطع وصفر العداد\n2- أو دوس Reset للعداد\n3- دوس Start الأخضر"},
    "642": {"tr": "Yağlama", "ar": "تنبيه تزييت", "cause": "تنبيه تزييت", "fix": "زيّت الماكينة"},
}

class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"CMS Bot V5 - All codes included")

def run_web(): HTTPServer(('0.0.0.0', PORT), H).serve_forever()

async def start(u,c): await u.message.reply_text("👷‍♂️ بوت CMS جاهز!\nابعت صورة واكتب رقمها مثل 615")

async def handle(u,c):
    txt = (u.message.text or u.message.caption or "")
    m = re.search(r'\d+', txt)
    if not m:
        await u.message.reply_text("اكتب رقم الكود مثل 615 مع الصورة")
        return
    code = m.group(0)
    f = FAULTS_DB.get(code)
    if f:
        await u.message.reply_text(f"✅ Kod: {code}\n🇹🇷 {f['tr']}\n🇸🇾 {f['ar']}\n\n❌ العذر:\n{f['cause']}\n\n✅ الحل:\n{f['fix']}")
    else:
        await u.message.reply_text(f"⚠️ كود {code} جديد - ضيفو للقاموس:\n{txt}")

threading.Thread(target=run_web, daemon=True).start()
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle))
print("CMS V5 Running...")
app.run_polling()
