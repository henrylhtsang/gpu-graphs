#!/usr/bin/env python3
"""Generate diagrams backed by versioned kernel specifications."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gpu_graph.model import load_spec  # noqa: E402
from gpu_graph.renderers import render_view  # noqa: E402
from gpu_graph.validation import validate_spec  # noqa: E402


def main() -> None:
    spec_paths = sorted((ROOT / "specs" / "kernels").glob("**/*.json"))
    for spec_path in spec_paths:
        spec = load_spec(spec_path)
        validate_spec(spec)
        for view in spec["views"]:
            svg_path = ROOT / view["output"]
            content = render_view(spec, view)
            svg_path.parent.mkdir(parents=True, exist_ok=True)
            if not svg_path.exists() or svg_path.read_text(encoding="utf-8") != content:
                svg_path.write_text(content, encoding="utf-8")
            print(f"rendered {svg_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
