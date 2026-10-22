# Sudoku Quest — System Architecture & Technical Specifications

**Version:** 2.0-Modular  
**Architecture Style:** Domain-Driven Modular Monolith with Event-Driven Real-Time Extensions  

---

## 1. Architectural Overview

Sudoku Quest is organized into cleanly separated layers:

```
+-------------------------------------------------------------------------+
|                              Presentation Layer                         |
|   HTML5 SPA Templates  *  Vanilla CSS3 Tokens  *  Modular ES6 Client    |
+-------------------------------------------------------------------------+
                                    |
                                    v (HTTP REST / WebSocket WS)
+-------------------------------------------------------------------------+
|                              Application & API Layer                    |
|   Flask Blueprints  *  Socket.IO Handlers  *  Session Middleware        |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                              Domain & Engine Layer                      |
|   Solvers (DLX, Bitwise)   *  Strategy Deductions (30+ algorithms)      |
|   Uniqueness Generators    *  Academy Curriculum & Quizzes              |
|   Variant Sudoku Handlers  *  Gamification & ELO Calculators            |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                              Persistence Layer                          |
|   SQLite Engine (WAL)      *  Repository Pattern   *  Connection Pool   |
|   500,000 JSONL Dataset    *  Schema Migrations    *  In-Memory Caches  |
+-------------------------------------------------------------------------+
```

---

## 2. Core Subsystems

### 2.1 The Algorithmic Engine (`engine/`)
- **Solvers:**
  - **Dancing Links (DLX):** Exact cover matrix representation using Knuth's Algorithm X for sub-millisecond solving and guaranteed solution enumeration.
  - **Bitwise Solver:** Ultra-compact 9-bit bitmask operations for blazing-fast candidate filtering.
  - **Backtracking Solver:** Heuristic backtracking using Minimum Remaining Values (MRV).
  - **Solution Counter:** Uniqueness testing stopping early if solutions > 1.
- **Generators:**
  - **Isomorphic Generator:** Rapid transformation of solved canonical grids via band/stack shuffling and digit permutations.
  - **Uniqueness Generator:** Controlled cell-digging with uniqueness verification for 10 distinct difficulty tiers.
  - **Symmetric Generator:** 180-degree rotational and diagonal symmetric clue distributions.
- **Human Deduction Engine (Strategies):**
  - **Singles:** Naked Single, Hidden Single.
  - **Intersections:** Pointing Pairs/Triples, Box/Line Reduction.
  - **Subsets:** Naked Pairs, Triples, Quads; Hidden Pairs, Triples, Quads.
  - **Fish:** X-Wing, Swordfish, Jellyfish, Finned Fish.
  - **Wings:** XY-Wing, XYZ-Wing, W-Wing.
  - **Coloring & Chains:** Simple Coloring, Multi-Coloring, 3D Medusa, XY-Chains, Remote Pairs.
  - **Uniqueness Techniques:** Unique Rectangle Types 1 through 6, Bivalue Universal Grave (BUG).

### 2.2 The Educational Academy (`academy/`)
- **Curriculum Engine:** 20 progressive lessons across 5 skill tiers (Novice, Apprentice, Adept, Expert, Master).
- **Interactive Exercises:** Specific puzzles designed to isolate and test single strategies.
- **Skill Diagnostic:** Assesses player proficiency and recommends targeted lessons.

### 2.3 The Variants System (`engine/variants/`)
- **Mini Sudoku (4×4, 6×6):** Reduced dimensions for fast play and children.
- **Monster Sudoku (16×16 Hexadoku):** 16 digits (0-9, A-F) with 4×4 boxes.
- **Sudoku X (Diagonal):** Both main diagonals must contain 1-9 without repetition.
- **Hyper Sudoku (Windoku):** 4 additional shaded 3×3 regions requiring unique 1-9.
- **Samurai Sudoku:** 5 overlapping 9×9 grids sharing corner 3×3 boxes.
- **Killer Sudoku:** Cages with arithmetic sum targets and no repeating digits.

### 2.4 Persistence & Repositories (`persistence/`)
- **Repository Pattern:** Decouples SQL queries from domain business logic.
- **Connection Management:** Connection pool with WAL mode, foreign keys, and query profiling.
- **Schema Migrations:** Versioned migration runner tracking applied migration scripts.

### 2.5 Gamification & ELO System (`gamification/`)
- **10-Tier Level Progression:** Exponential XP curves from Level 1 (Beginner) to Level 10 (Legend).
- **Authentic ELO & Glicko-2:** Dynamic rating updates based on opponent strength, solve time, zero mistakes, and pure solves.
- **Daily Challenges & Streaks:** Deterministically seeded puzzles with streak multipliers and freeze mechanics.
- **Achievements Catalog:** Over 50 criteria-evaluated badges and trophies.

---

## 3. Communication Protocols

- **RESTful Endpoints:** Standard JSON request/response bodies with JWT/Bearer token authorization.
- **WebSocket (Socket.IO):** Bi-directional real-time events for multiplayer matchmaking (`join_ranked_queue`, `match_found`), live opponent progress updates (`opponent_progress`), and match termination (`match_finished`).
