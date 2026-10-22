"""
Unit tests for Board and Cell models.
"""
import pytest
from engine.models.board import Board
from engine.models.cell import Cell
from core.exceptions import InvalidBoardError

def test_cell_initialization():
    c = Cell(row=0, col=0)
    assert c.value == 0
    assert c.is_empty
    assert not c.is_given
    assert len(c.candidates) == 9
    assert c.box == 0
    assert c.index == 0

    c2 = Cell(row=4, col=5)
    assert c2.box == 4
    assert c2.index == 41

def test_cell_toggle_notes():
    c = Cell(row=1, col=1)
    assert c.toggle_note(5) is True
    assert 5 in c.notes
    assert c.toggle_note(5) is False
    assert 5 not in c.notes

def test_board_load_and_serialization(easy_puzzle_board):
    assert easy_puzzle_board.clue_count == 32
    assert easy_puzzle_board.empty_count == 49
    s = easy_puzzle_board.to_string()
    assert len(s) == 81
    assert s.startswith("..3.2.6..")

def test_board_load_from_matrix(easy_puzzle_board):
    matrix = easy_puzzle_board.to_matrix()
    assert len(matrix) == 9
    assert len(matrix[0]) == 9
    b2 = Board(matrix)
    assert b2.to_string() == easy_puzzle_board.to_string()

def test_board_invalid_length():
    with pytest.raises(InvalidBoardError):
        Board("12345")

def test_board_peers(easy_puzzle_board):
    peers = easy_puzzle_board.get_peer_cells(0, 0)
    assert len(peers) == 20  # 8 row + 8 col + 4 remaining in box

def test_board_is_safe(easy_puzzle_board):
    # In easy puzzle: row 0 has '2' and '6' and '3'
    assert easy_puzzle_board.is_safe(0, 0, 2) is False
    assert easy_puzzle_board.is_safe(0, 0, 6) is False
    assert easy_puzzle_board.is_safe(0, 0, 4) is True

def test_board_undo_redo():
    b = Board()
    b.set_value(0, 0, 5)
    assert b.get_value(0, 0) == 5
    assert len(b.undo_stack) == 1

    reverted = b.undo()
    assert reverted.old_value == 0
    assert reverted.new_value == 5
    assert b.get_value(0, 0) == 0

    redone = b.redo()
    assert redone.new_value == 5
    assert b.get_value(0, 0) == 5

def test_board_conflicts():
    b = Board()
    b.set_value(0, 0, 5)
    b.set_value(0, 8, 5)  # Duplicate in row
    conflicts = b.find_conflicts()
    assert (0, 0) in conflicts
    assert (0, 8) in conflicts
    assert not b.is_valid()

def test_board_complete(easy_solution_board):
    assert easy_solution_board.is_valid()
    assert easy_solution_board.is_complete()
    assert easy_solution_board.clue_count == 81
    assert easy_solution_board.empty_count == 0

def test_board_clone(easy_puzzle_board):
    c = easy_puzzle_board.clone()
    assert c == easy_puzzle_board
    c.set_value(0, 0, 4)
    assert c.get_value(0, 0) == 4
    assert easy_puzzle_board.get_value(0, 0) == 0
