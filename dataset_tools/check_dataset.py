"""
check_dataset.py

Dataset integrity checker for GPR B-scan image datasets.

The utility recursively scans a dataset directory and reports:

- Total image files
- Valid and corrupted images
- Image dimensions
- Images with unexpected dimensions
- Exact duplicate images
- Duplicate filenames in different directories
- Missing numbers in numerically named image sequences

The script is read-only and does not modify or delete dataset files.

Author: Biswajit Gope
"""

import argparse
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image


SUPPORTED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tif",
    ".tiff",
}


def find_images(root_directory):
    """Recursively find supported image files."""

    root = Path(root_directory)

    if not root.exists():
        raise FileNotFoundError(
            f"Directory does not exist: {root}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Path is not a directory: {root}"
        )

    images = [
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    return sorted(images)


def calculate_hash(file_path):
    """Calculate SHA-256 hash of a file."""

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def inspect_image(image_path):
    """
    Verify that an image is readable and return its dimensions.
    """

    # First verify file integrity.
    with Image.open(image_path) as image:
        image.verify()

    # Reopen because verify() invalidates the image object.
    with Image.open(image_path) as image:
        width, height = image.size

    return width, height


def find_missing_numbers(image_files):
    """
    Find missing values among purely numeric image filenames.

    Example:
    1.png, 2.png, 4.png -> missing 3
    """

    numbers = []

    for image_path in image_files:
        if image_path.stem.isdigit():
            numbers.append(int(image_path.stem))

    if not numbers:
        return [], None, None

    unique_numbers = sorted(set(numbers))

    minimum = unique_numbers[0]
    maximum = unique_numbers[-1]

    existing = set(unique_numbers)

    missing = [
        number
        for number in range(minimum, maximum + 1)
        if number not in existing
    ]

    return missing, minimum, maximum


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Check image integrity, dimensions, duplicates, "
            "and numeric filename sequences in GPR datasets."
        )
    )

    parser.add_argument(
        "directory",
        help="Dataset directory to scan recursively",
    )

    parser.add_argument(
        "--width",
        type=int,
        default=64,
        help="Expected image width (default: 64)",
    )

    parser.add_argument(
        "--height",
        type=int,
        default=256,
        help="Expected image height (default: 256)",
    )

    parser.add_argument(
        "--skip-duplicates",
        action="store_true",
        help="Skip exact duplicate-file detection",
    )

    parser.add_argument(
        "--skip-missing",
        action="store_true",
        help="Skip numeric filename sequence checking",
    )

    args = parser.parse_args()

    print("=" * 80)
    print("GPR DATASET INTEGRITY CHECK")
    print("=" * 80)

    print(f"\nDataset directory : {args.directory}")
    print(
        f"Expected dimensions: "
        f"{args.width} x {args.height}"
    )

    try:
        image_files = find_images(args.directory)

    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"\nERROR: {error}")
        return

    print(f"Images detected   : {len(image_files)}")

    if not image_files:
        print("\nNo supported image files were found.")
        return

    valid_images = []
    corrupted_images = []
    unexpected_dimensions = []
    dimension_counter = Counter()

    filename_locations = defaultdict(list)

    print("\n" + "=" * 80)
    print("CHECKING IMAGE INTEGRITY AND DIMENSIONS")
    print("=" * 80)

    for index, image_path in enumerate(image_files, start=1):

        print(
            f"\rChecking images: "
            f"{index}/{len(image_files)}",
            end="",
            flush=True,
        )

        filename_locations[image_path.name].append(
            image_path
        )

        try:
            width, height = inspect_image(image_path)

            valid_images.append(image_path)

            dimension_counter[
                (width, height)
            ] += 1

            if (
                width != args.width
                or height != args.height
            ):
                unexpected_dimensions.append(
                    (
                        image_path,
                        width,
                        height,
                    )
                )

        except Exception as error:
            corrupted_images.append(
                (
                    image_path,
                    str(error),
                )
            )

    print()

    # ---------------------------------------------------------
    # Exact duplicate detection
    # ---------------------------------------------------------

    duplicate_groups = []

    if not args.skip_duplicates:

        print("\n" + "=" * 80)
        print("CHECKING FOR EXACT DUPLICATE FILES")
        print("=" * 80)

        hash_groups = defaultdict(list)

        for index, image_path in enumerate(
            valid_images,
            start=1,
        ):

            print(
                f"\rCalculating hashes: "
                f"{index}/{len(valid_images)}",
                end="",
                flush=True,
            )

            try:
                file_hash = calculate_hash(
                    image_path
                )

                hash_groups[file_hash].append(
                    image_path
                )

            except Exception as error:
                print(
                    f"\nCould not hash "
                    f"{image_path}: {error}"
                )

        print()

        duplicate_groups = [
            paths
            for paths in hash_groups.values()
            if len(paths) > 1
        ]

    # ---------------------------------------------------------
    # Duplicate filename detection
    # ---------------------------------------------------------

    duplicate_filenames = {
        filename: paths
        for filename, paths
        in filename_locations.items()
        if len(paths) > 1
    }

    # ---------------------------------------------------------
    # Missing numeric filenames
    # ---------------------------------------------------------

    missing_numbers = []
    numeric_min = None
    numeric_max = None

    if not args.skip_missing:
        (
            missing_numbers,
            numeric_min,
            numeric_max,
        ) = find_missing_numbers(
            image_files
        )

    # ---------------------------------------------------------
    # Results
    # ---------------------------------------------------------

    print("\n" + "=" * 80)
    print("IMAGE DIMENSIONS")
    print("=" * 80)

    for dimensions, count in sorted(
        dimension_counter.items()
    ):
        width, height = dimensions

        print(
            f"{width} x {height}: "
            f"{count} image(s)"
        )

    print("\n" + "=" * 80)
    print("UNEXPECTED DIMENSIONS")
    print("=" * 80)

    if unexpected_dimensions:

        for (
            image_path,
            width,
            height,
        ) in unexpected_dimensions:

            print(
                f"{image_path} "
                f"-> {width} x {height}"
            )

    else:
        print(
            "All valid images match the "
            "expected dimensions."
        )

    print("\n" + "=" * 80)
    print("CORRUPTED / UNREADABLE IMAGES")
    print("=" * 80)

    if corrupted_images:

        for image_path, error in corrupted_images:
            print(f"{image_path}")
            print(f"    Error: {error}")

    else:
        print(
            "No corrupted or unreadable "
            "images detected."
        )

    print("\n" + "=" * 80)
    print("EXACT DUPLICATES")
    print("=" * 80)

    if args.skip_duplicates:

        print("Duplicate detection was skipped.")

    elif duplicate_groups:

        for group_number, paths in enumerate(
            duplicate_groups,
            start=1,
        ):

            print(
                f"\nDuplicate group "
                f"{group_number}:"
            )

            for path in paths:
                print(f"    {path}")

    else:
        print("No exact duplicate images detected.")

    print("\n" + "=" * 80)
    print("DUPLICATE FILENAMES")
    print("=" * 80)

    if duplicate_filenames:

        for filename, paths in sorted(
            duplicate_filenames.items()
        ):

            print(f"\n{filename}")

            for path in paths:
                print(f"    {path}")

    else:
        print(
            "No duplicate filenames "
            "detected across directories."
        )

    print("\n" + "=" * 80)
    print("NUMERIC FILENAME SEQUENCE")
    print("=" * 80)

    if args.skip_missing:

        print(
            "Numeric filename sequence "
            "checking was skipped."
        )

    elif numeric_min is None:

        print(
            "No purely numeric image "
            "filenames were detected."
        )

    else:

        print(
            f"Detected numeric range: "
            f"{numeric_min} to {numeric_max}"
        )

        if missing_numbers:

            print(
                f"Missing numbers "
                f"({len(missing_numbers)}):"
            )

            print(
                ", ".join(
                    str(number)
                    for number
                    in missing_numbers
                )
            )

        else:
            print(
                "No missing numbers detected "
                "within the numeric range."
            )

    # ---------------------------------------------------------
    # Final summary
    # ---------------------------------------------------------

    print("\n" + "=" * 80)
    print("FINAL REPORT")
    print("=" * 80)

    print(
        f"Total image files          : "
        f"{len(image_files)}"
    )

    print(
        f"Valid readable images      : "
        f"{len(valid_images)}"
    )

    print(
        f"Corrupted/unreadable       : "
        f"{len(corrupted_images)}"
    )

    print(
        f"Unexpected dimensions      : "
        f"{len(unexpected_dimensions)}"
    )

    if args.skip_duplicates:
        print(
            "Exact duplicate groups      : "
            "Not checked"
        )
    else:
        print(
            f"Exact duplicate groups      : "
            f"{len(duplicate_groups)}"
        )

    print(
        f"Duplicate filename groups  : "
        f"{len(duplicate_filenames)}"
    )

    if args.skip_missing:
        print(
            "Missing numeric filenames   : "
            "Not checked"
        )
    else:
        print(
            f"Missing numeric filenames   : "
            f"{len(missing_numbers)}"
        )

    print("=" * 80)

    print(
        "\nDataset check completed. "
        "No files were modified or deleted."
    )


if __name__ == "__main__":
    main()
