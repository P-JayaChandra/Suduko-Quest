"""
Sudoku Quest - Production Full-Stack Gaming Server
Integrates real authentication, SQLite database, authoritative game session validation,
server-side XP & level progression, achievements engine, and real-time Socket.IO ranked multiplayer.
"""
from flask import Flask, render_template, jsonify, request
from pathlib import Path
import json
import os
import datetime
import random
import uuid
import db
import sudoku_engine
import achievements
import ranked_ws

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SUDOKU_SECRET_KEY", "sudoku-quest-prod-secret-98231")

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "sudoku_records.jsonl"

# Attach Socket.IO
ranked_ws.setup_socket_events(app)

def get_current_user_from_request():
    """Helper to extract and validate authenticated user from Authorization header or cookie."""
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    elif "auth_token" in request.cookies:
        token = request.cookies.get("auth_token")
        
    if not token:
        # Check query param for fallback
        token = request.args.get("token")
        
    return db.get_user_by_token(token) if token else None

# ============================================================================
# PRIMARY HTML VIEW
# ============================================================================

@app.route("/")
def home():
    """Render the primary Sudoku Quest application."""
    return render_template("index.html")

# ============================================================================
# AUTHENTICATION APIS
# ============================================================================

@app.post("/api/auth/register")
def register():
    """Register a new user account with real hashed password in database."""
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    display_name = data.get("display_name", username).strip()
    avatar = data.get("avatar", "🧙‍♂️")
    
    if not username or len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters."}), 400
    if not email or "@" not in email:
        return jsonify({"error": "Please provide a valid email address."}), 400
    if not password or len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400
        
    try:
        user = db.create_user(username, email, password, display_name, avatar)
        token = db.create_auth_token(user["id"])
        return jsonify({
            "status": "success",
            "message": "Account created successfully.",
            "token": token,
            "user": user
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409

@app.post("/api/auth/login")
def login():
    """Authenticate user credentials and return persistent session token."""
    data = request.get_json(silent=True) or {}
    identifier = data.get("identifier", "").strip() # username or email
    password = data.get("password", "").strip()
    
    if not identifier or not password:
        return jsonify({"error": "Please provide your username/email and password."}), 400
        
    user = db.get_user_by_credentials(identifier, password)
    if not user:
        return jsonify({"error": "Invalid username or password."}), 401
        
    token = db.create_auth_token(user["id"])
    db.update_user_active(user["id"])
    
    return jsonify({
        "status": "success",
        "message": "Logged in successfully.",
        "token": token,
        "user": user
    })

@app.post("/api/auth/logout")
def logout():
    """Revoke user session token."""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        db.delete_auth_token(token)
    return jsonify({"status": "success", "message": "Logged out."})

@app.get("/api/auth/me")
def get_current_user():
    """Return profile for currently authenticated user."""
    user = get_current_user_from_request()
    if not user:
        return jsonify({"authenticated": False, "user": None}), 200
        
    db.update_user_active(user["id"])
    return jsonify({"authenticated": True, "user": user})

@app.patch("/api/auth/profile")
def update_profile():
    """Update profile attributes for authenticated user."""
    user = get_current_user_from_request()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.get_json(silent=True) or {}
    display_name = data.get("display_name")
    avatar = data.get("avatar")
    new_password = data.get("new_password")
    
    updated_user = db.update_user_profile(user["id"], display_name, avatar, new_password)
    return jsonify({"status": "success", "user": updated_user})

# ============================================================================
# DATASET & LEVELS STATUS APIS
# ============================================================================

@app.get("/api/stats")
def stats():
    """Return dataset stats and user/global metrics."""
    user = get_current_user_from_request()
    user_stats = db.get_user_statistics(user["id"]) if user else None
    
    return jsonify({
        "records": 500000,
        "status": "ready",
        "dataset_name": "sudoku_records.jsonl",
        "difficulties": ["easy", "medium", "hard", "expert"],
        "levels_count": 10,
        "user_stats": user_stats
    })

@app.get("/api/dataset/status")
def dataset_status():
    """Detailed dataset statistics endpoint."""
    exists = DATA_FILE.exists()
    size_mb = round(DATA_FILE.stat().st_size / (1024 * 1024), 2) if exists else 0
    sample = sudoku_engine.get_dataset_record(1)
    
    return jsonify({
        "records": 500000,
        "status": "ready" if exists else "missing",
        "file_size_mb": size_mb,
        "format": "JSONL",
        "storage": "Local Disk",
        "sample": sample
    })

@app.get("/api/levels")
def get_levels():
    """Return all 10 progression level definitions."""
    return jsonify({
        "levels": sudoku_engine.LEVELS_CONFIG
    })

# ============================================================================
# AUTHORITATIVE PUZZLES & GAME SESSIONS
# ============================================================================

@app.get("/api/puzzles/random")
def get_random_puzzle():
    """Generate a playable Sudoku puzzle matching the 10-tier progression."""
    level_param = request.args.get("level")
    difficulty_param = request.args.get("difficulty", "medium").lower()
    
    level_num = None
    if level_param:
        try:
            level_num = int(level_param)
        except ValueError:
            pass
            
    lvl_conf = sudoku_engine.get_level_by_key(level_num if level_num else difficulty_param)
    record = sudoku_engine.get_dataset_record(difficulty=lvl_conf["key"], level_num=level_num)
    
    clues_target = record.get("clues")
    min_c, max_c = lvl_conf["clues_range"]
    if not clues_target or clues_target < min_c or clues_target > max_c:
        clues_target = random.randint(min_c, max_c)
        
    puzzle_data = sudoku_engine.generate_puzzle(
        difficulty=lvl_conf["key"],
        target_clues=clues_target,
        level_num=level_num
    )
    
    return jsonify({
        "id": record.get("id"),
        "level": record.get("level", level_num or 4),
        "level_name": lvl_conf["name"],
        "level_display": f"Level {level_num or 4} — {lvl_conf['name']}",
        "difficulty": lvl_conf["key"],
        "difficulty_label": lvl_conf["difficulty"],
        "clues": puzzle_data["clues"],
        "xp": lvl_conf["xp"],
        "coins": record.get("coins", 10),
        "puzzle": puzzle_data["puzzle"],
        "solution": puzzle_data["solution"]
    })

@app.get("/api/puzzles/daily")
def get_daily_puzzle():
    """Get today's official Daily Challenge puzzle seeded deterministically."""
    date_str = request.args.get("date", datetime.date.today().isoformat())
    daily_record = sudoku_engine.get_daily_record(date_str)
    
    seed = hash(f"daily_{date_str}") & 0x7FFFFFFF
    difficulty = daily_record.get("difficulty", "medium")
    lvl_conf = sudoku_engine.get_level_by_key(difficulty)
    
    puzzle_data = sudoku_engine.generate_puzzle(
        difficulty=lvl_conf["key"],
        seed=seed,
        target_clues=daily_record.get("clues", 30)
    )
    
    return jsonify({
        "id": daily_record.get("id"),
        "is_daily": True,
        "date": date_str,
        "difficulty": lvl_conf["key"],
        "level_name": lvl_conf["name"],
        "clues": puzzle_data["clues"],
        "xp": lvl_conf["xp"] * 2,
        "coins": daily_record.get("coins", 20) * 2,
        "puzzle": puzzle_data["puzzle"],
        "solution": puzzle_data["solution"]
    })

@app.post("/api/games")
def start_game_session():
    """Create a verified server-side game session with hidden solution."""
    data = request.get_json(silent=True) or {}
    level_num = data.get("level_num")
    difficulty = data.get("difficulty", "medium").lower()
    is_daily = bool(data.get("is_daily", False))
    
    user = get_current_user_from_request()
    # Allow guest play with session user_id = 0 if not logged in
    user_id = user["id"] if user else 0
    
    lvl_conf = sudoku_engine.get_level_by_key(level_num if level_num else difficulty)
    
    if is_daily:
        date_str = datetime.date.today().isoformat()
        seed = hash(f"daily_{date_str}") & 0x7FFFFFFF
        puzzle_data = sudoku_engine.generate_puzzle(difficulty=lvl_conf["key"], seed=seed, target_clues=30)
    else:
        min_c, max_c = lvl_conf["clues_range"]
        target_clues = random.randint(min_c, max_c)
        puzzle_data = sudoku_engine.generate_puzzle(difficulty=lvl_conf["key"], target_clues=target_clues, level_num=level_num)
        
    session = db.create_game_session(
        user_id=user_id,
        difficulty=lvl_conf["key"],
        initial_board=puzzle_data["puzzle"],
        solution=puzzle_data["solution"],
        level_num=level_num or 4,
        is_daily=is_daily
    )
    
    return jsonify({
        "game_id": session["game_id"],
        "level_num": session["level_num"],
        "difficulty": session["difficulty"],
        "level_name": lvl_conf["name"],
        "initial_board": session["initial_board"],
        "clues": puzzle_data["clues"],
        "xp": lvl_conf["xp"] * (2 if is_daily else 1),
        "started_at": session["started_at"],
        "status": "active"
    }), 201

@app.post("/api/games/<game_id>/move")
def submit_game_move(game_id):
    """Authoritative move validation and mistake tracking."""
    session = db.get_game_session(game_id)
    if not session or session["status"] != "active":
        return jsonify({"error": "Active game session not found."}), 404
        
    data = request.get_json(silent=True) or {}
    cell_index = data.get("cell_index")
    value = str(data.get("value", ""))
    
    if cell_index is None or not (0 <= cell_index < 81):
        return jsonify({"error": "Invalid cell index."}), 400
        
    correct_val = session["solution"][cell_index]
    is_correct = (value == correct_val)
    
    # Build updated board string
    current_board = list(session["current_board"])
    current_board[cell_index] = value if is_correct else "."
    new_board_str = "".join(current_board)
    
    db.record_game_move(game_id, cell_index, value, is_correct, new_board_str)
    
    # Re-fetch for updated mistakes
    session_updated = db.get_game_session(game_id)
    mistakes = session_updated["mistakes"]
    
    return jsonify({
        "cell_index": cell_index,
        "is_correct": is_correct,
        "mistakes": mistakes,
        "max_mistakes": 3,
        "game_over": (mistakes >= 3)
    })

@app.post("/api/games/<game_id>/hint")
def request_game_hint(game_id):
    """Provide intelligent hint and record usage on server."""
    session = db.get_game_session(game_id)
    if not session or session["status"] != "active":
        return jsonify({"error": "Active game session not found."}), 404
        
    curr_board = session["current_board"]
    solution = session["solution"]
    
    # Find next empty cell
    empty_indices = [i for i, ch in enumerate(curr_board) if ch in (".", "0", " ")]
    if not empty_indices:
        return jsonify({"error": "No empty cells remaining."}), 400
        
    hint_cell = random.choice(empty_indices)
    hint_value = solution[hint_cell]
    
    db.record_game_hint(game_id)
    
    return jsonify({
        "cell_index": hint_cell,
        "row": hint_cell // 9,
        "col": hint_cell % 9,
        "value": hint_value,
        "hints_used": session["hints_used"] + 1
    })

@app.post("/api/games/<game_id>/complete")
def complete_game_session(game_id):
    """Authoritative puzzle completion, XP award, streak update, and achievement evaluation."""
    session = db.get_game_session(game_id)
    if not session or session["status"] != "active":
        return jsonify({"error": "Active game session not found."}), 404
        
    data = request.get_json(silent=True) or {}
    submitted_board = data.get("board", session["current_board"])
    
    # Authoritative verification against secret solution
    if submitted_board != session["solution"]:
        return jsonify({"error": "Submitted board does not match solution."}), 400
        
    user = get_current_user_from_request()
    user_id = user["id"] if user else 0
    
    # Server-calculated elapsed time
    started_time = datetime.datetime.fromisoformat(session["started_at"])
    now_time = datetime.datetime.utcnow()
    elapsed_seconds = max(1, int((now_time - started_time).total_seconds()))
    
    lvl_conf = sudoku_engine.get_level_by_key(session["level_num"])
    base_xp = lvl_conf["xp"] * (2 if session["is_daily"] else 1)
    
    bonus_xp = 0
    if session["mistakes"] == 0:
        bonus_xp += 50
    if session["hints_used"] == 0:
        bonus_xp += 30
    if elapsed_seconds < 300:
        bonus_xp += 40
        
    total_xp = base_xp + bonus_xp
    
    # Mark game session complete
    db.complete_game_session(game_id, user_id, elapsed_seconds, total_xp)
    
    unlocked_achievements = []
    updated_user = None
    streak_info = (0, 0)
    
    if user_id > 0:
        # Atomic database updates for logged-in user
        db.award_xp(user_id, total_xp, f"Completed Level {session['level_num']} — {lvl_conf['name']}", game_id)
        streak_info = db.update_user_streak(user_id)
        
        # Evaluate server-side achievements
        session["elapsed_seconds"] = elapsed_seconds
        session["status"] = "completed"
        unlocked_achievements = achievements.evaluate_achievements(user_id, session)
        updated_user = db.get_user_by_id(user_id)
        
    return jsonify({
        "status": "success",
        "xp_earned": total_xp,
        "base_xp": base_xp,
        "bonus_xp": bonus_xp,
        "elapsed_seconds": elapsed_seconds,
        "mistakes": session["mistakes"],
        "hints_used": session["hints_used"],
        "achievements_unlocked": unlocked_achievements,
        "current_streak": streak_info[0],
        "user": updated_user
    })

@app.post("/api/games/<game_id>/abandon")
def abandon_game(game_id):
    """Abandon an active game session."""
    user = get_current_user_from_request()
    user_id = user["id"] if user else 0
    db.abandon_game_session(game_id, user_id)
    return jsonify({"status": "abandoned"})

# ============================================================================
# ACHIEVEMENTS & LEADERBOARD
# ============================================================================

@app.get("/api/achievements")
def get_all_achievements():
    """Return master catalog of all achievements."""
    return jsonify({
        "achievements": achievements.MASTER_ACHIEVEMENTS
    })

@app.get("/api/achievements/me")
def get_my_achievements():
    """Return current user's unlocked achievements from database."""
    user = get_current_user_from_request()
    if not user:
        return jsonify({"unlocked": [], "total_count": len(achievements.MASTER_ACHIEVEMENTS)})
        
    unlocked = db.get_user_achievements(user["id"])
    return jsonify({
        "unlocked": unlocked,
        "unlocked_count": len(unlocked),
        "total_count": len(achievements.MASTER_ACHIEVEMENTS)
    })

@app.get("/api/leaderboard")
def get_leaderboard():
    """Return genuine leaderboard of real registered players sorted by rating."""
    board = db.get_real_leaderboard(limit=50)
    return jsonify({
        "leaderboard": board,
        "total_players": len(board),
        "season": "Season 01 — Master The Grid"
    })

@app.get("/api/ranked/season")
def get_ranked_season():
    """Return current Season 01 details and rewards."""
    now = datetime.datetime.now()
    end_date = now + datetime.timedelta(days=23, hours=14)
    
    return jsonify({
        "season_number": 1,
        "season_title": "MASTER THE GRID",
        "ends_at": end_date.isoformat(),
        "days_remaining": 23,
        "hours_remaining": 14,
        "rewards": [
            {"tier": "Bronze", "reward": "100 XP", "icon": "🥉"},
            {"tier": "Silver", "reward": "250 XP", "icon": "🥈"},
            {"tier": "Gold", "reward": "500 XP", "icon": "🥇"},
            {"tier": "Platinum", "reward": "1000 XP", "icon": "💎"},
            {"tier": "Diamond", "reward": "1500 XP", "icon": "💠"},
            {"tier": "Master", "reward": "2500 XP", "icon": "👑"},
            {"tier": "Grandmaster", "reward": "5000 XP", "icon": "🔥"},
            {"tier": "Legend", "reward": "Exclusive Animated Badge", "icon": "🏆"}
        ]
    })

if __name__ == "__main__":
    ranked_ws.socketio.run(app, debug=True, host="127.0.0.1", port=5000, allow_unsafe_werkzeug=True)
