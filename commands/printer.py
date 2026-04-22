"""
Printing functionality for plant labels
"""
import glob
import os
import subprocess
import sys
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
        return None

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(devices):
            return devices[idx]
    except ValueError:
        pass

    print("Invalid selection.")
    return None


def _resolve_device_path(bus, address, serial=""):
    """Find the /dev/usb/lpX device node for a USB printer.

    Matches by scanning /sys/class/usbmisc/lp* device/uevent for bus/dev numbers.
    Falls back to the single lp device if only one exists and no serial is given.
    """
    lp_devices = sorted(glob.glob("/dev/usb/lp*"))
    if not lp_devices:
        return None

    for dev_path in lp_devices:
        base = Path(dev_path).name  # lp0
        dev_link = Path(f"/sys/class/usbmisc/{base}/device")
        if not dev_link.exists():
            continue

        # dev_link points to the USB interface (e.g. 3-1:1.0)
        # parent is the USB device (e.g. 3-1) which has busnum/devnum files
        usb_device = dev_link.resolve().parent
        busnum_file = usb_device / "busnum"
        devnum_file = usb_device / "devnum"

        if not busnum_file.exists() or not devnum_file.exists():
            continue

        try:
            sys_bus = busnum_file.read_text().strip()
            sys_dev = devnum_file.read_text().strip()

            if int(bus) == int(sys_bus) and int(address) == int(sys_dev):
                return dev_path
        except Exception:
            continue

    # Fallback: if only one lp device and no serial, assume it's the printer
    if len(lp_devices) == 1 and not serial:
        return lp_devices[0]

    return None


def print_label(plant_id_or_path: str) -> bool:
    """
    Print a label for a plant

    Args:
        plant_id_or_path: Plant ID or path to label PNG file

    Returns:
        True if print job was submitted successfully, False otherwise
    """
    # Discover and select USB printer
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

        # Resolve the USB device path
        device_path = _resolve_device_path(
            selected["bus"], selected["address"], selected.get("serial", "")
        )

        if not device_path:
            print(f"Error: Could not find USB device for {selected['description']}")
            print("Make sure the printer is connected and you have write permissions.")
            print("Run: newgrp lp   (or log out and back in)")
            return False

        # Verify device is writable
        if not os.path.exists(device_path) or not os.access(device_path, os.W_OK):
            print(f"Error: Cannot write to {device_path}")
            print("Run: newgrp lp   (or log out and back in)")
            return False

        # Write ESC/POS commands to the USB printer device
        print(f"Sending label to {device_path} ({selected['model']})...")
        with open(device_path, "wb") as device:
            # Clear any buffered data from previous jobs
            try:
                os.fsync(device.fileno())
            except Exception:
                pass
            device.write(result.stdout)
            device.flush()

        print(f"\u2713 Label printed: {label_path}")
        return True

    except FileNotFoundError:
        print(f"Error: phomemo-filter not found at {phomemo_filter}")
        print("Make sure phomemo-tools is available in the project")
        return False
    except PermissionError as e:
        print(f"Error: Permission denied writing to USB device: {e}")
        print("Run: newgrp lp   (or log out and back in)")
        return False
    except OSError as e:
        print(f"Error writing to USB device: {e}")
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
