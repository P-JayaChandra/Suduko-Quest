"""
Sudoku Quest - Uniqueness Strategies (Tier 5)
Implements Unique Rectangle Type 1 deadly pattern avoidance.
"""
from typing import Optional, List, Tuple, Set
import itertools
from engine.strategies.base_strategy import BaseStrategy, DeductionStep, StrategyTier
from engine.models.candidate_grid import CandidateGrid
from core.constants import GRID_SIZE

class UniqueRectangleType1(BaseStrategy):
    """
    Unique Rectangle (Type 1):
    A deadly pattern occurs if 4 cells at the corners of a rectangle spanning exactly two 3x3 blocks
    all contain only the same two candidates (X, Y).
    If three of the cells have only {X, Y} and the fourth cell has {X, Y} plus extra candidates,
    candidates X and Y can be eliminated from that fourth cell to prevent multiple solutions.
    """
    def __init__(self):
        super().__init__(name="Unique Rectangle Type 1", tier=StrategyTier.EXTREME, difficulty_rating=5.0)

    def find_step(self, grid: CandidateGrid) -> Optional[DeductionStep]:
        all_steps = self.find_all_steps(grid)
        return all_steps[0] if all_steps else None

    def find_all_steps(self, grid: CandidateGrid) -> List[DeductionStep]:
        steps = []

        # Iterate all pairs of rows
        for r1, r2 in itertools.combinations(range(GRID_SIZE), 2):
            # Iterate all pairs of cols
            for c1, c2 in itertools.combinations(range(GRID_SIZE), 2):
                # Verify that the 4 cells span exactly two 3x3 blocks
                b1 = (r1 // 3) * 3 + (c1 // 3)
                b2 = (r1 // 3) * 3 + (c2 // 3)
                b3 = (r2 // 3) * 3 + (c1 // 3)
                b4 = (r2 // 3) * 3 + (c2 // 3)

                boxes = {b1, b2, b3, b4}
                if len(boxes) != 2:
                    continue  # Must span exactly two blocks

                corners = [(r1, c1), (r1, c2), (r2, c1), (r2, c2)]
                # Check if all 4 corners are unsolved
                if any(grid.values[r][c] != 0 for (r, c) in corners):
                    continue

                corner_cands = [grid.get_candidates(r, c) for (r, c) in corners]

                # Look for 3 corners having identical bivalue candidates {X, Y}
                bivalue_indices = [i for i, cands in enumerate(corner_cands) if len(cands) == 2]
                if len(bivalue_indices) == 3:
                    # Check if the 3 corners share the exact same 2 candidates
                    i1, i2, i3 = bivalue_indices
                    if corner_cands[i1] == corner_cands[i2] == corner_cands[i3]:
                        pair = corner_cands[i1]
                        x, y = sorted(list(pair))

                        # Fourth corner
                        fourth_idx = ({0, 1, 2, 3} - set(bivalue_indices)).pop()
                        fourth_cands = corner_cands[fourth_idx]
                        fourth_cell = corners[fourth_idx]

                        # Fourth cell must contain both X and Y plus additional candidate(s)
                        if pair.issubset(fourth_cands) and len(fourth_cands) > 2:
                            eliminations = [
                                (fourth_cell[0], fourth_cell[1], x),
                                (fourth_cell[0], fourth_cell[1], y)
                            ]
                            steps.append(DeductionStep(
                                strategy_name=self.name,
                                tier=self.tier,
                                difficulty_rating=self.difficulty_rating,
                                action="eliminate",
                                eliminations=eliminations,
                                cause_cells=[corners[i1], corners[i2], corners[i3]],
                                secondary_cells=[fourth_cell],
                                explanation=(
                                    f"Unique Rectangle (Type 1) on candidates ({x},{y}) across Rows {r1+1},{r2+1} "
                                    f"and Columns {c1+1},{c2+1}. To avoid a deadly pattern with multiple solutions, "
                                    f"candidates {x} and {y} are eliminated from Cell (R{fourth_cell[0]+1}, C{fourth_cell[1]+1})."
                                )
                            ))

        return steps
