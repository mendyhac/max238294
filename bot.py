from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8309441924:AAH3x0Hpk2eZtZDXgjltDyh6YSckN0wpoE8" 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Бот живе! Напиши /help")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
print("🟢 Бот запущено! Чекаю повідомлень...")
app.run_polling()
