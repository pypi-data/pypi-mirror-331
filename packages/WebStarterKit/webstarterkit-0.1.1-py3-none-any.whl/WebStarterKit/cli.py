import argparse
import os
import sys
from .create_project import create_project_structure

def main():
    parser = argparse.ArgumentParser(
        description="Generate a basic web project structure (HTML, CSS, JS)."
    )
    parser.add_argument("project_name", help="Name of the project")
    parser.add_argument(
        "--path",
        help="Base path for the project (default: current directory)",
        default=os.getcwd(),
    )

    args = parser.parse_args()

    # Validate project name
    if not args.project_name.strip():
        print("Error: Project name cannot be empty.", file=sys.stderr)
        sys.exit(1)

    # Validate base path
    if not os.path.isdir(args.path):
        print(f"Error: The specified path '{args.path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Execute project creation
    try:
        create_project_structure(args.project_name, args.path)
        print(f"Project '{args.project_name}' successfully created at '{args.path}'.")
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
