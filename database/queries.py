"""
Database Operations Module

This module provides functions for interacting with the MySQL database, including
adding game data, clearing the table for a specific date, and checking if a user has
already submitted data for a specific game on the current date.
"""

from datetime import datetime

from database.db_setup import cursor, db_connection


def user_has_submitted(user, game, today):
    """
    Check if a user has submitted data for a specific game on the current date.

    Args:
        user (str): The user's name.
        game (str): The name of the game.
        today (str): The current date.

    Returns:
        bool: True if the user has submitted data, False otherwise.
    """
    query = f"SELECT * FROM nyt_rankbot WHERE user = '{user}' AND game = '{game}' AND date = '{today}'"
    cursor.execute(query)
    return cursor.fetchone() is not None


def add_game_to_database(new_data):
    """
    Add game data to the database.

    Args:
        new_data (Tuple[str, str, int, datetime]): Tuple containing user, game, score, and date.

    Returns:
        None
    """
    insert_query = (
        "INSERT INTO nyt_rankbot (user, game, score, date) VALUES (%s, %s, %s, %s)"
    )
    cursor.execute(insert_query, tuple(new_data))
    db_connection.commit()


def clear_table(today, user):
    """
    Clear the database table for a specific date and user.

    Args:
        today (str): The date for which the table should be cleared.
        user (str, optional): The user whose data should be cleared. Default is None, which clears all users.

    Returns:
        None
    """
    if user:
        clear_query = (
            f"DELETE FROM nyt_rankbot WHERE date = '{today}' AND user = '{user}'"
        )
    else:
        clear_query = f"DELETE FROM nyt_rankbot WHERE date = '{today}'"

    cursor.execute(clear_query)
    db_connection.commit()


def manual_add_to_database(today, user, game, score):
    """
    Add a user's game score to the database for a specific date.

    Args:
    - today (str): The date for which the score should be added.
    - user (str): The user for whom the score is being added.
    - game (str): The game for which the score is being added.
    - score (str): The score to be added.

    Returns:
    - None
    """
    # Construct the SQL query to insert data into the database
    insert_query = f"INSERT INTO nyt_rankbot (date, user, game, score) VALUES ('{today}', '{user}', '{game}', '{score}')"

    # Execute the query and commit changes
    cursor.execute(insert_query)
    db_connection.commit()
