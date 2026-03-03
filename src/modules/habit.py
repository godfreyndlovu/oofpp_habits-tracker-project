"""
habit.py
--------
Defines the Habit class — the core OOP model for the habit tracking application.
Encapsulates all habit-related attributes and streak calculation logic.
"""

from datetime import datetime, date, timedelta
from typing import List, Optional


class Habit:
    """
    Represents a single habit with a name, periodicity, and completion history.

    Attributes:
        habit_id (Optional[int]): Database ID assigned after persistence.
        name (str): Name/description of the habit.
        periodicity (str): 'daily' or 'weekly'.
        created_at (datetime): Timestamp when the habit was created.
        completions (List[datetime]): Sorted list of completion timestamps.
    """

    VALID_PERIODS = ("daily", "weekly")

    def __init__(
        self,
        name: str,
        periodicity: str,
        created_at: Optional[datetime] = None,
        habit_id: Optional[int] = None,
    ):
        """
        Initialise a Habit instance.

        Args:
            name (str): The habit name.
            periodicity (str): 'daily' or 'weekly'.
            created_at (datetime, optional): Creation timestamp. Defaults to now.
            habit_id (int, optional): Database ID. Defaults to None.

        Raises:
            ValueError: If periodicity is not 'daily' or 'weekly'.
        """
        if periodicity not in self.VALID_PERIODS:
            raise ValueError(
                f"Invalid periodicity '{periodicity}'. Must be one of {self.VALID_PERIODS}."
            )
        self.habit_id = habit_id
        self.name = name
        self.periodicity = periodicity
        self.created_at = created_at or datetime.now()
        self.completions: List[datetime] = []

    def check_off(self, completed_at: Optional[datetime] = None) -> datetime:
        """
        Mark the habit as completed at a given time.

        Args:
            completed_at (datetime, optional): Completion timestamp. Defaults to now.

        Returns:
            datetime: The recorded completion timestamp.
        """
        ts = completed_at or datetime.now()
        self.completions.append(ts)
        self.completions.sort()
        return ts

    def _period_key(self, dt: datetime) -> tuple:
        """Return a tuple identifying the period a datetime belongs to."""
        d = dt.date() if isinstance(dt, datetime) else dt
        if self.periodicity == "daily":
            return (d.year, d.timetuple().tm_yday)
        iso = d.isocalendar()
        return (iso[0], iso[1])

    def get_streak(self) -> int:
        """Return the current active streak as of today."""
        return self._calculate_streak(reference=date.today())

    def get_longest_streak(self) -> int:
        """Return the longest streak ever recorded for this habit."""
        if not self.completions:
            return 0
        periods = sorted(set(self._period_key(c) for c in self.completions))
        max_streak = current_streak = 1
        for i in range(1, len(periods)):
            if self._are_consecutive(periods[i - 1], periods[i]):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        return max_streak

    def _calculate_streak(self, reference: date) -> int:
        """Count consecutive completed periods backwards from reference date."""
        if not self.completions:
            return 0
        ref_key = self._period_key(datetime.combine(reference, datetime.min.time()))
        completed_periods = set(self._period_key(c) for c in self.completions)
        streak = 0
        current_key = ref_key
        while current_key in completed_periods:
            streak += 1
            current_key = self._previous_period(current_key)
        return streak

    def _are_consecutive(self, period_a: tuple, period_b: tuple) -> bool:
        """Check whether two period keys are directly consecutive."""
        if self.periodicity == "daily":
            date_a = date(period_a[0], 1, 1) + timedelta(days=period_a[1] - 1)
            date_b = date(period_b[0], 1, 1) + timedelta(days=period_b[1] - 1)
            return (date_b - date_a).days == 1
        monday_a = date.fromisocalendar(period_a[0], period_a[1], 1)
        monday_b = date.fromisocalendar(period_b[0], period_b[1], 1)
        return (monday_b - monday_a).days == 7

    def _previous_period(self, period_key: tuple) -> tuple:
        """Return the period key immediately before the given one."""
        if self.periodicity == "daily":
            d = date(period_key[0], 1, 1) + timedelta(days=period_key[1] - 2)
            return (d.year, d.timetuple().tm_yday)
        monday = date.fromisocalendar(period_key[0], period_key[1], 1)
        prev = monday - timedelta(weeks=1)
        iso = prev.isocalendar()
        return (iso[0], iso[1])

    def __repr__(self) -> str:
        return (
            f"Habit(id={self.habit_id}, name='{self.name}', "
            f"periodicity='{self.periodicity}', completions={len(self.completions)})"
        )
