from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import sqlite3
import datetime
import os
import openai

TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Додаємо ключ OpenAI

openai.api_key = OPENAI_API_KEY

conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    message_count INTEGER DEFAULT 0,
    premium INTEGER DEFAULT 0,
    last_reset DATE
)''')
conn.commit()

def main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📚 Домашка"), KeyboardButton("📝 Контрольна")],
        [KeyboardButton("💬 Чат з AI"), KeyboardButton("ℹ️ Про бота")],
        [KeyboardButton("💳 Оформити підписку")]
    ], resize_keyboard=True)

def check_message_limit(user_id):
    today = datetime.date.today().isoformat()
    cursor.execute("SELECT last_reset, message_count, premium FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if not result:
        cursor.execute("INSERT INTO users (user_id, message_count, premium, last_reset) VALUES (?, 0, 0, ?)", (user_id, today))
        conn.commit()
        return True
    last_reset, count, premium = result
    if premium == 1:
        return True
    if last_reset != today:
        cursor.execute("UPDATE users SET message_count = 0, last_reset = ? WHERE user_id = ?", (today, user_id))
        conn.commit()
        return True
    if count >= 3:
        return False
    return True

def update_message_count(user_id):
    cursor.execute("UPDATE users SET message_count = message_count + 1 WHERE user_id = ?", (user_id,))
    conn.commit()

async def ask_ai(question):
    """Функція для спілкування з AI"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ти дружній шкільний помічник. Відповідай українською мовою. Допомагай школярам з навчанням, домашками та життєвими порадами. Будь позитивним і підтримуючим."},
                {"role": "user", "content": question}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Помилка AI: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    check_message_limit(user_id)
    await update.message.reply_text(
        "👋 Привіт! Я твій шкільний помічник з AI!\nОбери потрібну опцію:",
        reply_markup=main_menu()
    )

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if not check_message_limit(user_id):
        await update.message.reply_text(
            "🚫 Ліміт повідомлень вичерпано!\n💳 Оформіть підписку за $5 - /premium",
            reply_markup=main_menu()
        )
        return
        
    update_message_count(user_id)
    
    text = update.message.text
    if text == "📚 Домашка":
        response = "📌 Домашні завдання:\n- Математика: стор. 45\n- Література: твір на п'ятницю"
    elif text == "📝 Контрольна":
        response = "📅 Найближчі контролі:\n- Понеділок: Алгебра\n- Середа: Історія"
    elif text == "💬 Чат з AI":
        response = "💬 Напиши своє питання прямо тут! Я відповім за допомогою AI 🤖"
    elif text == "ℹ️ Про бота":
        response = "🤖 Шкільний помічник v3.0\nЗ AI-асистентом!\nСтворено для зручності учнів!"
    elif text == "💳 Оформити підписку":
        response = "💳 Преміум-підписка ($5/місяць):\n- Безлімітні повідомлення\n- Пріоритетна підтримка\n- Необмежений доступ до AI\n\nОформіть: /premium"
    else:
        # Якщо це не кнопка, а звичайне повідомлення - відправляємо AI
        ai_response = await ask_ai(text)
        response = f"🤖 AI-помічник:\n{ai_response}"
    
    await update.message.reply_text(response, reply_markup=main_menu())

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await update.message.reply_text(
        "💳 Преміум-підписка ($5/місяць)\n\nЩо отримуєш:\n"
        "✅ Безлімітні повідомлення\n"
        "✅ Пріоритетна підтримка\n"
        "✅ Необмежений доступ до AI-чату\n\n"
        "Для оплати напиши: @твій_нікнейм\n"
        "Після оплати натисни /check_payment",
        reply_markup=main_menu()
    )

async def check_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    cursor.execute("UPDATE users SET premium = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    await update.message.reply_text(
        "✅ Premium-доступ активовано!\nТепер у тебе безлімітні повідомлення та доступ до AI!",
        reply_markup=main_menu()
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("premium", premium))
    app.add_handler(CommandHandler("check_payment", check_payment))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    print("🟢 Бот запущено з AI!")
    app.run_polling()

if __name__ == "__main__":
    main()
