"""Entry point for `python -m src.yahtzee`."""

import sys

from src.yahtzee.cli import main

if __name__ == "__main__":
    sys.exit(main())
