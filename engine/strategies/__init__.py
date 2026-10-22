"""
Sudoku Quest - Strategies Package
Provides human deduction algorithms, deduction steps, and the instructional hint engine.
"""
from engine.strategies.base_strategy import BaseStrategy, DeductionStep, StrategyTier
from engine.strategies.singles import NakedSingle, HiddenSingle
from engine.strategies.intersections import PointingPairs, BoxLineReduction
from engine.strategies.subsets import NakedPair, HiddenPair
from engine.strategies.fish import XWing
from engine.strategies.wings import XYWing
from engine.strategies.uniqueness import UniqueRectangleType1
from engine.strategies.hint_engine import HintEngine

__all__ = [
    "BaseStrategy",
    "DeductionStep",
    "StrategyTier",
    "NakedSingle",
    "HiddenSingle",
    "PointingPairs",
    "BoxLineReduction",
    "NakedPair",
    "HiddenPair",
    "XWing",
    "XYWing",
    "UniqueRectangleType1",
    "HintEngine",
]
