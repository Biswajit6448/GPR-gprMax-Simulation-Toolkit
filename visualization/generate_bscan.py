"""
generate_bscan.py

Utility for generating grayscale B-scan images from gprMax output files.

This script uses the official gprMax B-scan plotting utility and then
converts the generated image into a standardized grayscale image suitable
for visualization and machine/deep-learning dataset preparation.

Author: Biswajit Gope
"""

import argparse
import subprocess
import sys
from pathlib import Path

from PIL import Image


def generate_bscan(
    out_file,
    component="Ez",
    width=64,
    height=256,
    keep_original=True,
):
    """
    Generate and resize a B-scan image from a gprMax .out file.

    Parameters
    ----------
    out_file : str
        Path to the gprMax .out file.

    component : str
        Electromagnetic field component to plot.
        Default: Ez

    width : int
        Output image width in pixels.
        Default: 64

    height : int
        Output image height in pixels.
        Default: 256

    keep_original : bool
        If True, preserve a copy of the original generated PNG.
    """

    out_path = Path(out_file).resolve()

    if not out_path.exists():
        raise FileNotFoundError(
            f"Input file does not exist: {out_path}"
        )

    if out_path.suffix.lower() != ".out":
        raise ValueError(
            "Input file must be a gprMax .out file."
        )

    print("=" * 70)
    print("GPR B-SCAN GENERATOR")
    print("=" * 70)

    print(f"Input file : {out_path}")
    print(f"Component  : {component}")
    print(f"Output size: {width} x {height} pixels")

    print("\nGenerating B-scan using gprMax...")

    command = [
        sys.executable,
        "-m",
        "tools.plot_Bscan",
        str(out_path),
        component,
    ]

    subprocess.run(
        command,
        cwd=str(out_path.parent),
        check=True,
    )

    generated_png = out_path.with_suffix(".png")

    if not generated_png.exists():
        raise FileNotFoundError(
            "B-scan plotting completed, but the expected PNG "
            f"was not found:\n{generated_png}"
        )

    print(f"B-scan generated: {generated_png}")

    # Load the generated B-scan.
    with Image.open(generated_png) as image:
        grayscale = image.convert("L")

        if keep_original:
            original_path = out_path.with_name(
                out_path.stem + "_original.png"
            )

            grayscale.save(original_path)

            print(
                f"Original grayscale image saved: "
                f"{original_path}"
            )

        # Resize to standardized dimensions.
        resized = grayscale.resize(
            (width, height),
            Image.Resampling.LANCZOS,
        )

        resized.save(generated_png)

    print(
        f"Final grayscale B-scan saved: "
        f"{generated_png}"
    )

    print(
        f"Final dimensions: "
        f"{width} x {height} pixels"
    )

    print("=" * 70)
    print("PROCESSING COMPLETE")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate standardized grayscale B-scan images "
            "from gprMax output files."
        )
    )

    parser.add_argument(
        "out_file",
        help="Path to the gprMax .out file",
    )

    parser.add_argument(
        "--component",
        default="Ez",
        help="Field component to plot (default: Ez)",
    )

    parser.add_argument(
        "--width",
        type=int,
        default=64,
        help="Output image width (default: 64)",
    )

    parser.add_argument(
        "--height",
        type=int,
        default=256,
        help="Output image height (default: 256)",
    )

    parser.add_argument(
        "--no-original",
        action="store_true",
        help="Do not preserve the original generated image",
    )

    args = parser.parse_args()

    try:
        generate_bscan(
            out_file=args.out_file,
            component=args.component,
            width=args.width,
            height=args.height,
            keep_original=not args.no_original,
        )

    except Exception as error:
        print(f"\nERROR: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
