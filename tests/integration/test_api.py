"""
Integration tests for Flask REST API endpoints and authoritative session management.
"""
import pytest
import json
from app import app
import db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Sudoku Quest" in res.data or b"<!DOCTYPE html>" in res.data

def test_api_stats(client):
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ready"
    assert data["records"] == 500000
    assert data["levels_count"] == 10

def test_api_dataset_status(client):
    res = client.get("/api/dataset/status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["format"] == "JSONL"

def test_api_levels(client):
    res = client.get("/api/levels")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["levels"]) == 10

def test_api_puzzles_random(client):
    res = client.get("/api/puzzles/random?level=3")
    assert res.status_code == 200
    data = res.get_json()
    assert "puzzle" in data
    assert "solution" in data
    assert data["level"] == 3

def test_api_puzzles_daily(client):
    res = client.get("/api/puzzles/daily?date=2026-10-22")
    assert res.status_code == 200
    data = res.get_json()
    assert data["is_daily"] is True
    assert data["date"] == "2026-10-22"

def test_auth_workflow(client):
    # Register test user with unique username
    unique_suffix = db.uuid.uuid4().hex[:6]
    username = f"test_{unique_suffix}"
    email = f"test_{unique_suffix}@example.com"
    pwd = "securepassword123"

    reg_res = client.post("/api/auth/register", json={
        "username": username,
        "email": email,
        "password": pwd,
        "display_name": f"Tester {unique_suffix}"
    })
    assert reg_res.status_code == 201
    reg_data = reg_res.get_json()
    token = reg_data["token"]
    assert token is not None

    # Check /api/auth/me with Bearer token
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.get_json()
    assert me_data["authenticated"] is True
    assert me_data["user"]["username"] == username

    # Login test
    login_res = client.post("/api/auth/login", json={
        "identifier": username,
        "password": pwd
    })
    assert login_res.status_code == 200
    login_data = login_res.get_json()
    assert "token" in login_data

def test_game_session_and_hints(client):
    # Start game session
    start_res = client.post("/api/games", json={"level_num": 1, "difficulty": "beginner"})
    assert start_res.status_code == 201
    game_data = start_res.get_json()
    game_id = game_data["game_id"]
    assert game_id.startswith("gs_")

    # Request intelligent hint
    hint_res = client.post(f"/api/games/{game_id}/hint")
    assert hint_res.status_code == 200
    hint_data = hint_res.get_json()
    assert "cell_index" in hint_data
    assert "value" in hint_data
    assert "strategy" in hint_data
    assert "explanation" in hint_data
    assert hint_data["hints_used"] == 1

def test_legacy_game_validate(client):
    res = client.post("/api/game/validate", json={
        "board": "483921657967345821251876493548132976729564138136798245372689514814253769695417382"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["valid"] is True
    assert data["complete"] is True
    assert len(data["conflicts"]) == 0

def test_legacy_ranked_endpoints(client):
    match_res = client.get("/api/ranked/match")
    assert match_res.status_code == 200
    match_data = match_res.get_json()
    assert "match_id" in match_data
    assert "opponent" in match_data

    lb_res = client.get("/api/ranked/leaderboard")
    assert lb_res.status_code == 200
    lb_data = lb_res.get_json()
    assert "leaderboard" in lb_data
