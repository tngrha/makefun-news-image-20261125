#!/usr/bin/env python3
"""Entrypoint for news-image-20261125: copy the pre-rendered front page to /output.

The image was drawn by render.py (PIL + Noto Serif) from the verified 25 November
2026 stories listed in stories.md. This program does no network access and writes
the same bytes on every run.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))

def main():
    os.makedirs("/output", exist_ok=True)
    shutil.copyfile(os.path.join(HERE, "entry.png"), "/output/entry.png")

if __name__ == "__main__":
    main()
