"""
Sudoku Quest - Domain Exceptions Hierarchy
Provides structured exceptions for algorithmic failures, invalid boards, and game validation errors.
"""

class SudokuQuestError(Exception):
    """Base exception for all Sudoku Quest errors."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details: dict = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

class InvalidBoardError(SudokuQuestError):
    """Raised when a Sudoku grid has invalid dimensions, illegal characters, or rule violations."""
    def __init__(self, message: str, row: int = None, col: int = None, value: int = None):
        details = {}
        if row is not None:
            details["row"] = row
        if col is not None:
            details["col"] = col
        if value is not None:
            details["value"] = value
        super().__init__(message, code="INVALID_BOARD", details=details)

class UnsolvablePuzzleError(SudokuQuestError):
    """Raised when a puzzle has no mathematically valid solution."""
    def __init__(self, message: str = "Puzzle is unsolvable and has zero valid solutions."):
        super().__init__(message, code="UNSOLVABLE_PUZZLE")

class MultipleSolutionsError(SudokuQuestError):
    """Raised when a puzzle has more than one distinct solution (violating uniqueness requirement)."""
    def __init__(self, message: str = "Puzzle is invalid because it has multiple distinct solutions.", count: int = 2):
        super().__init__(message, code="MULTIPLE_SOLUTIONS", details={"solution_count": count})

class SolverTimeoutError(SudokuQuestError):
    """Raised when algorithmic search exceeds the configured time threshold."""
    def __init__(self, timeout_seconds: float):
        super().__init__(
            f"Solver search exceeded time threshold of {timeout_seconds:.2f}s.",
            code="SOLVER_TIMEOUT",
            details={"timeout_seconds": timeout_seconds}
        )

class GameSessionError(SudokuQuestError):
    """Raised when game session state is invalid, expired, or corrupted."""
    def __init__(self, message: str, game_id: str = None):
        super().__init__(message, code="GAME_SESSION_ERROR", details={"game_id": game_id} if game_id else {})

class AuthenticationError(SudokuQuestError):
    """Raised when user credentials, session tokens, or permissions fail."""
    def __init__(self, message: str = "Authentication failed."):
        super().__init__(message, code="AUTH_FAILED")
