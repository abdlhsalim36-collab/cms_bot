import os
import json
import logging
import re
import io
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from PIL import Image

app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Bot is Live!"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# جرب الموديلات بالترتيب من الأحدث للأقدم
def get_model():
    for name in ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash-exp", "gemini-flash-latest"]:
        try:
            m = genai.GenerativeModel(name)
            # اختبار سريع
            m.generate_content("hi")
            print(f"Using model: {name}")
            return m
        except Exception as e:
            print(f"Model {name} failed: {e}")
            continue
    return genai.GenerativeModel("gemini-1.5-flash")

model = get_model()

DB_FILE = "codes_db.json"
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}
def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
db = load_db()

SYSTEM_PROMPT = "انت خبير صيانة ماكينات CMS للخشب. اشرح الخطأ بلهجة سورية بسيطة واعطي 4 خطوات عملية للحل."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 ابعت صورة الخطأ واكتب معها 4339")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        caption = update.message.caption or ""
        m = re.search(r'\d{3,5}', caption)
        code = m.group(0) if m else "4339"
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        image = Image.open(io.BytesIO(image_bytes))
        await update.message.reply_text(f"🔍 عم حلل الكود {code}...")
        response = model.generate_content([f"{SYSTEM_PROMPT} الكود: {code}. الصورة فيها خطأ Tarak kapak metal plakasi.", image])
        ans = response.text
        db[code] = {"count":1, "solution":ans}
        save_db(db)
        await update.message.reply_text(f"✅ كود {code}:\n\n{ans}")
    except Exception as e:
        logger.error(e)
        await update.message.reply_text(f"خطأ: {e}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        resp = model.generate_content(f"{SYSTEM_PROMPT}\n{update.message.text}")
        await update.message.reply_text(resp.text)
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
