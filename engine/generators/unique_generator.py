"""
Sudoku Quest - Guaranteed Unique Puzzle Generator
Generates valid 9x9 Sudoku puzzles with guaranteed unique solutions, controlled clue counts,
and optional rotational/diagonal symmetry.
"""
import random
from typing import Optional, Tuple, Dict, List
from engine.models.board import Board
from engine.solvers.bitwise_solver import BitwiseSolver
from engine.solvers.solution_counter import SolutionCounter
from core.constants import LEVEL_DEFINITIONS, Difficulty, GRID_SIZE, CANONICAL_CELL_COUNT

CANONICAL_SEED_GRID = [
    [1, 2, 3, 4, 5, 6, 7, 8, 9],
    [4, 5, 6, 7, 8, 9, 1, 2, 3],
    [7, 8, 9, 1, 2, 3, 4, 5, 6],
    [2, 3, 1, 5, 6, 4, 8, 9, 7],
    [5, 6, 4, 8, 9, 7, 2, 3, 1],
    [8, 9, 7, 2, 3, 1, 5, 6, 4],
    [3, 1, 2, 6, 4, 5, 9, 7, 8],
    [6, 4, 5, 9, 7, 8, 3, 1, 2],
    [9, 7, 8, 3, 1, 2, 6, 4, 5],
]

class UniquePuzzleGenerator:
    """Produces verified Sudoku puzzles with unique solutions."""

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.counter = SolutionCounter(use_dlx=False, timeout_seconds=2.0)

    def generate_solved_grid(self) -> Board:
        """Generate a random valid solved 9x9 grid via isomorphic transformations."""
        digits = list(range(1, 10))
        self.rng.shuffle(digits)
        digit_map = {i + 1: digits[i] for i in range(9)}

        grid = [[digit_map[val] for val in row] for row in CANONICAL_SEED_GRID]

        # Band swaps (horizontal 3-row blocks)
        bands = [0, 1, 2]
        self.rng.shuffle(bands)
        grid = [row for b in bands for row in grid[b * 3 : b * 3 + 3]]

        # Row swaps within each band
        for b in range(3):
            rows = list(range(b * 3, b * 3 + 3))
            self.rng.shuffle(rows)
            band_rows = [grid[r] for r in rows]
            for i in range(3):
                grid[b * 3 + i] = band_rows[i]

        # Stack swaps (vertical 3-column blocks)
        stacks = [0, 1, 2]
        self.rng.shuffle(stacks)
        new_grid = []
        for r in range(9):
            row = []
            for s in stacks:
                row.extend(grid[r][s * 3 : s * 3 + 3])
            new_grid.append(row)
        grid = new_grid

        # Column swaps within each stack
        for s in range(3):
            cols = list(range(s * 3, s * 3 + 3))
            self.rng.shuffle(cols)
            for r in range(9):
                col_vals = [grid[r][c] for c in cols]
                for i in range(3):
                    grid[r][s * 3 + i] = col_vals[i]

        # Transposition (reflection across main diagonal) with 50% probability
        if self.rng.choice([True, False]):
            grid = [[grid[r][c] for r in range(9)] for c in range(9)]

        return Board(grid)

    def generate(
        self,
        level_num: int = 4,
        target_clues: Optional[int] = None,
        symmetry: str = "rotational",
    ) -> Dict[str, any]:
        """
        Generate a unique Sudoku puzzle tailored to difficulty level.
        symmetry: 'rotational' (180 deg), 'diagonal', or 'none'.
        """
        lvl_conf = LEVEL_DEFINITIONS.get(level_num, LEVEL_DEFINITIONS[4])
        min_c, max_c = lvl_conf["clues_range"]

        if target_clues is None or target_clues < 17 or target_clues > 65:
            target_clues = self.rng.randint(min_c, max_c)

        solved_board = self.generate_solved_grid()
        puzzle_board = solved_board.clone()

        # Build candidate removal cell pairs based on symmetry
        cell_pairs: List[Tuple[Tuple[int, int], Optional[Tuple[int, int]]]] = []
        visited = set()

        all_coords = [(r, c) for r in range(9) for c in range(9)]
        self.rng.shuffle(all_coords)

        for r, c in all_coords:
            if (r, c) in visited:
                continue

            if symmetry == "rotational":
                sym_r, sym_c = 8 - r, 8 - c
                if (r, c) == (sym_r, sym_c):
                    cell_pairs.append(((r, c), None))
                    visited.add((r, c))
                else:
                    cell_pairs.append(((r, c), (sym_r, sym_c)))
                    visited.add((r, c))
                    visited.add((sym_r, sym_c))
            elif symmetry == "diagonal":
                sym_r, sym_c = c, r
                if (r, c) == (sym_r, sym_c):
                    cell_pairs.append(((r, c), None))
                    visited.add((r, c))
                else:
                    cell_pairs.append(((r, c), (sym_r, sym_c)))
                    visited.add((r, c))
                    visited.add((sym_r, sym_c))
            else:
                cell_pairs.append(((r, c), None))
                visited.add((r, c))

        self.rng.shuffle(cell_pairs)

        current_clues = CANONICAL_CELL_COUNT

        for p1, p2 in cell_pairs:
            if current_clues <= target_clues:
                break

            r1, c1 = p1
            val1 = puzzle_board.get_value(r1, c1)
            puzzle_board.cells[r1][c1].value = 0

            val2 = 0
            if p2 is not None:
                r2, c2 = p2
                val2 = puzzle_board.get_value(r2, c2)
                puzzle_board.cells[r2][c2].value = 0

            # Test if puzzle still has exactly one solution
            if self.counter.is_unique(puzzle_board):
                # Safe removal!
                current_clues -= 2 if p2 is not None else 1
            else:
                # Removal breaks uniqueness! Restore digit(s)
                puzzle_board.cells[r1][c1].value = val1
                if p2 is not None:
                    puzzle_board.cells[r2][c2].value = val2

        return {
            "puzzle": puzzle_board.to_string(),
            "solution": solved_board.to_string(),
            "puzzle_matrix": puzzle_board.to_matrix(),
            "solution_matrix": solved_board.to_matrix(),
            "clues": puzzle_board.clue_count,
            "target_clues": target_clues,
            "level_num": level_num,
            "difficulty": lvl_conf["key"],
            "difficulty_name": lvl_conf["name"],
            "xp": lvl_conf["xp"],
            "is_unique": True,
            "symmetry": symmetry,
        }
