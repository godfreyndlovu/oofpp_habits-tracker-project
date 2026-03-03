"""
analytics.py
------------
Analytics module using functional programming. All functions are pure.
"""

from functools import reduce
from typing import List, Optional
from modules.habit import Habit


def get_all_habits(habits: List[Habit]) -> List[Habit]:
    """Return a list of all currently tracked habits."""
    return list(habits)


def get_habits_by_period(habits: List[Habit], periodicity: str) -> List[Habit]:
    """Return all habits matching the given periodicity (daily or weekly)."""
    return list(filter(lambda h: h.periodicity == periodicity, habits))


def get_longest_streak_all(habits: List[Habit]) -> Optional[Habit]:
    """Return the habit with the highest longest streak across all habits."""
    if not habits:
        return None
    return reduce(
        lambda a, b: a if a.get_longest_streak() >= b.get_longest_streak() else b,
        habits
    )


def get_longest_streak_for(habit: Habit) -> int:
    """Return the longest streak ever recorded for a specific habit."""
    return habit.get_longest_streak()


def get_current_streaks(habits: List[Habit]) -> List[dict]:
    """Return each habit name, periodicity, and current active streak as a list of dicts."""
    return list(map(lambda h: {
        "name": h.name,
        "periodicity": h.periodicity,
        "current_streak": h.get_streak(),
    }, habits))


def get_struggled_habits(habits: List[Habit], top_n: int = 3) -> List[Habit]:
    """Return top_n habits with the fewest completions (most struggled)."""
    return sorted(habits, key=lambda h: len(h.completions))[:top_n]
