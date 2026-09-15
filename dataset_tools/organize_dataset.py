"""
organize_dataset.py

Dataset organization utility for Ground-Penetrating Radar (GPR)
B-scan image datasets.

The utility recursively searches an input directory for supported
image files and copies selected images into a clean output dataset.

Features
--------
- Recursive image discovery
- Optional image-dimension filtering
- Optional preservation of source directory structure
- Flat-output mode
- Safe handling of duplicate filenames
- Non-destructive operation: source files are never modified or deleted
- Processing summary

Author: Biswajit Gope
"""

import argparse
import shutil
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
    """
    Recursively find supported image files.
    """

    root = Path(root_directory)

    if not root.exists():
        raise FileNotFoundError(
            f"Input directory does not exist: {root}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Input path is not a directory: {root}"
        )

    images = [
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    return sorted(images)


def get_image_dimensions(image_path):
    """
    Return image width and height.
    """

    with Image.open(image_path) as image:
        return image.size


def make_unique_path(destination):
    """
    Generate a unique destination path if a file with the
    same name already exists.

    Example
    -------
    1.png
    1_2.png
    1_3.png
    """

    if not destination.exists():
        return destination

    parent = destination.parent
    stem = destination.stem
    suffix = destination.suffix

    counter = 2

    while True:

        candidate = parent / (
            f"{stem}_{counter}{suffix}"
        )

        if not candidate.exists():
            return candidate

        counter += 1


def copy_image(
    source,
    destination,
):
    """
    Copy an image while preserving file metadata.
    """

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = make_unique_path(
        destination
    )

    shutil.copy2(
        source,
        destination,
    )

    return destination


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Organize GPR B-scan image datasets "
            "without modifying the source dataset."
        )
    )

    parser.add_argument(
        "input_directory",
        help="Directory containing source images",
    )

    parser.add_argument(
        "output_directory",
        help="Directory where organized images will be copied",
    )

    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help=(
            "Optional required image width. "
            "Must be used together with --height."
        ),
    )

    parser.add_argument(
        "--height",
        type=int,
        default=None,
        help=(
            "Optional required image height. "
            "Must be used together with --width."
        ),
    )

    parser.add_argument(
        "--flat",
        action="store_true",
        help=(
            "Copy all selected images directly into "
            "the output directory instead of preserving "
            "the source directory structure."
        ),
    )

    args = parser.parse_args()

    if (
        (args.width is None)
        != (args.height is None)
    ):
        parser.error(
            "--width and --height must be specified together."
        )

    input_root = Path(
        args.input_directory
    ).resolve()

    output_root = Path(
        args.output_directory
    ).resolve()

    if input_root == output_root:
        parser.error(
            "Input and output directories must be different."
        )

    # Prevent placing the output directory inside the input
    # directory because recursive scanning could later include
    # previously copied files.
    try:
        output_root.relative_to(input_root)

        parser.error(
            "Output directory must not be inside "
            "the input directory."
        )

    except ValueError:
        pass

    print("=" * 80)
    print("GPR DATASET ORGANIZER")
    print("=" * 80)

    print(
        f"\nInput directory : "
        f"{input_root}"
    )

    print(
        f"Output directory: "
        f"{output_root}"
    )

    if (
        args.width is not None
        and args.height is not None
    ):
        print(
            f"Dimension filter: "
            f"{args.width} x {args.height}"
        )
    else:
        print(
            "Dimension filter: None"
        )

    if args.flat:
        print(
            "Organization mode: Flat output"
        )
    else:
        print(
            "Organization mode: "
            "Preserve directory structure"
        )

    try:

        image_files = find_images(
            input_root
        )

    except (
        FileNotFoundError,
        NotADirectoryError,
    ) as error:

        print(
            f"\nERROR: {error}"
        )

        return

    print(
        f"Images detected : "
        f"{len(image_files)}"
    )

    if not image_files:

        print(
            "\nNo supported image files were found."
        )

        return

    copied = 0
    skipped_dimensions = 0
    unreadable = 0
    renamed_duplicates = 0

    print("\n" + "=" * 80)
    print("ORGANIZING DATASET")
    print("=" * 80)

    for index, source_path in enumerate(
        image_files,
        start=1,
    ):

        relative_path = source_path.relative_to(
            input_root
        )

        print(
            f"[{index}/{len(image_files)}] "
            f"{relative_path}"
        )

        try:

            width, height = get_image_dimensions(
                source_path
            )

        except Exception as error:

            unreadable += 1

            print(
                f"    SKIPPED - unreadable image: "
                f"{error}"
            )

            continue

        if args.width is not None:

            if (
                width != args.width
                or height != args.height
            ):

                skipped_dimensions += 1

                print(
                    f"    SKIPPED - dimensions "
                    f"{width} x {height}"
                )

                continue

        if args.flat:

            destination = (
                output_root
                / source_path.name
            )

        else:

            destination = (
                output_root
                / relative_path
            )

        original_destination = destination

        try:

            final_destination = copy_image(
                source_path,
                destination,
            )

            copied += 1

            if (
                final_destination
                != original_destination
            ):

                renamed_duplicates += 1

                print(
                    "    COPIED - duplicate filename "
                    f"renamed to "
                    f"{final_destination.name}"
                )

            else:

                print(
                    "    COPIED"
                )

        except Exception as error:

            unreadable += 1

            print(
                f"    FAILED: {error}"
            )

    print("\n" + "=" * 80)
    print("DATASET ORGANIZATION COMPLETE")
    print("=" * 80)

    print(
        f"Images detected             : "
        f"{len(image_files)}"
    )

    print(
        f"Images copied               : "
        f"{copied}"
    )

    print(
        f"Skipped by dimension filter : "
        f"{skipped_dimensions}"
    )

    print(
        f"Unreadable / failed         : "
        f"{unreadable}"
    )

    print(
        f"Duplicate filenames renamed : "
        f"{renamed_duplicates}"
    )

    print(
        f"Output directory            : "
        f"{output_root}"
    )

    print("=" * 80)

    print(
        "\nSource dataset was not modified."
    )


if __name__ == "__main__":
    main()
