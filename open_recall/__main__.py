"""
Main entry point for the Open_Recall application when run as a module.
This allows users to run the application with 'python -m open_recall'.
"""

import sys
from open_recall.cli import main

if __name__ == "__main__":
    sys.exit(main())
