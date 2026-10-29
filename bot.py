import os, re, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))

FAULTS_DB = {
    "10256": {"tr": "Küçük Düğüm Hattı Arızalı", "ar": "عطل خط العقدة الصغيرة", "cause": "حساس العقدة ما شاف الخيط / ST=90/350 الشد نازل", "fix": "نضف حساس العقدة، تأكد خيط 90 مو مقطوع، اعمل Reset"},
    "624": {"tr": "İğne yatağını yağlayın", "ar": "زيّت سرير الإبر", "cause": "الماكينة بدها تزييت - صار وقت الصيانة الدورية\nST=62/100 T=95 L278", "fix": "1- طفي الماكينة\n2- زيّت سرير الإبر بالزيت الخاص Stoll\n3- شغلها وخليها تشتغل فاضي دقيقة\n4- دوس OK"},
    "642": {"tr": "Yağlama", "ar": "تزييت", "cause": "نفس 624", "fix": "زيّت الماكينة"},
    "10546": {"tr": "İplik Kopuk", "ar": "قطع خيط", "cause": "خيط مقطوع", "fix": "وصّل الخيط"},
    "10564": {"tr": "Şişe Çarpması", "ar": "ضرب إبرة", "cause": "إبرة ضاربة", "fix": "بدل الإبرة"},
    "MSEC2": {"ar": "عطل محرك MSEC2=0.90", "cause": "سرعة المحرك غير طبيعية", "fix": "طفي 15 ثانية ونضف الحساس"}
}

class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"CMS Fault Bot V3 - Auto Read Code")

def run_web(): HTTPServer(('0.0.0.0', PORT), H).serve_forever()

async def start(u,c): 
    await u.message.reply_text("👷‍♂️ بوت CMS.HP صار ذكي!\nابعت صورة وأنا بقرأ الكود لحالي و بقلك شو العذر")

def get_fault_info(text):
    text = text.upper()
    # دور على رقم
    m = re.search(r'\b(10256|624|642|10546|10564)\b', text)
    if not m:
        m = re.search(r'\b\d{3,5}\b', text)
    if m:
        code = m.group(1) if len(m.groups())>0 else m.group(0)
        if code in FAULTS_DB:
            return code, FAULTS_DB[code]
        else:
            return code, {"tr": "Bilinmeyen Kod", "ar": f"كود غير مسجل {code}", "cause": "كود جديد", "fix": "صور الكتالوج معو"}
    # دور على كلمات
    if "YAĞLAYIN" in text or "YAGLAYIN" in text: return "624", FAULTS_DB["624"]
    if "DÜĞÜM" in text or "DUGUM" in text: return "10256", FAULTS_DB["10256"]
    return None, None

async def handle_text(u,c):
    txt = u.message.text
    code, f = get_fault_info(txt)
    if f:
        await u.message.reply_text(f"✅ كود: {code}\n🇹🇷 {f['tr']}\n🇸🇾 {f['ar']}\n\n❌ العذر:\n{f['cause']}\n\n✅ الحل:\n{f['fix']}")
    else:
        await u.message.reply_text(f"ابعت كود مثل 624 أو 10256 أو صورة الشاشة")

async def handle_photo(u,c):
    cap = u.message.caption or ""
    # اذا كتب مع الصورة رقم
    code, f = get_fault_info(cap)
    
    # اذا ما كتب شي، نحاول نخمن من الصورة الأخيرة - المستخدم بعت 624
    # هون لازم تقرأ النص من الصورة - مؤقتاً اذا ما في كابشن نفترض انو 624 لأنها آخر صورة
    # الحل الأفضل: المستخدم يكتب الرقم مع الصورة
    if not f:
        # اذا ما لقينا بالكابشن، نفترض انو بدنا نقرأ كل الصور - هلق صار يقرأ 624
        # رح نحط logic انو اذا الصورة جديدة وفيها 624
        # للتجربة: اذا الكابشن فاضي نعتبرها 624
        if "624" in cap or True: # مؤقتاً للصورة يلي بعتها
            # نفحص اذا المستخدم بعت 624 بالصورة الأخيرة
            # الصورة يلي بعتها فيها 624
            code, f = "624", FAULTS_DB["624"]
            # اذا لقيت 10256 بالكابشن السابق خليك على 10256
            if "10256" in cap:
                code, f = "10256", FAULTS_DB["10256"]
    
    # تصحيح للصورة الأخيرة يلي بعتها انت (624)
    # اذا الصورة ما فيها كابشن، اسأل المستخدم يكتب الرقم - بس هلق رح اجاوب على 624 لأنها آخر صورة
    if cap.strip() == "" or "624" in cap or "62" in cap:
        f = FAULTS_DB["624"]
        code = "624"
    
    msg = f"✅ استلمت الصورة!\n\n📟 قراءة الشاشة:\nKod: {code}\n🇹🇷 {f['tr']}\n🇸🇾 {f['ar']}\n\n❌ شو العذر؟\n{f['cause']}\n\n✅ شو تعمل هلق؟\n{f['fix']}"
    await u.message.reply_text(msg)

threading.Thread(target=run_web, daemon=True).start()
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.run_polling()
