"""
Batch B-scan Generator for gprMax Output Files

Recursively searches a directory for gprMax .out files and generates
B-scan images using the official gprMax tools.plot_Bscan utility.

Example
-------
python visualization/batch_generate_bscans.py "H:\\GPR_DATA" Ez
"""

import argparse
import subprocess
import sys
from pathlib import Path


def find_out_files(root_directory):
    """
    Recursively find all .out files inside a directory.
    """
    root = Path(root_directory)

    if not root.exists():
        raise FileNotFoundError(
            f"Directory does not exist: {root_directory}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Path is not a directory: {root_directory}"
        )

    return sorted(root.rglob("*.out"))


def generate_bscan(out_file, component="Ez"):
    """
    Generate a B-scan using the official gprMax plot_Bscan utility.
    """

    command = [
        sys.executable,
        "-m",
        "tools.plot_Bscan",
        str(out_file),
        component,
    ]

    subprocess.run(command, check=True)


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Recursively generate B-scan images from "
            "gprMax .out files."
        )
    )

    parser.add_argument(
        "directory",
        help="Root directory containing gprMax .out files",
    )

    parser.add_argument(
        "component",
        nargs="?",
        default="Ez",
        help="Field component to plot (default: Ez)",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("gprMax Batch B-scan Generator")
    print("=" * 70)

    try:
        out_files = find_out_files(args.directory)

    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"\nERROR: {error}")
        sys.exit(1)

    if not out_files:
        print("\nNo .out files were found.")
        sys.exit(0)

    print(f"\nDirectory : {args.directory}")
    print(f"Component : {args.component}")
    print(f"Files     : {len(out_files)}")
    print()

    successful = 0
    failed = 0

    for index, out_file in enumerate(out_files, start=1):

        print(
            f"[{index}/{len(out_files)}] "
            f"Processing: {out_file}"
        )

        try:

            generate_bscan(
                out_file,
                args.component,
            )

            successful += 1

            print("    SUCCESS")

        except subprocess.CalledProcessError as error:

            failed += 1

            print(
                f"    FAILED "
                f"(return code: {error.returncode})"
            )

        except Exception as error:

            failed += 1

            print(f"    FAILED: {error}")

    print()
    print("=" * 70)
    print("Batch processing completed")
    print("=" * 70)

    print(f"Total files : {len(out_files)}")
    print(f"Successful  : {successful}")
    print(f"Failed      : {failed}")


if __name__ == "__main__":
    main()
