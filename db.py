"""
Sudoku Quest - Database & Persistence Layer
Production SQLite database engine for real authentication, sessions,
games, XP transactions, achievements, streaks, ranked matches, and leaderboards.
"""
import sqlite3
import os
import uuid
import datetime
import hashlib
import hmac
import secrets
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "sudoku_quest.db"

def get_db():
    """Create a database connection configured for WAL mode and row mapping."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=20.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db():
    """Initialize all production database tables."""
    conn = get_db()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL COLLATE NOCASE,
        email TEXT UNIQUE NOT NULL COLLATE NOCASE,
        password_hash TEXT NOT NULL,
        display_name TEXT NOT NULL,
        avatar TEXT DEFAULT '🧙‍♂️',
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        current_streak INTEGER DEFAULT 0,
        best_streak INTEGER DEFAULT 0,
        last_played_date TEXT,
        puzzles_solved INTEGER DEFAULT 0,
        puzzles_failed INTEGER DEFAULT 0,
        ranked_rating INTEGER DEFAULT 1000,
        ranked_tier TEXT DEFAULT 'Bronze I',
        ranked_wins INTEGER DEFAULT 0,
        ranked_losses INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        last_active_at TEXT NOT NULL
    );
    """)

    # Auth Tokens Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS auth_tokens (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # Game Sessions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS game_sessions (
        id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        puzzle_id TEXT,
        difficulty TEXT NOT NULL,
        level_num INTEGER DEFAULT 1,
        initial_board TEXT NOT NULL,
        solution TEXT NOT NULL,
        current_board TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        mistakes INTEGER DEFAULT 0,
        hints_used INTEGER DEFAULT 0,
        consecutive_mistake_free INTEGER DEFAULT 0,
        started_at TEXT NOT NULL,
        completed_at TEXT,
        elapsed_seconds INTEGER DEFAULT 0,
        xp_awarded INTEGER DEFAULT 0,
        is_daily INTEGER DEFAULT 0,
        is_ranked INTEGER DEFAULT 0,
        ranked_match_id TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # User Achievements Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        achievement_code TEXT NOT NULL,
        unlocked_at TEXT NOT NULL,
        UNIQUE(user_id, achievement_code),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # XP Transactions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS xp_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        game_session_id TEXT,
        amount INTEGER NOT NULL,
        reason TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # Daily Challenges Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_challenges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_str TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        game_session_id TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        completed_at TEXT,
        score INTEGER DEFAULT 0,
        UNIQUE(date_str, user_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (game_session_id) REFERENCES game_sessions (id) ON DELETE CASCADE
    );
    """)

    # Ranked Matches Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ranked_matches (
        id TEXT PRIMARY KEY,
        player1_id INTEGER NOT NULL,
        player2_id INTEGER NOT NULL,
        puzzle_id TEXT NOT NULL,
        initial_board TEXT NOT NULL,
        solution TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        winner_id INTEGER,
        p1_rating_before INTEGER NOT NULL,
        p1_rating_after INTEGER,
        p2_rating_before INTEGER NOT NULL,
        p2_rating_after INTEGER,
        p1_progress INTEGER DEFAULT 0,
        p2_progress INTEGER DEFAULT 0,
        p1_mistakes INTEGER DEFAULT 0,
        p2_mistakes INTEGER DEFAULT 0,
        p1_time INTEGER,
        p2_time INTEGER,
        started_at TEXT NOT NULL,
        completed_at TEXT,
        FOREIGN KEY (player1_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (player2_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # Ensure default Guest user exists for unauthenticated gameplay sessions
    cursor.execute("""
    INSERT OR IGNORE INTO users (
        id, username, email, password_hash, display_name, avatar,
        created_at, updated_at, last_active_at
    ) VALUES (0, 'guest', 'guest@sudokuquest.local', 'none', 'Guest Player', '🧙‍♂️', '2026-01-01T00:00:00', '2026-01-01T00:00:00', '2026-01-01T00:00:00')
    """)

    conn.commit()
    conn.close()

# ============================================================================
# USER & AUTHENTICATION LOGIC
# ============================================================================

def create_user(username, email, password, display_name=None, avatar="🧙‍♂️"):
    """Register a new user with hashed password."""
    conn = get_db()
    cursor = conn.cursor()
    
    username = username.strip()
    email = email.strip().lower()
    display_name = (display_name or username).strip()
    
    # Check duplicate
    cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
    if cursor.fetchone():
        conn.close()
        raise ValueError("Username or email already exists.")
        
    pwd_hash = generate_password_hash(password)
    now_iso = datetime.datetime.utcnow().isoformat()
    
    cursor.execute("""
    INSERT INTO users (
        username, email, password_hash, display_name, avatar,
        xp, level, current_streak, best_streak, ranked_rating, ranked_tier,
        created_at, updated_at, last_active_at
    ) VALUES (?, ?, ?, ?, ?, 0, 1, 0, 0, 1000, 'Bronze I', ?, ?, ?)
    """, (username, email, pwd_hash, display_name, avatar, now_iso, now_iso, now_iso))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return get_user_by_id(user_id)

def get_user_by_id(user_id):
    """Retrieve user dictionary by ID without password hash."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, username, email, display_name, avatar, xp, level,
           current_streak, best_streak, last_played_date, puzzles_solved, puzzles_failed,
           ranked_rating, ranked_tier, ranked_wins, ranked_losses,
           created_at, updated_at, last_active_at
    FROM users WHERE id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_credentials(identifier, password):
    """Validate username/email and password."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (identifier.strip(), identifier.strip().lower()))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    user_dict = dict(row)
    if not check_password_hash(user_dict["password_hash"], password):
        return None
        
    del user_dict["password_hash"]
    return user_dict

def update_user_active(user_id):
    """Touch user's last active timestamp."""
    conn = get_db()
    now_iso = datetime.datetime.utcnow().isoformat()
    conn.execute("UPDATE users SET last_active_at = ? WHERE id = ?", (now_iso, user_id))
    conn.commit()
    conn.close()

def update_user_profile(user_id, display_name=None, avatar=None, new_password=None):
    """Update profile attributes and optional password."""
    conn = get_db()
    cursor = conn.cursor()
    now_iso = datetime.datetime.utcnow().isoformat()
    
    updates = ["updated_at = ?"]
    params = [now_iso]
    
    if display_name:
        updates.append("display_name = ?")
        params.append(display_name.strip())
        
    if avatar:
        updates.append("avatar = ?")
        params.append(avatar.strip())
        
    if new_password:
        updates.append("password_hash = ?")
        params.append(generate_password_hash(new_password))
        
    params.append(user_id)
    cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    conn.close()
    
    return get_user_by_id(user_id)

def create_auth_token(user_id, days=30):
    """Create a persistent secure authentication token."""
    token = secrets.token_hex(32)
    now = datetime.datetime.utcnow()
    expires = now + datetime.timedelta(days=days)
    
    conn = get_db()
    conn.execute("""
    INSERT INTO auth_tokens (token, user_id, created_at, expires_at)
    VALUES (?, ?, ?, ?)
    """, (token, user_id, now.isoformat(), expires.isoformat()))
    conn.commit()
    conn.close()
    
    return token

def get_user_by_token(token):
    """Validate auth token and return user."""
    if not token:
        return None
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT u.id, u.username, u.email, u.display_name, u.avatar, u.xp, u.level,
           u.current_streak, u.best_streak, u.last_played_date, u.puzzles_solved, u.puzzles_failed,
           u.ranked_rating, u.ranked_tier, u.ranked_wins, u.ranked_losses,
           u.created_at, u.updated_at, u.last_active_at,
           t.expires_at
    FROM auth_tokens t
    JOIN users u ON t.user_id = u.id
    WHERE t.token = ?
    """, (token,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    user_dict = dict(row)
    expires_at = datetime.datetime.fromisoformat(user_dict.pop("expires_at"))
    if datetime.datetime.utcnow() > expires_at:
        delete_auth_token(token)
        return None
        
    return user_dict

def delete_auth_token(token):
    """Revoke session token on logout."""
    conn = get_db()
    conn.execute("DELETE FROM auth_tokens WHERE token = ?", (token,))
    conn.commit()
    conn.close()

# ============================================================================
# XP, PROGRESSION & STREAKS
# ============================================================================

LEVEL_THRESHOLDS = [
    (1, 0, "Beginner"),
    (2, 100, "Novice"),
    (3, 250, "Easy Master"),
    (4, 500, "Medium Master"),
    (5, 850, "Advanced"),
    (6, 1300, "Hard Master"),
    (7, 1900, "Master"),
    (8, 2700, "Expert"),
    (9, 3700, "Grandmaster"),
    (10, 5000, "Legend")
]

def calculate_level_from_xp(xp):
    """Compute level number from cumulative XP."""
    current_level = 1
    for lvl, min_xp, _ in LEVEL_THRESHOLDS:
        if xp >= min_xp:
            current_level = lvl
        else:
            break
    return current_level

def award_xp(user_id, amount, reason, game_session_id=None):
    """Atomically award XP and log transaction."""
    if amount <= 0:
        return get_user_by_id(user_id)
        
    conn = get_db()
    cursor = conn.cursor()
    now_iso = datetime.datetime.utcnow().isoformat()
    
    cursor.execute("""
    INSERT INTO xp_transactions (user_id, game_session_id, amount, reason, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, game_session_id, amount, reason, now_iso))
    
    cursor.execute("SELECT xp FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
        
    new_xp = row["xp"] + amount
    new_level = calculate_level_from_xp(new_xp)
    
    cursor.execute("""
    UPDATE users SET xp = ?, level = ?, updated_at = ? WHERE id = ?
    """, (new_xp, new_level, now_iso, user_id))
    
    conn.commit()
    conn.close()
    return get_user_by_id(user_id)

def update_user_streak(user_id, play_date_str=None):
    """Atomically evaluate and update user consecutive day streak."""
    if not play_date_str:
        play_date_str = datetime.date.today().isoformat()
        
    play_date = datetime.date.fromisoformat(play_date_str)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT current_streak, best_streak, last_played_date FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return 0, 0
        
    curr_streak = user["current_streak"] or 0
    best_streak = user["best_streak"] or 0
    last_date_str = user["last_played_date"]
    
    if not last_date_str:
        curr_streak = 1
    else:
        last_date = datetime.date.fromisoformat(last_date_str)
        delta_days = (play_date - last_date).days
        if delta_days == 0:
            pass # Same day play, streak preserved
        elif delta_days == 1:
            curr_streak += 1
        elif delta_days > 1:
            curr_streak = 1
            
    best_streak = max(best_streak, curr_streak)
    now_iso = datetime.datetime.utcnow().isoformat()
    
    cursor.execute("""
    UPDATE users
    SET current_streak = ?, best_streak = ?, last_played_date = ?, updated_at = ?
    WHERE id = ?
    """, (curr_streak, best_streak, play_date_str, now_iso, user_id))
    
    conn.commit()
    conn.close()
    return curr_streak, best_streak

# ============================================================================
# GAME SESSIONS
# ============================================================================

def to_board_str(board):
    """Normalize any 2D grid, list, or string into flat 81-char string."""
    if isinstance(board, str):
        return board
    if isinstance(board, list):
        if len(board) == 9 and isinstance(board[0], list):
            return "".join("." if val in (0, ".", "0", None) else str(val) for row in board for val in row)
        elif len(board) == 81:
            return "".join("." if val in (0, ".", "0", None) else str(val) for val in board)
    return str(board)

def create_game_session(user_id, difficulty, initial_board, solution, level_num=1, is_daily=False, is_ranked=False, ranked_match_id=None):
    """Create a verified server-side game session with secret solution."""
    game_id = f"gs_{uuid.uuid4().hex[:16]}"
    now_iso = datetime.datetime.utcnow().isoformat()
    
    init_str = to_board_str(initial_board)
    sol_str = to_board_str(solution)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO game_sessions (
        id, user_id, difficulty, level_num, initial_board, solution, current_board,
        status, mistakes, hints_used, started_at, is_daily, is_ranked, ranked_match_id
    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'active', 0, 0, ?, ?, ?, ?)
    """, (
        game_id, user_id, difficulty, level_num, init_str, sol_str, init_str,
        now_iso, 1 if is_daily else 0, 1 if is_ranked else 0, ranked_match_id
    ))
    conn.commit()
    conn.close()
    
    return {
        "game_id": game_id,
        "difficulty": difficulty,
        "level_num": level_num,
        "initial_board": init_str,
        "started_at": now_iso,
        "status": "active"
    }


def get_game_session(game_id):
    """Get active game session data."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM game_sessions WHERE id = ?", (game_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def record_game_move(game_id, cell_index, value, is_correct, new_board_str):
    """Update board state and increment mistake count if wrong."""
    conn = get_db()
    cursor = conn.cursor()
    
    if is_correct:
        cursor.execute("""
        UPDATE game_sessions
        SET current_board = ?
        WHERE id = ? AND status = 'active'
        """, (new_board_str, game_id))
    else:
        cursor.execute("""
        UPDATE game_sessions
        SET mistakes = mistakes + 1
        WHERE id = ? AND status = 'active'
        """, (game_id,))
        
    conn.commit()
    conn.close()

def record_game_hint(game_id):
    """Increment server-side hint usage count."""
    conn = get_db()
    conn.execute("UPDATE game_sessions SET hints_used = hints_used + 1 WHERE id = ? AND status = 'active'", (game_id,))
    conn.commit()
    conn.close()

def complete_game_session(game_id, user_id, elapsed_seconds, xp_earned):
    """Mark game session as completed and increment solved count."""
    now_iso = datetime.datetime.utcnow().isoformat()
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    UPDATE game_sessions
    SET status = 'completed', completed_at = ?, elapsed_seconds = ?, xp_awarded = ?
    WHERE id = ? AND user_id = ?
    """, (now_iso, elapsed_seconds, xp_earned, game_id, user_id))
    
    cursor.execute("""
    UPDATE users
    SET puzzles_solved = puzzles_solved + 1, updated_at = ?
    WHERE id = ?
    """, (now_iso, user_id))
    
    conn.commit()
    conn.close()

def abandon_game_session(game_id, user_id):
    """Mark game session as abandoned."""
    now_iso = datetime.datetime.utcnow().isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE game_sessions
    SET status = 'abandoned', completed_at = ?
    WHERE id = ? AND user_id = ? AND status = 'active'
    """, (now_iso, game_id, user_id))
    cursor.execute("UPDATE users SET puzzles_failed = puzzles_failed + 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# ============================================================================
# ACHIEVEMENTS PERSISTENCE
# ============================================================================

def get_user_achievements(user_id):
    """Get list of unlocked achievement codes and unlock dates for user."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT achievement_code, unlocked_at FROM user_achievements WHERE user_id = ? ORDER BY unlocked_at DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"code": r["achievement_code"], "unlocked_at": r["unlocked_at"]} for r in rows]

def unlock_achievement(user_id, achievement_code, xp_reward=0, title="Achievement"):
    """Unlock an achievement atomically and award reward XP."""
    conn = get_db()
    cursor = conn.cursor()
    now_iso = datetime.datetime.utcnow().isoformat()
    
    try:
        cursor.execute("""
        INSERT INTO user_achievements (user_id, achievement_code, unlocked_at)
        VALUES (?, ?, ?)
        """, (user_id, achievement_code, now_iso))
        conn.commit()
        unlocked = True
    except sqlite3.IntegrityError:
        unlocked = False
        
    conn.close()
    
    if unlocked and xp_reward > 0:
        award_xp(user_id, xp_reward, f"Achievement: {title}")
        
    return unlocked

# ============================================================================
# LEADERBOARD & STATISTICS
# ============================================================================

def get_real_leaderboard(limit=50):
    """Query actual registered users sorted by ELO rating."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, username, display_name, avatar, ranked_rating, ranked_tier,
           ranked_wins, ranked_losses, puzzles_solved, xp, level
    FROM users
    WHERE puzzles_solved > 0 OR ranked_wins > 0 OR ranked_losses > 0 OR xp > 0
    ORDER BY ranked_rating DESC, ranked_wins DESC, xp DESC
    LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    leaderboard = []
    for rank_idx, r in enumerate(rows):
        total_ranked = (r["ranked_wins"] or 0) + (r["ranked_losses"] or 0)
        win_rate = f"{(r['ranked_wins'] / total_ranked * 100):.1f}%" if total_ranked > 0 else "0.0%"
        
        leaderboard.append({
            "rank": rank_idx + 1,
            "user_id": r["id"],
            "username": r["username"],
            "display_name": r["display_name"],
            "avatar": r["avatar"],
            "rating": r["ranked_rating"],
            "tier": r["ranked_tier"],
            "wins": r["ranked_wins"],
            "losses": r["ranked_losses"],
            "win_rate": win_rate,
            "xp": r["xp"],
            "level": r["level"]
        })
        
    return leaderboard

def get_user_statistics(user_id):
    """Aggregate authentic gameplay metrics for user."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Overall games count
    cursor.execute("""
    SELECT
        COUNT(*) as total_games,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_games,
        SUM(CASE WHEN status = 'completed' AND mistakes = 0 THEN 1 ELSE 0 END) as flawless_games,
        AVG(CASE WHEN status = 'completed' THEN elapsed_seconds ELSE NULL END) as avg_time,
        MIN(CASE WHEN status = 'completed' THEN elapsed_seconds ELSE NULL END) as best_time,
        SUM(mistakes) as total_mistakes,
        SUM(hints_used) as total_hints
    FROM game_sessions
    WHERE user_id = ?
    """, (user_id,))
    agg = dict(cursor.fetchone())
    
    # Breakdown by level/difficulty
    cursor.execute("""
    SELECT level_num, difficulty, COUNT(*) as count
    FROM game_sessions
    WHERE user_id = ? AND status = 'completed'
    GROUP BY level_num, difficulty
    ORDER BY level_num ASC
    """, (user_id,))
    level_counts = {f"level_{r['level_num']}": r["count"] for r in cursor.fetchall()}
    
    conn.close()
    return {
        "total_games": agg["total_games"] or 0,
        "completed_games": agg["completed_games"] or 0,
        "flawless_games": agg["flawless_games"] or 0,
        "avg_time_seconds": round(agg["avg_time"]) if agg["avg_time"] else 0,
        "best_time_seconds": agg["best_time"] or 0,
        "total_mistakes": agg["total_mistakes"] or 0,
        "total_hints": agg["total_hints"] or 0,
        "level_counts": level_counts
    }

# Initialize tables on import
init_db()
