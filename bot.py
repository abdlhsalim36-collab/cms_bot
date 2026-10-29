import os
import json
import logging
import re
import io
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN or not GEMINI_API_KEY:
    raise ValueError("BOT_TOKEN or GEMINI_API_KEY missing!")

genai.configure(api_key=GEMINI_API_KEY)
# الموديل الجديد الشغال
model = genai.GenerativeModel("gemini-2.0-flash")

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

SYSTEM_PROMPT = """
انت خبير صيانة ماكينات CMS للخشب موديل HP.
عندك صورة لشاشة الخطأ، اقرأ منها كود الخطأ ورسالة الخطأ التركية.

مهمتك تعطي حل عملي وسريع بالعربي بلهجة سورية بسيطة:

1. اشرح شو يعني الكود بجملة
2. شو سبب "Tarak kapak metal plakasi bastirildi" ؟
3. اعطي 4 خطوات عملية للحل من الاسهل للأصعب
4. اذكر الحساسات يلي لازم تنفحص

خليك عملي ومباشر، لا تكتب نظري كثير.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 ابعت صورة الشاشة واكتب معها بالتعليق رقم الكود مثل 4339\nانا رح اقرأ الصورة واعطيك الحل فوراً!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        caption = update.message.caption or ""
        match = re.search(r'\d{3,5}', caption)
        code = match.group(0) if match else "4339"
        
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        image = Image.open(io.BytesIO(image_bytes))

        await update.message.reply_text(f"🔍 عم حلل الكود {code} ... ثواني")

        prompt = f"{SYSTEM_PROMPT}\nالكود المتوقع: {code}\nحلل الصورة واعطي الحل."

        response = model.generate_content([prompt, image])
        ai_answer = response.text

        if code not in db:
            db[code] = {"count": 1, "solution": ai_answer, "auto_generated": True}
            save_db(db)
        
        await update.message.reply_text(f"✅ كود {code} - الحل:\n\n{ai_answer}")

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"صار خطأ: {e}\nجرب تبعت الصورة مرة تانية ومعها رقم الكود بالتعليق.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if len(text) > 20:
        m = re.match(r'^(\d{3,5})\s+(.+)', text, re.DOTALL)
        if m:
            code = m.group(1)
            sol = m.group(2)
            db[code] = {"count": db.get(code,{}).get("count",0)+1, "solution": sol, "auto_generated": False}
            save_db(db)
            await update.message.reply_text(f"تم حفظ الحل للكود {code} ✅")
            return
    try:
        response = model.generate_content(f"{SYSTEM_PROMPT}\nسؤال المستخدم: {text}")
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"خطأ: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
