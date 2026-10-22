"""
Sudoku Quest - Singles Strategies (Tier 1)
Implements Naked Single and Hidden Single logical deduction techniques.
"""
from typing import Optional, List, Tuple
from engine.strategies.base_strategy import BaseStrategy, DeductionStep, StrategyTier
from engine.models.candidate_grid import CandidateGrid
from core.constants import GRID_SIZE

class NakedSingle(BaseStrategy):
    """
    Naked Single: A cell has exactly one candidate remaining.
    All other digits have been ruled out by the cell's peers.
    """
    def __init__(self):
        super().__init__(name="Naked Single", tier=StrategyTier.BEGINNER, difficulty_rating=1.0)

    def find_step(self, grid: CandidateGrid) -> Optional[DeductionStep]:
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if grid.values[r][c] == 0:
                    cands = grid.get_candidates(r, c)
                    if len(cands) == 1:
                        digit = next(iter(cands))
                        return DeductionStep(
                            strategy_name=self.name,
                            tier=self.tier,
                            difficulty_rating=self.difficulty_rating,
                            action="place",
                            digit=digit,
                            target_cell=(r, c),
                            cause_cells=[(r, c)],
                            explanation=(
                                f"Cell (R{r+1}, C{c+1}) has only one possible candidate remaining: digit {digit}. "
                                f"All other 8 digits are already present in its row, column, or 3x3 block."
                            )
                        )
        return None

    def find_all_steps(self, grid: CandidateGrid) -> List[DeductionStep]:
        steps = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if grid.values[r][c] == 0:
                    cands = grid.get_candidates(r, c)
                    if len(cands) == 1:
                        digit = next(iter(cands))
                        steps.append(DeductionStep(
                            strategy_name=self.name,
                            tier=self.tier,
                            difficulty_rating=self.difficulty_rating,
                            action="place",
                            digit=digit,
                            target_cell=(r, c),
                            cause_cells=[(r, c)],
                            explanation=(
                                f"Cell (R{r+1}, C{c+1}) has only one possible candidate remaining: digit {digit}."
                            )
                        ))
        return steps

class HiddenSingle(BaseStrategy):
    """
    Hidden Single: Within a unit (Row, Column, or 3x3 Block), a candidate digit
    can only be placed in a single cell.
    """
    def __init__(self):
        super().__init__(name="Hidden Single", tier=StrategyTier.BEGINNER, difficulty_rating=1.2)

    def find_step(self, grid: CandidateGrid) -> Optional[DeductionStep]:
        all_steps = self.find_all_steps(grid)
        return all_steps[0] if all_steps else None

    def find_all_steps(self, grid: CandidateGrid) -> List[DeductionStep]:
        steps = []
        seen_placements = set()

        for d in range(1, 10):
            # Check Rows
            for r in range(GRID_SIZE):
                cells = grid.get_row_cells_with_candidate(r, d)
                if len(cells) == 1:
                    cell = cells[0]
                    if (cell, d) not in seen_placements:
                        seen_placements.add((cell, d))
                        steps.append(DeductionStep(
                            strategy_name=self.name,
                            tier=self.tier,
                            difficulty_rating=self.difficulty_rating,
                            action="place",
                            digit=d,
                            target_cell=cell,
                            cause_cells=[cell],
                            explanation=(
                                f"In Row {r+1}, digit {d} can only be placed in Cell (R{cell[0]+1}, C{cell[1]+1}). "
                                f"None of the other empty cells in Row {r+1} can accept {d}."
                            )
                        ))

            # Check Columns
            for c in range(GRID_SIZE):
                cells = grid.get_col_cells_with_candidate(c, d)
                if len(cells) == 1:
                    cell = cells[0]
                    if (cell, d) not in seen_placements:
                        seen_placements.add((cell, d))
                        steps.append(DeductionStep(
                            strategy_name=self.name,
                            tier=self.tier,
                            difficulty_rating=self.difficulty_rating,
                            action="place",
                            digit=d,
                            target_cell=cell,
                            cause_cells=[cell],
                            explanation=(
                                f"In Column {c+1}, digit {d} can only be placed in Cell (R{cell[0]+1}, C{cell[1]+1}). "
                                f"None of the other empty cells in Column {c+1} can accept {d}."
                            )
                        ))

            # Check Blocks (Boxes)
            for b in range(GRID_SIZE):
                cells = grid.get_box_cells_with_candidate(b, d)
                if len(cells) == 1:
                    cell = cells[0]
                    if (cell, d) not in seen_placements:
                        seen_placements.add((cell, d))
                        steps.append(DeductionStep(
                            strategy_name=self.name,
                            tier=self.tier,
                            difficulty_rating=self.difficulty_rating,
                            action="place",
                            digit=d,
                            target_cell=cell,
                            cause_cells=[cell],
                            explanation=(
                                f"In 3x3 Block {b+1}, digit {d} can only be placed in Cell (R{cell[0]+1}, C{cell[1]+1}). "
                                f"None of the other empty cells in Block {b+1} can accept {d}."
                            )
                        ))

        return steps
