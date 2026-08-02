"""Command-line entry point for validating and rendering kernel specs."""

from __future__ import annotations

import argparse
from pathlib import Path

from .model import load_spec
from .renderers import RENDERERS
from .validation import validate_spec


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--check", action="store_true", help="validate without writing an SVG")
    parser.add_argument(
        "--renderer",
        choices=sorted(RENDERERS),
        default="reconstruction-timeline",
        help="visual projection to render",
    )
    args = parser.parse_args()

    spec = load_spec(args.spec)
    validate_spec(spec)
    if args.check:
        print(f"validated {args.spec}")
        return

    content = RENDERERS[args.renderer](spec)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not args.output.exists() or args.output.read_text(encoding="utf-8") != content:
        args.output.write_text(content, encoding="utf-8")
    print(f"rendered {args.output}")


if __name__ == "__main__":
    main()
