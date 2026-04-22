#!/usr/bin/env python3

"""Send the picture to a Phomemo printer (M02 or M110/M120/M220)."""

import argparse
import os
import sys

from PIL import Image

PHOMEMO_M110_VENDOR = 0x0483
PHOMEMO_M110_PRODUCT = 0x5740
PHOMEMO_M02_PRODUCT = 0xb002


def _detect_model():
    """Detect printer model from connected USB device."""
    try:
        import usb.core
    except ModuleNotFoundError:
        return "m02"  # fallback to M02

    dev = usb.core.find(idVendor=PHOMEMO_M110_VENDOR, idProduct=PHOMEMO_M110_PRODUCT)
    if dev is not None:
        return "m110"
    return "m02"


# M02 protocol
def _m02_header():
    return b'\x1b\x40\x1b\x61\x01\x1f\x11\x02\x04'


def _m02_marker(lines, width_bytes):
    return b'\x1d\x76\x00' + width_bytes.to_bytes(2, 'little') + (lines - 1).to_bytes(2, 'little')


def _m02_footer():
    return b'\x1b\x64\x02\x1b\x64\x02\x1f\x11\x08\x1f\x11\x0e\x1f\x11\x07\x1f\x11\x09'


# M110/M120/M220 protocol
def _m110_header():
    return b'\x1b\x4e\x05\x1b\x4e\x0f\x1f\x11\x0a'


def _m110_marker(lines, width_bytes):
    return b'\x1d\x76\x00' + width_bytes.to_bytes(2, 'little') + (lines - 1).to_bytes(2, 'little')


def _m110_footer():
    return b'\x1f\xf0\x05\x00\x1f\xf0\x03\x00'


def print_line_m02(image, line, stdout):
    for x in range(int(image.width / 8)):
        byte = 0
        for bit in range(8):
            if image.getpixel((x * 8 + bit, line)) == 0:
                byte |= 1 << (7 - bit)
        if byte == 0x0a:
            byte = 0x14
        stdout.write(byte.to_bytes(1, 'little'))


def print_line_m110(image, line, stdout):
    width_bytes = int((image.width + 7) / 8)
    for x in range(width_bytes):
        byte = 0
        for bit in range(8):
            px_x = x * 8 + bit
            if px_x < image.width:
                if image.getpixel((px_x, line)) == 0:
                    byte |= 1 << (7 - bit)
            if byte == 0x0a:
                byte = 0x14
        stdout.write(byte.to_bytes(1, 'little'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-rotate", action="store_true", help="Disable auto-rotation")
    parser.add_argument("--model", choices=["m02", "m110"], help="Force printer model")
    parser.add_argument("file")
    args = parser.parse_args()

    try:
        image = Image.open(args.file)
    except Exception:
        print(f"Cannot open file {args.file}", file=sys.stderr)
        parser.print_usage()
        sys.exit(2)

    if not args.no_rotate and image.width > image.height:
        image = image.transpose(Image.ROTATE_90)

    # Detect model if not forced
    if args.model:
        model = args.model
    else:
        model = _detect_model()

    # Resize to printer width
    if model == "m02":
        image = image.resize(size=(384, int(image.height * 384 / image.width)))
        header = _m02_header()
        footer = _m02_footer()
        marker_fn = _m02_marker
        line_fn = print_line_m02
    else:
        image = image.resize(size=(384, int(image.height * 384 / image.width)))
        header = _m110_header()
        footer = _m110_footer()
        marker_fn = _m110_marker
        line_fn = print_line_m110

    image = image.convert(mode='1')

    with os.fdopen(sys.stdout.fileno(), "wb", closefd=False) as stdout:
        stdout.write(header)

        width_bytes = int((image.width + 7) / 8)
        remaining = image.height
        line = 0
        while remaining > 0:
            lines = remaining if remaining <= 256 else 256
            stdout.write(marker_fn(lines, width_bytes))
            for _ in range(lines):
                line_fn(image, line, stdout)
                line += 1
            remaining -= lines

        stdout.write(footer)


if __name__ == "__main__":
    main()
