import os, re, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))

FAULTS_DB = {
    "10256": {"tr": "Küçük Düğüm Hattı Arızalı", "ar": "عطل خط العقدة الصغيرة", "cause": "حساس العقدة ما شاف الخيط - ST=90/350 الشد نازل", "fix": "1- نضف حساس العقدة من الوبر\n2- تأكد خيط 90 مو مقطوع\n3- اعمل Reset"},
    "624": {"tr": "İğne yatağını yağlayın", "ar": "زيّت سرير الإبر", "cause": "الماكينة بدها تزييت - صيانة دورية ST=62/100", "fix": "زيّت سرير الإبر بزيت Stoll الخاص وشغلها فاضي دقيقة"},
    "615": {"tr": "Parça sayacı ST=0", "ar": "عداد القطع ST=0", "cause": "عداد القطع صفر - الماكينة خلصت العدد المطلوب ST=0/109 T=219 L569", "fix": "1- دوس على عداد القطع وصفر العداد\n2- أو زيد العدد المطلوب\n3- دوس Start"},
    "642": {"tr": "Yağlama Uyarısı", "ar": "تنبيه تزييت", "cause": "بدها تزييت", "fix": "زيّت الماكينة"},
    "10546": {"tr": "İplik", "ar": "خيط", "cause": "مشكلة خيط", "fix": "افحص الخيط"},
}

class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"CMS Bot V4 - Write code in caption!")

def run_web(): HTTPServer(('0.0.0.0', PORT), H).serve_forever()

async def start(u,c): await u.message.reply_text("👷‍♂️ بوت CMS.HP\n\n📸 طريقة الاستخدام الصح:\nابعت الصورة واكتب معها رقم الكود بالتعليق\nمثال: تبعت الصورة وتكتب تحتها 615\n\nورح قلك شو العذر والحل فوراً")

async def handle_text(u,c):
    txt = u.message.text
    m = re.search(r'\d+', txt)
    if not m: await u.message.reply_text("اكتب رقم العطل مثل 615"); return
    code = m.group(0)
    f = FAULTS_DB.get(code)
    if f: await u.message.reply_text(f"✅ كود: {code}\n🇹🇷 {f['tr']}\n🇸🇾 {f['ar']}\n\n❌ العذر:\n{f['cause']}\n\n✅ الحل:\n{f['fix']}")
    else: await u.message.reply_text(f"كود {code} جديد، ابعت صورة الشاشة مع الكود {code} مشان احفظو")

async def handle_photo(u,c):
    cap = u.message.caption or ""
    m = re.search(r'\d+', cap)
    if not m:
        await u.message.reply_text("⚠️ استلمت الصورة بس ما عرفت الكود!\n\nارجع ابعت نفس الصورة واكتب معها الرقم بالتعليق (caption)\nمثال: 615\n\nشايف الصورة الجديدة فيها 615 - اكتب 615 معها")
        return
    code = m.group(0)
    f = FAULTS_DB.get(code)
    if not f: f = {"tr": f"Kod {code}", "ar": f"كود {code}", "cause": "كود جديد", "fix": "صورلي الكتالوج"}
    await u.message.reply_text(f"✅ استلمت الصورة!\n\n📟 Kod: {code}\n🇹🇷 {f['tr']}\n🇸🇾 {f['ar']}\n\n❌ شو العذر؟\n{f['cause']}\n\n✅ شو تعمل هلق؟\n{f['fix']}")

threading.Thread(target=run_web, daemon=True).start()
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.run_polling()
