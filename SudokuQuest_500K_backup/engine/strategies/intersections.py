"""
Sudoku Quest - Intersection Strategies (Tier 2)
Implements Locked Candidates: Pointing Pairs/Triples (Box -> Line) and Box-Line Reduction (Line -> Box).
"""
from typing import Optional, List, Tuple
from engine.strategies.base_strategy import BaseStrategy, DeductionStep, StrategyTier
from engine.models.candidate_grid import CandidateGrid
from core.constants import GRID_SIZE

class PointingPairs(BaseStrategy):
    """
    Locked Candidates Type 1 (Pointing):
    If all occurrences of a candidate digit within a 3x3 block are confined to a single row
    or column, that digit can be eliminated from all other cells in that entire row or column.
    """
    def __init__(self):
        super().__init__(name="Pointing Pairs", tier=StrategyTier.INTERMEDIATE, difficulty_rating=2.6)

    def find_step(self, grid: CandidateGrid) -> Optional[DeductionStep]:
        all_steps = self.find_all_steps(grid)
        return all_steps[0] if all_steps else None

    def find_all_steps(self, grid: CandidateGrid) -> List[DeductionStep]:
        steps = []

        for d in range(1, 10):
            for b in range(GRID_SIZE):
                cells = grid.get_box_cells_with_candidate(b, d)
                if len(cells) in (2, 3):
                    rows = {r for (r, c) in cells}
                    cols = {c for (r, c) in cells}

                    # Confined to a single row
                    if len(rows) == 1:
                        target_row = next(iter(rows))
                        # Check if any cell in target_row outside box b has candidate d
                        eliminations = []
                        for c in range(GRID_SIZE):
                            cell_box = (target_row // 3) * 3 + (c // 3)
                            if cell_box != b and grid.has_candidate(target_row, c, d):
                                eliminations.append((target_row, c, d))

                        if eliminations:
                            steps.append(DeductionStep(
                                strategy_name=self.name,
                                tier=self.tier,
                                difficulty_rating=self.difficulty_rating,
                                action="eliminate",
                                digit=d,
                                eliminations=eliminations,
                                cause_cells=cells,
                                explanation=(
                                    f"Pointing Pair/Triple in Block {b+1}: All candidate placements for digit {d} "
                                    f"in Block {b+1} are locked in Row {target_row+1}. Therefore, digit {d} cannot "
                                    f"appear in any other cell of Row {target_row+1}."
                                )
                            ))

                    # Confined to a single column
                    if len(cols) == 1:
                        target_col = next(iter(cols))
                        eliminations = []
                        for r in range(GRID_SIZE):
                            cell_box = (r // 3) * 3 + (target_col // 3)
                            if cell_box != b and grid.has_candidate(r, target_col, d):
                                eliminations.append((r, target_col, d))

                        if eliminations:
                            steps.append(DeductionStep(
                                strategy_name=self.name,
                                tier=self.tier,
                                difficulty_rating=self.difficulty_rating,
                                action="eliminate",
                                digit=d,
                                eliminations=eliminations,
                                cause_cells=cells,
                                explanation=(
                                    f"Pointing Pair/Triple in Block {b+1}: All candidate placements for digit {d} "
                                    f"in Block {b+1} are locked in Column {target_col+1}. Therefore, digit {d} cannot "
                                    f"appear in any other cell of Column {target_col+1}."
                                )
                            ))

        return steps

class BoxLineReduction(BaseStrategy):
    """
    Locked Candidates Type 2 (Box-Line Reduction):
    If all occurrences of a candidate digit within a row or column are confined to a single
    3x3 block, that digit can be eliminated from all other cells in that 3x3 block.
    """
    def __init__(self):
        super().__init__(name="Box-Line Reduction", tier=StrategyTier.INTERMEDIATE, difficulty_rating=2.8)

    def find_step(self, grid: CandidateGrid) -> Optional[DeductionStep]:
        all_steps = self.find_all_steps(grid)
        return all_steps[0] if all_steps else None

    def find_all_steps(self, grid: CandidateGrid) -> List[DeductionStep]:
        steps = []

        for d in range(1, 10):
            # Check Rows -> Box
            for r in range(GRID_SIZE):
                cells = grid.get_row_cells_with_candidate(r, d)
                if len(cells) in (2, 3):
                    boxes = {(r // 3) * 3 + (c // 3) for (r, c) in cells}
                    if len(boxes) == 1:
                        target_box = next(iter(boxes))
                        # Find other cells in target_box that have candidate d and are not in row r
                        eliminations = []
                        br, bc = (target_box // 3) * 3, (target_box % 3) * 3
                        for box_r in range(3):
                            for box_c in range(3):
                                cell_r, cell_c = br + box_r, bc + box_c
                                if cell_r != r and grid.has_candidate(cell_r, cell_c, d):
                                    eliminations.append((cell_r, cell_c, d))

                        if eliminations:
                            steps.append(DeductionStep(
                                strategy_name=self.name,
                                tier=self.tier,
                                difficulty_rating=self.difficulty_rating,
                                action="eliminate",
                                digit=d,
                                eliminations=eliminations,
                                cause_cells=cells,
                                explanation=(
                                    f"Box-Line Reduction on Row {r+1}: All occurrences of candidate {d} in Row {r+1} "
                                    f"are confined to Block {target_box+1}. Therefore, digit {d} cannot appear "
                                    f"in any other cell of Block {target_box+1}."
                                )
                            ))

            # Check Columns -> Box
            for c in range(GRID_SIZE):
                cells = grid.get_col_cells_with_candidate(c, d)
                if len(cells) in (2, 3):
                    boxes = {(r // 3) * 3 + (c // 3) for (r, c) in cells}
                    if len(boxes) == 1:
                        target_box = next(iter(boxes))
                        eliminations = []
                        br, bc = (target_box // 3) * 3, (target_box % 3) * 3
                        for box_r in range(3):
                            for box_c in range(3):
                                cell_r, cell_c = br + box_r, bc + box_c
                                if cell_c != c and grid.has_candidate(cell_r, cell_c, d):
                                    eliminations.append((cell_r, cell_c, d))

                        if eliminations:
                            steps.append(DeductionStep(
                                strategy_name=self.name,
                                tier=self.tier,
                                difficulty_rating=self.difficulty_rating,
                                action="eliminate",
                                digit=d,
                                eliminations=eliminations,
                                cause_cells=cells,
                                explanation=(
                                    f"Box-Line Reduction on Column {c+1}: All occurrences of candidate {d} in Column {c+1} "
                                    f"are confined to Block {target_box+1}. Therefore, digit {d} cannot appear "
                                    f"in any other cell of Block {target_box+1}."
                                )
                            ))

        return steps
