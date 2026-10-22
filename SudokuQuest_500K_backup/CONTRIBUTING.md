# Contributing to Sudoku Quest

Thank you for your interest in contributing to **Sudoku Quest**. This document outlines development standards, coding conventions, testing guidelines, and the pull request process.

---

## 1. Development Principles

1. **Maintain High Architectural Quality:**
   - Write clean, modular, and self-documenting code.
   - Separate concerns across domain engines, data repositories, web services, and user interfaces.
   - Do not duplicate files, artificially bloat lines with comments, or generate boilerplate to inflate line counts.

2. **Preserve Backward Compatibility:**
   - Keep existing public API endpoints functional.
   - Preserve existing user data and database schemas via backward-compatible migrations.

3. **Verify Everything with Tests:**
   - Every algorithmic solver, generator, strategy, and API endpoint must be accompanied by unit and integration tests.
   - Test suites must be executable via `pytest`.

---

## 2. Setting Up the Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/P-JayaChandra/Suduko-Quest.git
   cd Suduko-Quest
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify environment and count LOC:**
   ```bash
   python scripts/count_loc.py
   pytest
   ```

5. **Start local development server:**
   ```bash
   python app.py
   ```
   Open `http://127.0.0.1:5000` in your web browser.

---

## 3. Code Standards & Style

- **Python:** PEP 8 style guide. Use type annotations (`typing`) where appropriate. Avoid bare `except:` clauses.
- **JavaScript:** ES6+ standards, clean async/await patterns, zero global leaks.
- **CSS:** Vanilla CSS custom properties (design tokens), BEM-like naming conventions, responsive flexbox and CSS grid.
- **Tests:** Place unit tests in `tests/unit/`, integration tests in `tests/integration/`, and end-to-end tests in `tests/e2e/`.

---

## 4. LOC Counting & Metric Integrity

Run `python scripts/count_loc.py` to verify lines of code before submitting changes.
- Do not count `.git`, virtual environments, or compiled `.pyc` files.
- The `data/sudoku_records.jsonl` dataset and SQLite databases are excluded from SLOC metrics.

---

## 5. Submitting Changes

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Run automated tests: `pytest`
3. Run LOC measurement: `python scripts/count_loc.py`
4. Commit your changes with descriptive messages: `git commit -m "feat(engine): add DLX exact cover solver"`
5. Request review before merging into `main`.
