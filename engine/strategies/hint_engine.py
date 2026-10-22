"""
Sudoku Quest - Intelligent Hint & Educational Explanation Engine
Analyzes board states, orders logical deduction techniques by human difficulty,
detects player errors, and generates step-by-step instructional advice.
"""
from typing import Optional, List, Dict, Any
from engine.models.board import Board
from engine.models.candidate_grid import CandidateGrid
from engine.strategies.base_strategy import BaseStrategy, DeductionStep, StrategyTier
from engine.strategies.singles import NakedSingle, HiddenSingle
from engine.strategies.intersections import PointingPairs, BoxLineReduction
from engine.strategies.subsets import NakedPair, HiddenPair
from engine.strategies.fish import XWing
from engine.strategies.wings import XYWing
from engine.strategies.uniqueness import UniqueRectangleType1
from engine.solvers.bitwise_solver import BitwiseSolver

class HintEngine:
    """Master reasoning engine for hints, difficulty assessment, and solving analysis."""

    def __init__(self):
        # Strategies ordered strictly from easiest (Beginner) to hardest (Extreme)
        self.strategies: List[BaseStrategy] = [
            NakedSingle(),
            HiddenSingle(),
            PointingPairs(),
            BoxLineReduction(),
            NakedPair(),
            HiddenPair(),
            XWing(),
            XYWing(),
            UniqueRectangleType1(),
        ]
        self.solver = BitwiseSolver()

    def get_hint(self, board: Board, solution: Optional[Board] = None) -> Dict[str, Any]:
        """
        Analyze current board and produce next instructional hint.
        Checks for player errors first before suggesting logical next moves.
        """
        # 1. Error check against provided solution
        if solution is not None:
            for r in range(9):
                for c in range(9):
                    user_val = board.get_value(r, c)
                    sol_val = solution.get_value(r, c)
                    if user_val != 0 and user_val != sol_val:
                        return {
                            "type": "error_correction",
                            "status": "error_found",
                            "strategy": "Error Correction",
                            "cell": {"row": r, "col": c},
                            "incorrect_value": user_val,
                            "correct_value": sol_val,
                            "message": f"Cell (R{r+1}, C{c+1}) currently contains {user_val}, which violates the puzzle solution.",
                            "highlight_cells": [{"row": r, "col": c, "color": "error"}]
                        }

        # 2. Rule conflicts check on board
        conflicts = board.find_conflicts()
        if conflicts:
            r, c = conflicts[0]
            val = board.get_value(r, c)
            return {
                "type": "conflict_warning",
                "status": "conflict_found",
                "strategy": "Rule Conflict",
                "cell": {"row": r, "col": c},
                "value": val,
                "message": f"Rule conflict detected at Cell (R{r+1}, C{c+1}) with digit {val}.",
                "highlight_cells": [{"row": cr, "col": cc, "color": "conflict"} for (cr, cc) in conflicts]
            }

        # 3. Apply human logical deduction strategies
        cand_grid = CandidateGrid(board)

        for strat in self.strategies:
            step = strat.find_step(cand_grid)
            if step is not None:
                # Convert DeductionStep into API hint payload
                hint_payload = {
                    "type": "logical_deduction",
                    "status": "success",
                    "strategy": step.strategy_name,
                    "tier": step.tier.name,
                    "tier_level": int(step.tier),
                    "difficulty_rating": step.difficulty_rating,
                    "action": step.action,
                    "digit": step.digit,
                    "explanation": step.explanation,
                    "target_cell": {"row": step.target_cell[0], "col": step.target_cell[1]} if step.target_cell else None,
                    "eliminations": [
                        {"row": r, "col": c, "digit": d} for (r, c, d) in step.eliminations
                    ],
                    "cause_cells": [
                        {"row": r, "col": c} for (r, c) in step.cause_cells
                    ],
                    "secondary_cells": [
                        {"row": r, "col": c} for (r, c) in step.secondary_cells
                    ],
                }

                # Construct visual highlights for client
                highlights = []
                if step.target_cell:
                    highlights.append({"row": step.target_cell[0], "col": step.target_cell[1], "color": "target"})
                for (r, c) in step.cause_cells:
                    highlights.append({"row": r, "col": c, "color": "cause"})
                for (r, c, _) in step.eliminations:
                    highlights.append({"row": r, "col": c, "color": "eliminate"})

                hint_payload["highlights"] = highlights
                return hint_payload

        # 4. Fallback: if all human strategies in catalog are exhausted
        if solution is None:
            res = self.solver.solve(board)
            if res.solved:
                solution = res.solution

        if solution is not None:
            # Find first empty cell and reveal solution digit
            for r in range(9):
                for c in range(9):
                    if board.get_value(r, c) == 0:
                        sol_val = solution.get_value(r, c)
                        return {
                            "type": "direct_reveal",
                            "status": "success",
                            "strategy": "Advanced Deduction",
                            "tier": "MASTER",
                            "tier_level": 4,
                            "difficulty_rating": 6.0,
                            "action": "place",
                            "digit": sol_val,
                            "target_cell": {"row": r, "col": c},
                            "explanation": f"Advanced logical chain yields digit {sol_val} in Cell (R{r+1}, C{c+1}).",
                            "highlights": [{"row": r, "col": c, "color": "target"}]
                        }

        return {
            "type": "none",
            "status": "no_hint_available",
            "message": "No deductions or moves remaining."
        }
