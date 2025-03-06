"""
Command-line interface for open-windsurf.
"""

import argparse
import sys
from typing import List

from open_windsurf.core import open_windsurf, validate_paths


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Open Windsurf instances for multiple directories/paths."
    )
    parser.add_argument(
        "paths", 
        nargs="+", 
        help="Directories or files to open in separate Windsurf instances"
    )
    parser.add_argument(
        "--wait", 
        action="store_true", 
        help="Wait for the Windsurf instances to close before exiting"
    )
    parser.add_argument(
        "--user-data-dir",
        help="Specify a custom user data directory for all instances"
    )
    parser.add_argument(
        "--profile",
        help="Use a specific profile for all instances"
    )
    parser.add_argument(
        "--new-window", 
        action="store_true", 
        help="Force opening in new windows"
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Validate paths
    valid_paths = validate_paths(args.paths)
    
    if not valid_paths:
        print("Error: No valid paths provided.", file=sys.stderr)
        sys.exit(1)
    
    # Open Windsurf for each path
    processes = []
    for path in valid_paths:
        process = open_windsurf(
            path=path,
            wait=args.wait,
            user_data_dir=args.user_data_dir,
            profile=args.profile,
            new_window=args.new_window
        )
        processes.append(process)
    
    # If wait flag is set, wait for all processes to complete
    if args.wait:
        for i, process in enumerate(processes):
            print(f"Waiting for Windsurf instance {i+1}/{len(processes)} to close...")
            process.wait()
    
    print(f"Opened {len(valid_paths)} Windsurf instance(s)")


if __name__ == "__main__":
    main()
