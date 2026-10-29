import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلا عبدو! ابعتلي رقم السؤال (مثال: 624)")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "624":
        await update.message.reply_text("✅ السؤال 624:\nالحل هو C - التكلفة الثابتة لا تتغير مع الإنتاج")
    else:
        await update.message.reply_text(f"استلمت: {text}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot started...")
app.run_polling()
