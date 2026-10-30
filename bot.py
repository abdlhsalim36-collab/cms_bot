import os, json, logging, re, io, threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from PIL import Image

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot is Live!"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def ask_gemini(prompt_or_parts):
    # جوجل غيرت الاسماء، منجرب كل الموديلات الجديدة
    models_to_try = [
        "gemini-3.8-flash",
        "gemini-2.5-flash",
        "gemini-flash-latest",
        "gemini-2.0-flash",
        "gemini-1.5-flash"
    ]
    for m_name in models_to_try:
        try:
            print(f"Trying model: {m_name}")
            resp = client.models.generate_content(model=m_name, contents=prompt_or_parts)
            print(f"Success with: {m_name}")
            return resp.text
        except Exception as e:
            print(f"Failed {m_name}: {e}")
            continue
    raise Exception("كل الموديلات فشلت - راجع API Key")

DB_FILE = "codes_db.json"
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}
def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, ensure_ascii=False, indent=2)
db = load_db()

SYSTEM_PROMPT = "انت خبير صيانة ماكينات CMS للخشب التركية. اشرح الخطأ بلهجة سورية بسيطة واعطي 4 خطوات عملية للحل."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 ابعت صورة الخطأ واكتب معها بالتعليق رقم الكود مثل 4339")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        caption = update.message.caption or ""
        m = re.search(r'\d{3,5}', caption)
        code = m.group(0) if m else "4339"
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        image = Image.open(io.BytesIO(image_bytes))
        await update.message.reply_text(f"🔍 عم حلل الكود {code}...")
        ans = ask_gemini([f"{SYSTEM_PROMPT} الكود: {code}", image])
        db[code] = {"solution": ans}
        save_db(db)
        await update.message.reply_text(f"✅ كود {code}:\n\n{ans}")
    except Exception as e:
        logger.error(e, exc_info=True)
        await update.message.reply_text(f"خطأ: {e}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ans = ask_gemini(f"{SYSTEM_PROMPT}\n{update.message.text}")
        await update.message.reply_text(ans)
    except Exception as e:
        await update.message.reply_text(f"خطأ: {e}")

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
