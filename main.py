from telegram.ext import CommandHandler, Updater, CallbackQueryHandler
from dotenv import load_dotenv
from handlers.button import button
from handlers.fetch_products import fetch_products
from handlers.start import start
import os

# Load environment variables
load_dotenv(os.path.join('config', '.env'))

# Get bot token from environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Initialize bot and handlers
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Add handlers
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('fetch', fetch_products))
dispatcher.add_handler(CallbackQueryHandler(button))

# Start bot
updater.start_polling()
