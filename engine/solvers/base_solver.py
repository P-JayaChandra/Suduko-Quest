"""
Sudoku Quest - Base Solver Architecture
Defines the standard solver interface, result container, and performance metrics tracking.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from dataclasses import dataclass, field
import time
from engine.models.board import Board

@dataclass
class SolverResult:
    """Standardized result returned by all Sudoku solvers."""
    solved: bool
    solution: Optional[Board] = None
    elapsed_ms: float = 0.0
    steps: int = 0
    solutions_count: int = 0
    solutions: List[Board] = field(default_factory=list)

class BaseSolver(ABC):
    """Abstract base class for all algorithmic solvers."""

    def __init__(self, timeout_seconds: float = 5.0):
        self.timeout_seconds = timeout_seconds
        self.steps = 0
        self.start_time = 0.0

    @abstractmethod
    def solve(self, board: Board) -> SolverResult:
        """Solve the given board and return SolverResult."""
        pass

    @abstractmethod
    def count_solutions(self, board: Board, max_count: int = 2) -> int:
        """Count distinct solutions up to max_count for uniqueness verification."""
        pass
