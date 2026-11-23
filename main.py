#!/usr/bin/env python3
"""Entry program for the 23 November 2026 world-news image.

The picture itself was drawn beforehand (with Pillow, at build time)
and is stored in this repository as entry.png. This program only places
an exact copy of it at $MAKEFUN_OUTPUT_DIR/entry.png, so the graded run
needs nothing beyond the Python standard library: no network, no extra
packages, nothing to install.

Before copying it checks the file is really a PNG inside the
competition limits (at most 1 MiB, at most 1024 pixels on a side),
then confirms the copy byte for byte, so the two graded runs always
produce identical output.
"""

import hashlib
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGE = os.path.join(HERE, "entry.png")

MAX_BYTES = 1_048_576
MAX_SIDE = 1024
MAGIC = b"\x89PNG\r\n\x1a\n"


def file_sha256(path):
    """SHA-256 hex digest of a file's whole contents."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_dimensions(path):
    """(width, height) from the PNG IHDR chunk; raises on bad input."""
    with open(path, "rb") as handle:
        head = handle.read(33)
    if head[:8] != MAGIC:
        raise ValueError("entry.png: bad magic bytes, not a PNG file")
    if head[12:16] != b"IHDR":
        raise ValueError("entry.png: IHDR chunk missing, not a PNG file")
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    if not os.path.isfile(IMAGE):
        print("error: entry.png is missing from the repository", file=sys.stderr)
        return 1
    n_bytes = os.path.getsize(IMAGE)
    if n_bytes > MAX_BYTES:
        print(f"error: entry.png is {n_bytes} bytes, over the 1 MiB limit",
              file=sys.stderr)
        return 1
    width, height = png_dimensions(IMAGE)
    if width > MAX_SIDE or height > MAX_SIDE:
        print(f"error: entry.png is {width}x{height}, over the 1024x1024 limit",
              file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    shutil.copyfile(IMAGE, target)
    if file_sha256(IMAGE) != file_sha256(target):
        print("error: copied file does not match the source", file=sys.stderr)
        return 1
    print(f"wrote {target} ({width}x{height}, {n_bytes} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
