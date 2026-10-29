import os
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from PIL import Image
import io
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

DB_FILE = "codes_db.json"
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}
def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
db = load_db()

SYSTEM_PROMPT = """
انت خبير صيانة ماكينات CMS للخشب، موديل HP.
مهمتك تعطي حل عملي وسريع بالعربي (لهجة سورية بسيطة) لأكواد الأخطاء.
1. اشرح شو يعني الكود بجملة واحدة
2. اعطي 3-4 خطوات عملية للحل من الاسهل للأصعب
3. اذكر الحساسات او القطع يلي لازم تنفحص
خليك عملي ومباشر.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 ابعت صورة لشاشة الخطأ واكتب معها رقم الكود مثل 615\nانا رح اقرأ الصورة واعطيك الحل فوراً بالذكاء الاصطناعي!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        caption = update.message.caption or update.message.text or ""
        match = re.search(r'\d{3,5}', caption)
        code = match.group(0) if match else "unknown"
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        image = Image.open(io.BytesIO(image_bytes))
        await update.message.reply_text(f"🔍 عم حلل الكود {code} ... ثواني")
        if code in db and db[code].get("solution") and not db[code].get("auto_generated"):
            saved_sol = db[code]["solution"]
            prompt = f"{SYSTEM_PROMPT}\nالكود: {code}\nالحل المحفوظ: {saved_sol}\nحلل الصورة واكد الحل."
        else:
            prompt = f"{SYSTEM_PROMPT}\nالكود الجديد: {code}\nحلل الصورة المرفقة والرسالة التركية الظاهرة."
        response = model.generate_content([prompt, image])
        ai_answer = response.text
        if code != "unknown" and code not in db:
            db[code] = {"count": 1, "solution": ai_answer, "auto_generated": True}
            save_db(db)
            header = f"🤖 كود {code} جديد - حل من الذكاء الاصطناعي:\n\n"
        else:
            if code != "unknown":
                db[code]["count"] = db[code].get("count",0)+1
                save_db(db)
            header = f"✅ كود {code} - الحل:\n\n"
        await update.message.reply_text(header + ai_answer)
    except Exception as e:
        logger.error(e)
        await update.message.reply_text(f"صار خطأ: {e}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if len(text) > 20:
        m = re.match(r'^(\d{3,5})\s+(.+)', text, re.DOTALL)
        if m:
            code = m.group(1); sol = m.group(2)
            db[code] = {"count": db.get(code,{}).get("count",0)+1, "solution": sol, "auto_generated": False}
            save_db(db)
            await update.message.reply_text(f"تم حفظ الحل الجديد للكود {code} ✅")
            return
    try:
        prompt = f"{SYSTEM_PROMPT}\nسؤال المستخدم: {text}"
        response = model.generate_content(prompt)
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
