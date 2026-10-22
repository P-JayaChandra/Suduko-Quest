"""
Unit tests for core configuration, constants, events, exceptions, and logger.
"""
import pytest
from core.config import Config, get_config
from core.constants import Difficulty, RankTier, LEVEL_DEFINITIONS, RANK_TIER_CONFIG
from core.exceptions import InvalidBoardError, UnsolvablePuzzleError, MultipleSolutionsError
from core.events import EventBus, Event
from core.logger import get_logger

def test_config_defaults():
    cfg = get_config()
    assert cfg.ENV in ["development", "production", "testing"]
    assert cfg.MAX_MISTAKES == 3
    assert cfg.DEFAULT_HINTS == 3
    assert cfg.SOLVER_TIMEOUT_SECONDS > 0
    assert cfg.DATA_DIR.name == "data"

def test_difficulty_enum_mapping():
    assert Difficulty.from_level_num(1) == Difficulty.BEGINNER
    assert Difficulty.from_level_num(4) == Difficulty.MEDIUM
    assert Difficulty.from_level_num(10) == Difficulty.LEGEND
    assert Difficulty.from_level_num(999) == Difficulty.MEDIUM  # Default fallback

def test_level_definitions():
    assert len(LEVEL_DEFINITIONS) == 10
    for lvl in range(1, 11):
        defn = LEVEL_DEFINITIONS[lvl]
        assert "key" in defn
        assert "name" in defn
        assert "clues_range" in defn
        assert "xp" in defn
        min_c, max_c = defn["clues_range"]
        assert 16 <= min_c <= max_c <= 65

def test_rank_tiers():
    assert len(RANK_TIER_CONFIG) == 8
    names = [t["name"] for t in RANK_TIER_CONFIG]
    assert "BRONZE" in names
    assert "DIAMOND" in names
    assert "LEGEND" in names

def test_exceptions_details():
    err = InvalidBoardError("Cell occupied", row=2, col=3, value=5)
    assert err.code == "INVALID_BOARD"
    assert err.details["row"] == 2
    assert err.details["col"] == 3
    assert err.details["value"] == 5

    unsolv = UnsolvablePuzzleError()
    assert unsolv.code == "UNSOLVABLE_PUZZLE"

    mult = MultipleSolutionsError(count=5)
    assert mult.code == "MULTIPLE_SOLUTIONS"
    assert mult.details["solution_count"] == 5

def test_event_bus():
    EventBus.clear()
    received_events = []

    def on_game_completed(event: Event):
        received_events.append(event)

    EventBus.subscribe("game.completed", on_game_completed)
    EventBus.publish("game.completed", game_id="test_123", xp=250)

    assert len(received_events) == 1
    assert received_events[0].name == "game.completed"
    assert received_events[0].payload["game_id"] == "test_123"
    assert received_events[0].payload["xp"] == 250

def test_logger():
    log = get_logger("test_logger")
    assert log is not None
    assert log.name == "test_logger"
