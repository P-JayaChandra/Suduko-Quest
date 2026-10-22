"""
Sudoku Quest - Heuristic Backtracking Solver
Standard recursive backtracking solver with forward checking and step-by-step tracing.
"""
import time
from typing import Optional, List, Tuple
from engine.solvers.base_solver import BaseSolver, SolverResult
from engine.models.board import Board
from core.constants import GRID_SIZE

class BacktrackingSolver(BaseSolver):
    """Heuristic backtracking solver with candidate propagation."""

    def __init__(self, timeout_seconds: float = 5.0):
        super().__init__(timeout_seconds=timeout_seconds)

    def solve(self, board: Board) -> SolverResult:
        start_ts = time.perf_counter()
        self.steps = 0
        working_board = board.clone()

        if not working_board.is_valid():
            return SolverResult(
                solved=False,
                elapsed_ms=(time.perf_counter() - start_ts) * 1000.0,
                steps=0,
                solutions_count=0
            )

        def search() -> bool:
            self.steps += 1
            if time.perf_counter() - start_ts > self.timeout_seconds:
                return False

            # Find cell with minimum remaining candidates
            best_cell = None
            min_cands = 10

            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    cell = working_board.get_cell(r, c)
                    if cell.is_empty:
                        # Find valid candidates
                        valid_cands = [d for d in range(1, 10) if working_board.is_safe(r, c, d)]
                        if len(valid_cands) == 0:
                            return False  # Dead end
                        if len(valid_cands) < min_cands:
                            min_cands = len(valid_cands)
                            best_cell = (cell, valid_cands)
                            if min_cands == 1:
                                break
                if best_cell and min_cands == 1:
                    break

            if best_cell is None:
                return True  # All cells filled

            target_cell, candidates = best_cell
            r, c = target_cell.row, target_cell.col

            for digit in candidates:
                target_cell.value = digit
                if search():
                    return True
                target_cell.value = 0

            return False

        solved = search()
        elapsed = (time.perf_counter() - start_ts) * 1000.0

        if solved:
            return SolverResult(
                solved=True,
                solution=working_board,
                elapsed_ms=elapsed,
                steps=self.steps,
                solutions_count=1,
                solutions=[working_board]
            )

        return SolverResult(
            solved=False,
            solution=None,
            elapsed_ms=elapsed,
            steps=self.steps,
            solutions_count=0
        )

    def count_solutions(self, board: Board, max_count: int = 2) -> int:
        start_ts = time.perf_counter()
        working_board = board.clone()
        if not working_board.is_valid():
            return 0

        solutions_count = 0

        def search():
            nonlocal solutions_count
            if solutions_count >= max_count:
                return
            if time.perf_counter() - start_ts > self.timeout_seconds:
                return

            best_cell = None
            min_cands = 10

            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    cell = working_board.get_cell(r, c)
                    if cell.is_empty:
                        valid_cands = [d for d in range(1, 10) if working_board.is_safe(r, c, d)]
                        if len(valid_cands) == 0:
                            return
                        if len(valid_cands) < min_cands:
                            min_cands = len(valid_cands)
                            best_cell = (cell, valid_cands)
                            if min_cands == 1:
                                break
                if best_cell and min_cands == 1:
                    break

            if best_cell is None:
                solutions_count += 1
                return

            target_cell, candidates = best_cell
            for digit in candidates:
                target_cell.value = digit
                search()
                target_cell.value = 0
                if solutions_count >= max_count:
                    return

        search()
        return solutions_count
