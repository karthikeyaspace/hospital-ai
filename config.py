from dotenv import load_dotenv
import os

load_dotenv()

env = {
    "TELEGRAM_ACCESS_TOKEN": os.getenv("TELEGRAM_ACCESS_TOKEN"),
    "TELEGRAM_BOT_USERNAME": os.getenv("TELEGRAM_BOT_USERNAME"),
    "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
}