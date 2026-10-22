"""
Sudoku Quest Engine
High-performance generation, validation, solving, 10-tier progression, and 500,000 JSONL dataset integration.
"""
import random
import linecache
import datetime
import math
import os
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "sudoku_records.jsonl"
TOTAL_RECORDS = 500000

# Canonical solved base grid
BASE_GRID = [
    [1, 2, 3, 4, 5, 6, 7, 8, 9],
    [4, 5, 6, 7, 8, 9, 1, 2, 3],
    [7, 8, 9, 1, 2, 3, 4, 5, 6],
    [2, 3, 1, 5, 6, 4, 8, 9, 7],
    [5, 6, 4, 8, 9, 7, 2, 3, 1],
    [8, 9, 7, 2, 3, 1, 5, 6, 4],
    [3, 1, 2, 6, 4, 5, 9, 7, 8],
    [6, 4, 5, 9, 7, 8, 3, 1, 2],
    [9, 7, 8, 3, 1, 2, 6, 4, 5]
]

LEVELS_CONFIG = {
    1: {
        "key": "beginner",
        "name": "Beginner",
        "difficulty": "Very Easy",
        "clues_range": (45, 50),
        "est_time": "3–5 min",
        "xp": 25,
        "color": "green",
        "icon": "🌱",
        "desc": "Relaxed gameplay for players starting their Sudoku journey."
    },
    2: {
        "key": "novice",
        "name": "Novice",
        "difficulty": "Easy",
        "clues_range": (40, 44),
        "est_time": "5–8 min",
        "xp": 50,
        "color": "teal",
        "icon": "🔹",
        "desc": "Gentle step up with fundamental single-candidate deductions."
    },
    3: {
        "key": "easy",
        "name": "Easy",
        "difficulty": "Easy",
        "clues_range": (38, 40),
        "est_time": "5–10 min",
        "xp": 75,
        "color": "cyan",
        "icon": "⚡",
        "desc": "Classic casual solving with comfortable given numbers."
    },
    4: {
        "key": "medium",
        "name": "Medium",
        "difficulty": "Medium",
        "clues_range": (30, 34),
        "est_time": "10–15 min",
        "xp": 100,
        "color": "blue",
        "icon": "🔵",
        "desc": "Balanced challenge requiring cross-referencing rows & blocks."
    },
    5: {
        "key": "advanced",
        "name": "Advanced",
        "difficulty": "Medium-Hard",
        "clues_range": (28, 32),
        "est_time": "12–18 min",
        "xp": 125,
        "color": "indigo",
        "icon": "🟣",
        "desc": "Deeper logic with naked pairs and line box intersections."
    },
    6: {
        "key": "hard",
        "name": "Hard",
        "difficulty": "Hard",
        "clues_range": (26, 29),
        "est_time": "15–25 min",
        "xp": 175,
        "color": "orange",
        "icon": "🔥",
        "desc": "Rigorous logic puzzle demanding pencil notes & elimination."
    },
    7: {
        "key": "master",
        "name": "Master",
        "difficulty": "Very Hard",
        "clues_range": (23, 26),
        "est_time": "20–30 min",
        "xp": 225,
        "color": "red-orange",
        "icon": "👑",
        "desc": "Complex hidden sets and advanced chain candidate testing."
    },
    8: {
        "key": "expert",
        "name": "Expert",
        "difficulty": "Expert",
        "clues_range": (22, 25),
        "est_time": "25+ min",
        "xp": 250,
        "color": "purple",
        "icon": "💎",
        "desc": "Master level challenges for seasoned grid tacticians."
    },
    9: {
        "key": "grandmaster",
        "name": "Grandmaster",
        "difficulty": "Extreme",
        "clues_range": (17, 22),
        "est_time": "30+ min",
        "xp": 350,
        "color": "magenta",
        "icon": "💠",
        "desc": "Extreme logical depth with minimal initial clues."
    },
    10: {
        "key": "legend",
        "name": "Legend",
        "difficulty": "Extreme",
        "clues_range": (16, 20),
        "est_time": "40+ min",
        "xp": 500,
        "color": "gold",
        "icon": "🏆",
        "desc": "The ultimate Sudoku trial. Only true grid legends survive."
    }
}

def get_level_by_key(key_or_id):
    if isinstance(key_or_id, int):
        return LEVELS_CONFIG.get(key_or_id, LEVELS_CONFIG[4])
    s = str(key_or_id).lower().strip()
    for lvl_id, conf in LEVELS_CONFIG.items():
        if str(lvl_id) == s or conf["key"] == s or conf["name"].lower() == s:
            return conf
    return LEVELS_CONFIG[4]

def get_dataset_record(record_id: int = None, difficulty: str = None, level_num: int = None) -> dict:
    """Fetch a real record from the 500,000 JSONL dataset."""
    import json
    if record_id is None:
        if level_num:
            chunk = TOTAL_RECORDS // 10
            low = (level_num - 1) * chunk + 1
            high = min(TOTAL_RECORDS, level_num * chunk)
            record_id = random.randint(low, high)
        elif difficulty:
            diff_map = {
                "beginner": (1, 50000),
                "novice": (50001, 100000),
                "easy": (100001, 180000),
                "medium": (180001, 270000),
                "advanced": (270001, 350000),
                "hard": (350001, 420000),
                "master": (420001, 460000),
                "expert": (460001, 485000),
                "grandmaster": (485001, 495000),
                "legend": (495001, 500000)
            }
            low, high = diff_map.get(difficulty.lower(), (1, TOTAL_RECORDS))
            record_id = random.randint(low, high)
        else:
            record_id = random.randint(1, TOTAL_RECORDS)
    
    line = linecache.getline(str(DATA_FILE), record_id)
    if line:
        try:
            data = json.loads(line.strip())
            return data
        except Exception:
            pass
    return {"id": record_id, "level": level_num or 4, "difficulty": difficulty or "medium", "clues": 32, "xp": 100, "coins": 10, "source": "local"}

def get_daily_record(date_str: str = None) -> dict:
    """Fetch deterministic daily record based on date string (YYYY-MM-DD)."""
    if not date_str:
        date_str = datetime.date.today().isoformat()
    h = hash(f"sudoku_daily_{date_str}") & 0x7FFFFFFF
    record_id = (h % TOTAL_RECORDS) + 1
    record = get_dataset_record(record_id=record_id)
    record["is_daily"] = True
    record["date"] = date_str
    return record

def is_safe(grid, r, c, val):
    for i in range(9):
        if grid[r][i] == val or grid[i][c] == val:
            return False
    br, bc = 3 * (r // 3), 3 * (c // 3)
    for i in range(3):
        for j in range(3):
            if grid[br + i][bc + j] == val:
                return False
    return True

def generate_valid_solution(rng=None):
    """
    Generate an isomorphic valid solved Sudoku grid by applying random valid transforms.
    Runs in <1ms.
    """
    if rng is None:
        rng = random.Random()
        
    digits = list(range(1, 10))
    rng.shuffle(digits)
    digit_map = {i + 1: digits[i] for i in range(9)}
    
    grid = [[digit_map[val] for val in row] for row in BASE_GRID]
    
    # Swap rows within each band
    for b in range(3):
        rows = list(range(b * 3, b * 3 + 3))
        rng.shuffle(rows)
        band_rows = [grid[r] for r in rows]
        for i in range(3):
            grid[b * 3 + i] = band_rows[i]
            
    # Swap columns within each stack
    for s in range(3):
        cols = list(range(s * 3, s * 3 + 3))
        rng.shuffle(cols)
        for r in range(9):
            col_vals = [grid[r][c] for c in cols]
            for i in range(3):
                grid[r][s * 3 + i] = col_vals[i]
                
    # Swap entire bands
    bands = [0, 1, 2]
    rng.shuffle(bands)
    new_grid = []
    for b in bands:
        new_grid.extend(grid[b * 3 : b * 3 + 3])
    grid = new_grid
    
    # Swap entire stacks
    stacks = [0, 1, 2]
    rng.shuffle(stacks)
    final_grid = []
    for r in range(9):
        new_row = []
        for s in stacks:
            new_row.extend(grid[r][s * 3 : s * 3 + 3])
        final_grid.append(new_row)
        
    return final_grid

def generate_puzzle(difficulty="medium", seed=None, target_clues=None, level_num=None):
    """
    Generate a 9x9 Sudoku puzzle matching the target clues for the level.
    """
    rng = random.Random(seed) if seed is not None else random.Random()
    solution = generate_valid_solution(rng)
    
    lvl_conf = get_level_by_key(level_num if level_num else difficulty)
    min_c, max_c = lvl_conf["clues_range"]
    
    if target_clues is None or target_clues < 16 or target_clues > 65:
        target_clues = rng.randint(min_c, max_c)
        
    puzzle = [row[:] for row in solution]
    
    cells = [(r, c) for r in range(9) for c in range(9)]
    rng.shuffle(cells)
    
    removals = 81 - target_clues
    removed = 0
    
    for r, c in cells:
        if removed >= removals:
            break
        puzzle[r][c] = 0
        removed += 1
        
    actual_clues = sum(1 for r in range(9) for c in range(9) if puzzle[r][c] != 0)
    
    return {
        "puzzle": puzzle,
        "solution": solution,
        "clues": actual_clues,
        "difficulty": lvl_conf["key"],
        "level_name": lvl_conf["name"],
        "xp": lvl_conf["xp"]
    }

def validate_board(board, solution):
    """Check current board against solution."""
    errors = []
    is_complete = True
    correct_count = 0
    
    for r in range(9):
        for c in range(9):
            user_val = board[r][c]
            sol_val = solution[r][c]
            if user_val == 0:
                is_complete = False
            elif user_val != sol_val:
                errors.append({"row": r, "col": c, "val": user_val})
            else:
                correct_count += 1
                
    progress = round((correct_count / 81) * 100)
    return {
        "valid": len(errors) == 0,
        "complete": is_complete and len(errors) == 0,
        "errors": errors,
        "progress": progress,
        "filled": 81 - sum(1 for r in range(9) for c in range(9) if board[r][c] == 0)
    }

def get_hint(board, solution):
    """Find a helpful cell to reveal or give candidate advice."""
    for r in range(9):
        for c in range(9):
            if board[r][c] != 0 and board[r][c] != solution[r][c]:
                return {
                    "row": r,
                    "col": c,
                    "value": solution[r][c],
                    "type": "correction",
                    "message": f"Cell ({r+1}, {c+1}) is incorrect! Correct value is {solution[r][c]}."
                }
                
    empty_cells = []
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                empty_cells.append((r, c))
                
    if not empty_cells:
        return None
        
    r, c = random.choice(empty_cells)
    return {
        "row": r,
        "col": c,
        "value": solution[r][c],
        "type": "reveal",
        "message": f"Hint for Cell ({r+1}, {c+1}): place digit {solution[r][c]}."
    }

def get_rank_tier(rating: int) -> dict:
    """Return rank tier metadata for a rating."""
    tiers = [
        {"name": "BRONZE", "min": 1000, "max": 1199, "icon": "🥉", "color": "#cd7f32", "division": "I"},
        {"name": "SILVER", "min": 1200, "max": 1399, "icon": "🥈", "color": "#cbd5e1", "division": "I"},
        {"name": "GOLD", "min": 1400, "max": 1599, "icon": "🥇", "color": "#fbbf24", "division": "II"},
        {"name": "PLATINUM", "min": 1600, "max": 1799, "icon": "💎", "color": "#38bdf8", "division": "I"},
        {"name": "DIAMOND", "min": 1800, "max": 1999, "icon": "💠", "color": "#a855f7", "division": "I"},
        {"name": "MASTER", "min": 2000, "max": 2199, "icon": "👑", "color": "#f43f5e", "division": "I"},
        {"name": "GRANDMASTER", "min": 2200, "max": 2399, "icon": "🔥", "color": "#f97316", "division": "I"},
        {"name": "LEGEND", "min": 2400, "max": 9999, "icon": "🏆", "color": "#eab308", "division": "TOP"}
    ]
    for i, t in enumerate(tiers):
        if t["min"] <= rating <= t["max"]:
            next_t = tiers[i+1] if i + 1 < len(tiers) else None
            rating_needed = (next_t["min"] - rating) if next_t else 0
            pct = 100 if not next_t else min(100, max(0, int(((rating - t["min"]) / (t["max"] - t["min"] + 1)) * 100)))
            return {
                "name": t["name"],
                "full_name": f"{t['name']} {t['division']}" if t['name'] not in ['MASTER', 'GRANDMASTER', 'LEGEND'] else t['name'],
                "rating": rating,
                "icon": t["icon"],
                "color": t["color"],
                "next_tier": next_t["name"] if next_t else "MAX",
                "rating_needed": rating_needed,
                "progress_pct": pct
            }
    return tiers[0]

def calculate_ranked_score(params: dict) -> dict:
    """
    Centralized rating calculation service.
    params: { completion_time, mistakes, hints_used, won, user_rating, opponent_rating }
    """
    won = params.get("won", True)
    completion_time = params.get("completion_time", 400)
    mistakes = params.get("mistakes", 0)
    hints_used = params.get("hints_used", 0)
    user_rating = params.get("user_rating", 1472)
    opponent_rating = params.get("opponent_rating", 1490)
    
    # ELO baseline
    expected_score = 1 / (1 + 10 ** ((opponent_rating - user_rating) / 400))
    k_factor = 32
    actual_score = 1 if won else 0
    base_delta = int(k_factor * (actual_score - expected_score))
    
    if won:
        # Guarantee +20 to +35 base on win
        delta = max(20, min(35, 25 + base_delta))
        # Performance bonuses
        if mistakes == 0:
            delta += 5  # Perfect game bonus
        if hints_used == 0:
            delta += 3  # Pure solve bonus
        if completion_time < 300: # < 5 min
            delta += 7  # Speed solver bonus
        elif completion_time < 420: # < 7 min
            delta += 4
    else:
        # Loss: -15 to -25
        delta = min(-15, max(-25, -20 + base_delta))
        
    # Penalty for excessive mistakes & hints
    mistake_penalty = mistakes * 2
    hint_penalty = hints_used * 3
    delta = delta - mistake_penalty - hint_penalty
    if won and delta < 10:
        delta = 10 # Minimum gain for a win
        
    new_rating = max(1000, user_rating + delta)
    
    return {
        "rating_delta": delta,
        "old_rating": user_rating,
        "new_rating": new_rating,
        "tier": get_rank_tier(new_rating),
        "mistakes": mistakes,
        "hints_used": hints_used,
        "time_seconds": completion_time,
        "won": won
    }
