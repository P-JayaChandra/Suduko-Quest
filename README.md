# Sudoku Quest — 500K Edition

> **Master the Grid.** Challenge yourself. Solve faster.

Sudoku Quest is a high-performance Sudoku gaming platform built with Flask, Vanilla JavaScript, and a local dataset of 500,000+ puzzles.

---

## 🌟 Key Features

### 1. 10-Tier Level Progression System
- **Level 1 — Beginner** (Very Easy • 3–5 min • 45–50 clues • +25 XP • Green)
- **Level 2 — Novice** (Easy • 5–8 min • 40–44 clues • +50 XP • Teal)
- **Level 3 — Easy** (Easy • 5–10 min • 38–40 clues • +75 XP • Cyan)
- **Level 4 — Medium** (Medium • 10–15 min • 30–34 clues • +100 XP • Blue)
- **Level 5 — Advanced** (Medium-Hard • 12–18 min • 28–32 clues • +125 XP • Indigo)
- **Level 6 — Hard** (Hard • 15–25 min • 26–29 clues • +175 XP • Orange)
- **Level 7 — Master** (Very Hard • 20–30 min • 23–26 clues • +225 XP • Red-Orange)
- **Level 8 — Expert** (Expert • 25+ min • 22–25 clues • +250 XP • Purple)
- **Level 9 — Grandmaster** (Extreme • 30+ min • 17–22 clues • +350 XP • Magenta)
- **Level 10 — Legend** (Extreme • 40+ min • 16–20 clues • +500 XP • Gold)

### 2. "YOUR SUDOKU JOURNEY" Progression Roadmap
- Visual connected pathway highlighting the player's current unlocked level and milestones.
- Unlocking mechanism: Solved puzzles unlock higher difficulty tiers step-by-step.

### 3. 🏆 Competitive Ranked League
- **8 Competitive Tiers:** Bronze (1000–1199), Silver (1200–1399), Gold (1400–1599), Platinum (1600–1799), Diamond (1800–1999), Master (2000–2199), Grandmaster (2200–2399), Legend (2400+).
- **Matchmaking Radar:** Ranked Solo Benchmark Matchmaking against rating-matched benchmark solvers.
- **Dynamic ELO Scoring:** Base rating changes (+20 to +35 on win, -15 to -25 on loss) with bonuses for speed, zero mistakes, and pure solves without hints.
- **Global Leaderboard:** Benchmark standings tracking rating, division tier, win rate %, and best solve times.
- **Season 01 ("MASTER THE GRID"):** 30-day competitive seasons with tier rewards.

### 4. 9×9 Sudoku Engine & Dataset Integration
- **500,000 JSONL Records:** Sub-millisecond isomorphic Sudoku generation and validation from `data/sudoku_records.jsonl`.
- **Gameplay Tools:** Pencil notes mode (`N`), intelligent hints (`H`), undo stack (`U`), live mistake detection (3 strikes), digital timer with anti-cheat pause curtain, and remaining number counts.
- **Daily Challenge:** Unique deterministic daily puzzle with streak tracking and 2x XP rewards.
- **Analytics & Achievements:** HTML5 Canvas performance chart, 8 metric cards, and 6 milestone trophies.

---

## 🚀 Getting Started

### 1. Requirements
```bash
pip install -r requirements.txt
```

### 2. Run Locally
```bash
python app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 🔌 API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Main Sudoku Quest Single-Page Application |
| `/api/stats` | `GET` | Dataset stats and engine health (backward compatible) |
| `/api/dataset/status` | `GET` | Detailed metadata of the 500,000 JSONL records |
| `/api/levels` | `GET` | Returns full 10-tier progression level definitions |
| `/api/puzzles/random?level=X` | `GET` | Generates a puzzle matching level (1–10) or difficulty |
| `/api/puzzles/daily` | `GET` | Generates today's official deterministic daily challenge |
| `/api/ranked/match` | `GET` | Generates a benchmark opponent and ranked puzzle |
| `/api/ranked/complete` | `POST` | Calculates rating adjustments and tier progression |
| `/api/ranked/leaderboard` | `GET` | Returns seasonal competitive leaderboard |
| `/api/ranked/season` | `GET` | Returns Season 01 details, ending time, and rewards |
| `/api/game/validate` | `POST` | Validates a 9×9 board state against the backend solution |
| `/api/game/hint` | `POST` | Returns smart hint coordinates and value |
| `/api/game/complete` | `POST` | Records game results, awards XP and milestone bonuses |
