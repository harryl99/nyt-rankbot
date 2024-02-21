"""
Helper Functions Module.

This module contains functions for tracking and displaying game scores in a Telegram bot. 
It utilizes a database to store user-submitted scores, calculates rankings, and generates scoreboards. 
The functionality includes adding new game scores, displaying today's rankings, and clearing the database for a given day.
"""

from datetime import datetime

import pandas as pd
import pytz
from telegram import Chat, Update, error

from database.queries import (
    add_game_to_database,
    clear_table,
    query_all_data,
    user_has_submitted,
)


def calculate_rankings():
    """
    Calculate and return the rankings based on today's scores.

    Returns:
    - sorted_df (pd.DataFrame): DataFrame containing sorted scores for each game.
    - total_points (pd.DataFrame): DataFrame containing total points for each user.
    """
    # Query all data from the db
    data = query_all_data()

    # Create DataFrame from the query result
    score_df = pd.DataFrame(data, columns=["id", "user", "game", "score", "date"])

    # Calculate rankings per date/game and assign points
    sorted_df = score_df.sort_values(by=["date", "game", "score"])
    sorted_df["points"] = sorted_df.groupby(["date", "game"])["score"].rank(
        method="min"
    )
    point_mapping = {1: 3, 2: 2, 3: 1}
    sorted_df["points"] = sorted_df["points"].map(point_mapping).fillna(0)

    return sorted_df


def calculate_period_total(sorted_df: pd.DataFrame, today: datetime.date, period: str):
    """
    Calculate total points for each user based on the given sorted DataFrame for a specified period.

    Parameters:
    - sorted_df (pandas.DataFrame): A DataFrame containing sorted data with a "date" column and a "points" column.
    - today (datetime.date): The date for which to calculate the total points.
    - period (str): A string indicating the period for which to calculate totals ('today' or 'month').

    Returns:
    - period_df (pandas.DataFrame): A subset of the input DataFrame for the specified period.
    - period_total_df (pandas.DataFrame): A DataFrame with the total points for each user in the specified period, sorted in descending order.
    """
    if period == "today":
        period_df = sorted_df[sorted_df["date"] == today]
    elif period == "month":
        start_of_month = datetime(today.year, today.month, 1)
        end_of_month = datetime(today.year, today.month + 1, 1) - pd.Timedelta(days=1)
        period_df = sorted_df[
            (sorted_df["date"] >= start_of_month.date())
            & (sorted_df["date"] <= end_of_month.date())
        ]
    else:
        raise ValueError("Invalid period. Use 'today' or 'month'.")

    period_total_df = period_df.groupby("user")["points"].sum().reset_index()
    period_total_df = period_total_df.sort_values(by="points", ascending=False)
    return period_df, period_total_df


def get_participants_count(update: Update, context):
    """
    Get the number of participants in the Telegram chat.

    Args:
    - update (telegram.Update): The update object.
    - context (telegram.ext.CallbackContext): The context object.

    Returns:
    - None
    """
    chat_id = update.message.chat_id
    chat = context.bot.get_chat(chat_id)

    # Check if the message comes from a group chat
    if chat.type not in (Chat.GROUP, Chat.SUPERGROUP):
        participants_count = 1
    else:
        # Get the number of participants (- 1 for the bot)
        participants_count = chat.get_members_count() - 1

    return participants_count


def add_game(user, game, score, context, update: Update):
    """
    Add a new game score to the database.
    Reports updated daily totals to Telegram if all users have submitted.

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

    # Add the new data to the database
    add_game_to_database(user, game, score, today)

    # Broadcast an updated scoreboard to the description/a message
    try:
        chat_id = update.message.chat_id
        scoreboard_msg = prepare_scoreboard_msg()
        context.bot.set_chat_description(chat_id, scoreboard_msg)
    except error.BadRequest:  # can't set private chat description
        pass
    # Broadcast an updated scoreboard to a message if all users submitted
    if check_all_submitted(context, update, today):
        update.message.reply_text("All users submitted!")
        show_scoreboard(update, context)


def check_all_submitted(context, update: Update, today):
    """
    This function checks if:
    (a) scores for 3 unique games have been submitted
    (b) the number of unique users who submitted scores for each game
    on the specified day is equal to the total number of participants.

    Parameters:
    - context: The context object for the Telegram bot.
    - update: The update object representing an incoming message.
    - today: The specific date for which to check submissions.

    Returns:
    None
    """
    participants_count = get_participants_count(update, context)
    sorted_df = calculate_rankings()
    sorted_df_today = sorted_df[sorted_df["date"] == today]
    all_submitted = all(
        [
            sorted_df_today["game"].nunique() == 3,
            (
                sorted_df_today.groupby("game")["user"].nunique() == participants_count
            ).all(),
        ]
    )
    return all_submitted


def show_scoreboard(update: Update, context):
    """
    Report daily/monthly totals to a Telegram message.

    Args:
    - update (telegram.Update): The update object.
    - context: The context object for the Telegram bot.

    Returns:
    - None
    """
    scoreboard_msg = prepare_scoreboard_msg()
    # Send the scoreboard message to Telegram
    update.message.reply_text(scoreboard_msg)


def prepare_scoreboard_msg():
    """
    Prepare a message for today's scoreboard, including game-specific scores, daily totals, and monthly totals.

    Returns:
    str: Scoreboard message for the day.
    """
    today = datetime.now(pytz.utc).date()
    # Calculate new rankings
    sorted_df = calculate_rankings()
    # Monthly total
    monthly_df, monthly_total_df = calculate_period_total(
        sorted_df, today, period="month"
    )
    # Today total
    today_df, today_total_df = calculate_period_total(sorted_df, today, period="today")

    # Prepare the message for today's scoreboard
    scoreboard_msg = ""
    # Iterate through unique games and append to the message
    for game in sorted_df[sorted_df["date"] == today]["game"].unique():
        game_today_df = sorted_df[
            (sorted_df["game"] == game) & (sorted_df["date"] == today)
        ]
        game_scoreboard_msg = f"🔢 {game} points 🔢\n{game_today_df[['user', 'score']].to_string(index=False, header=False)}\n\n"
        scoreboard_msg += game_scoreboard_msg
    # Append daily totals
    if len(today_total_df) == 0:
        scoreboard_msg += "No points scored for today! 😔\n\n"
    else:
        scoreboard_msg += f"👑 Daily totals 👑 \n{today_total_df.to_string(index=False, header=False)}\n\n"
    # Append monthly totals
    if len(monthly_total_df) == 0:
        scoreboard_msg += "No points scored for this month! 😢"
    else:
        scoreboard_msg += f"📅 Monthly totals 📅 \n{monthly_total_df.to_string(index=False, header=False)}"

    return scoreboard_msg


def clear_scoreboard(update: Update, context):
    """
    Clear the database table for today's date and a specific user (if provided), and send a confirmation message.

    Args:
    - update (telegram.Update): The update object.
    - user (str, optional): The user whose data should be cleared. Default is None, which clears all users.

    Returns:
    - None
    """
    # Parse arguments
    today = datetime.now(pytz.utc).date()
    user = context.args[0] if context.args else None

    # Call the function to clear data to the database
    clear_table(today, user)

    # Send a confirmation message
    if user:
        update.message.reply_text(
            f"Database table cleared for {today} and user {user} 🗑️!"
        )
    else:
        update.message.reply_text(f"Database table cleared for {today} 🗑️!")


def add_manual_score(update, context):
    """
    Add a user's game score to the database for today.

    Args:
    - update (telegram.Update): The update object.
    - context (telegram.ext.CallbackContext): The context object containing command arguments.

    Returns:
    - None
    """
    # Parse arguments
    if len(context.args) != 3:
        update.message.reply_text("Usage: /add <user> <game> <score>")
        return
    user, game, score = context.args
    today = datetime.now(pytz.utc).date()

    # Call the function to add data to the database
    add_game_to_database(user, game, score, today)

    # Send a confirmation message
    update.message.reply_text(f"Score added for {user} in {game}: {score}")
