"""
Sudoku Quest - Base Strategy Architecture
Defines the standard interface for human logical deduction algorithms, deduction step metadata,
visual highlight coordinates, and explanation generators.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Dict, Any
from enum import IntEnum
from dataclasses import dataclass, field
from engine.models.candidate_grid import CandidateGrid

class StrategyTier(IntEnum):
    """Categorization of human solving strategies by skill level."""
    BEGINNER = 1       # Naked Singles, Hidden Singles
    INTERMEDIATE = 2   # Locked Candidates, Pointing, Box-Line
    ADVANCED = 3       # Naked/Hidden Subsets, X-Wing
    MASTER = 4         # Swordfish, Jellyfish, Wings, Simple Coloring
    EXTREME = 5        # Unique Rectangles, 3D Medusa, Alternating Chains

@dataclass
class DeductionStep:
    """Represents a discrete logical deduction made by a strategy."""
    strategy_name: str
    tier: StrategyTier
    difficulty_rating: float
    action: str  # 'place' or 'eliminate'
    explanation: str
    digit: Optional[int] = None
    target_cell: Optional[Tuple[int, int]] = None  # (row, col) for placement
    eliminations: List[Tuple[int, int, int]] = field(default_factory=list)  # (row, col, digit)
    cause_cells: List[Tuple[int, int]] = field(default_factory=list)  # Primary pattern cells
    secondary_cells: List[Tuple[int, int]] = field(default_factory=list)  # Context/lock cells

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy": self.strategy_name,
            "tier": self.tier.name,
            "tier_level": int(self.tier),
            "difficulty_rating": self.difficulty_rating,
            "action": self.action,
            "explanation": self.explanation,
            "digit": self.digit,
            "target_cell": {"row": self.target_cell[0], "col": self.target_cell[1]} if self.target_cell else None,
            "eliminations": [
                {"row": r, "col": c, "digit": d} for (r, c, d) in self.eliminations
            ],
            "cause_cells": [
                {"row": r, "col": c} for (r, c) in self.cause_cells
            ],
            "secondary_cells": [
                {"row": r, "col": c} for (r, c) in self.secondary_cells
            ],
        }

class BaseStrategy(ABC):
    """Abstract base class for all logical deduction strategies."""

    def __init__(self, name: str, tier: StrategyTier, difficulty_rating: float):
        self.name = name
        self.tier = tier
        self.difficulty_rating = difficulty_rating

    @abstractmethod
    def find_step(self, grid: CandidateGrid) -> Optional[DeductionStep]:
        """Search grid and return first applicable deduction step, or None."""
        pass

    @abstractmethod
    def find_all_steps(self, grid: CandidateGrid) -> List[DeductionStep]:
        """Search grid and return all currently applicable deductions for this strategy."""
        pass
