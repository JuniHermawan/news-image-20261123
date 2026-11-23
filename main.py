#!/usr/bin/env python3
"""news-image-20261123: validate and copy the pre-drawn entry image.

The grader runs stdlib-only Python 3.13 with no network access, so this
program imports nothing beyond the standard library. It checks that the
bundled ``entry.png`` sitting next to this script is a real PNG within the
competition limits, then copies it byte-for-byte into the output directory
(``$MAKEFUN_OUTPUT_DIR``, default ``/output``) and verifies the copy.
"""

import hashlib
import os
import shutil
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_FILE_BYTES = 1_048_576          # 1 MiB
MAX_SIDE_PIXELS = 1024


def fail(message):
    """Print an error to stderr and exit non-zero."""
    print("error: " + message, file=sys.stderr)
    sys.exit(1)


def read_png_size(source_path):
    """Return (width, height, bit_depth, color_type) from the IHDR chunk.

    Also validates the IHDR bit-depth / color-type combination, so a
    truncated or non-standard PNG is rejected instead of copied blindly.
    """
    try:
        with open(source_path, "rb") as handle:
            header = handle.read(33)
    except OSError as exc:
        fail("cannot read %s: %s" % (source_path, exc))

    if len(header) < 33:
        fail("%s is too small to be a PNG (%d bytes)" % (source_path, len(header)))
    if header[:8] != PNG_MAGIC:
        fail("%s does not start with the PNG magic bytes" % source_path)

    chunk_length = int.from_bytes(header[8:12], "big")
    chunk_type = header[12:16]
    if chunk_type != b"IHDR" or chunk_length != 13:
        fail("%s: first chunk is not a 13-byte IHDR" % source_path)

    width = int.from_bytes(header[16:20], "big")
    height = int.from_bytes(header[20:24], "big")
    bit_depth = header[24]
    color_type = header[25]

    valid_depths = {0: (1, 2, 4, 8, 16), 2: (8, 16), 3: (1, 2, 4, 8),
                    4: (8, 16), 6: (8, 16)}
    if color_type not in valid_depths or bit_depth not in valid_depths[color_type]:
        fail("%s: invalid IHDR bit depth %d for color type %d"
             % (source_path, bit_depth, color_type))

    return width, height, bit_depth, color_type


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(script_dir, "entry.png")

    if not os.path.isfile(source_path):
        fail("entry.png not found next to main.py (%s)" % source_path)

    file_size = os.path.getsize(source_path)
    if file_size > MAX_FILE_BYTES:
        fail("entry.png is %d bytes, over the 1 MiB limit" % file_size)

    width, height, bit_depth, color_type = read_png_size(source_path)
    if width > MAX_SIDE_PIXELS or height > MAX_SIDE_PIXELS:
        fail("entry.png is %dx%d, over the 1024x1024 limit" % (width, height))

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        fail("cannot create output directory %s: %s" % (out_dir, exc))

    dest_path = os.path.join(out_dir, "entry.png")
    try:
        shutil.copyfile(source_path, dest_path)
    except OSError as exc:
        fail("cannot copy entry.png to %s: %s" % (dest_path, exc))

    digest_source = hashlib.sha256()
    digest_copy = hashlib.sha256()
    with open(source_path, "rb") as src, open(dest_path, "rb") as dst:
        while True:
            block = src.read(65536)
            if not block:
                break
            digest_source.update(block)
        while True:
            block = dst.read(65536)
            if not block:
                break
            digest_copy.update(block)

    if digest_source.hexdigest() != digest_copy.hexdigest():
        fail("copied entry.png failed SHA-256 verification")
    if os.path.getsize(dest_path) != file_size:
        fail("copied entry.png has the wrong byte count")

    print("wrote %s (%dx%d, %d bytes)" % (dest_path, width, height, file_size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
