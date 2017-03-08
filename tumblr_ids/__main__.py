"""main file for module."""
from .general_run import main
import sys

if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
