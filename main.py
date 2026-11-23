#!/usr/bin/env python3
"""news-image-20261123: validate and copy the pre-drawn entry image.

The entry image (entry.png, drawn at build time) ships next to this script.
At grade time the environment is Python 3.13 standard library only, so this
program deliberately imports nothing beyond the stdlib. It checks that
entry.png is a real PNG within the size limits, then copies it byte-for-byte
into $MAKEFUN_OUTPUT_DIR (default /output) and verifies the copy.

Usage:
    MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import hashlib
import os
import struct
import sys

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_DIMENSION = 1024
MAX_BYTES = 1_048_576  # 1 MiB


def fail(message):
    print("error: " + message, file=sys.stderr)
    return 1


def read_png_dimensions(path):
    """Return (width, height) from a PNG's IHDR chunk, or None if invalid."""
    with open(path, "rb") as handle:
        header = handle.read(33)
    if len(header) < 33:
        return None
    if header[:8] != PNG_SIGNATURE:
        return None
    # First chunk must be IHDR: 4-byte length, 4-byte type, 13-byte data.
    length, chunk_type = struct.unpack(">I4s", header[8:16])
    if chunk_type != b"IHDR" or length != 13:
        return None
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(script_dir, "entry.png")
    if not os.path.isfile(source):
        return fail("entry.png not found next to main.py (%s)" % source)

    size = os.path.getsize(source)
    if size > MAX_BYTES:
        return fail(
            "entry.png is %d bytes, over the %d-byte limit" % (size, MAX_BYTES)
        )

    dimensions = read_png_dimensions(source)
    if dimensions is None:
        return fail("entry.png is not a valid PNG (bad signature or IHDR)")
    width, height = dimensions
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        return fail(
            "entry.png is %dx%d, over the %dx%d limit"
            % (width, height, MAX_DIMENSION, MAX_DIMENSION)
        )

    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as exc:
        return fail("cannot create output directory %s: %s" % (output_dir, exc))
    target = os.path.join(output_dir, "entry.png")

    try:
        with open(source, "rb") as src, open(target, "wb") as dst:
            for block in iter(lambda: src.read(65536), b""):
                dst.write(block)
    except OSError as exc:
        return fail("copy failed: %s" % exc)

    if sha256_of(target) != sha256_of(source):
        return fail("copy verification failed: SHA-256 mismatch")

    print(
        "wrote %s (%dx%d, %d bytes)"
        % (target, width, height, size)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
