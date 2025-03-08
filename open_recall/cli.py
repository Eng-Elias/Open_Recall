#!/usr/bin/env python
"""
Open_Recall CLI - Command Line Interface for Open_Recall

This module provides command-line functionality for the Open_Recall application.
"""
import argparse
from enum import Enum
import os
import sys
import uvicorn
import webbrowser
from open_recall.main import app as fastapi_app, load_config


class CommandEnum(Enum):
    SERVER = "server"
    DESKTOP = "desktop"
    VERSION = "version"


def get_parser():
    """Create and return the argument parser for the CLI"""
    parser = argparse.ArgumentParser(
        description="Open_Recall - Find and analyze anything you've seen on your PC"
    )
    
    # Main command groups
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Server command
    server_parser = subparsers.add_parser(CommandEnum.SERVER.value, help="Start the Open_Recall server")
    server_parser.add_argument(
        "--host", 
        default=None,
        help="Host to bind the server to (default: from config or 127.0.0.1)"
    )
    server_parser.add_argument(
        "--port", 
        type=int, 
        default=None,
        help="Port to bind the server to (default: from config or 8000)"
    )
    server_parser.add_argument(
        "--no-browser", 
        action="store_true",
        help="Don't open a browser window automatically"
    )
    
    # Desktop command
    desktop_parser = subparsers.add_parser(CommandEnum.DESKTOP.value, help="Start the Open_Recall desktop application")
    
    # Version command
    version_parser = subparsers.add_parser(CommandEnum.VERSION.value, help="Show Open_Recall version")
    
    return parser

def main():
    """Main entry point for the CLI"""
    from open_recall import __version__

    parser = get_parser()

    args = parser.parse_args()

    config = load_config()
    
    if args.command == CommandEnum.SERVER.value:
        # Get host and port from args, environment variables, or config
        host = args.host or os.environ.get('OPEN_RECALL_HOST', config['app']['host'])
        port = args.port or int(os.environ.get('OPEN_RECALL_PORT', config['app']['port']))
        
        print(f"Starting Open_Recall server on http://{host}:{port}")
        
        # Open browser if not disabled
        if not args.no_browser:
            webbrowser.open(f"http://{host}:{port}")
        
        # Start the server
        uvicorn.run(fastapi_app, host=host, port=port)
    
    elif args.command == CommandEnum.DESKTOP.value:
        # Import here to avoid circular imports
        from open_recall.app import main as desktop_main
        app = desktop_main()
        app.main_loop()
    
    elif args.command == CommandEnum.VERSION.value:
        print(f"Open_Recall version {__version__}")
    
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
