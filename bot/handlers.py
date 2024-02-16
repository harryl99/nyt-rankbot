"""
Message handling module

This module defines functions and handlers to handle incoming messages in the Telegram Bot.
It includes handlers for specific commands, message patterns, and scoreboard display.
"""

from telegram import Update
from telegram.ext import CommandHandler, Filters, MessageHandler

from utils.calculate_attempts import (
    connections_attempts,
    mini_time,
    mini_time_app,
    wordle_attempts,
)
from utils.helpers import add_game, add_manual_score, clear_scoreboard, show_scoreboard
from utils.patterns import (
    connections_pattern,
    mini_pattern,
    mini_pattern_app,
    wordle_pattern,
)


def handle_messages(update: Update, context):
    """
    Handle incoming messages and parse relevant information.

    Args:
        update (Update): The incoming update containing the message.
        context: (Context): Additional context provided by the framework.

    Returns:
        None
    """

    # Extract relevant information from the incoming message
    message = update.message.text
    user = update.message.from_user.first_name

    # Check if the message matches any pattern
    if connections_pattern.search(message):
        attempts = connections_attempts(message)
        add_game(user, "Connections", attempts, context, update)
    elif mini_pattern.search(message):
        time = mini_time(message)
        add_game(user, "Mini", time, context, update)
    elif mini_pattern_app.search(message):
        time = mini_time_app(message)
        add_game(user, "Mini", time, context, update)
    elif wordle_pattern.search(message):
        attempts = wordle_attempts(message)
        add_game(user, "Wordle", attempts, context, update)


message_handler = MessageHandler(Filters.text & ~Filters.command, handle_messages)
scoreboard_handler = CommandHandler("scoreboard", show_scoreboard)
clear_handler = CommandHandler("clear", clear_scoreboard, pass_args=True)
add_handler = CommandHandler("add", add_manual_score, pass_args=True)
