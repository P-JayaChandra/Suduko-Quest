"""
Sudoku Quest - Authoritative Server-Side Achievements Engine
Evaluates gameplay events and unlocks database-persisted trophies atomically.
"""
import datetime
import db

MASTER_ACHIEVEMENTS = [
    # Progress
    {"code": "first_step", "cat": "progress", "icon": "🌱", "title": "First Step", "desc": "Complete your first Sudoku.", "xp": 50},
    {"code": "getting_started", "cat": "progress", "icon": "🔢", "title": "Getting Started", "desc": "Complete 5 puzzles.", "xp": 100},
    {"code": "puzzle_apprentice", "cat": "progress", "icon": "🧩", "title": "Puzzle Apprentice", "desc": "Complete 10 puzzles.", "xp": 150},
    {"code": "puzzle_master", "cat": "progress", "icon": "🧠", "title": "Puzzle Master", "desc": "Complete 50 puzzles.", "xp": 500},
    {"code": "sudoku_legend", "cat": "progress", "icon": "👑", "title": "Sudoku Legend", "desc": "Complete 100 puzzles.", "xp": 1000},

    # Speed
    {"code": "speed_demon", "cat": "speed", "icon": "⚡", "title": "Speed Demon", "desc": "Complete an Easy puzzle in under 5 minutes.", "xp": 100},
    {"code": "quick_thinker", "cat": "speed", "icon": "🚀", "title": "Quick Thinker", "desc": "Complete a Medium puzzle in under 8 minutes.", "xp": 150},
    {"code": "lightning_solver", "cat": "speed", "icon": "💨", "title": "Lightning Solver", "desc": "Complete a Hard puzzle in under 12 minutes.", "xp": 250},
    {"code": "master_speed", "cat": "speed", "icon": "⚡", "title": "Master Speed", "desc": "Complete an Expert puzzle in under 20 minutes.", "xp": 500},

    # Accuracy
    {"code": "perfect_solve", "cat": "accuracy", "icon": "🎯", "title": "Perfect Solve", "desc": "Complete a puzzle without making a mistake.", "xp": 150},
    {"code": "flawless", "cat": "accuracy", "icon": "💎", "title": "Flawless", "desc": "Complete 5 puzzles with zero mistakes.", "xp": 300},
    {"code": "precision_master", "cat": "accuracy", "icon": "🏹", "title": "Precision Master", "desc": "Complete 10 puzzles with zero mistakes.", "xp": 750},

    # Streak
    {"code": "streak_3", "cat": "streak", "icon": "🔥", "title": "Three Day Streak", "desc": "Play for 3 consecutive days.", "xp": 100},
    {"code": "streak_7", "cat": "streak", "icon": "🔥", "title": "Week Warrior", "desc": "Maintain a 7-day streak.", "xp": 250},
    {"code": "streak_14", "cat": "streak", "icon": "🔥", "title": "Fortnight Master", "desc": "Maintain a 14-day streak.", "xp": 500},
    {"code": "streak_30", "cat": "streak", "icon": "🔥", "title": "Monthly Master", "desc": "Maintain a 30-day streak.", "xp": 1000},

    # Mastery / Levels
    {"code": "lvl_beginner", "cat": "mastery", "icon": "🌱", "title": "Beginner", "desc": "Reach Beginner Level.", "xp": 25},
    {"code": "lvl_novice", "cat": "mastery", "icon": "🔹", "title": "Novice", "desc": "Reach Novice Level.", "xp": 50},
    {"code": "lvl_easy_master", "cat": "mastery", "icon": "⚡", "title": "Easy Master", "desc": "Complete the Easy level progression.", "xp": 100},
    {"code": "lvl_medium_master", "cat": "mastery", "icon": "🔵", "title": "Medium Master", "desc": "Complete the Medium level progression.", "xp": 150},
    {"code": "lvl_advanced", "cat": "mastery", "icon": "🟣", "title": "Advanced", "desc": "Reach Advanced Level.", "xp": 200},
    {"code": "lvl_hard_master", "cat": "mastery", "icon": "🔥", "title": "Hard Master", "desc": "Complete the Hard level progression.", "xp": 250},
    {"code": "lvl_master", "cat": "mastery", "icon": "👑", "title": "Master", "desc": "Reach Master Level.", "xp": 350},
    {"code": "lvl_expert", "cat": "mastery", "icon": "💎", "title": "Expert", "desc": "Reach Expert Level.", "xp": 400},
    {"code": "lvl_grandmaster", "cat": "mastery", "icon": "💠", "title": "Grandmaster", "desc": "Reach Grandmaster Level.", "xp": 450},
    {"code": "lvl_legend", "cat": "mastery", "icon": "🏆", "title": "Legend", "desc": "Reach Legend Level.", "xp": 500},

    # Ranked
    {"code": "first_ranked", "cat": "ranked", "icon": "🥉", "title": "First Ranked", "desc": "Complete your first Ranked match.", "xp": 100},
    {"code": "ranked_warrior", "cat": "ranked", "icon": "🏆", "title": "Ranked Warrior", "desc": "Win 10 Ranked matches.", "xp": 300},
    {"code": "rank_gold", "cat": "ranked", "icon": "💰", "title": "Gold Player", "desc": "Reach Gold rank.", "xp": 500},
    {"code": "rank_diamond", "cat": "ranked", "icon": "💎", "title": "Diamond Player", "desc": "Reach Diamond rank.", "xp": 1000},
    {"code": "rank_master", "cat": "ranked", "icon": "👑", "title": "Master Rank", "desc": "Reach Master rank.", "xp": 1500},
    {"code": "rank_grandmaster", "cat": "ranked", "icon": "🔥", "title": "Grandmaster Rank", "desc": "Reach Grandmaster rank.", "xp": 2500},
    {"code": "rank_legend", "cat": "ranked", "icon": "🏆", "title": "Ranked Legend", "desc": "Reach Legend rank.", "xp": 5000},

    # Special
    {"code": "no_hints", "cat": "special", "icon": "🧠", "title": "No Hints", "desc": "Complete 10 puzzles without using a hint.", "xp": 500},
    {"code": "clean_sweep", "cat": "special", "icon": "🎯", "title": "Clean Sweep", "desc": "Complete 3 consecutive puzzles without mistakes.", "xp": 300},
    {"code": "night_solver", "cat": "special", "icon": "🌙", "title": "Night Solver", "desc": "Complete a puzzle between 10 PM and 5 AM.", "xp": 100},
    {"code": "early_solver", "cat": "special", "icon": "☀️", "title": "Early Solver", "desc": "Complete a puzzle between 5 AM and 9 AM.", "xp": 100},
    {"code": "comeback", "cat": "special", "icon": "🔄", "title": "Comeback", "desc": "Complete a puzzle after previously failing a puzzle.", "xp": 150}
]

ACHIEVEMENT_BY_CODE = {a["code"]: a for a in MASTER_ACHIEVEMENTS}

def evaluate_achievements(user_id, game_session, user_stats=None, ranked_match=None):
    """
    Authoritatively evaluate game events against all achievement criteria.
    Returns list of newly unlocked achievement dictionaries.
    """
    if not user_stats:
        user_stats = db.get_user_statistics(user_id)
        
    user = db.get_user_by_id(user_id)
    if not user:
        return []
        
    unlocked_list = []
    
    def try_unlock(code):
        ach_def = ACHIEVEMENT_BY_CODE.get(code)
        if not ach_def:
            return
        if db.unlock_achievement(user_id, code, ach_def["xp"], ach_def["title"]):
            unlocked_list.append(ach_def)

    # Progress Criteria
    puzzles_solved = user.get("puzzles_solved", 0)
    if puzzles_solved >= 1:
        try_unlock("first_step")
    if puzzles_solved >= 5:
        try_unlock("getting_started")
    if puzzles_solved >= 10:
        try_unlock("puzzle_apprentice")
    if puzzles_solved >= 50:
        try_unlock("puzzle_master")
    if puzzles_solved >= 100:
        try_unlock("sudoku_legend")

    # Speed Criteria (for current game)
    if game_session and game_session.get("status") == "completed":
        elapsed = game_session.get("elapsed_seconds", 9999)
        diff = game_session.get("difficulty", "").lower()
        lvl = game_session.get("level_num", 1)
        
        if (diff in ["easy", "very easy"] or lvl <= 3) and elapsed < 300:
            try_unlock("speed_demon")
        if (diff in ["medium"] or lvl in [4, 5]) and elapsed < 480:
            try_unlock("quick_thinker")
        if (diff in ["hard"] or lvl in [6, 7]) and elapsed < 720:
            try_unlock("lightning_solver")
        if (diff in ["expert", "master", "grandmaster", "legend"] or lvl >= 8) and elapsed < 1200:
            try_unlock("master_speed")

        # Accuracy
        mistakes = game_session.get("mistakes", 0)
        if mistakes == 0:
            try_unlock("perfect_solve")
            
        flawless_count = user_stats.get("flawless_games", 0)
        if flawless_count >= 5:
            try_unlock("flawless")
        if flawless_count >= 10:
            try_unlock("precision_master")

        # Special Timing
        now = datetime.datetime.now()
        hour = now.hour
        if hour >= 22 or hour < 5:
            try_unlock("night_solver")
        elif 5 <= hour < 9:
            try_unlock("early_solver")

        if user.get("puzzles_failed", 0) > 0:
            try_unlock("comeback")

    # Streak Criteria
    curr_streak = user.get("current_streak", 0)
    best_streak = user.get("best_streak", 0)
    effective_streak = max(curr_streak, best_streak)
    if effective_streak >= 3:
        try_unlock("streak_3")
    if effective_streak >= 7:
        try_unlock("streak_7")
    if effective_streak >= 14:
        try_unlock("streak_14")
    if effective_streak >= 30:
        try_unlock("streak_30")

    # Mastery / Level
    lvl = user.get("level", 1)
    if lvl >= 1: try_unlock("lvl_beginner")
    if lvl >= 2: try_unlock("lvl_novice")
    if lvl >= 3: try_unlock("lvl_easy_master")
    if lvl >= 4: try_unlock("lvl_medium_master")
    if lvl >= 5: try_unlock("lvl_advanced")
    if lvl >= 6: try_unlock("lvl_hard_master")
    if lvl >= 7: try_unlock("lvl_master")
    if lvl >= 8: try_unlock("lvl_expert")
    if lvl >= 9: try_unlock("lvl_grandmaster")
    if lvl >= 10: try_unlock("lvl_legend")

    # Ranked
    ranked_wins = user.get("ranked_wins", 0)
    ranked_rating = user.get("ranked_rating", 1000)
    if ranked_match or ranked_wins > 0 or user.get("ranked_losses", 0) > 0:
        try_unlock("first_ranked")
    if ranked_wins >= 10:
        try_unlock("ranked_warrior")
    if ranked_rating >= 1400:
        try_unlock("rank_gold")
    if ranked_rating >= 1800:
        try_unlock("rank_diamond")
    if ranked_rating >= 2000:
        try_unlock("rank_master")
    if ranked_rating >= 2200:
        try_unlock("rank_grandmaster")
    if ranked_rating >= 2400:
        try_unlock("rank_legend")

    return unlocked_list
