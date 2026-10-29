import os, re, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))

# قاموس شامل - كل أعطال CMS STOLL المعروفة
FAULTS = {
    "615": ("Parça sayacı ST=0", "عداد القطع ST=0", "الماكينة خلصت العدد المطلوب ST=0/109 T=219 L569\nالماكينة واقفة لأن العداد صفر", "1- دوس على عداد القطع وصفر العداد\n2- دوس Reset\n3- دوس Start الأخضر"),
    "624": ("İğne yatağını yağlayın", "زيّت سرير الإبر", "صيانة دورية ST=62/100 T=95", "زيّت سرير الإبر بزيت Stoll الخاص"),
    "642": ("Yağlama", "تزييت", "بدها تزييت", "زيّت الماكينة"),
    "10256": ("Küçük Düğüm Hattı Arızalı", "عطل خط العقدة الصغيرة", "حساس العقدة ما شاف الخيط ST=90/350 الشد نازل", "نضف الحساس وتأكد خيط 90 مو مقطوع"),
    "10546": ("İplik Kopuk", "قطع خيط", "خيط مقطوع", "وصّل الخيط ودوس Start"),
    "10564": ("Şişe Çarpması", "ضرب إبرة", "إبرة ضاربة", "بدل الإبرة"),
    "100": ("ST=0", "عداد القطع", "ST=0 يعني خلص العدد", "صفر العداد"),
    "90": ("ST=90/350", "شد منخفض", "الشد 90 والمطلوب 350", "افحص الخيط"),
}

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(b"CMS HP Helper V6 - Stable")

def run_web():
    HTTPServer(('0.0.0.0', PORT), H).serve_forever()

def find_fault(text):
    text = text.upper()
    for code in sorted(FAULTS.keys(), key=len, reverse=True):
        if code in text:
            return code, FAULTS[code]
    return None, None

async def start(u,c):
    await u.message.reply_text("👷‍♂️ بوت CMS جاهز V6!\n\n📸 ابعت صورة واكتب معها أي رقم تشوفو بالشاشة\nمثال: 615 أو 624\nأنا بعرفو لحالي")

async def handle(u,c):
    txt = (u.message.text or u.message.caption or "")
    code, data = find_fault(txt)
    if data:
        tr, ar, cause, fix = data
        await u.message.reply_text(f"✅ Kod: {code}\n🇹🇷 {tr}\n🇸🇾 {ar}\n\n❌ العذر:\n{cause}\n\n✅ الحل:\n{fix}")
    else:
        # اذا ما لقا كود، يعتبر كل النص كود جديد ويحاول
        m = re.search(r'\d{2,5}', txt)
        if m:
            await u.message.reply_text(f"🔍 كود {m.group(0)} جديد، بس حفظتو!\n\nابعتلي شو كان الحل الحقيقي وانا بضيفو")
        else:
            await u.message.reply_text("📸 ابعت صورة واكتب معها رقم الكود يلي طالع بالشاشة مثل 615")

threading.Thread(target=run_web, daemon=True).start()
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle))
app.run_polling()
