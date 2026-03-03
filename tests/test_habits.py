import os, sys, pytest, gc, tempfile
from datetime import datetime, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from modules.habit import Habit
from modules.habit_manager import HabitManager
from modules import analytics
from modules import db_handler as db


@pytest.fixture(autouse=True)
def clean_db(tmp_path):
    """Use a unique temp file per test — avoids Windows file lock issues."""
    global TEST_DB
    TEST_DB = str(tmp_path / "test_habits.db")
    db.initialise_db(TEST_DB)
    yield
    gc.collect()  # Force-close any lingering SQLite connections on Windows


@pytest.fixture
def manager(): return HabitManager(TEST_DB)


TEST_DB = ""  # will be set by clean_db fixture

class TestHabitCreation:
    def test_valid_daily(self):
        h = Habit("Exercise", "daily")
        assert h.name == "Exercise" and h.periodicity == "daily"
    def test_valid_weekly(self):
        assert Habit("Journal", "weekly").periodicity == "weekly"
    def test_invalid_period_raises(self):
        with pytest.raises(ValueError): Habit("Bad", "monthly")
    def test_default_created_at(self):
        assert isinstance(Habit("T", "daily").created_at, datetime)
    def test_repr_contains_name(self):
        assert "Water" in repr(Habit("Water", "daily", habit_id=1))

class TestCheckOff:
    def test_adds_completion(self):
        h = Habit("Read", "daily")
        h.check_off(datetime(2025, 1, 5))
        assert len(h.completions) == 1
    def test_completions_sorted(self):
        h = Habit("Read", "daily")
        [h.check_off(datetime(2025, 1, d)) for d in [3, 1, 2]]
        assert h.completions == sorted(h.completions)
    def test_defaults_to_now(self):
        h = Habit("Read", "daily")
        before = datetime.now()
        h.check_off()
        assert before <= h.completions[0]
    def test_multiple_same_day(self):
        h = Habit("Water", "daily")
        b = datetime(2025, 1, 1)
        h.check_off(b.replace(hour=8)); h.check_off(b.replace(hour=20))
        assert len(h.completions) == 2

class TestStreaks:
    def test_daily_consecutive(self):
        h = Habit("Water", "daily")
        b = datetime(2025, 1, 1)
        [h.check_off(b + timedelta(days=i)) for i in range(7)]
        assert h.get_longest_streak() == 7
    def test_daily_with_gap(self):
        h = Habit("Water", "daily")
        b = datetime(2025, 1, 1)
        [h.check_off(b+timedelta(days=i)) for i in list(range(5))+list(range(6,10))]
        assert h.get_longest_streak() == 5
    def test_weekly_four_weeks(self):
        h = Habit("Journal", "weekly")
        b = datetime(2025, 1, 6)
        [h.check_off(b+timedelta(weeks=i)) for i in range(4)]
        assert h.get_longest_streak() == 4
    def test_weekly_with_gap(self):
        h = Habit("Journal", "weekly")
        b = datetime(2025, 1, 6)
        h.check_off(b)
        h.check_off(b+timedelta(weeks=1))
        h.check_off(b+timedelta(weeks=3))
        assert h.get_longest_streak() == 2
    def test_no_completions_zero(self):
        h = Habit("E", "daily")
        assert h.get_longest_streak() == 0
    def test_single_is_one(self):
        h = Habit("S", "daily")
        h.check_off(datetime(2025,1,1))
        assert h.get_longest_streak() == 1

class TestAnalytics:
    def _h(self):
        h1,h2,h3 = Habit("Water","daily"),Habit("Exercise","daily"),Habit("Journal","weekly")
        b = datetime(2025,1,1)
        [h1.check_off(b+timedelta(days=i)) for i in range(10)]
        [h2.check_off(b+timedelta(days=i)) for i in range(5)]
        [h3.check_off(b+timedelta(weeks=i)) for i in range(3)]
        return [h1,h2,h3]
    def test_get_all(self):
        assert len(analytics.get_all_habits(self._h())) == 3
    def test_filter_daily(self):
        d=analytics.get_habits_by_period(self._h(),"daily")
        assert len(d)==2
    def test_filter_weekly(self):
        w=analytics.get_habits_by_period(self._h(),"weekly")
        assert len(w)==1 and w[0].name=="Journal"
    def test_longest_all(self):
        b=analytics.get_longest_streak_all(self._h())
        assert b.name=="Water" and b.get_longest_streak()==10
    def test_longest_for(self):
        assert analytics.get_longest_streak_for(self._h()[1])==5
    def test_empty_returns_none(self):
        assert analytics.get_longest_streak_all([])==None
    def test_current_streaks_keys(self):
        s=analytics.get_current_streaks(self._h())
        assert all("name" in x and "current_streak" in x for x in s)
    def test_struggled(self):
        assert len(analytics.get_struggled_habits(self._h(),top_n=2))==2

class TestHabitManager:
    def test_create(self, manager):
        h=manager.create_habit("M","daily")
        assert h.habit_id is not None
    def test_duplicate_raises(self, manager):
        manager.create_habit("M","daily")
        with pytest.raises(ValueError): manager.create_habit("M","weekly")
    def test_delete(self, manager):
        manager.create_habit("T","weekly")
        manager.delete_habit("T")
        assert all(h.name!="T" for h in manager.get_all_habits())
    def test_delete_nonexistent(self, manager):
        with pytest.raises(ValueError): manager.delete_habit("Ghost")
    def test_checkoff(self, manager):
        manager.create_habit("Run","daily")
        ts=manager.check_off("Run")
        assert isinstance(ts,datetime)
    def test_checkoff_nonexistent(self, manager):
        with pytest.raises(ValueError): manager.check_off("Ghost")
    def test_empty_db(self, manager):
        assert manager.get_all_habits()==[]

class TestDatabase:
    def test_save_load(self):
        h=Habit("DBT","daily"); db.save_habit(h,TEST_DB)
        loaded=db.load_all_habits(TEST_DB)
        assert len(loaded)==1 and loaded[0].name=="DBT"
    def test_completion_persists(self):
        h=Habit("DBC","daily"); db.save_habit(h,TEST_DB)
        ts=datetime(2025,3,1,10,0); db.save_completion(h.habit_id,ts,TEST_DB)
        assert db.load_all_habits(TEST_DB)[0].completions[0]==ts
    def test_delete_cascades(self):
        h=Habit("DBD","weekly"); db.save_habit(h,TEST_DB)
        db.save_completion(h.habit_id,datetime(2025,3,1),TEST_DB)
        db.delete_habit(h.habit_id,TEST_DB)
        assert db.load_all_habits(TEST_DB)==[]
    def test_name_exists_true(self):
        h=Habit("DBE","daily"); db.save_habit(h,TEST_DB)
        assert db.habit_name_exists("DBE",TEST_DB) is True
    def test_name_exists_false(self):
        assert db.habit_name_exists("Ghost",TEST_DB) is False
    def test_multiple_habits(self):
        for n,p in [("A","daily"),("B","weekly"),("C","daily")]:
            db.save_habit(Habit(n,p),TEST_DB)
        assert len(db.load_all_habits(TEST_DB))==3
