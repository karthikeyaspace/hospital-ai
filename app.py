from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from config import env
from ai import AI

TELEGRAM_ACCESS_TOKEN = env['TELEGRAM_ACCESS_TOKEN']
TELEGRAM_BOT_USERNAME = env['TELEGRAM_BOT_USERNAME']


class Bot:
    def __init__(self):
        self.app = ApplicationBuilder().token(
            TELEGRAM_ACCESS_TOKEN).read_timeout(30).write_timeout(30).build()
        self.ai = AI()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_message = (
            "Welcome to Swiggles Hospital!\n\n"
            "I can help you with:\n"
            "1. Booking appointments - /bookappointment\n"
            "2. Getting medical reports - /getreport\n"
            "3. Reporting emergencies - /reportemergency\n\n"
            "4. Just type of your query and I'll do my best to help you.\n\n"
            "Type /help for more details."
        )
        await update.message.reply_text(welcome_message)

    # todo - usage of commands(interactive manner)

    async def book_appointment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Please provide the time of the appointment.")

    async def get_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Please provide the patient ID.")

    async def report_emergency(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Please provide the details of the emergency.")

    # handling general user message - not commands

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message_type = update.message.chat.type
        text = update.message.text
        id = update.message.chat.id

        print(f"User ({id}) in {message_type}: {text}")

        if message_type == "private":
            response = await self.ai.interact(str(id), text)
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("I'm sorry, I only work in private chats.")

    # error handler - mainly due to network or server
    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"An error occurred @app.py.handle_error: {context.error}")
        await update.message.reply_text("An error occurred. Please try again later.")

    def setup_handlers(self):
        # Command handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.start))
        self.app.add_handler(CommandHandler(
            "bookappointment", self.book_appointment))
        self.app.add_handler(CommandHandler("getreport", self.get_report))
        self.app.add_handler(CommandHandler(
            "emergency", self.report_emergency))

        # Message handler
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Error handler
        self.app.add_error_handler(self.handle_error)

    def start(self):
        print("Starting bot...")
        self.setup_handlers()
        print("Polling...")
        self.app.run_polling(poll_interval=3)


if __name__ == "__main__":
    bot = Bot()
    bot.start()
