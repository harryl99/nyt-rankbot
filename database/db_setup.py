"""
Script to initialize the database connection and create the required table.

This script uses the pymysql library to establish a connection to the database
using the credentials provided in the environment variables loaded from the .env file.
If non-existant, it creates a table named 'nyt_rankbot' with columns 'id', 'user', 'game', 'score', and 'date'.
"""

import os

import pymysql
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the database connection
db_config = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
}

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
