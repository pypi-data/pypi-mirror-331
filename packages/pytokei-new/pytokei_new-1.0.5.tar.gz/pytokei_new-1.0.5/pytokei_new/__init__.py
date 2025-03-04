# fmt: off
from ._pytokei import (CodeStats, Config,  # type: ignore[attr-defined]
                              Language, Languages, LanguageType, Report, Sort,
                              __version__, sort_types)

# fmt: on
import sys
from pathlib import Path
from ._pytokei import *

# Install data files on first import
_DATA_DIR = Path(__file__).parent / "data"
_IGNORE_FILE = _DATA_DIR / "ignore" / ".ignorerules.txt"

if not _IGNORE_FILE.exists():
    _DATA_DIR.mkdir(exist_ok=True)
    (_DATA_DIR / "ignore").mkdir(exist_ok=True)
    with open(_IGNORE_FILE, "w") as f:  # Create default if missing
        f.write("# Default ignore patterns\n")

__all__ = [
    "CodeStats",
    "Config",
    "Language",
    "Languages",
    "LanguageType",
    "Report",
    "Sort",
    "sort_types",
    "__version__",
]
