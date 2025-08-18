from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import openai
import random

TELEGRAM_TOKEN = "TELEGRAM_TOKEN"
OPENAI_API_KEY = "OPENAI_API_KEY"
openai.api_key = OPENAI_API_KEY

REACTIONS = [
    "😎 Легкотня! Ось відповідь:",
    "🧠 Це було цікаво! Відповідь нижче:",
    "💪 Зараз вирішимо!",
    "🔥 Лови відповідь!",
    "✅ Готово:"
]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ти шкільний помічник. Відповідай чітко, просто і з приколом."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response["choices"][0]["message"]["content"]
        intro = random.choice(REACTIONS)
        await update.message.reply_text(f"{intro}\n\n{reply}", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text("Упс! Щось пішло не так 🧨")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
