"""
habit_manager.py
----------------
HabitManager — orchestrates all habit operations between the CLI,
the Habit model, and the database layer.
"""

from datetime import datetime
from typing import List, Optional
from modules.habit import Habit
from modules import db_handler as db


class HabitManager:
    """
    Manages creating, deleting, checking off, and loading habits.
    Acts as the bridge between the CLI and the database.

    Attributes:
        db_path (str): Path to the SQLite database file.
    """

    def __init__(self, db_path: str):
        """
        Initialise the HabitManager and ensure the database schema exists.

        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.db_path = db_path
        db.initialise_db(db_path)

    def create_habit(self, name: str, periodicity: str) -> Habit:
        """
        Create and persist a new habit.

        Args:
            name (str): Habit name.
            periodicity (str): daily or weekly.

        Returns:
            Habit: The saved habit with its database ID.

        Raises:
            ValueError: If a habit with this name already exists.
        """
        if db.habit_name_exists(name, self.db_path):
            raise ValueError(f"A habit named '{name}' already exists.")
        habit = Habit(name=name, periodicity=periodicity)
        return db.save_habit(habit, self.db_path)

    def delete_habit(self, name: str) -> None:
        """
        Delete a habit by name.

        Args:
            name (str): Name of the habit to delete.

        Raises:
            ValueError: If no habit with this name is found.
        """
        habit = self._find_by_name(name)
        if habit is None:
            raise ValueError(f"No habit named '{name}' found.")
        db.delete_habit(habit.habit_id, self.db_path)

    def check_off(self, name: str, completed_at: Optional[datetime] = None) -> datetime:
        """
        Mark a habit as completed.

        Args:
            name (str): Name of the habit to check off.
            completed_at (datetime, optional): Timestamp. Defaults to now.

        Returns:
            datetime: The recorded completion timestamp.

        Raises:
            ValueError: If no habit with this name is found.
        """
        habit = self._find_by_name(name)
        if habit is None:
            raise ValueError(f"No habit named '{name}' found.")
        ts = completed_at or datetime.now()
        db.save_completion(habit.habit_id, ts, self.db_path)
        return ts

    def get_all_habits(self) -> List[Habit]:
        """Load and return all habits from the database."""
        return db.load_all_habits(self.db_path)

    def _find_by_name(self, name: str) -> Optional[Habit]:
        """Find a habit by name (case-insensitive). Returns None if not found."""
        habits = self.get_all_habits()
        return next((h for h in habits if h.name.lower() == name.lower()), None)
