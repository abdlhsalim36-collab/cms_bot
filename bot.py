import os, re, threading, base64, requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
GEMINI = os.getenv("GEMINI_API_KEY")
PORT = int(os.getenv("PORT", 10000))

class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"CMS AI Vision Bot LIVE")

def run_web(): HTTPServer(('0.0.0.0', PORT), H).serve_forever()

def ask_gemini(image_bytes, caption):
    if not GEMINI: return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI}"
    b64 = base64.b64encode(image_bytes).decode()
    prompt = f"""
    انت خبير صيانة ماكينات Stoll CMS HP.
    حلل صورة شاشة الماكينة. اقرأ Kod و Uyari Metni و ST و T و L و MSEC.
    اعطيني:
    1- Kod: ...
    2- الترجمة للعربي
    3- شو العذر الحقيقي؟ (ليش واقفة)
    4- الحل خطوة بخطوة بالعربي السوري العامي
    نص المستخدم: {caption}
    """
    data = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
    try:
        r = requests.post(url, json=data, timeout=30).json()
        return r['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"خطأ AI: {e}"

async def start(u,c): await u.message.reply_text("👷‍♂️ بوت CMS صار يشوف!\nابعت أي صورة بدون ما تكتب رقم، أنا بقرأها لحالي بالذكاء الاصطناعي")

async def handle(u,c):
    txt = u.message.text or u.message.caption or ""
    # اذا صورة
    if u.message.photo:
        photo = await u.message.photo[-1].get_file()
        b = await photo.download_as_bytearray()
        if GEMINI:
            await u.message.reply_text("🔍 عم اقرأ الصورة بالذكاء الاصطناعي... ثانية")
            ans = ask_gemini(bytes(b), txt)
            await u.message.reply_text(ans)
        else:
            # بدون AI - نحاول نقرأ الرقم
            m = re.search(r'\d+', txt)
            code = m.group(0) if m else "??"
            await u.message.reply_text(f"⚠️ لسه ما حطيت مفتاح GEMINI_API_KEY\nبس قريت الكود: {code}\n\nاذا بدك يقرأ لحالو بدون كتابة، حط مفتاح Gemini ب Render")
    else:
        await u.message.reply_text(f"اكتب سؤالك أو ابعت صورة\nالنص: {txt}")

threading.Thread(target=run_web, daemon=True).start()
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle))
print("CMS AI Bot Running")
app.run_polling()
