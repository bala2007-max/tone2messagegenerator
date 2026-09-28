"""
SQLite Database Module for Tone-Based Email & Message Generator.
Member 3 Module: Database Management & Message History.
"""

import os
import sqlite3
from datetime import datetime

# Base directory for database file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "tone_generator.db")


def get_connection(db_path=DEFAULT_DB_PATH):
    """
    Establishes and returns a connection to the SQLite database.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def create_table(db_path=DEFAULT_DB_PATH):
    """
    Creates the message_history table if it does not already exist.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_text TEXT NOT NULL,
                message_type TEXT NOT NULL,
                tone TEXT NOT NULL,
                language TEXT NOT NULL,
                length TEXT NOT NULL,
                generated_text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def save_history(input_text, message_type, tone, language, length, generated_text, db_path=DEFAULT_DB_PATH):
    """
    Saves a generated message history record into SQLite database with current timestamp.
    """
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO message_history (input_text, message_type, tone, language, length, generated_text, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (input_text, message_type, tone, language, length, generated_text, created_at))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_history(tone=None, message_type=None, db_path=DEFAULT_DB_PATH):
    """
    Retrieves all saved history records ordered by id DESC (newest first).
    Returns a list of dictionaries.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        query = """
            SELECT id, input_text, message_type, tone, language, length, generated_text, created_at
            FROM message_history
        """
        filters = []
        values = []
        if tone:
            filters.append("tone = ?")
            values.append(tone)
        if message_type:
            filters.append("message_type = ?")
            values.append(message_type)
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += " ORDER BY id DESC"
        cursor.execute(query, values)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_history_by_id(history_id, db_path=DEFAULT_DB_PATH):
    """
    Retrieves a single history record by its ID.
    Returns a dictionary or None if not found.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, input_text, message_type, tone, language, length, generated_text, created_at
            FROM message_history
            WHERE id = ?
        """, (history_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def delete_history(history_id, db_path=DEFAULT_DB_PATH):
    """
    Deletes a specific history record by ID.
    Returns True if deleted, False otherwise.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM message_history
            WHERE id = ?
        """, (history_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def clear_history(db_path=DEFAULT_DB_PATH):
    """
    Deletes all history records from the database.
    Returns the number of deleted rows.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM message_history")
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


if __name__ == "__main__":
    create_table()
    print(f"Database successfully created/verified at: {DEFAULT_DB_PATH}")
    print("Table 'message_history' is ready.")
