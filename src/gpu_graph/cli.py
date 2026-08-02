"""Command-line entry point for validating kernel specifications."""

from __future__ import annotations

import argparse
from pathlib import Path

from .model import load_spec
from .validation import validate_kernel_collection, validate_spec, validate_topic_spec


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    args = parser.parse_args()

    spec = load_spec(args.spec)
    if spec.get("schema_version") == "topic-0.1":
        validate_topic_spec(spec)
    elif spec.get("schema_version") == "collection-0.1":
        validate_kernel_collection(spec)
    else:
        validate_spec(spec)
    print(f"validated {args.spec}")


if __name__ == "__main__":
    main()
