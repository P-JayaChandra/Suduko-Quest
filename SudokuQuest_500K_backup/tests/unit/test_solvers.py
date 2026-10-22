"""
Unit tests for DLX, Bitwise, Backtracking solvers, and SolutionCounter.
"""
import pytest
from engine.solvers.bitwise_solver import BitwiseSolver
from engine.solvers.dlx import DLXSolver
from engine.solvers.backtracking import BacktrackingSolver
from engine.solvers.solution_counter import SolutionCounter

def test_bitwise_solver_easy(easy_puzzle_board, easy_solution_board, bitwise_solver):
    res = bitwise_solver.solve(easy_puzzle_board)
    assert res.solved is True
    assert res.solution is not None
    assert res.solution.to_string() == easy_solution_board.to_string()
    assert res.elapsed_ms < 50.0

def test_dlx_solver_easy(easy_puzzle_board, easy_solution_board, dlx_solver):
    res = dlx_solver.solve(easy_puzzle_board)
    assert res.solved is True
    assert res.solution is not None
    assert res.solution.to_string() == easy_solution_board.to_string()

def test_backtracking_solver_easy(easy_puzzle_board, easy_solution_board, backtracking_solver):
    res = backtracking_solver.solve(easy_puzzle_board)
    assert res.solved is True
    assert res.solution is not None
    assert res.solution.to_string() == easy_solution_board.to_string()

def test_bitwise_solver_hard(hard_puzzle_board, bitwise_solver):
    res = bitwise_solver.solve(hard_puzzle_board)
    assert res.solved is True
    assert res.solution.is_valid()
    assert res.solution.is_complete()

def test_solvers_unsolvable(unsolvable_board, bitwise_solver, dlx_solver, backtracking_solver):
    assert bitwise_solver.solve(unsolvable_board).solved is False
    assert dlx_solver.solve(unsolvable_board).solved is False
    assert backtracking_solver.solve(unsolvable_board).solved is False

def test_solution_counter_unique(easy_puzzle_board):
    sc = SolutionCounter(use_dlx=False)
    assert sc.is_unique(easy_puzzle_board) is True
    assert sc.count(easy_puzzle_board) == 1

def test_solution_counter_multiple(empty_board):
    sc = SolutionCounter(use_dlx=False)
    assert sc.is_unique(empty_board) is False
    assert sc.count(empty_board, max_count=2) == 2

def test_solution_counter_unsolvable(unsolvable_board):
    sc = SolutionCounter(use_dlx=False)
    solvable, unique, cnt = sc.assess_solvability(unsolvable_board)
    assert solvable is False
    assert unique is False
    assert cnt == 0
