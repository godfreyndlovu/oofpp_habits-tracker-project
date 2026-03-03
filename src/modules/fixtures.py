"""
fixtures.py
-----------
Seeds the database with 5 predefined habits and 4 weeks of example completions.
Run via the CLI: python3 src/main.py seed
"""

from datetime import datetime, timedelta
from modules.habit import Habit
from modules import db_handler as db

START_DATE = datetime(2025, 1, 1, 8, 0, 0)


def _day(n):
    """Return START_DATE offset by n days."""
    return START_DATE + timedelta(days=n)


def _week(n):
    """Return START_DATE offset by n weeks."""
    return START_DATE + timedelta(weeks=n)


PREDEFINED_HABITS = [
    {
        "name": "Drink 2L of water",
        "periodicity": "daily",
        "completions": [_day(d) for d in range(28) if d not in (9, 19)],
    },
    {
        "name": "Exercise for 30 minutes",
        "periodicity": "daily",
        "completions": [_day(d) for d in range(28) if d not in (3, 7, 14, 21)],
    },
    {
        "name": "Read for 20 minutes",
        "periodicity": "daily",
        "completions": [_day(d) for d in range(28) if d != 15],
    },
    {
        "name": "Weekly review / journaling",
        "periodicity": "weekly",
        "completions": [_week(w) for w in range(4)],
    },
    {
        "name": "Clean and tidy the house",
        "periodicity": "weekly",
        "completions": [_week(0), _week(1), _week(3)],
    },
]


def load_fixtures(db_path):
    """
    Seed the database with predefined habits and their completion data.
    Skips any habit that already exists by name.

    Args:
        db_path (str): Path to the SQLite database file.
    """
    db.initialise_db(db_path)
    for entry in PREDEFINED_HABITS:
        name = entry["name"]
        if db.habit_name_exists(name, db_path):
            print(f"  [skip] '{name}' already exists.")
            continue
        habit = Habit(name=name, periodicity=entry["periodicity"], created_at=START_DATE)
        db.save_habit(habit, db_path)
        for ts in entry["completions"]:
            db.save_completion(habit.habit_id, ts, db_path)
        print(f"  [ok]   '{name}' loaded ({len(entry['completions'])} completions).")
