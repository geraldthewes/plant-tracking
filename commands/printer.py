"""
Printing functionality for plant labels
"""
import glob
import os
import subprocess
import sys
import time
from pathlib import Path
from .label_generator import create_label

PHOMEMO_VENDOR_IDS = (0x0493, 0x0483)


def _find_usb_phomemo_devices():
    """Find Phomemo USB printers using pyusb.

    Returns a list of dicts with keys: model, bus, address, product_id, description
    """
    try:
        import usb.core
        import usb.util
    except ModuleNotFoundError:
        print("Error: python3-usb (pyusb) is not installed.")
        print("Install with: pip install pyusb")
        return []

    devices = []
    try:
        for vendor_id in PHOMEMO_VENDOR_IDS:
            for dev in usb.core.find(find_all=True, idVendor=vendor_id):
                # Get model from product ID
                product_id = dev.idProduct
                if product_id == 0xb002:
                    model = "M02"
                elif product_id == 0x8760:
                    model = "M110"
                elif product_id == 0x5740:
                    model = "M120/M220"
                else:
                    model = f"Unknown (0x{product_id:04x})"

                # Try to get serial number (may fail due to permissions)
                serial = ""
                try:
                    serial = usb.util.get_string(dev, dev.iSerialNumber) or ""
                except Exception:
                    pass

                description = f"Phomemo {model} (bus {dev.bus:03d}, dev {dev.address:03d})"
                if serial:
                    description += f" serial={serial}"

                devices.append({
                    "model": model,
                    "bus": dev.bus,
                    "address": dev.address,
                    "product_id": product_id,
                    "serial": serial,
                    "description": description,
                })
    except Exception as e:
        print(f"Error scanning USB devices: {e}")
        print("You may need to run this command with appropriate USB permissions.")
        print("Run: newgrp lp   (or log out and back in)")

    return devices


def _select_printer(devices):
    """Present available printers to the user and return the selected one."""
    print(f"\nFound {len(devices)} Phomemo USB printer(s):\n")
    for i, dev in enumerate(devices, 1):
        print(f"  {i}. {dev['description']}")
    print()

    choice = input("Select printer (1-{}): ".format(len(devices))).strip()
    if not choice:
        if len(devices) == 1:
            return devices[0]
        return None

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(devices):
            return devices[idx]
    except ValueError:
        pass

    print("Invalid selection.")
    return None


def print_label(plant_id_or_path: str) -> bool:
    """
    Print a label for a plant

    Args:
        plant_id_or_path: Plant ID or path to label PNG file

    Returns:
        True if print job was submitted successfully, False otherwise
    """
    # Discover and select USB printer (for model info)
    devices = _find_usb_phomemo_devices()
    if not devices:
        print("Error: No Phomemo USB printer found.")
        print("Connect the printer via USB and ensure it is powered on.")
        return False

    selected = _select_printer(devices)
    if selected is None:
        print("No printer selected. Aborting.")
        return False

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

    # Use lp command with media=w40h30 (works for M120)
    # Extract model from selected description, default to M120
    model = selected.get('model', 'M120')
    # Normalize model name to queue name (e.g., "M120/M220" -> "M120")
    if '/' in model:
        model = model.split('/')[0]
    queue_name = model  # assuming queue name matches model; adjust if needed

    try:
        # Print using lp with media=w40h30 option
        result = subprocess.run(
            ['lp', '-d', queue_name, '-o', 'media=w40h30', str(label_path)],
            capture_output=True,
            text=False,
        )

        if result.returncode != 0:
            stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else "Unknown error"
            print(f"Printing failed: {stderr}")
            return False

        print(f"\u2713 Label printed via lp: {label_path}")
        return True

    except FileNotFoundError:
        print(f"Error: lp command not found. Ensure CUPS is installed.")
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