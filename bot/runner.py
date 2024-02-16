"""
Runner module

This module initializes and runs the Telegram Bot, registering message and command handlers.
"""

import os

from dotenv import load_dotenv
from telegram.ext import Updater

from bot.handlers import clear_handler, message_handler, scoreboard_handler

# Load environment variables from .env file
load_dotenv()


def run_bot():
    """
    Initialize and run the Telegram Bot.

    Creates an Updater instance with the provided Telegram Bot token,
    registers message and command handlers, and starts polling for updates.
    """

    updater = Updater(token=os.getenv("TELEGRAM_BOT_TOKEN"), use_context=True)
    dispatcher = updater.dispatcher

    # Register message/command handlers
    dispatcher.add_handler(message_handler)
    dispatcher.add_handler(clear_handler)
    dispatcher.add_handler(scoreboard_handler)

    # Start the bot
    updater.start_polling(clean=True)
    updater.idle()
