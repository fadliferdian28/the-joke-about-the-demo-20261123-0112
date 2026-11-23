#!/usr/bin/env python3
"""Copy entry.txt into the grader's output directory.

The entry lives next to this script as entry.txt. This program reads it,
checks it is valid UTF-8 of 1-280 code points and not only whitespace, and
writes a byte-identical copy to $MAKEFUN_OUTPUT_DIR/entry.txt, verifying the
copy's sha256 before exiting. Stdlib only; it writes nowhere else.
"""

import hashlib
import os
import sys
from pathlib import Path

MAX_CHARS = 280


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(message: str) -> int:
    print(f"main.py: {message}", file=sys.stderr)
    return 1


def main() -> int:
    here = Path(__file__).resolve().parent
    source = here / "entry.txt"

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        return fail("MAKEFUN_OUTPUT_DIR is not set")

    try:
        payload = source.read_bytes()
    except OSError as exc:
        return fail(f"cannot read {source}: {exc}")

    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        return fail(f"entry.txt is not valid UTF-8: {exc}")

    if not 1 <= len(text) <= MAX_CHARS:
        return fail(f"entry is {len(text)} characters, must be 1-{MAX_CHARS}")
    if not text.strip():
        return fail("entry is only whitespace")

    dest = Path(out_dir) / "entry.txt"
    try:
        if source.resolve() == dest.resolve():
            return fail("source and destination are the same file")
    except OSError as exc:
        return fail(f"cannot resolve paths: {exc}")

    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.parent.is_dir():
            return fail(f"output path {dest.parent} is not a directory")
        dest.write_bytes(payload)
    except OSError as exc:
        return fail(f"cannot write {dest}: {exc}")

    try:
        written = dest.read_bytes()
    except OSError as exc:
        return fail(f"cannot read back {dest}: {exc}")
    if digest(written) != digest(payload):
        return fail("copy mismatch: output differs from entry.txt")

    print(f"wrote {dest} ({len(payload)} bytes, sha256 {digest(payload)[:12]}...)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
