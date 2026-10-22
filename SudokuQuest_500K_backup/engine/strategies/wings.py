"""
Sudoku Quest - Wing Strategies (Tier 4)
Implements XY-Wing (Y-Wing) bent-triple deduction pattern.
"""
from typing import Optional, List, Tuple, Set
import itertools
from engine.strategies.base_strategy import BaseStrategy, DeductionStep, StrategyTier
from engine.models.candidate_grid import CandidateGrid
from core.constants import GRID_SIZE

def _cells_see_each_other(c1: Tuple[int, int], c2: Tuple[int, int]) -> bool:
    """True if c1 and c2 share a row, column, or 3x3 block and are distinct."""
    if c1 == c2:
        return False
    r1, col1 = c1
    r2, col2 = c2
    if r1 == r2 or col1 == col2:
        return True
    return (r1 // 3) == (r2 // 3) and (col1 // 3) == (col2 // 3)

class XYWing(BaseStrategy):
    """
    XY-Wing (Y-Wing):
    A bivalue pivot cell with candidates (X, Y) connects to two bivalue pincer cells:
    Pincer 1 with candidates (X, Z) and Pincer 2 with candidates (Y, Z).
    Whichever value the pivot cell takes, one of the pincers must be Z.
    Therefore, any cell that sees BOTH pincers cannot contain candidate Z.
    """
    def __init__(self):
        super().__init__(name="XY-Wing", tier=StrategyTier.MASTER, difficulty_rating=4.4)

    def find_step(self, grid: CandidateGrid) -> Optional[DeductionStep]:
        all_steps = self.find_all_steps(grid)
        return all_steps[0] if all_steps else None

    def find_all_steps(self, grid: CandidateGrid) -> List[DeductionStep]:
        steps = []
        # Find all bivalue cells (exactly 2 candidates)
        bivalue_cells = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if grid.values[r][c] == 0 and len(grid.get_candidates(r, c)) == 2:
                    bivalue_cells.append((r, c))

        # Check every candidate pivot
        for pivot in bivalue_cells:
            pivot_cands = sorted(list(grid.get_candidates(pivot[0], pivot[1])))
            x, y = pivot_cands[0], pivot_cands[1]

            # Find peers of pivot that are bivalue
            pincers = [p for p in bivalue_cells if _cells_see_each_other(pivot, p)]

            # Look for Pincer 1 with (X, Z) and Pincer 2 with (Y, Z)
            for p1, p2 in itertools.combinations(pincers, 2):
                cands1 = grid.get_candidates(p1[0], p1[1])
                cands2 = grid.get_candidates(p2[0], p2[1])

                # Determine if one has X and other has Y with shared Z
                has_x_1 = x in cands1
                has_y_1 = y in cands1
                has_x_2 = x in cands2
                has_y_2 = y in cands2

                p1_is_xz = False
                p2_is_yz = False
                z = None

                if has_x_1 and not has_y_1 and has_y_2 and not has_x_2:
                    z1 = (cands1 - {x}).pop()
                    z2 = (cands2 - {y}).pop()
                    if z1 == z2 and z1 not in (x, y):
                        z = z1
                        p1_is_xz = True
                        p2_is_yz = True
                elif has_y_1 and not has_x_1 and has_x_2 and not has_y_2:
                    z1 = (cands1 - {y}).pop()
                    z2 = (cands2 - {x}).pop()
                    if z1 == z2 and z1 not in (x, y):
                        z = z1
                        p1_is_xz = True
                        p2_is_yz = True

                if z is not None:
                    # Find cells that see both p1 and p2 (excluding pivot, p1, p2)
                    eliminations = []
                    for r in range(GRID_SIZE):
                        for c in range(GRID_SIZE):
                            cell = (r, c)
                            if cell != pivot and cell != p1 and cell != p2 and grid.values[r][c] == 0:
                                if _cells_see_each_other(cell, p1) and _cells_see_each_other(cell, p2):
                                    if grid.has_candidate(r, c, z):
                                        eliminations.append((r, c, z))

                    if eliminations:
                        steps.append(DeductionStep(
                            strategy_name=self.name,
                            tier=self.tier,
                            difficulty_rating=self.difficulty_rating,
                            action="eliminate",
                            digit=z,
                            eliminations=eliminations,
                            cause_cells=[pivot, p1, p2],
                            explanation=(
                                f"XY-Wing with Pivot (R{pivot[0]+1}, C{pivot[1]+1}) candidates ({x},{y}) and Pincers "
                                f"(R{p1[0]+1}, C{p1[1]+1}) and (R{p2[0]+1}, C{p2[1]+1}). One pincer must be {z}. "
                                f"Therefore, candidate {z} is eliminated from cells that see both pincers."
                            )
                        ))

        return steps
