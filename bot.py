import os
import json
import logging
import re
import io
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types
from PIL import Image

# Flask
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

client = genai.Client(api_key=GEMINI_API_KEY)

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

SYSTEM_PROMPT = "انت خبير صيانة ماكينات CMS للخشب التركية. اشرح الخطأ بلهجة سورية بسيطة واعطي 4 خطوات عملية للحل. الكود بالصورة 10252 يعني: İplik Kopusu veya Büyük Düğüm = قطع الخيط او عقدة كبيرة."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 ابعت صورة الخطأ واكتب معها بالتعليق رقم الكود")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        caption = update.message.caption or ""
        m = re.search(r'\d{3,5}', caption)
        code = m.group(0) if m else caption or "10252"
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        image = Image.open(io.BytesIO(image_bytes))
        
        await update.message.reply_text(f"🔍 عم حلل الكود {code}...")

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                f"{SYSTEM_PROMPT} الكود: {code}",
                image
            ]
        )
        ans = response.text
        db[code] = {"solution": ans}
        save_db(db)
        await update.message.reply_text(f"✅ كود {code}:\n\n{ans}")
    except Exception as e:
        logger.error(e, exc_info=True)
        await update.message.reply_text(f"خطأ: {e}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{SYSTEM_PROMPT}\n{update.message.text}"
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"خطأ: {e}")

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Bot Started")
    app.run_polling()

if __name__ == "__main__":
    main()
