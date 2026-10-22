"""
Sudoku Quest - Application Configuration
Centralized configuration management with environment variable overrides and sensible defaults.
"""
import os
from pathlib import Path
from dataclasses import dataclass, field

BASE_DIR = Path(__file__).resolve().parent.parent

@dataclass
class Config:
    """Core application configuration settings."""
    ENV: str = field(default_factory=lambda: os.environ.get("FLASK_ENV", "development"))
    DEBUG: bool = field(default_factory=lambda: os.environ.get("FLASK_DEBUG", "1") == "1")
    TESTING: bool = False
    
    SECRET_KEY: str = field(
        default_factory=lambda: os.environ.get("SUDOKU_SECRET_KEY", "sudoku-quest-prod-secret-98231")
    )
    
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = field(default_factory=lambda: BASE_DIR / "data")
    DB_PATH: Path = field(default_factory=lambda: BASE_DIR / "data" / "sudoku_quest.db")
    DATASET_PATH: Path = field(default_factory=lambda: BASE_DIR / "data" / "sudoku_records.jsonl")
    
    # Game rules
    MAX_MISTAKES: int = 3
    DEFAULT_HINTS: int = 3
    SOLVER_TIMEOUT_SECONDS: float = 5.0
    
    # Session & Security
    TOKEN_EXPIRATION_DAYS: int = 30
    CORS_ALLOWED_ORIGINS: str = "*"
    
    # Database tuning
    DB_TIMEOUT: float = 20.0
    DB_WAL_MODE: bool = True

def get_config() -> Config:
    """Retrieve active configuration singleton."""
    return Config()
