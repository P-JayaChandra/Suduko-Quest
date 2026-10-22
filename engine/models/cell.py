"""
Sudoku Quest - Cell Model
Represents an individual grid cell with coordinate tracking, candidates, notes, and given status.
"""
from typing import Set, Optional
from dataclasses import dataclass, field

@dataclass
class Cell:
    """Represents a single cell within a Sudoku grid."""
    row: int
    col: int
    value: int = 0
    is_given: bool = False
    candidates: Set[int] = field(default_factory=lambda: set(range(1, 10)))
    notes: Set[int] = field(default_factory=set)
    is_error: bool = False

    @property
    def is_empty(self) -> bool:
        """True if the cell does not currently hold a placed digit."""
        return self.value == 0

    @property
    def box(self) -> int:
        """Return 0-indexed 3x3 block index (0 to 8)."""
        return (self.row // 3) * 3 + (self.col // 3)

    @property
    def index(self) -> int:
        """Return 0-indexed linear array index (0 to 80)."""
        return self.row * 9 + self.col

    def set_value(self, val: int, given: bool = False) -> None:
        """Assign digit value and adjust state."""
        self.value = val
        self.is_given = given
        if val != 0:
            self.candidates.clear()
            self.notes.clear()
        else:
            self.candidates = set(range(1, 10))
        self.is_error = False

    def clear(self) -> None:
        """Reset cell to empty state (unless locked as given)."""
        if not self.is_given:
            self.value = 0
            self.is_error = False
            self.candidates = set(range(1, 10))

    def toggle_note(self, val: int) -> bool:
        """Toggle a pencil mark note digit. Returns True if added, False if removed."""
        if self.is_empty:
            if val in self.notes:
                self.notes.remove(val)
                return False
            else:
                self.notes.add(val)
                return True
        return False

    def remove_candidate(self, val: int) -> bool:
        """Remove a candidate deduction digit. Returns True if removed."""
        if val in self.candidates:
            self.candidates.remove(val)
            return True
        return False

    def clone(self) -> "Cell":
        """Produce an independent copy of this cell."""
        c = Cell(
            row=self.row,
            col=self.col,
            value=self.value,
            is_given=self.is_given,
            candidates=set(self.candidates),
            notes=set(self.notes),
            is_error=self.is_error
        )
        return c

    def __hash__(self) -> int:
        return hash((self.row, self.col))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cell):
            return False
        return self.row == other.row and self.col == other.col

    def __repr__(self) -> str:
        return f"Cell(r={self.row}, c={self.col}, val={self.value}{'*' if self.is_given else ''})"

    @classmethod
    def validate_bounds(cls, row: int, col: int) -> bool:
        """Validate row and column are strictly between 0 and 8 inclusive."""
        if not (0 <= row <= 8 and 0 <= col <= 8):
            raise ValueError(f"Cell coordinates out of bounds: ({row}, {col})")
        return True
