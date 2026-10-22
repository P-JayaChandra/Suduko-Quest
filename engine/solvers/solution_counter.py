"""
Sudoku Quest - Solution Counter and Uniqueness Validator
Quickly verifies if a puzzle has exactly one unique solution, zero solutions, or multiple solutions.
"""
from typing import Tuple
from engine.models.board import Board
from engine.solvers.bitwise_solver import BitwiseSolver
from engine.solvers.dlx import DLXSolver

class SolutionCounter:
    """Specialized service for testing uniqueness of Sudoku boards."""

    def __init__(self, use_dlx: bool = False, timeout_seconds: float = 3.0):
        self.solver = DLXSolver(timeout_seconds=timeout_seconds) if use_dlx else BitwiseSolver(timeout_seconds=timeout_seconds)

    def is_unique(self, board: Board) -> bool:
        """True if and only if the board has exactly 1 valid solution."""
        return self.solver.count_solutions(board, max_count=2) == 1

    def count(self, board: Board, max_count: int = 2) -> int:
        """Count solutions up to max_count."""
        return self.solver.count_solutions(board, max_count=max_count)

    def assess_solvability(self, board: Board) -> Tuple[bool, bool, int]:
        """
        Returns (is_solvable, is_unique, count).
        """
        cnt = self.solver.count_solutions(board, max_count=2)
        if cnt == 0:
            return False, False, 0
        elif cnt == 1:
            return True, True, 1
        else:
            return True, False, cnt
