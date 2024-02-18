"""
Script to initialize the database connection and create the required table.

This script uses SQLalchemy to establish a connection to a local SQLite database.
If the database file does not exist, it creates a table named 'nyt_rankbot' with columns 'id', 'user', 'game', 'score', and 'date'.
"""

import os

from sqlalchemy import Column, Date, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration
db_file_path = f"{os.path.join(os.getcwd(), 'database/nyt_rankbot.db')}"
db_url = f"sqlite:///{db_file_path}"
engine = create_engine(db_url)

# Declarative base
Base = declarative_base()


class NytRankbot(Base):
    """
    SQLAlchemy model representing the 'nyt_rankbot' table.

    Attributes:
    - id (int): Primary key, auto-incremented.
    - user (str): Name of the user, not nullable.
    - game (str): Name of the game, not nullable.
    - score (int): Score achieved by the user in the game, not nullable.
    - date (Date): Date when the score was achieved, not nullable.
    """

    __tablename__ = "nyt_rankbot"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(255), nullable=False)
    game = Column(String(255), nullable=False)
    score = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)


# Create the table
Base.metadata.create_all(engine)

# Create a session factory
SessionFactory = sessionmaker(bind=engine)
