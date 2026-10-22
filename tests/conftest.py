"""
Sudoku Quest - Pytest Test Fixtures and Configurations
"""
import pytest
from engine.models.board import Board
from engine.solvers.bitwise_solver import BitwiseSolver
from engine.solvers.dlx import DLXSolver
from engine.solvers.backtracking import BacktrackingSolver

# Classic benchmark easy puzzle
EASY_PUZZLE_STR = (
    "003020600"
    "900305001"
    "001806400"
    "008102900"
    "700000008"
    "006708200"
    "002609500"
    "800203009"
    "005010300"
)

EASY_PUZZLE_SOLUTION = (
    "483921657"
    "967345821"
    "251876493"
    "548132976"
    "729564138"
    "136798245"
    "372689514"
    "814253769"
    "695417382"
)

# Classic benchmark hard puzzle (Arto Inkala's AI Escargot)
HARD_PUZZLE_STR = (
    "100007090"
    "030020008"
    "009600500"
    "005300900"
    "010080002"
    "600004000"
    "300000010"
    "040000007"
    "007000300"
)

# Multi-solution puzzle (empty or near-empty)
MULTI_SOLUTION_PUZZLE_STR = (
    "000000000"
    "000000000"
    "000000000"
    "000000000"
    "000000000"
    "000000000"
    "000000000"
    "000000000"
    "000000000"
)

# Unsolvable puzzle (two 1s in first row)
UNSOLVABLE_PUZZLE_STR = (
    "110000000"
    "000000000"
    "000000000"
    "000000000"
    "000000000"
    "000000000"
    "000000000"
    "000000000"
    "000000000"
)

@pytest.fixture
def easy_puzzle_board() -> Board:
    return Board(EASY_PUZZLE_STR)

@pytest.fixture
def easy_solution_board() -> Board:
    return Board(EASY_PUZZLE_SOLUTION)

@pytest.fixture
def hard_puzzle_board() -> Board:
    return Board(HARD_PUZZLE_STR)

@pytest.fixture
def empty_board() -> Board:
    return Board(MULTI_SOLUTION_PUZZLE_STR)

@pytest.fixture
def unsolvable_board() -> Board:
    return Board(UNSOLVABLE_PUZZLE_STR)

@pytest.fixture
def bitwise_solver() -> BitwiseSolver:
    return BitwiseSolver(timeout_seconds=3.0)

@pytest.fixture
def dlx_solver() -> DLXSolver:
    return DLXSolver(timeout_seconds=3.0)

@pytest.fixture
def backtracking_solver() -> BacktrackingSolver:
    return BacktrackingSolver(timeout_seconds=3.0)
