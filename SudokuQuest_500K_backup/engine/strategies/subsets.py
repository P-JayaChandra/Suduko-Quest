"""
Sudoku Quest - Subset Strategies (Tier 3)
Implements Naked Pairs, Naked Triples, Hidden Pairs, and Hidden Triples.
"""
from typing import Optional, List, Tuple, Set
import itertools
from engine.strategies.base_strategy import BaseStrategy, DeductionStep, StrategyTier
from engine.models.candidate_grid import CandidateGrid
from core.constants import GRID_SIZE

def _get_units() -> List[Tuple[str, int, List[Tuple[int, int]]]]:
    """Returns all 27 units: 9 rows, 9 columns, 9 blocks."""
    units = []
    # Rows
    for r in range(GRID_SIZE):
        units.append(("Row", r, [(r, c) for c in range(GRID_SIZE)]))
    # Columns
    for c in range(GRID_SIZE):
        units.append(("Column", c, [(r, c) for r in range(GRID_SIZE)]))
    # Blocks
    for b in range(GRID_SIZE):
        br, bc = (b // 3) * 3, (b % 3) * 3
        coords = [(br + r, bc + c) for r in range(3) for c in range(3)]
        units.append(("Block", b, coords))
    return units

class NakedPair(BaseStrategy):
    """
    Naked Pair: Exactly two cells in a unit contain the exact same two candidates.
    Those two candidates can be eliminated from all other cells in that unit.
    """
    def __init__(self):
        super().__init__(name="Naked Pair", tier=StrategyTier.ADVANCED, difficulty_rating=3.0)

    def find_step(self, grid: CandidateGrid) -> Optional[DeductionStep]:
        all_steps = self.find_all_steps(grid)
        return all_steps[0] if all_steps else None

    def find_all_steps(self, grid: CandidateGrid) -> List[DeductionStep]:
        steps = []
        for unit_type, unit_idx, cells in _get_units():
            # Find empty cells with exactly 2 candidates
            pair_cells = [
                (r, c) for (r, c) in cells
                if grid.values[r][c] == 0 and len(grid.get_candidates(r, c)) == 2
            ]

            # Compare pairs of cells
            for c1, c2 in itertools.combinations(pair_cells, 2):
                cands1 = grid.get_candidates(c1[0], c1[1])
                cands2 = grid.get_candidates(c2[0], c2[1])

                if cands1 == cands2:
                    digits = sorted(list(cands1))
                    # Check other cells in this unit for eliminations
                    eliminations = []
                    for (r, c) in cells:
                        if (r, c) != c1 and (r, c) != c2 and grid.values[r][c] == 0:
                            for d in digits:
                                if grid.has_candidate(r, c, d):
                                    eliminations.append((r, c, d))

                    if eliminations:
                        steps.append(DeductionStep(
                            strategy_name=self.name,
                            tier=self.tier,
                            difficulty_rating=self.difficulty_rating,
                            action="eliminate",
                            eliminations=eliminations,
                            cause_cells=[c1, c2],
                            explanation=(
                                f"Naked Pair in {unit_type} {unit_idx+1}: Cells (R{c1[0]+1}, C{c1[1]+1}) and "
                                f"(R{c2[0]+1}, C{c2[1]+1}) both exclusively hold candidates {digits}. "
                                f"Therefore, {digits} can be eliminated from all other cells in {unit_type} {unit_idx+1}."
                            )
                        ))

        return steps

class HiddenPair(BaseStrategy):
    """
    Hidden Pair: Exactly two candidate digits appear in only the same two cells of a unit.
    All other candidates in those two cells can be eliminated.
    """
    def __init__(self):
        super().__init__(name="Hidden Pair", tier=StrategyTier.ADVANCED, difficulty_rating=3.4)

    def find_step(self, grid: CandidateGrid) -> Optional[DeductionStep]:
        all_steps = self.find_all_steps(grid)
        return all_steps[0] if all_steps else None

    def find_all_steps(self, grid: CandidateGrid) -> List[DeductionStep]:
        steps = []
        for unit_type, unit_idx, cells in _get_units():
            empty_cells = [(r, c) for (r, c) in cells if grid.values[r][c] == 0]
            # Map digit -> cells where it can appear
            digit_cells = {}
            for d in range(1, 10):
                matching = [(r, c) for (r, c) in empty_cells if grid.has_candidate(r, c, d)]
                if len(matching) == 2:
                    digit_cells[d] = tuple(sorted(matching))

            # Look for two digits having identical two cells
            for d1, d2 in itertools.combinations(digit_cells.keys(), 2):
                if digit_cells[d1] == digit_cells[d2]:
                    target_cells = list(digit_cells[d1])
                    c1, c2 = target_cells[0], target_cells[1]
                    # Check if either cell has other candidates to eliminate
                    eliminations = []
                    for cell in (c1, c2):
                        for extra_d in grid.get_candidates(cell[0], cell[1]):
                            if extra_d != d1 and extra_d != d2:
                                eliminations.append((cell[0], cell[1], extra_d))

                    if eliminations:
                        steps.append(DeductionStep(
                            strategy_name=self.name,
                            tier=self.tier,
                            difficulty_rating=self.difficulty_rating,
                            action="eliminate",
                            eliminations=eliminations,
                            cause_cells=[c1, c2],
                            explanation=(
                                f"Hidden Pair in {unit_type} {unit_idx+1}: Digits {d1} and {d2} appear only in "
                                f"Cells (R{c1[0]+1}, C{c1[1]+1}) and (R{c2[0]+1}, C{c2[1]+1}). All other candidates "
                                f"can be eliminated from these two cells."
                            )
                        ))

        return steps
