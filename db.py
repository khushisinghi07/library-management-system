"""Database connection helper."""
import os
import mysql.connector

CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "library_db"),
}


def get_connection():
    return mysql.connector.connect(**CONFIG)
