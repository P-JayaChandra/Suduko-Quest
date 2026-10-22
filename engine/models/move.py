"""
Sudoku Quest - Move and History Model
Encapsulates individual player actions, undo/redo state transitions, and move validation records.
"""
from dataclasses import dataclass, field
from typing import Set, Optional
import datetime
from core.constants import MoveType

@dataclass
class Move:
    """Represents a discrete board modification step."""
    row: int
    col: int
    old_value: int
    new_value: int
    move_type: MoveType = MoveType.DIGIT
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    old_notes: Set[int] = field(default_factory=set)
    new_notes: Set[int] = field(default_factory=set)
    is_correct: Optional[bool] = None

    @property
    def cell_index(self) -> int:
        return self.row * 9 + self.col

    def to_dict(self) -> dict:
        return {
            "row": self.row,
            "col": self.col,
            "cell_index": self.cell_index,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "move_type": self.move_type.value if hasattr(self.move_type, "value") else str(self.move_type),
            "timestamp": self.timestamp,
            "old_notes": list(self.old_notes),
            "new_notes": list(self.new_notes),
            "is_correct": self.is_correct,
        }
