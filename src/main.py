"""
main.py
-------
Entry point for the Habit Tracker CLI application.
Uses Click to expose commands: seed, create, delete, checkoff, list, analyse, streak.
Run with: python3 src/main.py <command>
"""

import sys
import os

# Ensure src/ is on the path so 'modules' imports resolve correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import click
from modules.habit_manager import HabitManager
from modules import analytics
from modules.fixtures import load_fixtures

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "habits.db")
SAMPLE_DB = os.path.join(os.path.dirname(__file__), "data", "sample_habits.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

manager = HabitManager(DB_PATH)


@click.group()
def cli():
    """HabitTracker -- build streaks, break bad habits, analyse your progress."""
    pass


@cli.command("seed")
def seed():
    """Load 5 predefined habits with 4 weeks of example completion data."""
    click.echo("Loading fixtures into sample_habits.db...")
    os.makedirs(os.path.dirname(SAMPLE_DB), exist_ok=True)
    load_fixtures(SAMPLE_DB)
    click.echo("Done. Copy src/data/sample_habits.db to src/data/habits.db to use this data.")


@cli.command("create")
@click.option("--name", prompt="Habit name", help="Name of the new habit.")
@click.option(
    "--period",
    prompt="Periodicity (daily/weekly)",
    type=click.Choice(["daily", "weekly"]),
    help="How often the habit repeats.",
)
def create_habit(name, period):
    """Create a new habit and save it to the database."""
    try:
        habit = manager.create_habit(name, period)
        click.echo(f"[ok] Created habit '{habit.name}' ({habit.periodicity}).")
    except ValueError as e:
        click.echo(f"[error] {e}")


@cli.command("delete")
@click.option("--name", prompt="Habit name to delete", help="Name of the habit to remove.")
def delete_habit(name):
    """Delete a habit and all its completion history."""
    try:
        manager.delete_habit(name)
        click.echo(f"[ok] Deleted habit '{name}'.")
    except ValueError as e:
        click.echo(f"[error] {e}")


@cli.command("checkoff")
@click.option("--name", prompt="Habit name", help="Name of the habit to check off.")
def check_off(name):
    """Mark a habit as completed right now."""
    try:
        ts = manager.check_off(name)
        click.echo(f"[ok] '{name}' checked off at {ts.strftime('%Y-%m-%d %H:%M')}.")
    except ValueError as e:
        click.echo(f"[error] {e}")


@cli.command("list")
@click.option(
    "--period",
    default=None,
    type=click.Choice(["daily", "weekly"]),
    help="Filter habits by periodicity.",
)
def list_habits(period):
    """List all tracked habits, optionally filtered by period."""
    habits = manager.get_all_habits()
    if period:
        habits = analytics.get_habits_by_period(habits, period)
    if not habits:
        click.echo("No habits found.")
        return
    click.echo(f"\n{'ID':<5} {'Name':<35} {'Period':<10} {'Completions':<14} {'Streak'}")
    click.echo("-" * 72)
    for h in habits:
        click.echo(
            f"{h.habit_id:<5} {h.name:<35} {h.periodicity:<10} "
            f"{len(h.completions):<14} {h.get_streak()}"
        )
    click.echo()


@cli.command("analyse")
def analyse():
    """Display a full analytics summary of all habits."""
    habits = manager.get_all_habits()
    if not habits:
        click.echo("No habits found. Run 'seed' or create some habits first.")
        return

    click.echo("\n=== ALL TRACKED HABITS ===")
    for h in analytics.get_all_habits(habits):
        click.echo(f"  - {h.name} ({h.periodicity})")

    click.echo("\n=== DAILY HABITS ===")
    for h in analytics.get_habits_by_period(habits, "daily"):
        click.echo(f"  - {h.name}")

    click.echo("\n=== WEEKLY HABITS ===")
    for h in analytics.get_habits_by_period(habits, "weekly"):
        click.echo(f"  - {h.name}")

    click.echo("\n=== CURRENT STREAKS ===")
    for entry in analytics.get_current_streaks(habits):
        click.echo(f"  - {entry['name']}: {entry['current_streak']} {entry['periodicity']} period(s)")

    best = analytics.get_longest_streak_all(habits)
    if best:
        click.echo("\n=== LONGEST STREAK OVERALL ===")
        click.echo(f"  - '{best.name}' -- {best.get_longest_streak()} period(s)")

    click.echo("\n=== MOST STRUGGLED (fewest completions) ===")
    for h in analytics.get_struggled_habits(habits):
        click.echo(f"  - {h.name}: {len(h.completions)} completion(s)")
    click.echo()


@cli.command("streak")
@click.option("--name", prompt="Habit name", help="Habit to check the streak for.")
def streak(name):
    """Show the current and longest streak for a specific habit."""
    habits = manager.get_all_habits()
    match = next((h for h in habits if h.name.lower() == name.lower()), None)
    if not match:
        click.echo(f"No habit named '{name}' found.")
        return
    click.echo(f"\n'{match.name}' ({match.periodicity}):")
    click.echo(f"  Current streak : {match.get_streak()} period(s)")
    click.echo(f"  Longest streak : {analytics.get_longest_streak_for(match)} period(s)\n")


if __name__ == "__main__":
    cli()
