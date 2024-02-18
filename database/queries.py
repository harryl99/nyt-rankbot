"""
Database Operations Module

This module provides functions for interacting with the SQLAlchemy database, including
adding game data, clearing the table for a specific date, and checking if a user has
already submitted data for a specific game on the current date.
"""

from database.db_setup import NytRankbot, SessionFactory


def query_all_data():
    """
    Queries all data from the 'nyt_rankbot' table in the database.

    Returns:
    - data_tuples: A list of tuples containing the fetched data from the database.
    """
    session = SessionFactory()
    data = session.query(NytRankbot).all()
    session.close()

    # Extract attributes from instances and create a list of tuples
    data_tuples = [
        (item.id, item.user, item.game, item.score, item.date) for item in data
    ]

    return data_tuples


def user_has_submitted(user, game, today):
    """
    Check if a user has submitted data for a specific game on the current date.

    Returns:
        bool: True if the user has submitted data, False otherwise.
    """
    session = SessionFactory()
    submitted = (
        session.query(NytRankbot).filter_by(user=user, game=game, date=today).first()
        is not None
    )
    session.close()
    return submitted


def add_game_to_database(user, game, score, today):
    """
    Add game data to the database.

    Args:
        user (str): The user's name.
        game (str): The name of the game.
        score (str): The score for the game.
        today (datetime.date): The date for which the data is being added.

    Returns:
        None
    """
    new_data = NytRankbot(
        user=user,
        game=game,
        score=score,
        date=today,
    )

    session = SessionFactory()
    session.add(new_data)

    session.commit()
    session.close()


def clear_table(today, user=None):
    """
    Clear the database table for a specific date and user.

    Returns:
        None
    """
    session = SessionFactory()
    try:
        if user:
            session.query(NytRankbot).filter_by(date=today, user=user).delete()
        else:
            session.query(NytRankbot).filter_by(date=today).delete()
        session.commit()
    finally:
        session.close()
