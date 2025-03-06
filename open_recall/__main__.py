"""
Main entry point for the OpenRecall application when run as a module.
This file is required by Briefcase to execute the package.
"""

from open_recall.app import main

if __name__ == "__main__":
    app = main()
    app.main_loop()
