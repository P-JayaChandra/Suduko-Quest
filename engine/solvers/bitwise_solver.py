"""
Sudoku Quest - Ultra-Fast Bitwise Solver
Uses 9-bit integer bitmasks for row, column, and block constraints with Minimum Remaining Values (MRV).
Achieves sub-millisecond solving speeds and rapid uniqueness verification.
"""
import time
from typing import Optional, List, Tuple
from engine.solvers.base_solver import BaseSolver, SolverResult
from engine.models.board import Board
from core.constants import GRID_SIZE

ALL_DIGITS_MASK = 0x1FF  # Binary 111111111 (digits 1 to 9)

class BitwiseSolver(BaseSolver):
    """Blazing fast bitmask Sudoku solver."""

    def __init__(self, timeout_seconds: float = 5.0):
        super().__init__(timeout_seconds=timeout_seconds)

    def solve(self, board: Board) -> SolverResult:
        start_ts = time.perf_counter()
        self.steps = 0

        # Build initial masks
        row_masks = [0] * 9
        col_masks = [0] * 9
        box_masks = [0] * 9
        grid = [[0] * 9 for _ in range(9)]
        empty_cells = []

        for r in range(9):
            for c in range(9):
                val = board.get_value(r, c)
                grid[r][c] = val
                if val != 0:
                    bit = 1 << (val - 1)
                    b = (r // 3) * 3 + (c // 3)
                    if (row_masks[r] & bit) or (col_masks[c] & bit) or (box_masks[b] & bit):
                        # Initial board contains conflict
                        return SolverResult(
                            solved=False,
                            elapsed_ms=(time.perf_counter() - start_ts) * 1000.0,
                            steps=0,
                            solutions_count=0
                        )
                    row_masks[r] |= bit
                    col_masks[c] |= bit
                    box_masks[b] |= bit
                else:
                    empty_cells.append((r, c))

        if not empty_cells:
            # Board was already complete and valid
            return SolverResult(
                solved=True,
                solution=board.clone(),
                elapsed_ms=(time.perf_counter() - start_ts) * 1000.0,
                steps=1,
                solutions_count=1,
                solutions=[board.clone()]
            )

        solution_grid = None

        def search() -> bool:
            nonlocal solution_grid
            self.steps += 1

            if time.perf_counter() - start_ts > self.timeout_seconds:
                return False

            # Find empty cell with Minimum Remaining Values (MRV)
            best_idx = -1
            best_r, best_c = -1, -1
            best_mask = 0
            min_candidates = 10

            for i, (r, c) in enumerate(empty_cells):
                b = (r // 3) * 3 + (c // 3)
                used = row_masks[r] | col_masks[c] | box_masks[b]
                candidates_mask = (~used) & ALL_DIGITS_MASK
                count = bin(candidates_mask).count("1")

                if count == 0:
                    # Dead end: empty cell with no possible candidates
                    return False

                if count < min_candidates:
                    min_candidates = count
                    best_idx = i
                    best_r, best_c = r, c
                    best_mask = candidates_mask
                    if count == 1:
                        # Naked single found, optimal choice
                        break

            if best_idx == -1:
                # All cells filled!
                solution_grid = [row[:] for row in grid]
                return True

            r, c = best_r, best_c
            b = (r // 3) * 3 + (c // 3)
            # Remove chosen cell from list
            empty_cells.pop(best_idx)

            curr_mask = best_mask
            while curr_mask > 0:
                # Extract lowest set bit
                lsb = curr_mask & -curr_mask
                digit = lsb.bit_length()

                # Place digit
                grid[r][c] = digit
                row_masks[r] |= lsb
                col_masks[c] |= lsb
                box_masks[b] |= lsb

                if search():
                    return True

                # Backtrack
                grid[r][c] = 0
                row_masks[r] &= ~lsb
                col_masks[c] &= ~lsb
                box_masks[b] &= ~lsb

                curr_mask &= ~lsb

            # Restore empty cell
            empty_cells.insert(best_idx, (r, c))
            return False

        solved = search()
        elapsed = (time.perf_counter() - start_ts) * 1000.0

        if solved and solution_grid:
            sol_board = Board(solution_grid)
            return SolverResult(
                solved=True,
                solution=sol_board,
                elapsed_ms=elapsed,
                steps=self.steps,
                solutions_count=1,
                solutions=[sol_board]
            )

        return SolverResult(
            solved=False,
            solution=None,
            elapsed_ms=elapsed,
            steps=self.steps,
            solutions_count=0
        )

    def count_solutions(self, board: Board, max_count: int = 2) -> int:
        """Count distinct solutions up to max_count using bitwise backtracking."""
        start_ts = time.perf_counter()
        row_masks = [0] * 9
        col_masks = [0] * 9
        box_masks = [0] * 9
        grid = [[0] * 9 for _ in range(9)]
        empty_cells = []

        for r in range(9):
            for c in range(9):
                val = board.get_value(r, c)
                grid[r][c] = val
                if val != 0:
                    bit = 1 << (val - 1)
                    b = (r // 3) * 3 + (c // 3)
                    if (row_masks[r] & bit) or (col_masks[c] & bit) or (box_masks[b] & bit):
                        return 0
                    row_masks[r] |= bit
                    col_masks[c] |= bit
                    box_masks[b] |= bit
                else:
                    empty_cells.append((r, c))

        if not empty_cells:
            return 1

        solutions_found = 0

        def search() -> None:
            nonlocal solutions_found
            if solutions_found >= max_count:
                return

            if time.perf_counter() - start_ts > self.timeout_seconds:
                return

            best_idx = -1
            best_r, best_c = -1, -1
            best_mask = 0
            min_candidates = 10

            for i, (r, c) in enumerate(empty_cells):
                b = (r // 3) * 3 + (c // 3)
                used = row_masks[r] | col_masks[c] | box_masks[b]
                candidates_mask = (~used) & ALL_DIGITS_MASK
                count = bin(candidates_mask).count("1")

                if count == 0:
                    return

                if count < min_candidates:
                    min_candidates = count
                    best_idx = i
                    best_r, best_c = r, c
                    best_mask = candidates_mask
                    if count == 1:
                        break

            if best_idx == -1:
                solutions_found += 1
                return

            r, c = best_r, best_c
            b = (r // 3) * 3 + (c // 3)
            empty_cells.pop(best_idx)

            curr_mask = best_mask
            while curr_mask > 0:
                lsb = curr_mask & -curr_mask
                digit = lsb.bit_length()

                grid[r][c] = digit
                row_masks[r] |= lsb
                col_masks[c] |= lsb
                box_masks[b] |= lsb

                search()

                grid[r][c] = 0
                row_masks[r] &= ~lsb
                col_masks[c] &= ~lsb
                box_masks[b] &= ~lsb

                if solutions_found >= max_count:
                    empty_cells.insert(best_idx, (r, c))
                    return

                curr_mask &= ~lsb

            empty_cells.insert(best_idx, (r, c))

        search()
        return solutions_found
