"""
Sudoku Quest - Real-Time Ranked Matchmaking & Multiplayer Engine
Powered by Flask-SocketIO with real queue, real matchmaking, live opponent progress,
authoritative server-side completion validation, and genuine ELO rating updates.
"""
import time
import datetime
import uuid
import threading
from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room
import db
import sudoku_engine
import achievements

# Shared Matchmaking Queue and Active Matches
MATCHMAKING_QUEUE = {} # { user_id: { "sid": sid, "user": dict, "joined_at": float, "rating": int } }
ACTIVE_MATCHES = {}    # { match_id: { "p1": dict, "p2": dict, "solution": str, "started_at": float, "completed": bool } }
USER_SOCKETS = {}      # { sid: user_id }
SOCKET_USERS = {}      # { user_id: sid }
QUEUE_LOCK = threading.Lock()

socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")

def calculate_elo_delta(winner_rating, loser_rating, K=32):
    """Compute authentic ELO rating changes."""
    expected_winner = 1.0 / (1.0 + 10.0 ** ((loser_rating - winner_rating) / 400.0))
    expected_loser = 1.0 / (1.0 + 10.0 ** ((winner_rating - loser_rating) / 400.0))
    
    delta_winner = max(12, min(40, round(K * (1.0 - expected_winner))))
    delta_loser = max(10, min(36, round(K * expected_loser)))
    
    return delta_winner, delta_loser

def setup_socket_events(app):
    """Attach socketio to Flask app and register events."""
    socketio.init_app(app)

    @socketio.on("connect")
    def handle_connect():
        pass

    @socketio.on("disconnect")
    def handle_disconnect():
        sid = request.sid
        with QUEUE_LOCK:
            user_id = USER_SOCKETS.pop(sid, None)
            if user_id:
                SOCKET_USERS.pop(user_id, None)
                MATCHMAKING_QUEUE.pop(user_id, None)

    @socketio.on("auth")
    def handle_auth(data):
        """Authenticate websocket connection with user auth token."""
        token = data.get("token") if isinstance(data, dict) else None
        user = db.get_user_by_token(token) if token else None
        sid = request.sid
        
        if user:
            with QUEUE_LOCK:
                USER_SOCKETS[sid] = user["id"]
                SOCKET_USERS[user["id"]] = sid
            emit("auth_ok", {
                "user_id": user["id"],
                "username": user["username"],
                "display_name": user["display_name"],
                "rating": user["ranked_rating"],
                "tier": user["ranked_tier"]
            })
        else:
            emit("auth_error", {"message": "Invalid or expired session token."})

    @socketio.on("join_ranked_queue")
    def handle_join_queue(data):
        """Add authenticated player to the genuine matchmaking queue."""
        sid = request.sid
        user_id = USER_SOCKETS.get(sid)
        if not user_id:
            token = data.get("token") if isinstance(data, dict) else None
            user = db.get_user_by_token(token) if token else None
            if user:
                user_id = user["id"]
                USER_SOCKETS[sid] = user_id
                SOCKET_USERS[user_id] = sid
            else:
                emit("error", {"message": "Please log in to participate in Ranked matches."})
                return

        user = db.get_user_by_id(user_id)
        if not user:
            emit("error", {"message": "User not found."})
            return

        with QUEUE_LOCK:
            # Check if another authentic player is waiting in queue
            matched_opponent = None
            now_ts = time.time()
            
            for other_uid, other_entry in list(MATCHMAKING_QUEUE.items()):
                if other_uid != user_id:
                    matched_opponent = other_entry
                    del MATCHMAKING_QUEUE[other_uid]
                    break
                    
            if matched_opponent:
                # MATCH FOUND! Create live multiplayer room & game
                match_id = f"rm_{uuid.uuid4().hex[:12]}"
                p1_user = matched_opponent["user"]
                p2_user = user
                p1_sid = matched_opponent["sid"]
                p2_sid = sid
                
                # Pick ranked difficulty based on ratings
                avg_rating = (p1_user["ranked_rating"] + p2_user["ranked_rating"]) // 2
                lvl_num = 5 if avg_rating < 1400 else (6 if avg_rating < 1800 else 7)
                lvl_conf = sudoku_engine.get_level_by_key(lvl_num)
                
                puzzle_data = sudoku_engine.generate_puzzle(
                    difficulty=lvl_conf["key"],
                    level_num=lvl_num
                )
                
                # Create match in memory
                ACTIVE_MATCHES[match_id] = {
                    "match_id": match_id,
                    "p1": {"user_id": p1_user["id"], "sid": p1_sid, "username": p1_user["username"], "display_name": p1_user["display_name"], "avatar": p1_user["avatar"], "rating": p1_user["ranked_rating"], "tier": p1_user["ranked_tier"], "progress": 0, "mistakes": 0, "completed": False},
                    "p2": {"user_id": p2_user["id"], "sid": p2_sid, "username": p2_user["username"], "display_name": p2_user["display_name"], "avatar": p2_user["avatar"], "rating": p2_user["ranked_rating"], "tier": p2_user["ranked_tier"], "progress": 0, "mistakes": 0, "completed": False},
                    "solution": puzzle_data["solution"],
                    "difficulty": lvl_conf["key"],
                    "level_num": lvl_num,
                    "started_at": now_ts + 3.0,
                    "completed": False
                }
                
                # Join socket rooms
                join_room(match_id, sid=p1_sid)
                join_room(match_id, sid=p2_sid)
                
                # Send match_found with real opponent information to both
                socketio.emit("match_found", {
                    "match_id": match_id,
                    "opponent": {
                        "username": p2_user["username"],
                        "display_name": p2_user["display_name"],
                        "avatar": p2_user["avatar"],
                        "rating": p2_user["ranked_rating"],
                        "tier": p2_user["ranked_tier"]
                    },
                    "level": lvl_num,
                    "level_name": lvl_conf["name"]
                }, to=p1_sid)
                
                socketio.emit("match_found", {
                    "match_id": match_id,
                    "opponent": {
                        "username": p1_user["username"],
                        "display_name": p1_user["display_name"],
                        "avatar": p1_user["avatar"],
                        "rating": p1_user["ranked_rating"],
                        "tier": p1_user["ranked_tier"]
                    },
                    "level": lvl_num,
                    "level_name": lvl_conf["name"]
                }, to=p2_sid)
                
                # Broadcast start with board after 3s
                def start_match_broadcast():
                    time.sleep(3.0)
                    socketio.emit("match_start", {
                        "match_id": match_id,
                        "initial_board": puzzle_data["puzzle"],
                        "clues": puzzle_data["clues"],
                        "level": lvl_num,
                        "level_name": lvl_conf["name"],
                        "started_at": datetime.datetime.utcnow().isoformat()
                    }, room=match_id)
                    
                threading.Thread(target=start_match_broadcast, daemon=True).start()
                
            else:
                # Add to queue and report genuine queue status
                MATCHMAKING_QUEUE[user_id] = {
                    "sid": sid,
                    "user": user,
                    "joined_at": now_ts,
                    "rating": user["ranked_rating"]
                }
                emit("queue_joined", {
                    "status": "waiting",
                    "queue_count": len(MATCHMAKING_QUEUE),
                    "user_rating": user["ranked_rating"]
                })

    @socketio.on("leave_ranked_queue")
    def handle_leave_queue():
        sid = request.sid
        user_id = USER_SOCKETS.get(sid)
        if user_id:
            with QUEUE_LOCK:
                MATCHMAKING_QUEUE.pop(user_id, None)
            emit("queue_left", {"status": "left"})

    @socketio.on("player_progress")
    def handle_player_progress(data):
        """Relay real-time solve progress to match opponent."""
        match_id = data.get("match_id")
        progress_pct = data.get("progress_pct", 0)
        mistakes = data.get("mistakes", 0)
        
        match = ACTIVE_MATCHES.get(match_id)
        if not match:
            return
            
        sid = request.sid
        user_id = USER_SOCKETS.get(sid)
        
        # Broadcast progress to the other player
        if match["p1"]["user_id"] == user_id:
            match["p1"]["progress"] = progress_pct
            match["p1"]["mistakes"] = mistakes
            socketio.emit("opponent_progress", {
                "progress_pct": progress_pct,
                "mistakes": mistakes
            }, to=match["p2"]["sid"])
        elif match["p2"]["user_id"] == user_id:
            match["p2"]["progress"] = progress_pct
            match["p2"]["mistakes"] = mistakes
            socketio.emit("opponent_progress", {
                "progress_pct": progress_pct,
                "mistakes": mistakes
            }, to=match["p1"]["sid"])

    @socketio.on("player_complete")
    def handle_player_complete(data):
        """Authoritatively validate match solve and finalize ELO rating."""
        match_id = data.get("match_id")
        board = data.get("board")
        elapsed_seconds = data.get("elapsed_seconds", 300)
        mistakes = data.get("mistakes", 0)
        
        match = ACTIVE_MATCHES.get(match_id)
        if not match or match.get("completed"):
            return
            
        sid = request.sid
        user_id = USER_SOCKETS.get(sid)
        
        # Verify board against secret server solution
        if board != match["solution"]:
            emit("error", {"message": "Invalid puzzle solution submission."})
            return
            
        match["completed"] = True
        is_p1 = (match["p1"]["user_id"] == user_id)
        winner = match["p1"] if is_p1 else match["p2"]
        loser = match["p2"] if is_p1 else match["p1"]
        
        # Calculate rating deltas
        delta_win, delta_lose = calculate_elo_delta(winner["rating"], loser["rating"])
        new_win_rating = winner["rating"] + delta_win
        new_lose_rating = max(1000, loser["rating"] - delta_lose)
        
        new_win_tier = sudoku_engine.get_rank_tier(new_win_rating)["name"]
        new_lose_tier = sudoku_engine.get_rank_tier(new_lose_rating)["name"]
        
        # Atomically update database for both players
        conn = db.get_db()
        now_iso = datetime.datetime.utcnow().isoformat()
        
        conn.execute("""
        UPDATE users
        SET ranked_rating = ?, ranked_tier = ?, ranked_wins = ranked_wins + 1, puzzles_solved = puzzles_solved + 1, updated_at = ?
        WHERE id = ?
        """, (new_win_rating, new_win_tier, now_iso, winner["user_id"]))
        
        conn.execute("""
        UPDATE users
        SET ranked_rating = ?, ranked_tier = ?, ranked_losses = ranked_losses + 1, updated_at = ?
        WHERE id = ?
        """, (new_lose_rating, new_lose_tier, now_iso, loser["user_id"]))
        
        conn.commit()
        conn.close()
        
        # Award XP and check achievements
        db.award_xp(winner["user_id"], 250, "Ranked Victory")
        db.award_xp(loser["user_id"], 50, "Ranked Participation")
        achievements.evaluate_achievements(winner["user_id"], None, ranked_match=True)
        achievements.evaluate_achievements(loser["user_id"], None, ranked_match=True)
        
        # Broadcast match_finished to both players
        socketio.emit("match_finished", {
            "winner_id": winner["user_id"],
            "winner_name": winner["display_name"],
            "p1_result": {
                "is_winner": is_p1,
                "rating_delta": delta_win if is_p1 else -delta_lose,
                "new_rating": new_win_rating if is_p1 else new_lose_rating,
                "new_tier": new_win_tier if is_p1 else new_lose_tier,
                "xp_earned": 250 if is_p1 else 50,
                "time_seconds": elapsed_seconds
            },
            "p2_result": {
                "is_winner": not is_p1,
                "rating_delta": -delta_lose if is_p1 else delta_win,
                "new_rating": new_lose_rating if is_p1 else new_win_rating,
                "new_tier": new_lose_tier if is_p1 else new_win_tier,
                "xp_earned": 50 if is_p1 else 250,
                "time_seconds": elapsed_seconds
            }
        }, room=match_id)
        
        del ACTIVE_MATCHES[match_id]
