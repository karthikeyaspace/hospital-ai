from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from config import env
import ai

TELEGRAM_ACCESS_TOKEN = env['TELEGRAM_ACCESS_TOKEN']
TELEGRAM_BOT_USERNAME = env['TELEGRAM_BOT_USERNAME']


# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("A Swiggles Bot, send me a message to get started!")


async def welp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welp, I'm just a bot. I can't do much. But I can help you with some stuff. Just send me a message to get started!")


# Messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text

    print(f"User ({update.message.chat.id}) in {message_type}: {text}")

    if message_type == "private":
        response = await ai.respond(text)
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("I'm sorry, I only work in private chats.")


# Error handler
async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"An error occurred: {context.error}")
    await update.message.reply_text("An error occurred. Please try again later.")


# Main
def main():
    print("Starting bot...")
    app = Application.builder().token(TELEGRAM_ACCESS_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", welp))

    # Message handler
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))

    # Error handler
    app.add_error_handler(handle_error)

    print("Polling...")
    app.run_polling(poll_interval=3)


if __name__ == "__main__":
    main()
