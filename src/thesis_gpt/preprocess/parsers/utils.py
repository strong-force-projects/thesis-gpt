import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def validate_latex_path(path_str: str) -> Path:
    """
    Validates the provided path for LaTeX processing.

    Args:
        path_str (str): Path to a LaTeX file or directory.

    Returns:
        Path: A validated Path object.

    Raises:
        SystemExit: If the path is invalid or doesn't contain LaTeX files.
    """
    path = Path(path_str)

    if not path.exists():
        logger.error(f"The provided path does not exist: {path}")
        sys.exit(1)

    if path.is_dir():
        if not any(path.glob("*.tex")):
            logger.error(f"No LaTeX files found in the provided directory: {path}")
            sys.exit(1)
    elif path.is_file():
        if path.suffix != ".tex":
            logger.error(f"The provided file is not a .tex file: {path}")
            sys.exit(1)
    else:
        logger.error(f"Invalid path: {path}")
        sys.exit(1)

    return path
