"""
Main entry point for the Open_Recall application when run as a module.
This allows users to run the application with 'python -m open_recall'.
"""

import os
import sys

if __name__ == "__main__":
    # Check if running in desktop app mode via environment variable
    if os.environ.get('IS_OPEN_RECALL_DESKTOP_APP'):
        from open_recall.app import main
        main()
    # Otherwise, use the CLI entry point
    else:
        from open_recall.cli import main
        sys.exit(main())
