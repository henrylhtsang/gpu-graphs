#!/usr/bin/env python3
"""Run generated-artifact QA for every specification-backed kernel graph."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gpu_graph.model import load_spec  # noqa: E402
from gpu_graph.qa import inspect_png, inspect_svg  # noqa: E402
from gpu_graph.renderers import render_view  # noqa: E402
from gpu_graph.validation import validate_spec  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stage",
        choices=("svg", "artifacts", "all"),
        default="all",
        help="QA generated SVGs, PNG companions, or both",
    )
    parser.add_argument(
        "specs",
        nargs="*",
        type=Path,
        help="optional spec paths; defaults to every JSON spec under specs/kernels",
    )
    args = parser.parse_args()

    spec_paths = args.specs or sorted((ROOT / "specs" / "kernels").glob("**/*.json"))
    failures: list[str] = []
    checked_views = 0

    for requested_path in spec_paths:
        spec_path = requested_path if requested_path.is_absolute() else ROOT / requested_path
        spec = load_spec(spec_path)
        validate_spec(spec)
        for view in spec["views"]:
            checked_views += 1
            svg_path = ROOT / view["output"]
            label = f"{spec_path.relative_to(ROOT)}::{view['id']}"
            if not svg_path.exists():
                failures.append(f"{label}: svg.missing: {svg_path.relative_to(ROOT)}")
                continue
            svg_content = svg_path.read_text(encoding="utf-8")

            if args.stage in {"svg", "all"}:
                expected = render_view(spec, view)
                if svg_content != expected:
                    failures.append(
                        f"{label}: svg.stale: run make generate to refresh {view['output']}"
                    )
                failures.extend(
                    f"{label}: {issue}" for issue in inspect_svg(spec, view, svg_content)
                )

            if args.stage in {"artifacts", "all"}:
                png_path = svg_path.with_suffix(".png")
                failures.extend(
                    f"{label}: {issue}" for issue in inspect_png(png_path, svg_content)
                )

    if failures:
        print("Kernel graph QA failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        raise SystemExit(1)

    print(f"kernel graph QA passed · {checked_views} view(s) · stage={args.stage}")


if __name__ == "__main__":
    main()
