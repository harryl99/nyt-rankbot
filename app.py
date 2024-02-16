import os
import re
from datetime import datetime

import pandas as pd
import pymysql
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    JobQueue,
    MessageHandler,
    Updater,
)

# Load environment variables from .env file
load_dotenv()

# Database configuration
db_config = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
}

# Telegram bot token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize the database connection
db_connection = pymysql.connect(**db_config)
cursor = db_connection.cursor()

# SQL statement to create the table
create_table_query = """
CREATE TABLE IF NOT EXISTS nyt_rankbot (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user VARCHAR(255) NOT NULL,
    game VARCHAR(255) NOT NULL,
    score INT NOT NULL,
    date DATE NOT NULL
);
"""
cursor.execute(create_table_query)
db_connection.commit()

# Initialize the Telegram bot
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Regular expressions for different patterns
connections_pattern = re.compile(r"Connections \nPuzzle #[0-9]+")
mini_pattern = re.compile(r"badges\/games\/mini.+t=([0-9]+)")
wordle_pattern = re.compile(r"Wordle [0-9]+ ([0-9])/[0-9]")


def connections_attempts(message):
    connection_colours = "🟨🟩🟦🟪"
    connections_lines = message.splitlines()
    connections_lines = [
        line
        for line in connections_lines
        if any(square in line for square in connection_colours)
    ]
    attempts = len(connections_lines)
    return attempts


def mini_time(message):
    time = mini_pattern.search(message).group(1)
    return time


def wordle_attempts(message):
    attempts = wordle_pattern.search(message).group(1)
    return attempts


def calculate_rankings():
    # Query data from the database
    query = "SELECT * FROM nyt_rankbot"
    cursor.execute(query)
    data = cursor.fetchall()

    # Create DataFrame from the query result
    print(data)
    score_df = pd.DataFrame(data, columns=["id", "user", "game", "score", "date"])

    # Your existing calculate_rankings logic
    today_df = score_df[score_df["date"] == pd.to_datetime("today").date()]
    sorted_df = today_df.sort_values(by=["game", "score"])
    sorted_df["points"] = sorted_df.groupby("game")["score"].rank(method="min")
    point_mapping = {1: 3, 2: 2, 3: 1}
    sorted_df["points"] = sorted_df["points"].map(point_mapping).fillna(0)
    total_points = sorted_df.groupby("user")["points"].sum().reset_index()
    total_points = total_points.sort_values(by="points", ascending=False)

    return sorted_df, total_points


# Function to add a new game to the database
def add_game(user, game, score, context, update):
    # Check if the user has already submitted a game for today
    if user_has_submitted(user, game):
        update.message.reply_text(
            f"{user} has already submitted a score for '{game}' today 🤨!"
        )
        return

    # Parse the new data
    today = datetime.today().date()
    new_data = [user, game, score, today]

    # Add the new data to the database
    add_game_to_database(new_data)

    # Calculate new rankings
    sorted_df, total_points = calculate_rankings()
    new_rankings = sorted_df.loc[sorted_df["game"] == game][["user", "score"]]

    # Prepare the combined message to send
    combined_msg = (
        f"{user}'s score of '{score}' detected for '{game}'!\n\n"
        f"🔢 {game} scoreboard 🔢\n{new_rankings.to_string(index=False, header=False)}\n\n"
        f"👑 Total points 👑\n{total_points.to_string(index=False, header=False)}"
    )

    # Send the combined message to Telegram
    context.bot.send_message(chat_id=update.message.chat_id, text=combined_msg)


def add_game_to_database(new_data):
    # Insert the new data into the database
    insert_query = (
        "INSERT INTO nyt_rankbot (user, game, score, date) VALUES (%s, %s, %s, %s)"
    )
    cursor.execute(insert_query, tuple(new_data))
    db_connection.commit()


def handle_messages(update: Update, context: CallbackContext):
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
    elif wordle_pattern.search(message):
        attempts = wordle_attempts(message)
        add_game(user, "Wordle", attempts, context, update)


def clear_table(update: Update, context: CallbackContext):
    # Get today's date
    today = datetime.today().date()

    # Clear the database table for today's date
    clear_query = f"DELETE FROM nyt_rankbot WHERE date = '{today}'"
    cursor.execute(clear_query)
    db_connection.commit()

    # Send a confirmation message
    update.message.reply_text(f"Database table cleared for {today}!")


# Command handler for /scoreboard command
def today_scoreboard(update: Update, context: CallbackContext):
    # Calculate today's rankings
    sorted_df, total_points = calculate_rankings()

    # Prepare the message for today's scoreboard
    scoreboard_msg = ""
    # Iterate through unique games and append to the message
    for game in sorted_df["game"].unique():
        game_df = sorted_df[sorted_df["game"] == game]
        game_scoreboard_msg = f"🔢 {game} scoreboard 🔢\n{game_df[['user', 'score']].to_string(index=False, header=False)}\n\n"
        scoreboard_msg += game_scoreboard_msg

    # Append total points message
    if len(total_points) == 0:
        scoreboard_msg = "No points scored for today! 😔"
    else:
        scoreboard_msg += f"👑 Total points today 👑 \n{total_points.to_string(index=False, header=False)}"

    # Send the scoreboard message to Telegram
    update.message.reply_text(scoreboard_msg)


# Function to check if the user has already submitted a game for today
def user_has_submitted(user, game):
    today = datetime.today().date()
    query = f"SELECT * FROM nyt_rankbot WHERE user = '{user}' AND game = '{game}' AND date = '{today}'"
    cursor.execute(query)
    return cursor.fetchone() is not None


# Register message/command handlers
message_handler = MessageHandler(Filters.text & ~Filters.command, handle_messages)
dispatcher.add_handler(message_handler)
clear_handler = CommandHandler("clear", clear_table)
dispatcher.add_handler(clear_handler)
scoreboard_handler = CommandHandler("scoreboard", today_scoreboard)
dispatcher.add_handler(scoreboard_handler)

# Start the bot
updater.start_polling(clean=True)
updater.idle()
