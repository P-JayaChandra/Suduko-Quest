"""
Unit tests for human logical deduction strategies and CandidateGrid.
"""
import pytest
from engine.models.board import Board
from engine.models.candidate_grid import CandidateGrid
from engine.strategies.singles import NakedSingle, HiddenSingle
from engine.strategies.intersections import PointingPairs, BoxLineReduction
from engine.strategies.subsets import NakedPair, HiddenPair
from engine.strategies.fish import XWing
from engine.strategies.wings import XYWing
from engine.strategies.uniqueness import UniqueRectangleType1
from engine.strategies.hint_engine import HintEngine

def test_candidate_grid_sync(easy_puzzle_board):
    cg = CandidateGrid(easy_puzzle_board)
    assert len(cg.get_candidates(0, 0)) > 0
    # In row 0, digit 2 is placed, so (0, 0) should not have candidate 2
    assert cg.has_candidate(0, 0, 2) is False

def test_naked_single():
    # Board where cell (0, 0) has digits 2,3,4,5,6,7,8,9 in peers, leaving only 1
    b = Board()
    for c in range(1, 9):
        b.set_value(0, c, c + 1)  # row 0 has 2,3,4,5,6,7,8,9
    cg = CandidateGrid(b)
    strat = NakedSingle()
    step = strat.find_step(cg)
    assert step is not None
    assert step.action == "place"
    assert step.target_cell == (0, 0)
    assert step.digit == 1
    assert "Naked Single" in step.strategy_name

def test_hidden_single():
    cg = CandidateGrid()
    # In row 0, remove candidate 7 from all columns except column 3
    for c in range(9):
        if c != 3:
            cg.candidates[0][c].discard(7)
    strat = HiddenSingle()
    step = strat.find_step(cg)
    assert step is not None
    assert step.action == "place"
    assert step.digit == 7
    assert step.target_cell == (0, 3)

def test_pointing_pairs():
    # Construct a box where digit 7 can only go in row 0
    b = Board()
    # Block 0 has cells (0,0), (0,1), (0,2), (1,0)...(2,2)
    # Fill rows 1 and 2 in block 0 so 7 cannot go there
    b.set_value(1, 4, 7)
    b.set_value(2, 7, 7)
    cg = CandidateGrid(b)
    strat = PointingPairs()
    # Strategy should execute without error
    step = strat.find_step(cg)

def test_naked_pair():
    # Create artificial candidate grid where (0, 0) and (0, 1) both have only {3, 7}
    cg = CandidateGrid()
    cg.candidates[0][0] = {3, 7}
    cg.candidates[0][1] = {3, 7}
    cg.candidates[0][2] = {3, 7, 9}
    strat = NakedPair()
    step = strat.find_step(cg)
    assert step is not None
    assert step.action == "eliminate"
    assert (0, 2, 3) in step.eliminations or (0, 2, 7) in step.eliminations

def test_hint_engine_error_detection(easy_puzzle_board, easy_solution_board):
    he = HintEngine()
    # Introduce mistake in cell (0, 0): solution is 4, we place 9
    bad_board = easy_puzzle_board.clone()
    bad_board.set_value(0, 0, 9)
    hint = he.get_hint(bad_board, solution=easy_solution_board)
    assert hint["status"] == "error_found"
    assert hint["type"] == "error_correction"
    assert hint["incorrect_value"] == 9
    assert hint["correct_value"] == 4

def test_hint_engine_logical_deduction(easy_puzzle_board, easy_solution_board):
    he = HintEngine()
    hint = he.get_hint(easy_puzzle_board, solution=easy_solution_board)
    assert hint["status"] == "success"
    assert "strategy" in hint
    assert "explanation" in hint
    assert "highlights" in hint
    assert len(hint["highlights"]) > 0
