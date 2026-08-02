"""Command-line entry point for validating kernel specifications."""

from __future__ import annotations

import argparse
from pathlib import Path

from .model import load_spec
from .validation import validate_spec


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    args = parser.parse_args()

    spec = load_spec(args.spec)
    validate_spec(spec)
    print(f"validated {args.spec}")


if __name__ == "__main__":
    main()
