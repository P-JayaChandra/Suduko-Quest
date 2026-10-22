"""
Sudoku Quest - Structured Logging Configuration
Provides unified logger instances with standardized formatters and rotation.
"""
import logging
import sys
from pathlib import Path

def get_logger(name: str = "sudoku_quest") -> logging.Logger:
    """Obtain configured logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger
