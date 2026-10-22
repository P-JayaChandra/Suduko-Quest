"""
Unit tests for UniquePuzzleGenerator.
"""
import pytest
from engine.generators.unique_generator import UniquePuzzleGenerator
from engine.models.board import Board
from engine.solvers.solution_counter import SolutionCounter

def test_generate_solved_grid():
    gen = UniquePuzzleGenerator(seed=42)
    grid = gen.generate_solved_grid()
    assert grid.is_valid()
    assert grid.is_complete()
    assert grid.clue_count == 81

def test_generate_unique_puzzle_beginner():
    gen = UniquePuzzleGenerator(seed=123)
    data = gen.generate(level_num=1, target_clues=46, symmetry="rotational")

    assert data["is_unique"] is True
    assert data["level_num"] == 1
    assert data["difficulty"] == "beginner"

    board = Board(data["puzzle"])
    counter = SolutionCounter()
    assert counter.is_unique(board) is True
    assert abs(board.clue_count - 46) <= 4

def test_generate_unique_puzzle_symmetry():
    gen = UniquePuzzleGenerator(seed=999)
    data = gen.generate(level_num=4, symmetry="rotational")

    board = Board(data["puzzle"])
    # Verify rotational symmetry: for each (r, c), (8-r, 8-c) has matching empty/filled status
    for r in range(9):
        for c in range(9):
            is_empty_1 = (board.get_value(r, c) == 0)
            is_empty_2 = (board.get_value(8 - r, 8 - c) == 0)
            assert is_empty_1 == is_empty_2
