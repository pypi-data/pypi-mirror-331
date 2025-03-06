"""
Main CLI implementation for the Fabulous CLI.
"""
import sys
import argparse
from . import __version__


def main():
    """
    Entry point for the Fabulous CLI.
    """
    parser = argparse.ArgumentParser(
        description="Fabulous CLI - A basic Python CLI example"
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("message", nargs="?", default="Hello, Fabulous World!", 
                      help="Message to display")

    args = parser.parse_args()
    
    print(f"✨ Fabulous says: {args.message} ✨")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())