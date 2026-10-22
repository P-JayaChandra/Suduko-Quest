"""
Sudoku Quest - Global Constants and Enumerations
Defines system-wide enums, difficulty mappings, rank tiers, grid geometries, and scoring factors.
"""
from enum import Enum, IntEnum, auto
from typing import Dict, Tuple, Any

class GridDimension(IntEnum):
    """Standard grid size dimensions."""
    MINI_4 = 4
    JUNIOR_6 = 6
    CLASSIC_9 = 9
    MAXI_12 = 12
    MONSTER_16 = 16

class Difficulty(str, Enum):
    """10-Tier progression difficulty levels."""
    BEGINNER = "beginner"
    NOVICE = "novice"
    EASY = "easy"
    MEDIUM = "medium"
    ADVANCED = "advanced"
    HARD = "hard"
    MASTER = "master"
    EXPERT = "expert"
    GRANDMASTER = "grandmaster"
    LEGEND = "legend"

    @classmethod
    def from_level_num(cls, level_num: int) -> "Difficulty":
        mapping = {
            1: cls.BEGINNER,
            2: cls.NOVICE,
            3: cls.EASY,
            4: cls.MEDIUM,
            5: cls.ADVANCED,
            6: cls.HARD,
            7: cls.MASTER,
            8: cls.EXPERT,
            9: cls.GRANDMASTER,
            10: cls.LEGEND,
        }
        return mapping.get(level_num, cls.MEDIUM)

class RankTier(str, Enum):
    """Ranked competitive multiplayer league tiers."""
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"
    DIAMOND = "DIAMOND"
    MASTER = "MASTER"
    GRANDMASTER = "GRANDMASTER"
    LEGEND = "LEGEND"

class GameStatus(str, Enum):
    """Status of an authoritative game session."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    FAILED = "failed"

class MoveType(str, Enum):
    """Player board action types."""
    DIGIT = "digit"
    NOTE = "note"
    ERASE = "erase"
    HINT = "hint"
    UNDO = "undo"
    REDO = "redo"

# Clue counts and target parameters per level
LEVEL_DEFINITIONS: Dict[int, Dict[str, Any]] = {
    1: {
        "key": Difficulty.BEGINNER.value,
        "name": "Beginner",
        "difficulty": "Very Easy",
        "clues_range": (45, 50),
        "est_time": "3–5 min",
        "xp": 25,
        "color": "#10b981",
        "icon": "🌱",
        "desc": "Relaxed gameplay for players starting their Sudoku journey.",
    },
    2: {
        "key": Difficulty.NOVICE.value,
        "name": "Novice",
        "difficulty": "Easy",
        "clues_range": (40, 44),
        "est_time": "5–8 min",
        "xp": 50,
        "color": "#14b8a6",
        "icon": "🔹",
        "desc": "Gentle step up with fundamental single-candidate deductions.",
    },
    3: {
        "key": Difficulty.EASY.value,
        "name": "Easy",
        "difficulty": "Easy",
        "clues_range": (38, 40),
        "est_time": "5–10 min",
        "xp": 75,
        "color": "#06b6d4",
        "icon": "⚡",
        "desc": "Classic casual solving with comfortable given numbers.",
    },
    4: {
        "key": Difficulty.MEDIUM.value,
        "name": "Medium",
        "difficulty": "Medium",
        "clues_range": (30, 34),
        "est_time": "10–15 min",
        "xp": 100,
        "color": "#3b82f6",
        "icon": "🔵",
        "desc": "Balanced challenge requiring cross-referencing rows & blocks.",
    },
    5: {
        "key": Difficulty.ADVANCED.value,
        "name": "Advanced",
        "difficulty": "Medium-Hard",
        "clues_range": (28, 32),
        "est_time": "12–18 min",
        "xp": 125,
        "color": "#6366f1",
        "icon": "🟣",
        "desc": "Deeper logic with naked pairs and line box intersections.",
    },
    6: {
        "key": Difficulty.HARD.value,
        "name": "Hard",
        "difficulty": "Hard",
        "clues_range": (26, 29),
        "est_time": "15–25 min",
        "xp": 175,
        "color": "#f97316",
        "icon": "🔥",
        "desc": "Rigorous logic puzzle demanding pencil notes & elimination.",
    },
    7: {
        "key": Difficulty.MASTER.value,
        "name": "Master",
        "difficulty": "Very Hard",
        "clues_range": (23, 26),
        "est_time": "20–30 min",
        "xp": 225,
        "color": "#ef4444",
        "icon": "👑",
        "desc": "Complex hidden sets and advanced chain candidate testing.",
    },
    8: {
        "key": Difficulty.EXPERT.value,
        "name": "Expert",
        "difficulty": "Expert",
        "clues_range": (22, 25),
        "est_time": "25+ min",
        "xp": 250,
        "color": "#a855f7",
        "icon": "💎",
        "desc": "Master level challenges for seasoned grid tacticians.",
    },
    9: {
        "key": Difficulty.GRANDMASTER.value,
        "name": "Grandmaster",
        "difficulty": "Extreme",
        "clues_range": (17, 22),
        "est_time": "30+ min",
        "xp": 350,
        "color": "#ec4899",
        "icon": "💠",
        "desc": "Extreme logical depth with minimal initial clues.",
    },
    10: {
        "key": Difficulty.LEGEND.value,
        "name": "Legend",
        "difficulty": "Extreme",
        "clues_range": (16, 20),
        "est_time": "40+ min",
        "xp": 500,
        "color": "#eab308",
        "icon": "🏆",
        "desc": "The ultimate Sudoku trial. Only true grid legends survive.",
    },
}

# Competitive Ranked Tiers definition
RANK_TIER_CONFIG = [
    {"name": RankTier.BRONZE.value, "min": 1000, "max": 1199, "icon": "🥉", "color": "#cd7f32", "division": "I"},
    {"name": RankTier.SILVER.value, "min": 1200, "max": 1399, "icon": "🥈", "color": "#cbd5e1", "division": "I"},
    {"name": RankTier.GOLD.value, "min": 1400, "max": 1599, "icon": "🥇", "color": "#fbbf24", "division": "II"},
    {"name": RankTier.PLATINUM.value, "min": 1600, "max": 1799, "icon": "💎", "color": "#38bdf8", "division": "I"},
    {"name": RankTier.DIAMOND.value, "min": 1800, "max": 1999, "icon": "💠", "color": "#a855f7", "division": "I"},
    {"name": RankTier.MASTER.value, "min": 2000, "max": 2199, "icon": "👑", "color": "#f43f5e", "division": "I"},
    {"name": RankTier.GRANDMASTER.value, "min": 2200, "max": 2399, "icon": "🔥", "color": "#f97316", "division": "I"},
    {"name": RankTier.LEGEND.value, "min": 2400, "max": 9999, "icon": "🏆", "color": "#eab308", "division": "TOP"},
]

MAX_ALLOWED_MISTAKES = 3
DEFAULT_HINTS_PER_GAME = 3
CANONICAL_CELL_COUNT = 81
GRID_SIZE = 9
BOX_SIZE = 3
TOTAL_CONSTRAINTS_9X9 = 324  # 81 cell constraints + 81 row-digit + 81 col-digit + 81 box-digit
TOTAL_POSSIBILITIES_9X9 = 729  # 81 cells * 9 digits
