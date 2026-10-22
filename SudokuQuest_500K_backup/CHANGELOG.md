# Changelog

All notable changes to the **Sudoku Quest** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Created `scripts/count_loc.py` for reproducible, honest line-of-code measurement.
- Created `PROJECT_AUDIT.md` comprehensive technical audit and architectural roadmap.
- Created `ARCHITECTURE.md` documenting modular layer design.
- Created `CONTRIBUTING.md` and `SECURITY.md`.
- Added `flask-socketio`, `python-socketio`, and `pytest` dependencies to `requirements.txt`.

---

## [1.0.0] - 2026-10-22

### Added
- Initial baseline commit for Sudoku Quest with 500,000 puzzles dataset.
- 10-tier level progression system.
- Ranked multiplayer matchmaking via Socket.IO.
- SQLite persistence layer with users, sessions, achievements, and ranked matches.
- Dark theme frontend single-page application.
