"""
Main script to execute the chat bot and set up the database.

This script imports the necessary modules, executes the code in the 'database' module
to set up the database, and then runs the chat bot using the 'run_bot' function from
the 'bot.runner' module.
"""

from bot.runner import run_bot
from database import db_setup  # The code in the file will be executed

if __name__ == "__main__":

    # Run the bot
    run_bot()
