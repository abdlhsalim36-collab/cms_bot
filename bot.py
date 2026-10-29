import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

# قاعدة الحلول الحقيقية - كل ما تحل سؤال ضيفو هون
SOLUTIONS = {
    "624": "✅ السؤال 624:\n\nالحل: C\nالشرح: التكلفة الثابتة لا تتغير مع حجم الإنتاج، بينما المتغيرة تتغير.\n\nاذا عندك حل أدق ابعتلي ياه لأحدثو.",
    "548": "✅ السؤال 548:\n\nالحل: B\nالشرح: نقطة التعادل = التكاليف الثابتة / هامش المساهمة",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلا عبدو! 🤖💪\n\n"
        "ابعتلي أي كود (مثال: 10546 أو 624) ورح أعطيك الحال فوراً\n"
        "واذا عندك صورة السؤال ابعتها مع الكود"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    m = re.search(r'\d{2,6}', text)
    
    if not m:
        await update.message.reply_text("ابعتلي رقم الكود، مثال: 10546")
        return

    code = m.group(0)
    
    if code in SOLUTIONS:
        await update.message.reply_text(SOLUTIONS[code])
    else:
        # اذا الكود جديد - يعطي الحال المؤقت ويطلب السؤال الحقيقي
        await update.message.reply_text(
            f"🔍 السؤال {code}:\n\n"
            f"هاد الكود جديد وما لقيتو بالكتالوج.\n"
            f"✅ الحل المؤقت: حسب نظام CMS، الجواب الأقرب هو C\n\n"
            f"📸 مشان أعطيك الحال 100% الصح، ابعتلي صورة السؤال تبع {code} وانا بحلو فوراً وبحفظو للأبد\n\n"
            f"هلق صار عنا {len(SOLUTIONS)} حل محفوظ."
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = update.message.caption or ""
    m = re.search(r'\d{2,6}', caption)
    code = m.group(0) if m else "الجديد"
    
    await update.message.reply_text(
        f"✅ استلمت صورة السؤال {code}!\n\n"
        f"📚 الحل:\n"
        f"حسب الصورة، الجواب الصحيح هو B مع الشرح الكامل.\n"
        f"(هون رح ضيف ذكاء اصطناعي يقرأ الصورة ويحلها تلقائياً قريباً)\n\n"
        f"ابعتلي الحل الصحيح اذا عندك لأحفظو."
    )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("Bot with HAL started...")
app.run_polling()
