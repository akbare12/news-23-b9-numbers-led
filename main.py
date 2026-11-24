#!/usr/bin/env python3
"""Copy entry.png to MAKEFUN_OUTPUT_DIR/entry.png.

The only output is os.environ["MAKEFUN_OUTPUT_DIR"]/entry.png; nothing is
ever written next to this file (the grader runs it from a read-only /bot).
"""
import hashlib
import os
import shutil
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def png_size(path):
    """Read PNG dimensions from the IHDR chunk (stdlib only, no PIL)."""
    with open(path, "rb") as f:
        head = f.read(33)
    if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        raise ValueError("not a PNG file")
    w = int.from_bytes(head[16:20], "big")
    h = int.from_bytes(head[20:24], "big")
    return w, h


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    if sha256(SRC) != sha256(dst):
        print("FAIL: sha256 mismatch", file=sys.stderr)
        return 1
    w, h = png_size(dst)
    if (w, h) != (1024, 1024):
        print(f"FAIL: entry.png is {w}x{h}, expected 1024x1024",
              file=sys.stderr)
        return 1
    size = os.path.getsize(dst)
    if size > 1048576:
        print(f"FAIL: entry.png is {size} bytes (> 1 MiB)", file=sys.stderr)
        return 1
    print(f"OK: wrote {dst} (1024x1024, {size} bytes, "
          f"sha256 {sha256(dst)[:16]}...)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
