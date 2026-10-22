"""
Sudoku Quest - Fish Strategies (Tier 4)
Implements X-Wing and Swordfish 2D constraint elimination patterns.
"""
from typing import Optional, List, Tuple
import itertools
from engine.strategies.base_strategy import BaseStrategy, DeductionStep, StrategyTier
from engine.models.candidate_grid import CandidateGrid
from core.constants import GRID_SIZE

class XWing(BaseStrategy):
    """
    X-Wing:
    When a candidate digit appears in exactly two cells in each of two rows (or columns),
    and those cells share the same two columns (or rows), that digit can be eliminated
    from all other cells in those two columns (or rows).
    """
    def __init__(self):
        super().__init__(name="X-Wing", tier=StrategyTier.ADVANCED, difficulty_rating=3.8)

    def find_step(self, grid: CandidateGrid) -> Optional[DeductionStep]:
        all_steps = self.find_all_steps(grid)
        return all_steps[0] if all_steps else None

    def find_all_steps(self, grid: CandidateGrid) -> List[DeductionStep]:
        steps = []

        for d in range(1, 10):
            # Row-based X-Wing (eliminate from columns)
            row_candidates = {}
            for r in range(GRID_SIZE):
                cols = [c for c in range(GRID_SIZE) if grid.has_candidate(r, c, d)]
                if len(cols) == 2:
                    row_candidates[r] = tuple(cols)

            for r1, r2 in itertools.combinations(row_candidates.keys(), 2):
                if row_candidates[r1] == row_candidates[r2]:
                    c1, c2 = row_candidates[r1]
                    eliminations = []
                    for r in range(GRID_SIZE):
                        if r != r1 and r != r2:
                            if grid.has_candidate(r, c1, d):
                                eliminations.append((r, c1, d))
                            if grid.has_candidate(r, c2, d):
                                eliminations.append((r, c2, d))

                    if eliminations:
                        steps.append(DeductionStep(
                            strategy_name=self.name,
                            tier=self.tier,
                            difficulty_rating=self.difficulty_rating,
                            action="eliminate",
                            digit=d,
                            eliminations=eliminations,
                            cause_cells=[(r1, c1), (r1, c2), (r2, c1), (r2, c2)],
                            explanation=(
                                f"X-Wing on digit {d}: In Rows {r1+1} and {r2+1}, digit {d} appears in exactly two "
                                f"columns (Columns {c1+1} and {c2+1}). Therefore, digit {d} can be eliminated from "
                                f"all other cells in Columns {c1+1} and {c2+1}."
                            )
                        ))

            # Column-based X-Wing (eliminate from rows)
            col_candidates = {}
            for c in range(GRID_SIZE):
                rows = [r for r in range(GRID_SIZE) if grid.has_candidate(r, c, d)]
                if len(rows) == 2:
                    col_candidates[c] = tuple(rows)

            for c1, c2 in itertools.combinations(col_candidates.keys(), 2):
                if col_candidates[c1] == col_candidates[c2]:
                    r1, r2 = col_candidates[c1]
                    eliminations = []
                    for c in range(GRID_SIZE):
                        if c != c1 and c != c2:
                            if grid.has_candidate(r1, c, d):
                                eliminations.append((r1, c, d))
                            if grid.has_candidate(r2, c, d):
                                eliminations.append((r2, c, d))

                    if eliminations:
                        steps.append(DeductionStep(
                            strategy_name=self.name,
                            tier=self.tier,
                            difficulty_rating=self.difficulty_rating,
                            action="eliminate",
                            digit=d,
                            eliminations=eliminations,
                            cause_cells=[(r1, c1), (r2, c1), (r1, c2), (r2, c2)],
                            explanation=(
                                f"X-Wing on digit {d}: In Columns {c1+1} and {c2+1}, digit {d} appears in exactly two "
                                f"rows (Rows {r1+1} and {r2+1}). Therefore, digit {d} can be eliminated from "
                                f"all other cells in Rows {r1+1} and {r2+1}."
                            )
                        ))

        return steps
