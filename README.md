# Habit Tracker

This is a command-line Python application to **create, track, and analyse** daily and weekly habits that I developed as part of the IU course *Object Oriented and Functional Programming with Python (DLBDSOOFPP01)*.

---

## Project Overview

This project demonstrates the design and implementation of a habit tracking system built entirely in Python. It focuses on combining **object-oriented programming (OOP)** and **functional programming (FP)** principles to deliver a clean, testable, and well-structured backend application.

### Core Application Features

- Create, manage, and delete daily or weekly habits
- Check off habits as completed
- Track streaks automatically — current and longest
- Persist all data using SQLite
- Analyse habits using functional programming techniques
- Fully tested with pytest

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/godfreyndlovu/oofpp_habits-tracker-project.git
cd oofpp_habits-tracker-project
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Dependencies

| Package | Purpose |
|---|---|
| click | CLI framework for clean, structured command handling |
| pytest | Unit and integration testing framework |

Both are lightweight, well-maintained, and standard choices for Python projects of this scope. `click` was chosen over a simple `input()` loop because it automatically generates help text, handles argument parsing, and keeps command logic cleanly separated from business logic.

---

## Usage

All commands are run from the project root.

### Load predefined habits and example data

```bash
python src/main.py seed
```

This populates `sample_habits.db` with 5 predefined habits and 4 weeks of completion data. To use this as your live database:

```bash
cp src/data/sample_habits.db src/data/habits.db
```

### Create a new habit

```bash
python src/main.py create --name "Meditate" --period daily
```

### Check off a habit as completed

```bash
python src/main.py checkoff --name "Meditate"
```

### List all habits

```bash
python src/main.py list

# Filter by period
python src/main.py list --period daily
python src/main.py list --period weekly
```

### View full analytics summary

```bash
python src/main.py analyse
```

### Check streak for a specific habit

```bash
python src/main.py streak --name "Read for 20 minutes"
```

### Delete a habit

```bash
python src/main.py delete --name "Meditate"
```

### Get help

```bash
python src/main.py --help
```

---

## Below I have included an Example Session

A typical end-to-end workflow from a fresh install:

```bash
# Load the predefined habits and sample data
python src/main.py seed
cp src/data/sample_habits.db src/data/habits.db

# See what habits are loaded
python src/main.py list

# Output:
# ID    Name                                Period     Completions    Streak
# ----------------------------------------------------------------------
# 1     Drink 2L of water                   daily      26             0
# 2     Exercise for 30 minutes             daily      24             0
# 3     Read for 20 minutes                 daily      27             0
# 4     Weekly review / journaling          weekly     4              0
# 5     Clean and tidy the house            weekly     3              0

# Check off a habit today
python src/main.py checkoff --name "Drink 2L of water"
# [ok] 'Drink 2L of water' checked off at 2025-01-01 09:00.

# Check the streak
python src/main.py streak --name "Drink 2L of water"
# 'Drink 2L of water' (daily):
#   Current streak : 1 period(s)
#   Longest streak : 9 period(s)

# Run full analytics
python src/main.py analyse
```

---

## Running Tests

```bash
python -m pytest tests/ -v --disable-warnings
```

Expected output:

```
collected 36 items

36 passed in 0.XX s  
(In my example, 36 passed in 1.82s)
```

### What is tested

The test suite covers four areas:

- **Habit creation** — valid and invalid periodicity, default timestamps, repr output
- **Check-off logic** — completion recording, timestamp sorting, multiple completions per day
- **Streak calculation** — consecutive daily streaks, weekly streaks, gap detection, edge cases with zero or single completions
- **Analytics functions** — filtering by period, longest streak across all habits, longest streak for a single habit, current streaks, struggled habits
- **HabitManager** — create, delete, check-off, duplicate detection, error handling
- **Database persistence** — save and load habits, completion persistence, cascade delete, name existence checks

---

## Project Structure

```
habit_tracker/
├── src/
│   ├── main.py                  # CLI entry point (click)
│   ├── data/
│   │   ├── habits.db            # Live user database (auto-created)
│   │   └── sample_habits.db     # Populated by seed command
│   └── modules/
│       ├── habit.py             # Habit class (OOP)
│       ├── habit_manager.py     # Orchestrates all habit operations
│       ├── db_handler.py        # SQLite persistence layer
│       ├── analytics.py         # Analytics module (functional programming)
│       └── fixtures.py          # Predefined seed data
├── tests/
│   └── test_habits.py           # Unit and integration tests (pytest)
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md
```

---

## Design and Implementation

### Object-Oriented Programming (OOP)

The `Habit` class is the core model of the application. It encapsulates all habit-related data — name, periodicity, creation date, and completion history — along with the streak calculation logic. Key methods include `check_off()` which records a timestamped completion, `get_streak()` which calculates the current active streak counting backwards from today, and `get_longest_streak()` which scans the full completion history to find the highest consecutive period count.

The `HabitManager` class sits on top of this, handling all create, delete, check-off, and retrieval operations by coordinating between the `Habit` model and the database layer. This separation means the `Habit` class stays focused purely on domain logic, while `HabitManager` handles orchestration.

### Functional Programming (FP)

The `analytics.py` module is implemented entirely using functional programming principles. All functions are pure — they take data in and return results without modifying any state or producing side effects. Specific examples:

- `get_habits_by_period(habits, period)` uses `filter` to return only habits matching the given periodicity
- `get_current_streaks(habits)` uses `map` to transform each habit into a summary dictionary containing its name, period, and active streak
- `get_longest_streak_all(habits)` uses `functools.reduce` to fold the entire habit list down to the single habit with the highest longest streak
- `get_struggled_habits(habits)` uses `sorted` with a lambda key to rank habits by completion count ascending

This design makes every analytics function independently testable and completely decoupled from the database and CLI layers.

### Persistence

Data is stored in a local SQLite database using Python's built-in `sqlite3` module — no external database server required. Two tables are used: `habits` stores habit definitions and `completions` stores each individual check-off event, linked to its habit via a foreign key with CASCADE delete. This means deleting a habit automatically removes all its completion records. The relational structure keeps the data normalised and makes streak queries clean and efficient.

SQLite was chosen over a JSON file approach because it handles relational data more robustly, enforces referential integrity, and is more representative of real-world backend development — while still being entirely file-based and dependency-free.

---

## Predefined Habits

The app ships with 5 predefined habits across both periods:

| Name | Periodicity |
|---|---|
| Drink 2L of water | daily |
| Exercise for 30 minutes | daily |
| Read for 20 minutes | daily |
| Weekly review / journaling | weekly |
| Clean and tidy the house | weekly |

Each habit includes 4 weeks of example completion data with intentional gaps to allow streak-breaking scenarios to be tested and demonstrated.

---

## Reflection

One of the difficult parts of building this application was getting the streak calculation to work properly, especially for weekly habits around the start and end of the year where the week numbering doesn't always line up with the calendar year. It took some trial and error to figure out that Python's `date.isocalendar()` was the right tool for this purpose rather than just doing simple date arithmetic.

Keeping the analytics functions separate from the rest of the code turned out to be one of the better decisions made early on. Because each function only takes in data and returns a result, testing was much simpler; no database setup needed, just create a few habits and pass them in. This made it a lot easier to catch bugs quickly.

If I were to do this again, I would probably create a separate class for completions rather than just storing datetime objects in a list. This would make it easier to add extra information to each check-off later on, like a note or a rating, without having to rework everything.

Going forward, the app could be extended with a simple web interface, more detailed analytics like completion rates over time, and cloud storage so habits are not just saved locally.
---

## Project Info

**Course:** Object Oriented and Functional Programming with Python — DLBDSOOFPP01 (IU International University)

**GitHub:** https://github.com/godfreyndlovu/oofpp_habits-tracker-project