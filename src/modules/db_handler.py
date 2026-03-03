"""
db_handler.py
-------------
Handles all SQLite database interactions.
Provides functions to initialise, save, load, and delete habits and completions.
"""

import sqlite3
from datetime import datetime
from modules.habit import Habit

DATE_FMT = "%Y-%m-%d %H:%M:%S"


def get_connection(db_path: str) -> sqlite3.Connection:
    """Return a SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialise_db(db_path: str) -> None:
    """Create the habits and completions tables if they do not exist."""
    with get_connection(db_path) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS habits (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL UNIQUE,
                periodicity TEXT NOT NULL,
                created_at  TEXT NOT NULL
            )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS completions (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id     INTEGER NOT NULL,
                completed_at TEXT NOT NULL,
                FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
            )"""
        )


def save_habit(habit: Habit, db_path: str) -> Habit:
    """Insert a new habit into the database and assign its generated ID."""
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO habits (name, periodicity, created_at) VALUES (?, ?, ?)",
            (habit.name, habit.periodicity, habit.created_at.strftime(DATE_FMT))
        )
        habit.habit_id = cursor.lastrowid
    return habit


def delete_habit(habit_id: int, db_path: str) -> None:
    """Delete a habit and all its completions (CASCADE) from the database."""
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))


def save_completion(habit_id: int, completed_at: datetime, db_path: str) -> None:
    """Insert a timestamped completion record for a habit."""
    with get_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO completions (habit_id, completed_at) VALUES (?, ?)",
            (habit_id, completed_at.strftime(DATE_FMT))
        )


def load_all_habits(db_path: str) -> list:
    """Load all habits and their completions from the database."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT id, name, periodicity, created_at FROM habits ORDER BY id"
        ).fetchall()
        habits = []
        for row in rows:
            h = Habit(
                name=row[1],
                periodicity=row[2],
                created_at=datetime.strptime(row[3], DATE_FMT),
                habit_id=row[0],
            )
            completions = conn.execute(
                "SELECT completed_at FROM completions WHERE habit_id = ? ORDER BY completed_at",
                (row[0],)
            ).fetchall()
            for c in completions:
                h.completions.append(datetime.strptime(c[0], DATE_FMT))
            habits.append(h)
    return habits


def habit_name_exists(name: str, db_path: str) -> bool:
    """Return True if a habit with the given name already exists."""
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT 1 FROM habits WHERE name = ?", (name,)).fetchone()
    return row is not None
