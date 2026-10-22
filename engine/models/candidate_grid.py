"""
Sudoku Quest - Candidate Grid
Manages explicit candidate sets for all 81 cells with bitmask indexing,
peer queries, and candidate elimination tracking.
"""
from typing import List, Set, Dict, Tuple, Optional
from engine.models.board import Board
from core.constants import GRID_SIZE

ALL_CANDIDATES = frozenset(range(1, 10))

class CandidateGrid:
    """Manages the full 9x9 candidate matrix for human deduction strategies."""

    def __init__(self, board: Optional[Board] = None):
        # 9x9 matrix of candidate sets
        self.candidates: List[List[Set[int]]] = [
            [set(range(1, 10)) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)
        ]
        self.values: List[List[int]] = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]

        if board is not None:
            self.sync_from_board(board)

    def sync_from_board(self, board: Board) -> None:
        """Initialize candidate states directly from a Board instance."""
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                val = board.get_value(r, c)
                self.values[r][c] = val
                if val != 0:
                    self.candidates[r][c] = set()
                else:
                    self.candidates[r][c] = set(range(1, 10))

        # Eliminate candidates seen by placed digits
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                val = self.values[r][c]
                if val != 0:
                    self._eliminate_peer_candidates(r, c, val)

    def _eliminate_peer_candidates(self, row: int, col: int, val: int) -> None:
        """Remove placed digit from candidate sets of all peer cells."""
        # Row
        for c in range(GRID_SIZE):
            self.candidates[row][c].discard(val)
        # Col
        for r in range(GRID_SIZE):
            self.candidates[r][col].discard(val)
        # Box
        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(3):
            for c in range(3):
                self.candidates[br + r][bc + c].discard(val)

    def get_candidates(self, row: int, col: int) -> Set[int]:
        return self.candidates[row][col]

    def has_candidate(self, row: int, col: int, digit: int) -> bool:
        return digit in self.candidates[row][col]

    def eliminate(self, row: int, col: int, digit: int) -> bool:
        """Eliminate a candidate from cell (row, col). Returns True if candidate was present."""
        if digit in self.candidates[row][col]:
            self.candidates[row][col].discard(digit)
            return True
        return False

    def set_value(self, row: int, col: int, digit: int) -> None:
        """Place digit in cell and update peer candidates."""
        self.values[row][col] = digit
        self.candidates[row][col].clear()
        self._eliminate_peer_candidates(row, col, digit)

    def get_row_cells_with_candidate(self, row: int, digit: int) -> List[Tuple[int, int]]:
        return [(row, c) for c in range(GRID_SIZE) if digit in self.candidates[row][c]]

    def get_col_cells_with_candidate(self, col: int, digit: int) -> List[Tuple[int, int]]:
        return [(r, col) for r in range(GRID_SIZE) if digit in self.candidates[r][col]]

    def get_box_cells_with_candidate(self, box: int, digit: int) -> List[Tuple[int, int]]:
        br, bc = (box // 3) * 3, (box % 3) * 3
        return [
            (br + r, bc + c)
            for r in range(3)
            for c in range(3)
            if digit in self.candidates[br + r][bc + c]
        ]

    def clone(self) -> "CandidateGrid":
        cloned = CandidateGrid()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                cloned.values[r][c] = self.values[r][c]
                cloned.candidates[r][c] = set(self.candidates[r][c])
        return cloned

    def get_candidate_count(self, row: int, col: int) -> int:
        """Return number of active candidates for cell using bit population count."""
        mask = self.get_mask(row, col) if hasattr(self, 'get_mask') else self.grid[row][col]
        return bin(mask).count('1')
