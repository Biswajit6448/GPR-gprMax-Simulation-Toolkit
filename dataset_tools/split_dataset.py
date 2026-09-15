"""
split_dataset.py

Train / validation / test dataset splitting utility for
Ground-Penetrating Radar (GPR) B-scan image datasets.

Features
--------
- Recursive image discovery
- Train / validation / test splitting
- Configurable split ratios
- Reproducible random splitting using a fixed seed
- Optional image-dimension filtering
- Non-destructive operation
- Safe output-directory handling
- Processing summary

Author: Biswajit Gope
"""

import argparse
import random
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


def image_has_dimensions(
    image_path,
    required_width,
    required_height,
):
    """
    Check whether an image matches the required dimensions.
    """

    try:
        with Image.open(image_path) as image:
            width, height = image.size

        return (
            width == required_width
            and height == required_height
        )

    except Exception:
        return False


def make_unique_path(destination):
    """
    Prevent accidental overwriting if duplicate filenames exist.
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


def copy_files(
    files,
    destination_directory,
):
    """
    Copy files into a dataset split directory.
    """

    destination_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    copied = 0
    renamed = 0
    failed = 0

    for source_path in files:

        destination = (
            destination_directory
            / source_path.name
        )

        final_destination = make_unique_path(
            destination
        )

        if final_destination != destination:
            renamed += 1

        try:

            shutil.copy2(
                source_path,
                final_destination,
            )

            copied += 1

        except Exception as error:

            failed += 1

            print(
                f"FAILED: {source_path}"
            )

            print(
                f"        {error}"
            )

    return copied, renamed, failed


def calculate_split_counts(
    total_images,
    train_ratio,
    val_ratio,
):
    """
    Calculate the number of images assigned to each split.
    """

    train_count = int(
        total_images * train_ratio
    )

    val_count = int(
        total_images * val_ratio
    )

    test_count = (
        total_images
        - train_count
        - val_count
    )

    return (
        train_count,
        val_count,
        test_count,
    )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Split GPR B-scan images into "
            "train, validation, and test datasets."
        )
    )

    parser.add_argument(
        "input_directory",
        help=(
            "Directory containing the source "
            "GPR B-scan images"
        ),
    )

    parser.add_argument(
        "output_directory",
        help=(
            "Directory where train, val, "
            "and test folders will be created"
        ),
    )

    parser.add_argument(
        "--train",
        type=float,
        default=0.70,
        help=(
            "Training-set ratio "
            "(default: 0.70)"
        ),
    )

    parser.add_argument(
        "--val",
        type=float,
        default=0.15,
        help=(
            "Validation-set ratio "
            "(default: 0.15)"
        ),
    )

    parser.add_argument(
        "--test",
        type=float,
        default=0.15,
        help=(
            "Test-set ratio "
            "(default: 0.15)"
        ),
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help=(
            "Random seed for reproducible "
            "dataset splitting "
            "(default: 42)"
        ),
    )

    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help=(
            "Optional required image width. "
            "Must be used with --height."
        ),
    )

    parser.add_argument(
        "--height",
        type=int,
        default=None,
        help=(
            "Optional required image height. "
            "Must be used with --width."
        ),
    )

    args = parser.parse_args()

    # ---------------------------------------------------------
    # Validate dimensions
    # ---------------------------------------------------------

    if (
        (args.width is None)
        != (args.height is None)
    ):
        parser.error(
            "--width and --height must "
            "be specified together."
        )

    # ---------------------------------------------------------
    # Validate ratios
    # ---------------------------------------------------------

    if (
        args.train < 0
        or args.val < 0
        or args.test < 0
    ):
        parser.error(
            "Split ratios cannot be negative."
        )

    ratio_sum = (
        args.train
        + args.val
        + args.test
    )

    if abs(ratio_sum - 1.0) > 1e-9:
        parser.error(
            "--train, --val, and --test "
            "must add up to 1.0."
        )

    # ---------------------------------------------------------
    # Paths
    # ---------------------------------------------------------

    input_root = Path(
        args.input_directory
    ).resolve()

    output_root = Path(
        args.output_directory
    ).resolve()

    if input_root == output_root:
        parser.error(
            "Input and output directories "
            "must be different."
        )

    try:

        output_root.relative_to(
            input_root
        )

        parser.error(
            "Output directory must not be "
            "inside the input directory."
        )

    except ValueError:
        pass

    # ---------------------------------------------------------
    # Header
    # ---------------------------------------------------------

    print("=" * 80)
    print("GPR TRAIN / VALIDATION / TEST DATASET SPLITTER")
    print("=" * 80)

    print(
        f"\nInput directory : "
        f"{input_root}"
    )

    print(
        f"Output directory: "
        f"{output_root}"
    )

    print(
        f"\nTrain ratio     : "
        f"{args.train:.2f}"
    )

    print(
        f"Validation ratio: "
        f"{args.val:.2f}"
    )

    print(
        f"Test ratio      : "
        f"{args.test:.2f}"
    )

    print(
        f"Random seed     : "
        f"{args.seed}"
    )

    if args.width is not None:

        print(
            f"Dimension filter: "
            f"{args.width} x {args.height}"
        )

    else:

        print(
            "Dimension filter: None"
        )

    # ---------------------------------------------------------
    # Find images
    # ---------------------------------------------------------

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
        f"\nImages detected : "
        f"{len(image_files)}"
    )

    if not image_files:

        print(
            "\nNo supported images were found."
        )

        return

    # ---------------------------------------------------------
    # Optional dimension filtering
    # ---------------------------------------------------------

    if args.width is not None:

        valid_images = []

        skipped = 0

        print(
            "\nChecking image dimensions..."
        )

        for image_path in image_files:

            if image_has_dimensions(
                image_path,
                args.width,
                args.height,
            ):

                valid_images.append(
                    image_path
                )

            else:

                skipped += 1

        image_files = valid_images

        print(
            f"Images matching dimensions: "
            f"{len(image_files)}"
        )

        print(
            f"Images skipped            : "
            f"{skipped}"
        )

    if not image_files:

        print(
            "\nNo images remain after filtering."
        )

        return

    # ---------------------------------------------------------
    # Shuffle reproducibly
    # ---------------------------------------------------------

    random_generator = random.Random(
        args.seed
    )

    random_generator.shuffle(
        image_files
    )

    # ---------------------------------------------------------
    # Calculate split sizes
    # ---------------------------------------------------------

    (
        train_count,
        val_count,
        test_count,
    ) = calculate_split_counts(
        len(image_files),
        args.train,
        args.val,
    )

    train_end = train_count

    val_end = (
        train_count
        + val_count
    )

    train_files = image_files[
        :train_end
    ]

    val_files = image_files[
        train_end:val_end
    ]

    test_files = image_files[
        val_end:
    ]

    # ---------------------------------------------------------
    # Display planned split
    # ---------------------------------------------------------

    print("\n" + "=" * 80)
    print("DATASET SPLIT")
    print("=" * 80)

    print(
        f"Training images   : "
        f"{len(train_files)}"
    )

    print(
        f"Validation images : "
        f"{len(val_files)}"
    )

    print(
        f"Test images       : "
        f"{len(test_files)}"
    )

    # ---------------------------------------------------------
    # Copy files
    # ---------------------------------------------------------

    print(
        "\nCopying training images..."
    )

    (
        train_copied,
        train_renamed,
        train_failed,
    ) = copy_files(
        train_files,
        output_root / "train",
    )

    print(
        "Copying validation images..."
    )

    (
        val_copied,
        val_renamed,
        val_failed,
    ) = copy_files(
        val_files,
        output_root / "val",
    )

    print(
        "Copying test images..."
    )

    (
        test_copied,
        test_renamed,
        test_failed,
    ) = copy_files(
        test_files,
        output_root / "test",
    )

    total_copied = (
        train_copied
        + val_copied
        + test_copied
    )

    total_renamed = (
        train_renamed
        + val_renamed
        + test_renamed
    )

    total_failed = (
        train_failed
        + val_failed
        + test_failed
    )

    # ---------------------------------------------------------
    # Final report
    # ---------------------------------------------------------

    print("\n" + "=" * 80)
    print("DATASET SPLITTING COMPLETE")
    print("=" * 80)

    print(
        f"Total selected images : "
        f"{len(image_files)}"
    )

    print(
        f"Training images copied: "
        f"{train_copied}"
    )

    print(
        f"Validation images copied: "
        f"{val_copied}"
    )

    print(
        f"Test images copied    : "
        f"{test_copied}"
    )

    print(
        f"Total images copied   : "
        f"{total_copied}"
    )

    print(
        f"Duplicate names safely renamed: "
        f"{total_renamed}"
    )

    print(
        f"Failed copies         : "
        f"{total_failed}"
    )

    print(
        f"Output directory      : "
        f"{output_root}"
    )

    print("=" * 80)

    print(
        "\nSource dataset was not modified."
    )

    print(
        "\nIMPORTANT RESEARCH NOTE:"
    )

    print(
        "This mode performs an image-level random split. "
        "Related images from the same simulation family "
        "should be grouped before splitting when avoiding "
        "data leakage is required."
    )


if __name__ == "__main__":
    main()
