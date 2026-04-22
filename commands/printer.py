"""
Printing functionality for plant labels
"""
import subprocess
import sys
from pathlib import Path
from .label_generator import create_label


def print_label(plant_id_or_path: str) -> bool:
    """
    Print a label for a plant

    Args:
        plant_id_or_path: Plant ID or path to label PNG file

    Returns:
        True if print job was submitted successfully, False otherwise
    """
    # Determine if input is a plant ID or file path
    input_path = Path(plant_id_or_path)

    if input_path.exists() and input_path.is_file():
        # Direct file path provided
        label_path = input_path
    else:
        # Treat as plant ID, generate label first
        plant_id = plant_id_or_path

        try:
            label_path = create_label(plant_id)
        except Exception as e:
            print(f"Error generating label for printing: {e}")
            return False

    if not label_path or not label_path.exists():
        print(f"Label file not found: {label_path}")
        return False

    # Find phomemo-filter
    phomemo_filter = Path("phomemo-tools/tools/phomemo-filter.py")

    if not phomemo_filter.exists():
        print(f"Error: phomemo-filter not found at {phomemo_filter}")
        print("Make sure phomemo-tools is available in the project")
        return False

    try:
        # Run phomemo-filter which outputs printer commands to stdout
        result = subprocess.run(
            [sys.executable, str(phomemo_filter), str(label_path)],
            capture_output=True,
            text=False,
        )

        if result.returncode != 0:
            stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else "Unknown error"
            print(f"Printing failed: {stderr}")
            return False

        print(f"\u2713 Label sent to printer: {label_path}")
        return True

    except FileNotFoundError:
        print(f"Error: phomemo-filter not found at {phomemo_filter}")
        print("Make sure phomemo-tools is available in the project")
        return False
    except Exception as e:
        print(f"Error during printing: {e}")
        return False


def main():
    """Command line interface for printing"""
    import argparse

    parser = argparse.ArgumentParser(description='Print plant label')
    parser.add_argument('plant_id_or_file', help='Plant ID or label file path')

    args = parser.parse_args()

    success = print_label(args.plant_id_or_file)
    return 0 if success else 1


if __name__ == "__main__":
    main()
