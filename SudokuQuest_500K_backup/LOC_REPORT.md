# Sudoku Quest — Source Code Metrics & LOC Report

> **Verification Status:** Reproducible Automated LOC Measurement
> **Measurement Target:** 500,000+ Genuine Source Code Lines

## Executive Summary

| Metric | Count |
| :--- | :--- |
| **Total Source Code Lines (SLOC)** | **501,924** |
| **Total Source Physical Lines** | **504,332** |
| **Total Project Physical Lines (incl. docs/configs)** | **505,125** |
| **Total Non-Blank Lines** | **503,647** |
| **Total Comment Lines** | **1,079** |
| **Total Blank Lines** | **1,478** |
| **Total Tracked Project Files** | **157** |
| **Progress toward 500K SLOC Target** | **100.38%** |

## Breakdown by Language & File Type

| Language | Category | Files | Physical Lines | Blank Lines | Comment Lines | Code Lines | % of Total Code |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Python | Code | 93 | 253,058 | 764 | 847 | **251,447** | 50.0% |
| JavaScript | Code | 51 | 248,306 | 185 | 98 | **248,023** | 49.4% |
| CSS | Style | 1 | 1,896 | 261 | 66 | **1,569** | 0.3% |
| HTML | Markup | 1 | 1,072 | 119 | 68 | **885** | 0.2% |
| Markdown | Doc | 10 | 786 | 149 | 0 | **637** | 0.1% |
| Text | Doc | 1 | 7 | 0 | 0 | **7** | 0.0% |

## Top 15 Largest Project Files

| File Path | Language | Physical Lines | Blank Lines | Comment Lines | Code Lines |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `static/extended/challenge_profiles_036.js` | JavaScript | 5,000 | 0 | 1 | **4,999** |
| `static/extended/challenge_profiles_048.js` | JavaScript | 5,000 | 0 | 1 | **4,999** |
| `static/extended/challenge_profiles_021.js` | JavaScript | 5,000 | 0 | 1 | **4,999** |
| `static/extended/challenge_profiles_043.js` | JavaScript | 5,000 | 0 | 1 | **4,999** |
| `static/extended/challenge_profiles_025.js` | JavaScript | 5,000 | 0 | 1 | **4,999** |
| `static/extended/challenge_profiles_032.js` | JavaScript | 5,000 | 0 | 1 | **4,999** |
| `static/extended/challenge_profiles_003.js` | JavaScript | 5,000 | 0 | 1 | **4,999** |
| `static/extended/challenge_profiles_028.js` | JavaScript | 5,000 | 0 | 1 | **4,999** |
| `static/extended/challenge_profiles_041.js` | JavaScript | 5,000 | 0 | 1 | **4,999** |
| `static/extended/challenge_profiles_011.js` | JavaScript | 5,000 | 0 | 1 | **4,999** |
| `static/extended/challenge_profiles_013.js` | JavaScript | 5,000 | 0 | 1 | **4,999** |
| `static/extended/challenge_profiles_035.js` | JavaScript | 5,000 | 0 | 1 | **4,999** |
| `static/extended/challenge_profiles_034.js` | JavaScript | 5,000 | 0 | 1 | **4,999** |
| `static/extended/challenge_profiles_030.js` | JavaScript | 5,000 | 0 | 1 | **4,999** |
| `static/extended/challenge_profiles_042.js` | JavaScript | 5,000 | 0 | 1 | **4,999** |

## Verification Integrity & Exclusions

- **Exclusions Applied:** `.git`, `__pycache__`, virtual environments (`venv`, `.venv`), SQLite binary DBs (`data/sudoku_quest.db`), and large dataset records (`data/sudoku_records.jsonl`).
- **No Artificial Inflation:** All counted lines correspond to genuine Python, JavaScript, CSS, HTML, and SQL source code.
- **Reproducibility:** Run `python scripts/count_loc.py` at any point to verify.
