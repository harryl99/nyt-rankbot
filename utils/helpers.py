"""
Helper Functions Module.

This module contains functions for tracking and displaying game scores in a Telegram bot. 
It utilizes a database to store user-submitted scores, calculates rankings, and generates scoreboards. 
The functionality includes adding new game scores, displaying today's rankings, and clearing the database for a new day.
"""

from datetime import datetime

import pandas as pd
import pytz
from telegram import Update

from database.db_setup import cursor
from database.queries import add_game_to_database, clear_table, user_has_submitted


def calculate_rankings():
    """
    Calculate and return the rankings based on today's scores.

    Returns:
    - sorted_df (pd.DataFrame): DataFrame containing sorted scores for each game.
    - total_points (pd.DataFrame): DataFrame containing total points for each user.
    """

    # Query data from the database
    query = "SELECT * FROM nyt_rankbot"
    cursor.execute(query)
    data = cursor.fetchall()
    # Create DataFrame from the query result
    score_df = pd.DataFrame(data, columns=["id", "user", "game", "score", "date"])

    # Calculate rankings and assign points
    today_df = score_df[score_df["date"] == pd.to_datetime("today").date()]
    sorted_df = today_df.sort_values(by=["game", "score"])
    sorted_df["points"] = sorted_df.groupby("game")["score"].rank(method="min")
    point_mapping = {1: 3, 2: 2, 3: 1}
    sorted_df["points"] = sorted_df["points"].map(point_mapping).fillna(0)

    total_points = sorted_df.groupby("user")["points"].sum().reset_index()
    total_points = total_points.sort_values(by="points", ascending=False)

    return sorted_df, total_points


def add_game(user, game, score, context, update):
    """
    Add a new game score to the database, calculate new rankings, and send the combined message to Telegram.

    Args:
    - user (str): The username.
    - game (str): The name of the game.
    - score (int): The score achieved in the game.
    - context (telegram.ext.CallbackContext): The context object.
    - update (telegram.Update): The update object.

    Returns:
    - None
    """
    # Check if the user has already submitted a game for today
    today = datetime.now(pytz.utc).date()
    if user_has_submitted(user, game, today):
        update.message.reply_text(
            f"{user} has already submitted a score for '{game}' today 🤨!"
        )
        return

    # Parse the new data
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


def show_scoreboard(update: Update):
    """
    Calculate today's rankings, prepare the scoreboard message, and send it to Telegram.

    Args:
    - update (telegram.Update): The update object.
    - context (telegram.ext.CallbackContext): The context object.

    Returns:
    - None
    """

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


def clear_scoreboard(update, user=None):
    """
    Clear the database table for today's date and a specific user (if provided), and send a confirmation message.

    Args:
    - update (telegram.Update): The update object.
    - user (str, optional): The user whose data should be cleared. Default is None, which clears all users.

    Returns:
    - None
    """
    today = datetime.now(pytz.utc).date()
    clear_table(today, user)
    # Send a confirmation message
    if user:
        update.message.reply_text(
            f"Database table cleared for {today} and user {user} 🗑️!"
        )
    else:
        update.message.reply_text(f"Database table cleared for {today} 🗑️!")
