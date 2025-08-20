user_id = update.message.from_user.id
    
    cursor.execute(
        "UPDATE users SET premium = 1 WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
    
    await update.message.reply_text(
        "✅ Premium-доступ активовано!\nТепер у тебе безлімітні повідомлення!",
        reply_markup=main_menu()
    )

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("premium", premium))
    app.add_handler(CommandHandler("check_payment", check_payment))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    
    print("🟢 Бот запущено!")
    app.run_polling()

if name == "main":
    main()
