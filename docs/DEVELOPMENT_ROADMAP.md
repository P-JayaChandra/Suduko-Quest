# Sudoku Quest — Comprehensive Engineering Development Roadmap (125 Tasks)

> **Document Version:** 1.0.0  
> **Repository:** [https://github.com/P-JayaChandra/Suduko-Quest](https://github.com/P-JayaChandra/Suduko-Quest)  
> **Target:** 125 Production-Grade Engineering Tasks across 20 Milestones  
> **Standard:** Strict Conventional Commits, Discrete PRs, Preserved Original UI, 100% Passing Tests

---

## Summary Table of 20 Milestones

| Milestone | Focus Domain | Tasks | Target Scope |
| :--- | :--- | :--- | :--- |
| **Milestone 1** | Repository Cleanup & Configuration | TASK-001 to TASK-006 | Git hygiene, dependencies, .gitignore, config |
| **Milestone 2** | Core Domain Model Hardening | TASK-007 to TASK-012 | Board, Cell, Move, CandidateGrid bitmasks |
| **Milestone 3** | Sudoku Rules & Grid Constraints | TASK-013 to TASK-018 | Row, col, box conflicts, peer propagation |
| **Milestone 4** | Exact Cover Engine & Dancing Links (DLX) | TASK-019 to TASK-024 | Knuth Algorithm X, toroidal nodes, cover/uncover |
| **Milestone 5** | Bitwise Solving & High-Throughput Verification | TASK-025 to TASK-030 | 9-bit bitmask solvers, MRV heuristic |
| **Milestone 6** | Puzzle Uniqueness & Minimal Clue Reduction | TASK-031 to TASK-036 | Single-solution generator, symmetry, daily seeds |
| **Milestone 7** | Human Deduction Strategies — Singles & Subsets | TASK-037 to TASK-042 | Naked/Hidden Singles, Pairs, Triples, Quads |
| **Milestone 8** | Human Deduction Strategies — Intersections, Fish & Wings | TASK-043 to TASK-048 | Pointing Pairs, X-Wing, Swordfish, XY-Wing |
| **Milestone 9** | Intelligent Explanatory Hint Engine | TASK-049 to TASK-054 | Tiered hints, natural language explanations |
| **Milestone 10** | Difficulty Classification & Standard Rating (SE) | TASK-055 to TASK-060 | Sudoku Explainer grading, 10-tier calibration |
| **Milestone 11** | Game State Management & Anti-Tamper Security | TASK-061 to TASK-066 | HMAC hashes, 3-strike rules, auto-save |
| **Milestone 12** | Precision Timer & Anti-Cheat Pause Curtain | TASK-067 to TASK-072 | Monotonic timer, pause curtain, anti-tamper |
| **Milestone 13** | 10-Tier Level Progression & XP Award Rules | TASK-073 to TASK-078 | Sequential unlocks, dynamic XP, streaks |
| **Milestone 14** | Competitive Ranked ELO & Leaderboard Engine | TASK-079 to TASK-084 | ELO calculations, 8 tiers, benchmark bots |
| **Milestone 15** | Achievements Engine & Milestone Unlocks | TASK-085 to TASK-090 | 12 achievements, event-driven unlocking |
| **Milestone 16** | Database Resilience, WAL & Connection Pooling | TASK-091 to TASK-096 | SQLite WAL mode, transactions, indexing, backups |
| **Milestone 17** | REST API Validation, Blueprints & Error Handling | TASK-097 to TASK-102 | JSON error handlers, rate limiting, health |
| **Milestone 18** | JavaScript Game Controller & State Synchronization | TASK-103 to TASK-108 | Notes cleanup, undo/redo, UI preservation |
| **Milestone 19** | Keyboard Accessibility & Screen Reader Support | TASK-109 to TASK-114 | Arrow keys, ARIA attributes, shortcuts |
| **Milestone 20** | Performance Profiling, Security & QA Hardening | TASK-115 to TASK-125 | Benchmarks, SQLi/XSS tests, cross-platform |

---

## Detailed Task Specifications

### TASK-001: Exclude redundant in-tree backup directory from repository
- **Milestone:** Milestone 1: Repository Cleanup & Configuration
- **Affected Files:** `SudokuQuest_500K_backup/, .gitignore`
- **Implementation Approach:** Remove the duplicate SudokuQuest_500K_backup/ directory from git tracking and add ignore rule to prevent re-addition.
- **Tests Required:** Verify working tree cleanliness and run git status.
- **Acceptance Criteria:** Working tree clean; repository size decreased; baseline tests unaffected.

### TASK-002: Normalize and pin runtime and testing dependencies in requirements.txt
- **Milestone:** Milestone 1: Repository Cleanup & Configuration
- **Affected Files:** `requirements.txt`
- **Implementation Approach:** Ensure all production dependencies (Flask, flask-socketio, python-socketio, simple-websocket, Werkzeug) and test dependencies (pytest, pytest-flask) are documented with compatible version constraints.
- **Tests Required:** python -m pytest test suite discovery check.
- **Acceptance Criteria:** Clean installation in virtual environment without missing module errors.

### TASK-003: Update pytest configuration with coverage reporting and markers
- **Milestone:** Milestone 1: Repository Cleanup & Configuration
- **Affected Files:** `pytest.ini, tests/conftest.py`
- **Implementation Approach:** Add pytest.ini with testpaths, python_files, python_functions, and custom markers (unit, integration, slow, benchmark).
- **Tests Required:** Execute pytest --markers and verify registered marker output.
- **Acceptance Criteria:** Test discovery correctly categorizes unit and integration tests without warnings.

### TASK-004: Standardize .gitignore with comprehensive OS, IDE, and SQLite patterns
- **Milestone:** Milestone 1: Repository Cleanup & Configuration
- **Affected Files:** `.gitignore`
- **Implementation Approach:** Expand .gitignore to include SQLite transient WAL files, pytest caches, coverage files, and temporary OS files.
- **Tests Required:** git status check against untracked local SQLite files.
- **Acceptance Criteria:** No local databases, cache files, or IDE metadata appear in untracked files.

### TASK-005: Establish environment configuration loading with fallback defaults
- **Milestone:** Milestone 1: Repository Cleanup & Configuration
- **Affected Files:** `core/config.py`
- **Implementation Approach:** Enhance configuration loader to read from environment variables (SECRET_KEY, FLASK_ENV, DATABASE_PATH) with safe development fallbacks.
- **Tests Required:** tests/unit/test_core.py covering default and custom environment variables.
- **Acceptance Criteria:** Config properly overrides values when environment variables are supplied.

### TASK-006: Add reproducible LOC measurement script documentation and tests
- **Milestone:** Milestone 1: Repository Cleanup & Configuration
- **Affected Files:** `scripts/count_loc.py, tests/unit/test_core.py`
- **Implementation Approach:** Ensure scripts/count_loc.py cleanly distinguishes genuine application code from data catalogs and backup directories.
- **Tests Required:** python scripts/count_loc.py automated execution test.
- **Acceptance Criteria:** LOC report generated with exact SLOC, physical lines, and language distribution.

### TASK-007: Implement immutable Cell coordinate validation
- **Milestone:** Milestone 2: Core Domain Model Hardening
- **Affected Files:** `engine/models/cell.py`
- **Implementation Approach:** Add boundary validation in Cell model to enforce 0 <= row <= 8 and 0 <= col <= 8 with custom exception raising.
- **Tests Required:** tests/unit/test_board.py testing negative index and out-of-bound coordinates.
- **Acceptance Criteria:** Invalid coordinates raise InvalidMoveError before grid mutation.

### TASK-008: Implement Cell given/fixed status immutability enforcement
- **Milestone:** Milestone 2: Core Domain Model Hardening
- **Affected Files:** `engine/models/cell.py`
- **Implementation Approach:** Prevent modification of cell value if cell.is_given is True unless explicitly unprotecting.
- **Tests Required:** tests/unit/test_board.py testing write attempt to given cell.
- **Acceptance Criteria:** Modifying given cell raises InvalidMoveError without changing value.

### TASK-009: Implement CandidateGrid bitmask representation and bit operations
- **Milestone:** Milestone 2: Core Domain Model Hardening
- **Affected Files:** `engine/models/candidate_grid.py`
- **Implementation Approach:** Optimize candidate storage per cell using 9-bit bitmask integers (1<<digit) for fast bitwise intersection and elimination.
- **Tests Required:** tests/unit/test_board.py testing candidate set, remove, toggle, and count.
- **Acceptance Criteria:** Candidate operations execute in sub-microsecond time with 100% accuracy.

### TASK-010: Implement Move domain object with undo/redo serialization
- **Milestone:** Milestone 2: Core Domain Model Hardening
- **Affected Files:** `engine/models/move.py`
- **Implementation Approach:** Create structured Move class storing previous value, new value, previous candidates, and timestamp with JSON serialization.
- **Tests Required:** tests/unit/test_board.py testing serialization and deserialization.
- **Acceptance Criteria:** Move history round-trips to JSON without loss of candidate or timestamp data.

### TASK-011: Implement Board cloning and deepcopy memory optimization
- **Milestone:** Milestone 2: Core Domain Model Hardening
- **Affected Files:** `engine/models/board.py`
- **Implementation Approach:** Add board.fast_clone() method that copies flat cell arrays and candidate bitmasks without expensive copy.deepcopy overhead.
- **Tests Required:** tests/unit/test_board.py comparing clone equality and memory independence.
- **Acceptance Criteria:** Cloning 1000 boards takes less than 50 milliseconds; modifying clone leaves original untouched.

### TASK-012: Implement 81-character compact string Board serialization and parsing
- **Milestone:** Milestone 2: Core Domain Model Hardening
- **Affected Files:** `engine/models/board.py`
- **Implementation Approach:** Support standard 81-character puzzle string format (dots or zeros for empty cells) with bidirectional conversion.
- **Tests Required:** tests/unit/test_board.py testing 81-char parsing and formatting.
- **Acceptance Criteria:** All 81-char valid puzzles parse accurately; malformed strings raise InvalidBoardError.

### TASK-013: Implement row conflict detection with coordinate mapping
- **Milestone:** Milestone 3: Sudoku Rules & Grid Constraints
- **Affected Files:** `engine/models/board.py, sudoku_engine.py`
- **Implementation Approach:** Add get_row_conflicts(row) returning exact cell coordinate pairs sharing duplicate non-zero digits.
- **Tests Required:** tests/unit/test_board.py testing duplicate digits across rows.
- **Acceptance Criteria:** All duplicate row values accurately reported with coordinates.

### TASK-014: Implement column conflict detection with coordinate mapping
- **Milestone:** Milestone 3: Sudoku Rules & Grid Constraints
- **Affected Files:** `engine/models/board.py, sudoku_engine.py`
- **Implementation Approach:** Add get_col_conflicts(col) returning exact cell coordinate pairs sharing duplicate non-zero digits.
- **Tests Required:** tests/unit/test_board.py testing duplicate digits across columns.
- **Acceptance Criteria:** All duplicate column values accurately reported with coordinates.

### TASK-015: Implement 3x3 box (block) conflict detection with coordinate mapping
- **Milestone:** Milestone 3: Sudoku Rules & Grid Constraints
- **Affected Files:** `engine/models/board.py, sudoku_engine.py`
- **Implementation Approach:** Add get_box_conflicts(box_index) returning exact cell coordinate pairs sharing duplicate non-zero digits.
- **Tests Required:** tests/unit/test_board.py testing duplicate digits across 3x3 blocks.
- **Acceptance Criteria:** All duplicate box values accurately reported with coordinates.

### TASK-016: Implement comprehensive Board.is_valid() constraint checker
- **Milestone:** Milestone 3: Sudoku Rules & Grid Constraints
- **Affected Files:** `engine/models/board.py`
- **Implementation Approach:** Provide high-speed method checking that no row, column, or box contains duplicate non-zero digits.
- **Tests Required:** tests/unit/test_board.py testing valid, partial, and violated boards.
- **Acceptance Criteria:** Method returns False immediately upon first violation; True for valid partial grids.

### TASK-017: Implement Board.is_complete() win-condition checker
- **Milestone:** Milestone 3: Sudoku Rules & Grid Constraints
- **Affected Files:** `engine/models/board.py`
- **Implementation Approach:** Provide fast check verifying all 81 cells are non-zero and every house contains digits 1-9.
- **Tests Required:** tests/unit/test_board.py testing complete valid vs complete invalid boards.
- **Acceptance Criteria:** Returns True only when grid is 100% filled and valid.

### TASK-018: Implement cell peer calculation and peer candidate propagation
- **Milestone:** Milestone 3: Sudoku Rules & Grid Constraints
- **Affected Files:** `engine/models/board.py, engine/models/candidate_grid.py`
- **Implementation Approach:** Pre-calculate the 20 peers for each cell index to achieve O(1) candidate elimination on digit placement.
- **Tests Required:** tests/unit/test_board.py testing peer count and peer indices.
- **Acceptance Criteria:** Every cell has exactly 20 unique peers; placing a digit eliminates it from all peer candidate sets.

### TASK-019: Implement circular doubly-linked toroidal node structure in DLX
- **Milestone:** Milestone 4: Exact Cover Engine & Dancing Links
- **Affected Files:** `engine/solvers/dlx.py`
- **Implementation Approach:** Build four-way linked DLXNode (left, right, up, down) and ColumnHeader with size counters.
- **Tests Required:** tests/unit/test_solvers.py testing circular link construction and traversal.
- **Acceptance Criteria:** Toroidal grid links correctly in 2D space without dangling pointers.

### TASK-020: Implement 324-column exact cover matrix generator for 9x9 Sudoku
- **Milestone:** Milestone 4: Exact Cover Engine & Dancing Links
- **Affected Files:** `engine/solvers/dlx.py`
- **Implementation Approach:** Generate standard Sudoku exact cover matrix with 4 constraint types: Cell (81), Row-Digit (81), Col-Digit (81), Box-Digit (81).
- **Tests Required:** tests/unit/test_solvers.py verifying 324 columns and 729 rows.
- **Acceptance Criteria:** Generated exact cover matrix matches canonical 324-column constraints.

### TASK-021: Implement Column cover and uncover operations in DLX
- **Milestone:** Milestone 4: Exact Cover Engine & Dancing Links
- **Affected Files:** `engine/solvers/dlx.py`
- **Implementation Approach:** Implement Knuth Algorithm X column covering (detaching column and rows) and uncovering (exact reverse restoration).
- **Tests Required:** tests/unit/test_solvers.py verifying matrix state before and after cover/uncover.
- **Acceptance Criteria:** Matrix structure perfectly restored to initial state after complete uncover cycle.

### TASK-022: Implement Algorithm X recursive search with heuristic column selection
- **Milestone:** Milestone 4: Exact Cover Engine & Dancing Links
- **Affected Files:** `engine/solvers/dlx.py`
- **Implementation Approach:** Select column with minimum remaining size (MRV heuristic) to minimize search branching factor.
- **Tests Required:** tests/unit/test_solvers.py testing solution of standard and hard puzzles.
- **Acceptance Criteria:** DLX solves standard hard puzzles in under 10 milliseconds.

### TASK-023: Implement solution counting limit in DLX to verify uniqueness without exhaustive search
- **Milestone:** Milestone 4: Exact Cover Engine & Dancing Links
- **Affected Files:** `engine/solvers/dlx.py`
- **Implementation Approach:** Add max_solutions parameter allowing early termination once 2 solutions are found.
- **Tests Required:** tests/unit/test_solvers.py testing puzzle with 2 solutions stopping at limit.
- **Acceptance Criteria:** Search terminates immediately upon discovering max_solutions, saving CPU cycles.

### TASK-024: Benchmark and profile DLX solver memory footprint
- **Milestone:** Milestone 4: Exact Cover Engine & Dancing Links
- **Affected Files:** `engine/solvers/dlx.py, tests/unit/test_solvers.py`
- **Implementation Approach:** Ensure DLX matrix reuse avoids unnecessary GC allocations across repeated solve invocations.
- **Tests Required:** tests/unit/test_solvers.py testing 50 consecutive solves.
- **Acceptance Criteria:** Memory usage remains flat across repeated solve runs.

### TASK-025: Implement 9-bit bitmask row, column, and box occupancy tracker
- **Milestone:** Milestone 5: Bitwise Solving & High-Throughput Verification
- **Affected Files:** `engine/solvers/bitwise_solver.py`
- **Implementation Approach:** Track placed digits using three 9-element integer arrays (row_bits, col_bits, box_bits).
- **Tests Required:** tests/unit/test_solvers.py verifying bitmask representation.
- **Acceptance Criteria:** Placing digit toggles bit with |= (1 << digit); conflict check is single bitwise AND.

### TASK-026: Implement bitwise candidate bitmask calculation using low-bit extraction
- **Milestone:** Milestone 5: Bitwise Solving & High-Throughput Verification
- **Affected Files:** `engine/solvers/bitwise_solver.py`
- **Implementation Approach:** Calculate legal candidate digits for cell (r, c) using bitwise NOT and AND operations: ~(row_bits[r] | col_bits[c] | box_bits[b]) & 0x1FF.
- **Tests Required:** tests/unit/test_solvers.py testing candidate bitmask against board state.
- **Acceptance Criteria:** Candidates calculated in single CPU instruction cycle.

### TASK-027: Implement bitwise backtracking solver with Minimum Remaining Values (MRV)
- **Milestone:** Milestone 5: Bitwise Solving & High-Throughput Verification
- **Affected Files:** `engine/solvers/bitwise_solver.py`
- **Implementation Approach:** Traverse unassigned cells prioritizing cell with fewest set bits in candidate mask.
- **Tests Required:** tests/unit/test_solvers.py comparing bitwise solver speed against backtracking.
- **Acceptance Criteria:** Bitwise solver solves 100 easy-to-hard puzzles in under 100 milliseconds.

### TASK-028: Implement Bitwise fast validity checker
- **Milestone:** Milestone 5: Bitwise Solving & High-Throughput Verification
- **Affected Files:** `engine/solvers/bitwise_solver.py`
- **Implementation Approach:** Verify complete 81-cell grid validity by verifying every house bitmask equals 0x1FF (511).
- **Tests Required:** tests/unit/test_solvers.py testing bitwise full grid validation.
- **Acceptance Criteria:** Full board validation completes in less than 5 microseconds.

### TASK-029: Implement batch solution validator for dataset integrity checks
- **Milestone:** Milestone 5: Bitwise Solving & High-Throughput Verification
- **Affected Files:** `engine/solvers/bitwise_solver.py, tests/unit/test_solvers.py`
- **Implementation Approach:** Create utility verifying large batches of puzzle/solution string pairs efficiently.
- **Tests Required:** tests/unit/test_solvers.py validating batch of 200 sample puzzles.
- **Acceptance Criteria:** Batch validator flags invalid or mismatched solutions with zero false positives.

### TASK-030: Add fallback cascade solver orchestrator
- **Milestone:** Milestone 5: Bitwise Solving & High-Throughput Verification
- **Affected Files:** `engine/solvers/__init__.py`
- **Implementation Approach:** Provide unified solve_sudoku(grid, method='auto') that chooses Bitwise for fast solves and DLX for complex/uniqueness verification.
- **Tests Required:** tests/unit/test_solvers.py testing unified solver dispatch.
- **Acceptance Criteria:** Auto method selects optimal solver and returns clean SolutionResult.

### TASK-031: Implement SolutionCounter class using DLX and Bitwise hybrid
- **Milestone:** Milestone 6: Puzzle Uniqueness & Minimal Clue Reduction
- **Affected Files:** `engine/solvers/solution_counter.py`
- **Implementation Approach:** Create dedicated counter returning exact solution counts up to a configurable ceiling.
- **Tests Required:** tests/unit/test_solvers.py testing boards with 0, 1, 2, and 5+ solutions.
- **Acceptance Criteria:** Accurately distinguishes unique puzzles (count == 1) from multi-solution puzzles.

### TASK-032: Implement UniqueGenerator with guaranteed single-solution guarantee
- **Milestone:** Milestone 6: Puzzle Uniqueness & Minimal Clue Reduction
- **Affected Files:** `engine/generators/unique_generator.py`
- **Implementation Approach:** Generate full valid grid using randomized bitwise solver, then remove clues while checking uniqueness after each removal.
- **Tests Required:** tests/unit/test_generator.py testing 5 generated puzzles for single solution.
- **Acceptance Criteria:** 100% of generated puzzles have exactly one solution.

### TASK-033: Implement symmetrical clue removal (rotational, horizontal, vertical)
- **Milestone:** Milestone 6: Puzzle Uniqueness & Minimal Clue Reduction
- **Affected Files:** `engine/generators/unique_generator.py`
- **Implementation Approach:** Support rotational 180-degree symmetry in puzzle generation for visually pleasing boards.
- **Tests Required:** tests/unit/test_generator.py testing symmetry of generated clue patterns.
- **Acceptance Criteria:** Puzzles generated with symmetry='rotational' exhibit perfect 180-degree clue symmetry.

### TASK-034: Implement minimal puzzle clue reduction (irreducible puzzle test)
- **Milestone:** Milestone 6: Puzzle Uniqueness & Minimal Clue Reduction
- **Affected Files:** `engine/generators/unique_generator.py`
- **Implementation Approach:** Verify whether removing any additional clue from puzzle produces multiple solutions (minimal puzzle condition).
- **Tests Required:** tests/unit/test_generator.py testing minimality on sample puzzles.
- **Acceptance Criteria:** Minimal puzzles verified; adding any cell removal produces count > 1.

### TASK-035: Implement difficulty-targeted clue count generator parameterization
- **Milestone:** Milestone 6: Puzzle Uniqueness & Minimal Clue Reduction
- **Affected Files:** `engine/generators/unique_generator.py`
- **Implementation Approach:** Map 10 game progression levels to appropriate clue count ranges (Beginner: 45-50, Legend: 17-22).
- **Tests Required:** tests/unit/test_generator.py verifying clue counts across levels 1 to 10.
- **Acceptance Criteria:** Clue counts strictly adhere to tier specifications in README.md.

### TASK-036: Implement seedable deterministic puzzle generator for Daily Challenge
- **Milestone:** Milestone 6: Puzzle Uniqueness & Minimal Clue Reduction
- **Affected Files:** `engine/generators/unique_generator.py`
- **Implementation Approach:** Allow integer or date string seed (e.g., 2026-10-22) to produce identical puzzle for all users on given day.
- **Tests Required:** tests/unit/test_generator.py testing identical seeds produce identical grids.
- **Acceptance Criteria:** Identical seeds yield identical puzzle boards and solutions deterministically.

### TASK-037: Implement BaseStrategy abstract interface and HintResult contract
- **Milestone:** Milestone 7: Human Deduction Strategies — Singles & Subsets
- **Affected Files:** `engine/strategies/base_strategy.py`
- **Implementation Approach:** Define standard strategy interface with find_hints(board, candidates) returning structured Hint objects.
- **Tests Required:** tests/unit/test_strategies.py testing interface compliance.
- **Acceptance Criteria:** All strategies implement uniform interface with difficulty rank, explanation, and target cells.

### TASK-038: Implement Naked Singles detection strategy
- **Milestone:** Milestone 7: Human Deduction Strategies — Singles & Subsets
- **Affected Files:** `engine/strategies/singles.py`
- **Implementation Approach:** Detect cells that have only 1 legal candidate remaining in their candidate mask.
- **Tests Required:** tests/unit/test_strategies.py testing Naked Single scenario.
- **Acceptance Criteria:** Correctly identifies cell, value, and generates clear human-readable explanation.

### TASK-039: Implement Hidden Singles detection strategy across rows, columns, and boxes
- **Milestone:** Milestone 7: Human Deduction Strategies — Singles & Subsets
- **Affected Files:** `engine/strategies/singles.py`
- **Implementation Approach:** Detect digit that appears as candidate in only one cell within a house, even if that cell has other candidates.
- **Tests Required:** tests/unit/test_strategies.py testing Hidden Single in row, col, and box.
- **Acceptance Criteria:** Accurately identifies house type, index, cell coordinate, and digit.

### TASK-040: Implement Naked Pairs elimination strategy
- **Milestone:** Milestone 7: Human Deduction Strategies — Singles & Subsets
- **Affected Files:** `engine/strategies/subsets.py`
- **Implementation Approach:** Detect two cells in a house sharing the exact same two candidates, eliminating those candidates from all other cells in the house.
- **Tests Required:** tests/unit/test_strategies.py testing Naked Pair eliminations.
- **Acceptance Criteria:** Correctly identifies pair cells and candidate eliminations.

### TASK-041: Implement Naked Triples and Quads elimination strategy
- **Milestone:** Milestone 7: Human Deduction Strategies — Singles & Subsets
- **Affected Files:** `engine/strategies/subsets.py`
- **Implementation Approach:** Detect 3 cells sharing 3 candidates (or 4 sharing 4) within a house and eliminate them from peers.
- **Tests Required:** tests/unit/test_strategies.py testing Naked Triple scenario.
- **Acceptance Criteria:** Eliminates candidates from peers without false positives.

### TASK-042: Implement Hidden Pairs, Triples, and Quads detection strategy
- **Milestone:** Milestone 7: Human Deduction Strategies — Singles & Subsets
- **Affected Files:** `engine/strategies/subsets.py`
- **Implementation Approach:** Detect N digits that appear in only N cells within a house, eliminating all other candidates from those N cells.
- **Tests Required:** tests/unit/test_strategies.py testing Hidden Pair elimination.
- **Acceptance Criteria:** Identifies hidden subset and marks surplus candidates for elimination.

### TASK-043: Implement Pointing Pairs/Triples (Locked Candidates Type 1)
- **Milestone:** Milestone 8: Human Deduction Strategies — Intersections, Fish & Wings
- **Affected Files:** `engine/strategies/intersections.py`
- **Implementation Approach:** When all candidates for a digit in a box lie on single row or column, eliminate that candidate from rest of row/column.
- **Tests Required:** tests/unit/test_strategies.py testing Pointing Pair deduction.
- **Acceptance Criteria:** Correctly identifies box-line alignment and eliminates from row/col.

### TASK-044: Implement Box-Line Reduction (Locked Candidates Type 2)
- **Milestone:** Milestone 8: Human Deduction Strategies — Intersections, Fish & Wings
- **Affected Files:** `engine/strategies/intersections.py`
- **Implementation Approach:** When all candidates for a digit in a row or column lie within single box, eliminate that candidate from rest of box.
- **Tests Required:** tests/unit/test_strategies.py testing Box-Line reduction.
- **Acceptance Criteria:** Eliminates candidate from remaining box cells.

### TASK-045: Implement X-Wing detection strategy across rows and columns
- **Milestone:** Milestone 8: Human Deduction Strategies — Intersections, Fish & Wings
- **Affected Files:** `engine/strategies/fish.py`
- **Implementation Approach:** Identify 2 rows where a digit occurs in only 2 columns, and those columns match, eliminating the digit from rest of columns.
- **Tests Required:** tests/unit/test_strategies.py testing X-Wing elimination pattern.
- **Acceptance Criteria:** Accurately detects 4 corner cells and eliminates from target columns.

### TASK-046: Implement Swordfish and Jellyfish 3-line and 4-line fish patterns
- **Milestone:** Milestone 8: Human Deduction Strategies — Intersections, Fish & Wings
- **Affected Files:** `engine/strategies/fish.py`
- **Implementation Approach:** Detect 3x3 and 4x4 candidate alignments across parallel houses and eliminate candidates in perpendicular houses.
- **Tests Required:** tests/unit/test_strategies.py testing Swordfish deduction.
- **Acceptance Criteria:** Correctly identifies fish structure and performs eliminations.

### TASK-047: Implement XY-Wing (Y-Wing) deduction strategy
- **Milestone:** Milestone 8: Human Deduction Strategies — Intersections, Fish & Wings
- **Affected Files:** `engine/strategies/wings.py`
- **Implementation Approach:** Detect pivot cell with candidates {A, B} seeing pincer cells with {A, C} and {B, C}, eliminating C from cells seeing both pincers.
- **Tests Required:** tests/unit/test_strategies.py testing XY-Wing pattern.
- **Acceptance Criteria:** Identifies pivot, pincers, and target elimination cells.

### TASK-048: Implement Unique Rectangle (Type 1 & Type 2) uniqueness deductions
- **Milestone:** Milestone 8: Human Deduction Strategies — Intersections, Fish & Wings
- **Affected Files:** `engine/strategies/uniqueness.py`
- **Implementation Approach:** Exploit puzzle uniqueness property to avoid deadly patterns of 4 cells sharing 2 digits across 2 boxes.
- **Tests Required:** tests/unit/test_strategies.py testing Unique Rectangle Type 1.
- **Acceptance Criteria:** Eliminates deadly candidates to ensure uniqueness is preserved.

### TASK-049: Build HintEngine tiered deduction pipeline
- **Milestone:** Milestone 9: Intelligent Explanatory Hint Engine
- **Affected Files:** `engine/strategies/hint_engine.py`
- **Implementation Approach:** Order strategies by cognitive difficulty (Naked Singles -> Hidden Singles -> Intersections -> Subsets -> Wings -> Fish).
- **Tests Required:** tests/unit/test_strategies.py testing easiest hint returned first.
- **Acceptance Criteria:** Always offers simplest logical step before suggesting advanced techniques.

### TASK-050: Implement natural language hint explanation formatting
- **Milestone:** Milestone 9: Intelligent Explanatory Hint Engine
- **Affected Files:** `engine/strategies/hint_engine.py`
- **Implementation Approach:** Generate clear, encouraging text explaining WHY the deduction is valid (e.g. 'In Row 4, digit 7 can only appear in Box 5...').
- **Tests Required:** tests/unit/test_strategies.py verifying explanation string quality.
- **Acceptance Criteria:** Explanations are concise, grammatically correct, and reference specific coordinates.

### TASK-051: Implement smart error detection hint when board contains conflicts or invalid digits
- **Milestone:** Milestone 9: Intelligent Explanatory Hint Engine
- **Affected Files:** `engine/strategies/hint_engine.py`
- **Implementation Approach:** Before looking for deduction strategies, check if current board has conflicting or incorrect user digits and alert user gently.
- **Tests Required:** tests/unit/test_strategies.py testing hint on invalid user board.
- **Acceptance Criteria:** Hint identifies specific wrong cell rather than failing silently.

### TASK-052: Implement progressive 3-stage hint disclosure (Area -> Technique -> Direct Value)
- **Milestone:** Milestone 9: Intelligent Explanatory Hint Engine
- **Affected Files:** `engine/strategies/hint_engine.py`
- **Implementation Approach:** Stage 1 highlights the relevant house/region; Stage 2 names the technique; Stage 3 reveals cell and value if requested.
- **Tests Required:** tests/unit/test_strategies.py testing progressive hint stages.
- **Acceptance Criteria:** API returns structured hint supporting tiered frontend reveal.

### TASK-053: Add candidate elimination hint visualization payload
- **Milestone:** Milestone 9: Intelligent Explanatory Hint Engine
- **Affected Files:** `engine/strategies/hint_engine.py`
- **Implementation Approach:** Include coordinates of primary cells, secondary cells, and eliminated candidates in hint JSON payload.
- **Tests Required:** tests/unit/test_strategies.py testing payload structure.
- **Acceptance Criteria:** Payload contains exact cell list for UI highlighting.

### TASK-054: Ensure backward compatibility with legacy /api/game/hint and /api/games/<id>/hint
- **Milestone:** Milestone 9: Intelligent Explanatory Hint Engine
- **Affected Files:** `app.py, engine/strategies/hint_engine.py`
- **Implementation Approach:** Support both legacy {row, col, value} format and rich explanatory hint payload seamlessly.
- **Tests Required:** tests/integration/test_api.py testing hint endpoint responses.
- **Acceptance Criteria:** Legacy frontend continues working without code modification.

### TASK-055: Implement human-logic solver simulator for difficulty grading
- **Milestone:** Milestone 10: Difficulty Classification & Standard Rating
- **Affected Files:** `engine/solvers/logical_grader.py`
- **Implementation Approach:** Simulate human solver applying strategies progressively until puzzle is solved, recording highest strategy rank needed.
- **Tests Required:** tests/unit/test_generator.py testing difficulty classification of sample puzzles.
- **Acceptance Criteria:** Puzzles solvable only with singles classified as Easy; requiring fish classified as Hard/Expert.

### TASK-056: Implement Sudoku Explainer (SE) style numerical rating calculation
- **Milestone:** Milestone 10: Difficulty Classification & Standard Rating
- **Affected Files:** `engine/solvers/logical_grader.py`
- **Implementation Approach:** Compute numerical rating from 1.0 (Very Easy) to 9.5+ (Extreme) based on deduction technique weights and step count.
- **Tests Required:** tests/unit/test_generator.py testing SE ratings for known benchmark boards.
- **Acceptance Criteria:** Output aligns with standard competitive Sudoku difficulty metrics.

### TASK-057: Calibrate 10-Tier level progression system with SE rating thresholds
- **Milestone:** Milestone 10: Difficulty Classification & Standard Rating
- **Affected Files:** `sudoku_engine.py, engine/solvers/logical_grader.py`
- **Implementation Approach:** Map levels 1-10 to concrete SE score bands (Level 1: 1.0-1.5, Level 5: 3.5-4.5, Level 10: 8.0+).
- **Tests Required:** tests/unit/test_generator.py verifying level band boundaries.
- **Acceptance Criteria:** Each tier correctly filters and verifies puzzles matching its difficulty band.

### TASK-058: Implement Givens count and symmetry scoring metrics
- **Milestone:** Milestone 10: Difficulty Classification & Standard Rating
- **Affected Files:** `engine/solvers/logical_grader.py`
- **Implementation Approach:** Compute clue count distribution, row/column balance, and rotational symmetry coefficient.
- **Tests Required:** tests/unit/test_generator.py testing symmetry metrics.
- **Acceptance Criteria:** Returns structural metrics in puzzle metadata.

### TASK-059: Integrate difficulty grading into dataset verification script
- **Milestone:** Milestone 10: Difficulty Classification & Standard Rating
- **Affected Files:** `scripts/verify_dataset.py`
- **Implementation Approach:** Provide automated script to audit a sample of sudoku_records.jsonl verifying correct tier tags.
- **Tests Required:** tests/integration/test_api.py checking dataset sample ratings.
- **Acceptance Criteria:** Audited sample confirms 100% adherence to declared difficulty tier.

### TASK-060: Expose difficulty analysis endpoint in REST API
- **Milestone:** Milestone 10: Difficulty Classification & Standard Rating
- **Affected Files:** `app.py`
- **Implementation Approach:** Add /api/puzzles/analyze endpoint accepting 81-char string and returning SE rating, technique breakdown, and solvability.
- **Tests Required:** tests/integration/test_api.py testing /api/puzzles/analyze.
- **Acceptance Criteria:** Returns HTTP 200 with complete difficulty breakdown.

### TASK-061: Implement GameSession dataclass with server-side validation state
- **Milestone:** Milestone 11: Game State Management & Anti-Tamper Security
- **Affected Files:** `core/models/session.py, app.py`
- **Implementation Approach:** Store active puzzle ID, initial board, current board, solution hash, start timestamp, mistake count, and hints used in session.
- **Tests Required:** tests/integration/test_api.py testing session lifecycle.
- **Acceptance Criteria:** Client cannot forge solved state without matching server solution.

### TASK-062: Implement secure HMAC puzzle solution hashing
- **Milestone:** Milestone 11: Game State Management & Anti-Tamper Security
- **Affected Files:** `core/security.py, app.py`
- **Implementation Approach:** Never expose raw solution string to client; send SHA-256 HMAC hash of solution with server secret key for validation verification.
- **Tests Required:** tests/integration/test_api.py verifying solution is not exposed in /api/puzzles/random.
- **Acceptance Criteria:** Response contains puzzle clues and puzzle_id; full solution string is never transmitted to client.

### TASK-063: Implement server-side 3-strike mistake enforcement
- **Milestone:** Milestone 11: Game State Management & Anti-Tamper Security
- **Affected Files:** `app.py, db.py`
- **Implementation Approach:** Track invalid moves on server; reject moves once 3 strikes are reached unless game is restarted.
- **Tests Required:** tests/integration/test_api.py testing 3-strike failure condition.
- **Acceptance Criteria:** Submitting 3 invalid moves transitions game status to 'failed'.

### TASK-064: Implement game completion validation and anti-speedhack checks
- **Milestone:** Milestone 11: Game State Management & Anti-Tamper Security
- **Affected Files:** `app.py`
- **Implementation Approach:** Ensure game completion time is physically plausible (> 15 seconds) before awarding full XP and leaderboard records.
- **Tests Required:** tests/integration/test_api.py testing rapid completion rejection.
- **Acceptance Criteria:** Completion under 10 seconds flagged as suspicious and denied XP bonus.

### TASK-065: Implement active game auto-save and resume endpoint
- **Milestone:** Milestone 11: Game State Management & Anti-Tamper Security
- **Affected Files:** `app.py, db.py`
- **Implementation Approach:** Persist in-flight board state and elapsed seconds to SQLite so users can reload page without losing progress.
- **Tests Required:** tests/integration/test_api.py testing save and resume flow.
- **Acceptance Criteria:** Reloading active game restores identical board state and timer.

### TASK-066: Implement session cleanup cron/purge for abandoned games
- **Milestone:** Milestone 11: Game State Management & Anti-Tamper Security
- **Affected Files:** `db.py`
- **Implementation Approach:** Purge games abandoned for more than 7 days from active session tables to keep database lightweight.
- **Tests Required:** tests/integration/test_api.py testing purge routine.
- **Acceptance Criteria:** Old abandoned sessions successfully archived without touching completed records.

### TASK-067: Implement server-validated pause/resume timestamps
- **Milestone:** Milestone 12: Precision Timer & Anti-Cheat Pause Curtain
- **Affected Files:** `app.py, db.py`
- **Implementation Approach:** Record pause_timestamp and resume_timestamp in session to prevent client clock manipulation while paused.
- **Tests Required:** tests/integration/test_api.py testing pause/resume duration deduction.
- **Acceptance Criteria:** Paused duration is accurately deducted from total elapsed time.

### TASK-068: Ensure client pause curtain prevents puzzle visibility during pause
- **Milestone:** Milestone 12: Precision Timer & Anti-Cheat Pause Curtain
- **Affected Files:** `static/app.js`
- **Implementation Approach:** Confirm DOM board blur and overlay curtain activate immediately upon pause and board numbers remain invisible until resume.
- **Tests Required:** tests/unit/test_board.py testing pause state logic.
- **Acceptance Criteria:** Board cannot be inspected via styles or DOM text while paused.

### TASK-069: Implement high-resolution monotonic timer calculation in backend
- **Milestone:** Milestone 12: Precision Timer & Anti-Cheat Pause Curtain
- **Affected Files:** `core/time_utils.py`
- **Implementation Approach:** Use time.monotonic() for server duration delta calculation to prevent system clock shift errors.
- **Tests Required:** tests/unit/test_core.py testing monotonic delta precision.
- **Acceptance Criteria:** Timer calculations immune to daylight savings or system clock updates.

### TASK-070: Implement max pause duration policy
- **Milestone:** Milestone 12: Precision Timer & Anti-Cheat Pause Curtain
- **Affected Files:** `core/config.py, app.py`
- **Implementation Approach:** Limit total accumulated pause time in ranked matches to 10 minutes to prevent infinite matchmaking stalling.
- **Tests Required:** tests/integration/test_api.py testing max pause timeout.
- **Acceptance Criteria:** Exceeding max pause time auto-forfeits ranked match.

### TASK-071: Format time utilities for MM:SS and HH:MM:SS display
- **Milestone:** Milestone 12: Precision Timer & Anti-Cheat Pause Curtain
- **Affected Files:** `core/time_utils.py, static/app.js`
- **Implementation Approach:** Ensure consistent formatting between Python backend and JavaScript frontend.
- **Tests Required:** tests/unit/test_core.py testing duration formatting.
- **Acceptance Criteria:** Times format identically in backend logs and frontend UI.

### TASK-072: Add automated tests for timer pause and resume state transitions
- **Milestone:** Milestone 12: Precision Timer & Anti-Cheat Pause Curtain
- **Affected Files:** `tests/integration/test_api.py`
- **Implementation Approach:** Simulate multi-pause games and verify total net solve time equals active play time.
- **Tests Required:** pytest tests/integration/test_api.py -k timer.
- **Acceptance Criteria:** Net solve time accurate to within 1 second.

### TASK-073: Formalize LevelConfig dataclass for all 10 progression tiers
- **Milestone:** Milestone 13: 10-Tier Level Progression & XP Award Rules
- **Affected Files:** `core/models/level.py, sudoku_engine.py`
- **Implementation Approach:** Define level metadata (name, min_clues, max_clues, base_xp, unlock_threshold, badge, color) in strongly typed structure.
- **Tests Required:** tests/unit/test_core.py verifying all 10 level definitions.
- **Acceptance Criteria:** All 10 levels match README specification with complete metadata.

### TASK-074: Implement sequential level unlock validation in backend
- **Milestone:** Milestone 13: 10-Tier Level Progression & XP Award Rules
- **Affected Files:** `db.py, app.py`
- **Implementation Approach:** Enforce requirement: Level N can only be played if Level N-1 has at least 1 completed solve recorded for user.
- **Tests Required:** tests/integration/test_api.py testing locked level request rejection.
- **Acceptance Criteria:** Requesting locked level returns HTTP 403 Forbidden with unlock requirement.

### TASK-075: Implement dynamic XP calculation with speed, hint, and mistake bonuses
- **Milestone:** Milestone 13: 10-Tier Level Progression & XP Award Rules
- **Affected Files:** `app.py, db.py`
- **Implementation Approach:** Calculate final XP: base_xp + speed_bonus - (hints_used * 15) - (mistakes * 20) with minimum floor.
- **Tests Required:** tests/unit/test_core.py testing XP formula boundary cases.
- **Acceptance Criteria:** Clean solves earn maximum XP; hints/mistakes reduce bonus proportionally.

### TASK-076: Implement Daily Challenge 2x XP multiplier and streak tracking
- **Milestone:** Milestone 13: 10-Tier Level Progression & XP Award Rules
- **Affected Files:** `app.py, db.py`
- **Implementation Approach:** Award 2x XP for completing today's daily challenge and increment user's daily_streak if consecutive day.
- **Tests Required:** tests/integration/test_api.py testing daily streak increment and reset.
- **Acceptance Criteria:** Daily challenge awards double XP; missing a day resets streak to 1.

### TASK-077: Implement Player Level calculation based on cumulative XP curve
- **Milestone:** Milestone 13: 10-Tier Level Progression & XP Award Rules
- **Affected Files:** `core/models/level.py`
- **Implementation Approach:** Map total player XP to player account level using quadratic progression formula (level = sqrt(xp / 100)).
- **Tests Required:** tests/unit/test_core.py testing level calculation across XP tiers.
- **Acceptance Criteria:** Player level scales smoothly from Level 1 to Level 100+.

### TASK-078: Ensure /api/levels endpoint returns full tier status including user unlock state
- **Milestone:** Milestone 13: 10-Tier Level Progression & XP Award Rules
- **Affected Files:** `app.py`
- **Implementation Approach:** Return level list annotated with is_unlocked: bool for authenticated session.
- **Tests Required:** tests/integration/test_api.py testing /api/levels response schema.
- **Acceptance Criteria:** Frontend roadmap highlights unlocked levels and locks inaccessible tiers.

### TASK-079: Implement standard ELO rating adjustment calculator
- **Milestone:** Milestone 14: Competitive Ranked ELO & Leaderboard Engine
- **Affected Files:** `core/elo.py, ranked_ws.py`
- **Implementation Approach:** Implement ELO formula: E = 1 / (1 + 10^((R_opp - R_player) / 400)) with dynamic K-factor based on match count.
- **Tests Required:** tests/unit/test_core.py testing win, loss, and draw ELO calculations.
- **Acceptance Criteria:** Rating changes match international chess standard ELO adjustments.

### TASK-080: Implement 8 Competitive Tier boundary definitions
- **Milestone:** Milestone 14: Competitive Ranked ELO & Leaderboard Engine
- **Affected Files:** `core/constants.py, ranked_ws.py`
- **Implementation Approach:** Define rating bands: Bronze (1000-1199), Silver (1200-1399), Gold (1400-1599), Platinum (1600-1799), Diamond (1800-1999), Master (2000-2199), Grandmaster (2200-2399), Legend (2400+).
- **Tests Required:** tests/unit/test_core.py testing rating-to-tier mappings.
- **Acceptance Criteria:** Tier names and icons accurately assigned based on current ELO.

### TASK-081: Implement Ranked Solo Benchmark Matchmaking engine
- **Milestone:** Milestone 14: Competitive Ranked ELO & Leaderboard Engine
- **Affected Files:** `ranked_ws.py, app.py`
- **Implementation Approach:** Pair player against benchmark bot with matched ELO rating and realistic completion speed distribution.
- **Tests Required:** tests/integration/test_api.py testing matchmaking opponent generation.
- **Acceptance Criteria:** Opponent rating is within +/- 75 points of player rating.

### TASK-082: Implement Season 01 ('MASTER THE GRID') leaderboard pagination and caching
- **Milestone:** Milestone 14: Competitive Ranked ELO & Leaderboard Engine
- **Affected Files:** `db.py, app.py`
- **Implementation Approach:** Query top 100 leaderboard with rank, user, rating, tier, win_rate, and best_time with 30-second memory cache.
- **Tests Required:** tests/integration/test_api.py testing leaderboard endpoint and caching.
- **Acceptance Criteria:** Leaderboard responds in under 10 milliseconds.

### TASK-083: Implement seasonal tier demotion protection
- **Milestone:** Milestone 14: Competitive Ranked ELO & Leaderboard Engine
- **Affected Files:** `core/elo.py`
- **Implementation Approach:** Prevent player from dropping below tier floor during a 3-game grace period after entering new tier.
- **Tests Required:** tests/unit/test_core.py testing demotion buffer.
- **Acceptance Criteria:** Demotion buffer protects rank on initial losses.

### TASK-084: Implement match history logging and win/loss statistics
- **Milestone:** Milestone 14: Competitive Ranked ELO & Leaderboard Engine
- **Affected Files:** `db.py`
- **Implementation Approach:** Record completed match entries with opponent, puzzle seed, duration, rating delta, and final standings.
- **Tests Required:** tests/integration/test_api.py testing match history persistence.
- **Acceptance Criteria:** History accurately reflects in player profile.

### TASK-085: Refactor achievements catalog into strongly typed definitions
- **Milestone:** Milestone 15: Achievements Engine & Milestone Unlocks
- **Affected Files:** `achievements.py`
- **Implementation Approach:** Define 12 distinct achievements (e.g. 'First Step', 'Speed Demon', 'Flawless Solve', 'Grandmaster Solved') with evaluation rules.
- **Tests Required:** tests/unit/test_core.py verifying achievement catalog completeness.
- **Acceptance Criteria:** All 12 achievements defined with badge, condition, and XP reward.

### TASK-086: Implement event-driven achievement evaluation pipeline
- **Milestone:** Milestone 15: Achievements Engine & Milestone Unlocks
- **Affected Files:** `achievements.py, core/events.py`
- **Implementation Approach:** Subscribe achievement engine to GAME_COMPLETED events and check criteria asynchronously.
- **Tests Required:** tests/unit/test_core.py testing event-triggered unlocks.
- **Acceptance Criteria:** Qualified achievements unlocked without blocking game completion response.

### TASK-087: Implement 'Speed Demon' achievement check (< 3 min solve)
- **Milestone:** Milestone 15: Achievements Engine & Milestone Unlocks
- **Affected Files:** `achievements.py`
- **Implementation Approach:** Verify solve completed in under 180 seconds on Level 3 or higher without mistakes.
- **Tests Required:** tests/unit/test_core.py testing Speed Demon unlock conditions.
- **Acceptance Criteria:** Unlocks exactly when conditions are satisfied.

### TASK-088: Implement 'Flawless Solve' achievement check (0 mistakes, 0 hints)
- **Milestone:** Milestone 15: Achievements Engine & Milestone Unlocks
- **Affected Files:** `achievements.py`
- **Implementation Approach:** Verify game completed with zero strikes and zero hints used.
- **Tests Required:** tests/unit/test_core.py testing Flawless Solve criteria.
- **Acceptance Criteria:** Unlocks only on completely pure solves.

### TASK-089: Implement 'Daily Dedication' 7-day streak achievement check
- **Milestone:** Milestone 15: Achievements Engine & Milestone Unlocks
- **Affected Files:** `achievements.py`
- **Implementation Approach:** Verify user has completed 7 consecutive daily challenges.
- **Tests Required:** tests/unit/test_core.py testing streak achievement condition.
- **Acceptance Criteria:** Unlocks on 7th consecutive daily solve.

### TASK-090: Expose unlocked achievements in user profile and stats API
- **Milestone:** Milestone 15: Achievements Engine & Milestone Unlocks
- **Affected Files:** `app.py, db.py`
- **Implementation Approach:** Include unlocked timestamp, progress percentage, and badge icon in /api/user/achievements.
- **Tests Required:** tests/integration/test_api.py testing achievement API.
- **Acceptance Criteria:** Returns full list of locked and unlocked achievements.

### TASK-091: Implement SQLite connection context manager with WAL mode verification
- **Milestone:** Milestone 16: Database Resilience, WAL & Connection Pooling
- **Affected Files:** `db.py`
- **Implementation Approach:** Ensure every SQLite connection enables PRAGMA journal_mode=WAL, PRAGMA synchronous=NORMAL, and foreign key enforcement.
- **Tests Required:** tests/integration/test_api.py checking PRAGMA settings on active connection.
- **Acceptance Criteria:** Connections execute in WAL mode without database locked errors.

### TASK-092: Implement automatic database schema initialization and idempotency
- **Milestone:** Milestone 16: Database Resilience, WAL & Connection Pooling
- **Affected Files:** `db.py`
- **Implementation Approach:** Ensure init_db() safely creates all necessary tables (users, games, achievements, ranked_matches) using IF NOT EXISTS.
- **Tests Required:** tests/integration/test_api.py running init_db() twice consecutively.
- **Acceptance Criteria:** Subsequent calls succeed without error or data loss.

### TASK-093: Implement atomic transaction management with rollback on failure
- **Milestone:** Milestone 16: Database Resilience, WAL & Connection Pooling
- **Affected Files:** `db.py`
- **Implementation Approach:** Wrap multi-table operations (e.g. game completion + XP award + achievement check) in single atomic transaction.
- **Tests Required:** tests/integration/test_api.py testing rollback on simulated exception.
- **Acceptance Criteria:** Rollback prevents orphaned rows or corrupted XP balances.

### TASK-094: Implement database indexes on frequent query columns
- **Milestone:** Milestone 16: Database Resilience, WAL & Connection Pooling
- **Affected Files:** `db.py`
- **Implementation Approach:** Add indexes on games(user_id, status), games(level), ranked_matches(player_id), and users(rating DESC).
- **Tests Required:** tests/integration/test_api.py verifying index presence via PRAGMA index_list.
- **Acceptance Criteria:** Query execution plan uses indexes for fast lookups.

### TASK-095: Implement database integrity check routine
- **Milestone:** Milestone 16: Database Resilience, WAL & Connection Pooling
- **Affected Files:** `db.py, scripts/check_db.py`
- **Implementation Approach:** Provide check_database_integrity() function executing PRAGMA integrity_check and logging anomalies.
- **Tests Required:** tests/integration/test_api.py testing integrity check output.
- **Acceptance Criteria:** Returns 'ok' on clean database.

### TASK-096: Add automated SQLite backup utility
- **Milestone:** Milestone 16: Database Resilience, WAL & Connection Pooling
- **Affected Files:** `db.py`
- **Implementation Approach:** Implement backup_database(backup_dir) using SQLite Online Backup API (sqlite3.backup).
- **Tests Required:** tests/integration/test_api.py testing backup creation and restoration.
- **Acceptance Criteria:** Backup completes without locking active readers/writers.

### TASK-097: Implement centralized JSON error handling with consistent schemas
- **Milestone:** Milestone 17: REST API Validation, Blueprints & Error Handling
- **Affected Files:** `app.py, core/exceptions.py`
- **Implementation Approach:** Register Flask error handlers for 400, 403, 404, 422, 500 returning uniform {'success': false, 'error': '...', 'code': ...} payload.
- **Tests Required:** tests/integration/test_api.py testing invalid route and malformed input.
- **Acceptance Criteria:** All error responses return clean JSON instead of HTML error pages.

### TASK-098: Implement request payload validation decorator
- **Milestone:** Milestone 17: REST API Validation, Blueprints & Error Handling
- **Affected Files:** `core/validation.py, app.py`
- **Implementation Approach:** Create @validate_payload(schema) decorator checking required fields, data types, and value bounds.
- **Tests Required:** tests/integration/test_api.py testing missing and extra fields in POST request.
- **Acceptance Criteria:** Malformed payloads rejected with descriptive HTTP 400 messages.

### TASK-099: Implement /api/game/validate coordinate and value bounds validation
- **Milestone:** Milestone 17: REST API Validation, Blueprints & Error Handling
- **Affected Files:** `app.py`
- **Implementation Approach:** Enforce 0 <= row <= 8, 0 <= col <= 8, 1 <= value <= 9 on move submission.
- **Tests Required:** tests/integration/test_api.py submitting out-of-range moves.
- **Acceptance Criteria:** Returns HTTP 400 for out-of-range values with specific field error.

### TASK-100: Implement backward-compatible alias endpoints for legacy API clients
- **Milestone:** Milestone 17: REST API Validation, Blueprints & Error Handling
- **Affected Files:** `app.py`
- **Implementation Approach:** Ensure /api/game/validate routes to /api/games/<id>/move and /api/game/hint routes to /api/games/<id>/hint.
- **Tests Required:** tests/integration/test_api.py testing both endpoint paths.
- **Acceptance Criteria:** Both legacy and modern endpoints return identical valid responses.

### TASK-101: Implement rate limiting on puzzle generation and hint endpoints
- **Milestone:** Milestone 17: REST API Validation, Blueprints & Error Handling
- **Affected Files:** `core/rate_limiter.py, app.py`
- **Implementation Approach:** Protect against API spam by limiting /api/puzzles/random to 30 requests/minute per session.
- **Tests Required:** tests/integration/test_api.py testing rate limit threshold.
- **Acceptance Criteria:** Excess requests return HTTP 429 Too Many Requests.

### TASK-102: Add API health check and version metadata endpoint
- **Milestone:** Milestone 17: REST API Validation, Blueprints & Error Handling
- **Affected Files:** `app.py`
- **Implementation Approach:** Provide /api/health returning system status, engine version, database connectivity, and timestamp.
- **Tests Required:** tests/integration/test_api.py testing /api/health.
- **Acceptance Criteria:** Returns HTTP 200 with status: 'healthy'.

### TASK-103: Preserve all existing HTML elements, IDs, classes, and styling in UI
- **Milestone:** Milestone 18: JavaScript Game Controller & State Synchronization
- **Affected Files:** `templates/index.html, static/style.css`
- **Implementation Approach:** Verify that all UI updates are strictly logic-only, preserving exact DOM hierarchy, button IDs, and visual CSS styling.
- **Tests Required:** Manual DOM node inspection and baseline regression tests.
- **Acceptance Criteria:** Zero modifications to CSS styles, fonts, layout, or visual presentation.

### TASK-104: Harden notes/pencil mode toggling and candidate cleanup
- **Milestone:** Milestone 18: JavaScript Game Controller & State Synchronization
- **Affected Files:** `static/app.js`
- **Implementation Approach:** When user places a confirmed digit in a cell, automatically clear that candidate from notes of all peer cells.
- **Tests Required:** Verify note cleanup in browser simulator.
- **Acceptance Criteria:** Entering a number automatically eliminates it from peer cell pencil marks.

### TASK-105: Implement multi-level Undo/Redo stack with candidate note restoration
- **Milestone:** Milestone 18: JavaScript Game Controller & State Synchronization
- **Affected Files:** `static/app.js`
- **Implementation Approach:** Ensure Undo ('U' or Undo button) accurately restores previous value AND previous pencil notes for that cell.
- **Tests Required:** Verify sequential undo and redo operations.
- **Acceptance Criteria:** Undo restores cell value and exact pencil marks present prior to move.

### TASK-106: Implement remaining number counter accuracy updates
- **Milestone:** Milestone 18: JavaScript Game Controller & State Synchronization
- **Affected Files:** `static/app.js`
- **Implementation Approach:** Update 1-9 keypad counters in real-time, dimming keypad digits when all 9 instances are placed on board.
- **Tests Required:** Verify keypad count decrements on digit placement.
- **Acceptance Criteria:** Numbers with 9 correct placements correctly dim and disable.

### TASK-107: Harden client-side timer against tab background throttling
- **Milestone:** Milestone 18: JavaScript Game Controller & State Synchronization
- **Affected Files:** `static/app.js`
- **Implementation Approach:** Use performance.now() and actual timestamp differences rather than relying solely on setInterval ticks.
- **Tests Required:** Simulate tab switching for 60 seconds.
- **Acceptance Criteria:** Timer displays true elapsed time without drift when tab returns to foreground.

### TASK-108: Add graceful network failure and offline retry banner
- **Milestone:** Milestone 18: JavaScript Game Controller & State Synchronization
- **Affected Files:** `static/app.js`
- **Implementation Approach:** Catch network fetch failures gracefully and display retry prompt without clearing active board state.
- **Tests Required:** Simulate offline network condition on move submission.
- **Acceptance Criteria:** Board state preserved and retry button appears seamlessly.

### TASK-109: Implement full arrow-key board navigation (Up, Down, Left, Right)
- **Milestone:** Milestone 19: Keyboard Accessibility & Screen Reader Support
- **Affected Files:** `static/app.js`
- **Implementation Approach:** Allow players to navigate 9x9 grid cells smoothly using Arrow keys with row/column boundary wrapping.
- **Tests Required:** Verify keyboard cell focus traversal.
- **Acceptance Criteria:** Arrow keys shift active cell focus reliably without page scrolling.

### TASK-110: Implement Numpad and Top-Row number input mapping
- **Milestone:** Milestone 19: Keyboard Accessibility & Screen Reader Support
- **Affected Files:** `static/app.js`
- **Implementation Approach:** Support keys 1-9 (main keyboard and Numpad) for digit entry and Delete/Backspace for clearing.
- **Tests Required:** Verify keystroke handling across all number inputs.
- **Acceptance Criteria:** Both standard and Numpad inputs place digits correctly.

### TASK-111: Implement standard keyboard shortcuts (N for notes, H for hint, U for undo, P for pause)
- **Milestone:** Milestone 19: Keyboard Accessibility & Screen Reader Support
- **Affected Files:** `static/app.js`
- **Implementation Approach:** Bind global hotkeys without conflicting with browser default shortcuts.
- **Tests Required:** Verify shortcut trigger handling.
- **Acceptance Criteria:** Shortcuts toggle modes accurately.

### TASK-112: Add ARIA attributes and live region for screen reader cell announcements
- **Milestone:** Milestone 19: Keyboard Accessibility & Screen Reader Support
- **Affected Files:** `templates/index.html, static/app.js`
- **Implementation Approach:** Add aria-label='Row X, Column Y, Value Z' and aria-live='polite' announcements for placed digits and errors without altering CSS.
- **Tests Required:** Verify DOM accessibility tree inspection.
- **Acceptance Criteria:** Screen readers announce cell coordinates and values accurately.

### TASK-113: Ensure focus outlines are clear and accessible without altering design aesthetic
- **Milestone:** Milestone 19: Keyboard Accessibility & Screen Reader Support
- **Affected Files:** `static/style.css`
- **Implementation Approach:** Maintain high-visibility focus indicators for keyboard navigation while preserving custom dark theme aesthetics.
- **Tests Required:** Verify keyboard focus visibility across all buttons and grid cells.
- **Acceptance Criteria:** Focus states clearly visible without breaking layout.

### TASK-114: Implement Escape key modal dismiss and pause handling
- **Milestone:** Milestone 19: Keyboard Accessibility & Screen Reader Support
- **Affected Files:** `static/app.js`
- **Implementation Approach:** Pressing Escape closes active dialogs (stats, settings, win modal) or toggles pause cleanly.
- **Tests Required:** Verify modal closing on Escape keypress.
- **Acceptance Criteria:** Modals close smoothly and return focus to active grid cell.

### TASK-115: Benchmark solver throughput across 1,000 diverse puzzles
- **Milestone:** Milestone 20: Performance Profiling, Security & QA Hardening
- **Affected Files:** `scripts/benchmark_solvers.py, tests/unit/test_solvers.py`
- **Implementation Approach:** Measure solve times for Bitwise, DLX, and Backtracking solvers across 1,000 test cases.
- **Tests Required:** python scripts/benchmark_solvers.py.
- **Acceptance Criteria:** Average solve time under 2 milliseconds; zero failures.

### TASK-116: Implement automated secret scanning check in test suite
- **Milestone:** Milestone 20: Performance Profiling, Security & QA Hardening
- **Affected Files:** `tests/unit/test_core.py`
- **Implementation Approach:** Scan repository files for exposed API keys, private keys, or plain passwords before commits.
- **Tests Required:** pytest tests/unit/test_core.py -k secret.
- **Acceptance Criteria:** Zero exposed credentials detected across all tracked files.

### TASK-117: Implement comprehensive SQL injection vulnerability test suite
- **Milestone:** Milestone 20: Performance Profiling, Security & QA Hardening
- **Affected Files:** `tests/integration/test_api.py`
- **Implementation Approach:** Submit malicious SQL payloads (e.g. "' OR 1=1; --") to all API endpoints and verify parameterized query safety.
- **Tests Required:** pytest tests/integration/test_api.py -k injection.
- **Acceptance Criteria:** All inputs safely escaped; zero SQL injection vulnerabilities.

### TASK-118: Implement XSS sanitization check for user names and leaderboard data
- **Milestone:** Milestone 20: Performance Profiling, Security & QA Hardening
- **Affected Files:** `tests/integration/test_api.py, app.py`
- **Implementation Approach:** Ensure all user-supplied text rendered on leaderboard is properly escaped via Jinja2 autoescaping.
- **Tests Required:** pytest tests/integration/test_api.py -k xss.
- **Acceptance Criteria:** HTML tags in usernames escaped safely.

### TASK-119: Add end-to-end integration test simulating full 10-level playthrough
- **Milestone:** Milestone 20: Performance Profiling, Security & QA Hardening
- **Affected Files:** `tests/integration/test_api.py`
- **Implementation Approach:** Simulate user journey solving Level 1 through Level 10 sequentially, verifying unlocks and XP accumulation.
- **Tests Required:** pytest tests/integration/test_api.py -k playthrough.
- **Acceptance Criteria:** Full playthrough passes with correct XP awards and unlocked tiers.

### TASK-120: Add end-to-end ranked matchmaking and ELO update integration test
- **Milestone:** Milestone 20: Performance Profiling, Security & QA Hardening
- **Affected Files:** `tests/integration/test_api.py`
- **Implementation Approach:** Simulate ranked match against benchmark bot, verify rating calculation, tier promotion, and leaderboard updates.
- **Tests Required:** pytest tests/integration/test_api.py -k ranked.
- **Acceptance Criteria:** Ranked workflow executes cleanly and updates leaderboard.

### TASK-121: Implement comprehensive LOC counting and categorization validation
- **Milestone:** Milestone 20: Performance Profiling, Security & QA Hardening
- **Affected Files:** `scripts/count_loc.py, tests/unit/test_core.py`
- **Implementation Approach:** Verify that scripts/count_loc.py accurately identifies and reports source LOC without counting excluded directories.
- **Tests Required:** python scripts/count_loc.py.
- **Acceptance Criteria:** Accurate LOC report written to LOC_REPORT.md.

### TASK-122: Update DEVELOPMENT_PROGRESS.md with verified milestone completion logs
- **Milestone:** Milestone 20: Performance Profiling, Security & QA Hardening
- **Affected Files:** `docs/DEVELOPMENT_PROGRESS.md`
- **Implementation Approach:** Record all completed tasks, commit hashes, pull requests, test summaries, and LOC measurements.
- **Tests Required:** Verify documentation completeness.
- **Acceptance Criteria:** Tracker is 100% synchronized with actual Git commits and PRs.

### TASK-123: Validate frontend visual layout integrity against original baseline
- **Milestone:** Milestone 20: Performance Profiling, Security & QA Hardening
- **Affected Files:** `templates/index.html, static/style.css`
- **Implementation Approach:** Perform regression audit verifying exact match of visual elements, font imports, colors, buttons, and animations.
- **Tests Required:** Interface regression audit.
- **Acceptance Criteria:** Original UI is 100% preserved functionally and visually.

### TASK-124: Verify cross-platform compatibility on Windows, Linux, and macOS
- **Milestone:** Milestone 20: Performance Profiling, Security & QA Hardening
- **Affected Files:** `tests/conftest.py, app.py`
- **Implementation Approach:** Ensure file path handling uses pathlib.Path or os.path cleanly without hardcoded Windows or Unix slashes.
- **Tests Required:** pytest tests/.
- **Acceptance Criteria:** All tests execute and pass cleanly across operating systems.

### TASK-125: Prepare final release tag and production deployment documentation
- **Milestone:** Milestone 20: Performance Profiling, Security & QA Hardening
- **Affected Files:** `README.md, ARCHITECTURE.md`
- **Implementation Approach:** Document production startup using Gunicorn/Waitress, reverse proxy configuration, and maintenance procedures.
- **Tests Required:** Documentation review.
- **Acceptance Criteria:** Clean, professional deployment and maintenance guide.
