"""
Sudoku Quest - Sudoku Board Model
High-performance, rich representation of a 9x9 Sudoku grid with row, column, and box views,
candidate matrix computation, move undo/redo history, conflict detection, and string serialization.
"""
from typing import List, Tuple, Set, Optional, Dict, Iterator
from engine.models.cell import Cell
from engine.models.move import Move
from core.constants import GRID_SIZE, BOX_SIZE, CANONICAL_CELL_COUNT, MoveType
from core.exceptions import InvalidBoardError

class Board:
    """Primary 9x9 Sudoku Board container."""

    def __init__(self, initial_data: Optional[any] = None):
        self.cells: List[List[Cell]] = [
            [Cell(r, c) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)
        ]
        self.undo_stack: List[Move] = []
        self.redo_stack: List[Move] = []

        if initial_data is not None:
            self.load(initial_data)

    def load(self, data: any) -> "Board":
        """
        Load grid data from:
        - 81-char string (digits 1-9 and 0 or . for blanks)
        - 9x9 nested list of integers
        - 81-element flat list of integers
        """
        if isinstance(data, str):
            clean_str = "".join(c for c in data.strip() if c.isdigit() or c in ".-_ ")
            if len(clean_str) != CANONICAL_CELL_COUNT:
                raise InvalidBoardError(f"Expected 81 characters for standard board, received {len(clean_str)}.")
            for i, ch in enumerate(clean_str):
                r, c = i // GRID_SIZE, i % GRID_SIZE
                val = int(ch) if ch.isdigit() else 0
                self.cells[r][c].set_value(val, given=(val != 0))
        elif isinstance(data, list):
            if len(data) == GRID_SIZE and isinstance(data[0], list):
                for r in range(GRID_SIZE):
                    for c in range(GRID_SIZE):
                        val = int(data[r][c])
                        self.cells[r][c].set_value(val, given=(val != 0))
            elif len(data) == CANONICAL_CELL_COUNT:
                for i, val in enumerate(data):
                    r, c = i // GRID_SIZE, i % GRID_SIZE
                    v = int(val)
                    self.cells[r][c].set_value(v, given=(v != 0))
            else:
                raise InvalidBoardError("Invalid list dimensions for board loading.")
        elif isinstance(data, Board):
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    src = data.cells[r][c]
                    self.cells[r][c] = src.clone()
        else:
            raise InvalidBoardError(f"Unsupported board data type: {type(data)}")

        self.recalculate_all_candidates()
        self.undo_stack.clear()
        self.redo_stack.clear()
        return self

    def get_cell(self, row: int, col: int) -> Cell:
        """Retrieve cell at (row, col)."""
        return self.cells[row][col]

    def get_cell_by_index(self, index: int) -> Cell:
        """Retrieve cell at flat 0-80 index."""
        return self.cells[index // GRID_SIZE][index % GRID_SIZE]

    def get_value(self, row: int, col: int) -> int:
        return self.cells[row][col].value

    def set_value(self, row: int, col: int, value: int, record_move: bool = True) -> bool:
        """
        Set value on cell. If record_move is True, pushes action onto undo stack.
        Returns True if value changed.
        """
        cell = self.cells[row][col]
        if cell.is_given:
            return False

        old_val = cell.value
        if old_val == value:
            return False

        old_notes = set(cell.notes)
        cell.set_value(value, given=False)

        if record_move:
            move = Move(
                row=row,
                col=col,
                old_value=old_val,
                new_value=value,
                old_notes=old_notes,
                new_notes=set(),
                move_type=MoveType.DIGIT if value != 0 else MoveType.ERASE
            )
            self.undo_stack.append(move)
            self.redo_stack.clear()

        self.recalculate_peers_candidates(row, col)
        return True

    def undo(self) -> Optional[Move]:
        """Undo last player move. Returns the reverted move or None."""
        if not self.undo_stack:
            return None
        move = self.undo_stack.pop()
        cell = self.cells[move.row][move.col]
        cell.value = move.old_value
        cell.notes = set(move.old_notes)
        self.redo_stack.append(move)
        self.recalculate_peers_candidates(move.row, move.col)
        return move

    def redo(self) -> Optional[Move]:
        """Redo last undone move. Returns reapplied move or None."""
        if not self.redo_stack:
            return None
        move = self.redo_stack.pop()
        cell = self.cells[move.row][move.col]
        cell.value = move.new_value
        cell.notes = set(move.new_notes)
        self.undo_stack.append(move)
        self.recalculate_peers_candidates(move.row, move.col)
        return move

    def row_values(self, row: int) -> List[int]:
        """List of all 9 digit values in row."""
        return [self.cells[row][c].value for c in range(GRID_SIZE)]

    def col_values(self, col: int) -> List[int]:
        """List of all 9 digit values in column."""
        return [self.cells[r][col].value for r in range(GRID_SIZE)]

    def box_values(self, box: int) -> List[int]:
        """List of all 9 digit values in 3x3 block."""
        br = (box // 3) * 3
        bc = (box % 3) * 3
        return [self.cells[br + r][bc + c].value for r in range(3) for c in range(3)]

    def row_cells(self, row: int) -> List[Cell]:
        return [self.cells[row][c] for c in range(GRID_SIZE)]

    def col_cells(self, col: int) -> List[Cell]:
        return [self.cells[r][col] for r in range(GRID_SIZE)]

    def box_cells(self, box: int) -> List[Cell]:
        br = (box // 3) * 3
        bc = (box % 3) * 3
        return [self.cells[br + r][bc + c] for r in range(3) for c in range(3)]

    def get_peer_cells(self, row: int, col: int) -> Set[Cell]:
        """Retrieve all 20 unique peer cells in the same row, col, and box."""
        peers = set()
        for c in range(GRID_SIZE):
            if c != col:
                peers.add(self.cells[row][c])
        for r in range(GRID_SIZE):
            if r != row:
                peers.add(self.cells[r][col])
        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(3):
            for c in range(3):
                pr, pc = br + r, bc + c
                if pr != row or pc != col:
                    peers.add(self.cells[pr][pc])
        return peers

    def is_safe(self, row: int, col: int, value: int) -> bool:
        """True if digit value does not collide with existing placed digits in peers."""
        if value < 1 or value > 9:
            return False
        for c in range(GRID_SIZE):
            if c != col and self.cells[row][c].value == value:
                return False
        for r in range(GRID_SIZE):
            if r != row and self.cells[r][col].value == value:
                return False
        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(3):
            for c in range(3):
                pr, pc = br + r, bc + c
                if (pr != row or pc != col) and self.cells[pr][pc].value == value:
                    return False
        return True

    def recalculate_all_candidates(self) -> None:
        """Compute candidate sets for every empty cell."""
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                cell = self.cells[r][c]
                if cell.is_empty:
                    used = set()
                    for peer in self.get_peer_cells(r, c):
                        if not peer.is_empty:
                            used.add(peer.value)
                    cell.candidates = set(range(1, 10)) - used
                else:
                    cell.candidates.clear()

    def recalculate_peers_candidates(self, row: int, col: int) -> None:
        """Update candidate sets for target cell and all its peers."""
        cells_to_update = self.get_peer_cells(row, col) | {self.cells[row][col]}
        for cell in cells_to_update:
            if cell.is_empty:
                used = {peer.value for peer in self.get_peer_cells(cell.row, cell.col) if not peer.is_empty}
                cell.candidates = set(range(1, 10)) - used
            else:
                cell.candidates.clear()

    def find_conflicts(self) -> List[Tuple[int, int]]:
        """Return list of (row, col) coordinates of all cells violating Sudoku rules."""
        conflicts = set()
        # Row conflicts
        for r in range(GRID_SIZE):
            seen: Dict[int, List[int]] = {}
            for c in range(GRID_SIZE):
                v = self.cells[r][c].value
                if v != 0:
                    seen.setdefault(v, []).append(c)
            for v, cols in seen.items():
                if len(cols) > 1:
                    for c in cols:
                        conflicts.add((r, c))

        # Col conflicts
        for c in range(GRID_SIZE):
            seen: Dict[int, List[int]] = {}
            for r in range(GRID_SIZE):
                v = self.cells[r][c].value
                if v != 0:
                    seen.setdefault(v, []).append(r)
            for v, rows in seen.items():
                if len(rows) > 1:
                    for r in rows:
                        conflicts.add((r, c))

        # Box conflicts
        for b in range(GRID_SIZE):
            seen: Dict[int, List[Tuple[int, int]]] = {}
            for cell in self.box_cells(b):
                v = cell.value
                if v != 0:
                    seen.setdefault(v, []).append((cell.row, cell.col))
            for v, coords in seen.items():
                if len(coords) > 1:
                    conflicts.update(coords)

        return sorted(list(conflicts))

    def is_valid(self) -> bool:
        """Check if board contains zero rule conflicts."""
        return len(self.find_conflicts()) == 0

    def is_complete(self) -> bool:
        """Check if all 81 cells are filled without conflicts."""
        if not self.is_valid():
            return False
        return all(not cell.is_empty for row in self.cells for cell in row)

    @property
    def clue_count(self) -> int:
        """Number of non-empty cells."""
        return sum(1 for row in self.cells for cell in row if not cell.is_empty)

    @property
    def empty_count(self) -> int:
        """Number of empty cells remaining."""
        return CANONICAL_CELL_COUNT - self.clue_count

    def to_string(self, empty_char: str = ".") -> str:
        """Serialize board to 81-character string."""
        chars = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                val = self.cells[r][c].value
                chars.append(str(val) if val != 0 else empty_char)
        return "".join(chars)

    def to_matrix(self) -> List[List[int]]:
        """Export as 9x9 matrix of integers."""
        return [[self.cells[r][c].value for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]

    def clone(self) -> "Board":
        """Produce an independent deep clone of the board."""
        new_board = Board()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                new_board.cells[r][c] = self.cells[r][c].clone()
        return new_board

    def __str__(self) -> str:
        """Formatted ASCII representation with box dividers."""
        lines = []
        for r in range(GRID_SIZE):
            if r % 3 == 0 and r != 0:
                lines.append("------+-------+------")
            row_chars = []
            for c in range(GRID_SIZE):
                if c % 3 == 0 and c != 0:
                    row_chars.append("|")
                val = self.cells[r][c].value
                row_chars.append(str(val) if val != 0 else ".")
            lines.append(" ".join(row_chars))
        return "\n".join(lines)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Board):
            return False
        return self.to_string() == other.to_string()
