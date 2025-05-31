from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "7714246447:AAHeDU2JfjqQs1f26TOnQDvgqTT5Qg5Xm14"

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я бот, который умеет работать с файлами. Команды:\n"
                                  "/start - начать\n"
                                  "/help - помощь\n"
                                  "/readfile - прочитать файл text.txt\n"
                                  "/echo [текст] - повторить текст")

# Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Доступные команды:\n"
                                  "/start - начать\n"
                                  "/help - помощь\n"
                                  "/readfile - прочитать файл\n"
                                  "/echo [текст] - повторить текст")

# Обработчик команды /echo
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = ' '.join(context.args)
    if text:
        await update.message.reply_text(f"Вы сказали: {text}")
    else:
        await update.message.reply_text("Напишите что-нибудь после /echo")

# Обработчик команды /readfile
async def read_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        with open('AI/summary.txt', 'r', encoding='utf-8') as file:
            content = file.read()
            if content:
                await update.message.reply_text(f"Содержимое файла:\n{content}")
            else:
                await update.message.reply_text("Файл пуст")
    except FileNotFoundError:
        await update.message.reply_text("Файл summary.txt не найден")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

# Обработчик обычных сообщений
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Я не понимаю. Введите /help для списка команд")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("echo", echo))
    application.add_handler(CommandHandler("readfile", read_file))

    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    print("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()