# Habit Tracker

Python CLI app to create, track, and analyse daily and weekly habits.
Built for IU course DLBDSOOFPP01.

---

## Project Structure

    habit_tracker/
    +-- src/
    +   +-- main.py              # CLI entry point (click)
    +   +-- data/               # SQLite database files
    +   +-- modules/
    +       +-- habit.py        # Habit class (OOP)
    +       +-- habit_manager.py
    +       +-- db_handler.py   # SQLite persistence
    +       +-- analytics.py    # Functional analytics
    +       +-- fixtures.py     # Seed data
    +-- tests/
    +   +-- test_habits.py
    +-- requirements.txt
    +-- pytest.ini
    +-- README.md

---

## Installation

    git clone https://github.com/<your_username>/<your_repo>
    cd habit_tracker
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

---

## Commands

    # Load 5 predefined habits with 4 weeks of data
    python3 src/main.py seed

    # Create a habit
    python3 src/main.py create --name "Meditate" --period daily

    # Check off a habit
    python3 src/main.py checkoff --name "Meditate"

    # List all habits
    python3 src/main.py list
    python3 src/main.py list --period daily

    # Full analytics
    python3 src/main.py analyse

    # Streak for a habit
    python3 src/main.py streak --name "Read for 20 minutes"

    # Delete a habit
    python3 src/main.py delete --name "Meditate"

---

## Running Tests

    pytest -v

---

## Design

OOP: Habit class and HabitManager encapsulate all domain logic.
FP:  analytics.py uses pure functions, map, filter, functools.reduce.
DB:  SQLite with two tables: habits and completions (CASCADE delete).

---

## Predefined Habits

- Drink 2L of water (daily)
- Exercise for 30 minutes (daily)
- Read for 20 minutes (daily)
- Weekly review / journaling (weekly)
- Clean and tidy the house (weekly)
