#!/usr/bin/env python3
"""Entry program for news-image-20261125 (rev2, full-day edition).

Copies the pre-rendered broadsheet (entry.png, drawn by render.py from the
verified 25 November 2026 news list in stories.md) to /output/entry.png.

Deterministic and offline: same input bytes, same output bytes, every run.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("wrote %s (%d bytes)" % (dst, os.path.getsize(dst)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
