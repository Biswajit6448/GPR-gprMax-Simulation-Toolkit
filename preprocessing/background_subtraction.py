"""
background_subtraction.py

Generic background-subtraction utility for gprMax output files.

The script subtracts the receiver data of a background-only simulation
from the corresponding target + background simulation.

Author: Biswajit Gope
"""

import argparse
from pathlib import Path

import h5py
import numpy as np


def subtract_background(target_file, background_file, output_file):
    """
    Subtract a background-only gprMax response from a target-containing
    gprMax response.

    Parameters
    ----------
    target_file : str or Path
        gprMax .out file containing target + background response.

    background_file : str or Path
        gprMax .out file containing background-only response.

    output_file : str or Path
        Path where the subtracted .out file will be saved.
    """

    target_file = Path(target_file)
    background_file = Path(background_file)
    output_file = Path(output_file)

    if not target_file.exists():
        raise FileNotFoundError(f"Target file not found: {target_file}")

    if not background_file.exists():
        raise FileNotFoundError(
            f"Background file not found: {background_file}"
        )

    print("=" * 70)
    print("gprMax Background Subtraction")
    print("=" * 70)

    print(f"Target file     : {target_file}")
    print(f"Background file : {background_file}")
    print(f"Output file     : {output_file}")

    # Copy the complete target .out structure first
    with h5py.File(target_file, "r") as target:
        with h5py.File(output_file, "w") as output:

            # Copy root attributes
            for key, value in target.attrs.items():
                output.attrs[key] = value

            # Copy all groups/datasets
            for key in target.keys():
                target.copy(key, output)

    # Perform receiver-wise subtraction
    with h5py.File(target_file, "r") as target, \
         h5py.File(background_file, "r") as background, \
         h5py.File(output_file, "r+") as output:

        if "rxs" not in target or "rxs" not in background:
            raise KeyError(
                "Receiver group 'rxs' was not found in one of the files."
            )

        target_receivers = list(target["rxs"].keys())
        background_receivers = list(background["rxs"].keys())

        if target_receivers != background_receivers:
            raise ValueError(
                "Target and background files have different receiver structures."
            )

        print(f"\nReceivers detected: {len(target_receivers)}")

        for receiver in target_receivers:

            target_components = target[f"rxs/{receiver}"]
            background_components = background[f"rxs/{receiver}"]

            for component in target_components.keys():

                if component not in background_components:
                    raise KeyError(
                        f"{component} missing from background receiver {receiver}"
                    )

                target_data = target_components[component][:]
                background_data = background_components[component][:]

                if target_data.shape != background_data.shape:
                    raise ValueError(
                        f"Shape mismatch for {receiver}/{component}: "
                        f"{target_data.shape} vs {background_data.shape}"
                    )

                subtracted_data = target_data - background_data

                output[f"rxs/{receiver}/{component}"][...] = subtracted_data

                print(
                    f"{receiver}/{component}: "
                    f"shape={subtracted_data.shape}, "
                    f"min={subtracted_data.min():.6e}, "
                    f"max={subtracted_data.max():.6e}"
                )

    print("\nBackground subtraction completed successfully.")
    print(f"Saved to: {output_file}")


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Subtract a background-only gprMax simulation from a "
            "target + background simulation."
        )
    )

    parser.add_argument(
        "target",
        help="Target + background gprMax .out file"
    )

    parser.add_argument(
        "background",
        help="Background-only gprMax .out file"
    )

    parser.add_argument(
        "output",
        help="Output .out filename"
    )

    args = parser.parse_args()

    subtract_background(
        args.target,
        args.background,
        args.output
    )


if __name__ == "__main__":
    main()
