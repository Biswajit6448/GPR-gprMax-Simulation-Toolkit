"""
normalize_bscans.py

B-scan image normalization utility for Ground-Penetrating Radar datasets.

The utility recursively processes GPR B-scan images and creates normalized
grayscale copies suitable for machine/deep-learning dataset preparation.

The original dataset is never modified.

Author: Biswajit Gope
"""

import argparse
from pathlib import Path

import numpy as np
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
            f"Input directory does not exist: {root}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Input path is not a directory: {root}"
        )

    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def minmax_normalize(image_array):
    """
    Normalize image intensities using min-max normalization.

    The image is first represented in floating point and normalized
    to the range [0, 1]. It is then converted to an 8-bit image
    in the range [0, 255].
    """

    array = image_array.astype(np.float32)

    minimum = np.min(array)
    maximum = np.max(array)

    if maximum > minimum:
        normalized = (
            (array - minimum)
            / (maximum - minimum)
        )
    else:
        normalized = np.zeros_like(
            array,
            dtype=np.float32,
        )

    normalized = np.clip(
        normalized * 255.0,
        0,
        255,
    )

    return normalized.astype(np.uint8)


def process_image(
    input_path,
    output_path,
    width=None,
    height=None,
):
    """
    Convert an image to grayscale, optionally resize it,
    normalize its intensity, and save the result.
    """

    with Image.open(input_path) as image:

        grayscale = image.convert("L")

        if width is not None and height is not None:
            grayscale = grayscale.resize(
                (width, height),
                Image.Resampling.LANCZOS,
            )

        image_array = np.asarray(grayscale)

    normalized_array = minmax_normalize(
        image_array
    )

    normalized_image = Image.fromarray(
        normalized_array,
        mode="L",
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    normalized_image.save(output_path)


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Normalize GPR B-scan images while preserving "
            "the original dataset."
        )
    )

    parser.add_argument(
        "input_directory",
        help="Directory containing input B-scan images",
    )

    parser.add_argument(
        "output_directory",
        help="Directory where normalized images will be saved",
    )

    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help=(
            "Optional output image width. "
            "Must be used together with --height."
        ),
    )

    parser.add_argument(
        "--height",
        type=int,
        default=None,
        help=(
            "Optional output image height. "
            "Must be used together with --width."
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
            "Input and output directories must be different "
            "to protect the original dataset."
        )

    print("=" * 80)
    print("GPR B-SCAN NORMALIZATION")
    print("=" * 80)

    print(f"\nInput directory : {input_root}")
    print(f"Output directory: {output_root}")

    if args.width is not None:
        print(
            f"Output dimensions: "
            f"{args.width} x {args.height}"
        )
    else:
        print(
            "Output dimensions: "
            "Preserve original image dimensions"
        )

    try:
        image_files = find_images(
            input_root
        )

    except (
        FileNotFoundError,
        NotADirectoryError,
    ) as error:
        print(f"\nERROR: {error}")
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

    successful = 0
    failed = 0

    print("\n" + "=" * 80)
    print("NORMALIZING B-SCAN IMAGES")
    print("=" * 80)

    for index, input_path in enumerate(
        image_files,
        start=1,
    ):

        relative_path = input_path.relative_to(
            input_root
        )

        output_path = (
            output_root
            / relative_path
        )

        print(
            f"[{index}/{len(image_files)}] "
            f"{relative_path}"
        )

        try:

            process_image(
                input_path=input_path,
                output_path=output_path,
                width=args.width,
                height=args.height,
            )

            successful += 1

            print("    SUCCESS")

        except Exception as error:

            failed += 1

            print(
                f"    FAILED: {error}"
            )

    print("\n" + "=" * 80)
    print("NORMALIZATION COMPLETE")
    print("=" * 80)

    print(
        f"Total images : "
        f"{len(image_files)}"
    )

    print(
        f"Successful   : "
        f"{successful}"
    )

    print(
        f"Failed       : "
        f"{failed}"
    )

    print(
        f"Output folder: "
        f"{output_root}"
    )

    print("=" * 80)

    print(
        "\nOriginal dataset was not modified."
    )


if __name__ == "__main__":
    main()
