#!/usr/bin/env python3
"""Entry program for the 23 November 2026 world-news image.

Takes the pre-drawn entry.png built by draw_image.py and places an
exact copy at $MAKEFUN_OUTPUT_DIR/entry.png. Before copying it checks
the file is a real PNG inside the competition limits (at most 1 MiB,
at most 1024 on a side), then confirms the copy byte for byte so two
runs always produce the same output. Standard library only; no network.
"""

import hashlib
import os
import shutil
import struct
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(ROOT, "entry.png")

LIMIT_BYTES = 1_048_576
LIMIT_SIDE = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def read_png_dimensions(path):
    """Return (width, height) from the IHDR chunk, or fail loudly."""
    with open(path, "rb") as handle:
        prefix = handle.read(33)
    if prefix[:8] != PNG_MAGIC:
        raise ValueError("not a PNG file: bad magic bytes")
    if prefix[12:16] != b"IHDR":
        raise ValueError("not a PNG file: IHDR chunk missing")
    return struct.unpack(">II", prefix[16:24])


def digest(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def run():
    destination_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not destination_dir:
        print("error: MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 1
    if not os.path.exists(SOURCE):
        print("error: entry.png is missing, run draw_image.py first",
              file=sys.stderr)
        return 1
    byte_count = os.path.getsize(SOURCE)
    if byte_count > LIMIT_BYTES:
        print(f"error: entry.png is {byte_count} bytes, over the 1 MiB "
              "limit", file=sys.stderr)
        return 1
    width, height = read_png_dimensions(SOURCE)
    if width > LIMIT_SIDE or height > LIMIT_SIDE:
        print(f"error: entry.png is {width}x{height}, over the 1024x1024 "
              "limit", file=sys.stderr)
        return 1
    os.makedirs(destination_dir, exist_ok=True)
    target = os.path.join(destination_dir, "entry.png")
    shutil.copyfile(SOURCE, target)
    if digest(SOURCE) != digest(target):
        print("error: copy does not match the source", file=sys.stderr)
        return 1
    print(f"wrote {target} ({width}x{height}, {byte_count} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
