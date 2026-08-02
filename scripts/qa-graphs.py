#!/usr/bin/env python3
"""Run artifact QA for every direct LLM-authored graph and kernel view."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gpu_graph.model import load_spec  # noqa: E402
from gpu_graph.qa import (  # noqa: E402
    inspect_collection_svg,
    inspect_direct_svg,
    inspect_png,
    inspect_svg,
)
from gpu_graph.validation import (  # noqa: E402
    validate_kernel_collection,
    validate_spec,
    validate_topic_spec,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stage",
        choices=("svg", "artifacts", "all"),
        default="all",
        help="QA LLM-authored SVGs, PNG companions, or both",
    )
    args = parser.parse_args()

    failures: list[str] = []
    checked_kernel_views = 0
    checked_direct_svgs = 0
    claimed_svgs: dict[Path, str] = {}
    kernel_claimed_svgs: dict[Path, str] = {}

    for spec_path in sorted((ROOT / "specs" / "kernels").glob("**/*.json")):
        spec = load_spec(spec_path)
        if spec.get("schema_version") == "collection-0.1":
            validate_kernel_collection(spec)
            for record in spec["kernels"]:
                checked_kernel_views += 1
                svg_path = ROOT / record["output"]
                label = f"{spec_path.relative_to(ROOT)}::{record['id']}"
                relative_svg = svg_path.relative_to(ROOT)
                prior_owner = kernel_claimed_svgs.get(relative_svg)
                if prior_owner is not None:
                    failures.append(
                        f"{relative_svg}: reconstruction.duplicate: claimed by "
                        f"{prior_owner} and {label}"
                    )
                    continue
                kernel_claimed_svgs[relative_svg] = label
                if not svg_path.exists():
                    failures.append(
                        f"{label}: svg.missing: {svg_path.relative_to(ROOT)}"
                    )
                    continue
                svg_content = svg_path.read_text(encoding="utf-8")
                if args.stage in {"svg", "all"}:
                    failures.extend(
                        f"{label}: {issue}"
                        for issue in inspect_collection_svg(record, svg_content)
                    )
                if args.stage in {"artifacts", "all"}:
                    failures.extend(
                        f"{label}: {issue}"
                        for issue in inspect_png(svg_path.with_suffix(".png"), svg_content)
                    )
            continue
        validate_spec(spec)
        for view in spec["views"]:
            checked_kernel_views += 1
            svg_path = ROOT / view["output"]
            label = f"{spec_path.relative_to(ROOT)}::{view['id']}"
            relative_svg = svg_path.relative_to(ROOT)
            prior_owner = kernel_claimed_svgs.get(relative_svg)
            if prior_owner is not None:
                failures.append(
                    f"{relative_svg}: reconstruction.duplicate: claimed by "
                    f"{prior_owner} and {label}"
                )
                continue
            kernel_claimed_svgs[relative_svg] = label
            if not svg_path.exists():
                failures.append(f"{label}: svg.missing: {svg_path.relative_to(ROOT)}")
                continue
            svg_content = svg_path.read_text(encoding="utf-8")

            if args.stage in {"svg", "all"}:
                failures.extend(
                    f"{label}: {issue}" for issue in inspect_svg(spec, view, svg_content)
                )

            if args.stage in {"artifacts", "all"}:
                png_path = svg_path.with_suffix(".png")
                failures.extend(
                    f"{label}: {issue}" for issue in inspect_png(png_path, svg_content)
                )

    for spec_path in sorted((ROOT / "specs" / "topics").glob("*.json")):
        topic_spec = load_spec(spec_path)
        validate_topic_spec(topic_spec)
        matches = sorted(ROOT.glob(topic_spec["coverage"]["glob"]))
        if not matches:
            failures.append(
                f"{spec_path.relative_to(ROOT)}: coverage.empty: "
                f"{topic_spec['coverage']['glob']} matched no SVGs"
            )
        for svg_path in matches:
            checked_direct_svgs += 1
            relative_svg = svg_path.relative_to(ROOT)
            prior_owner = claimed_svgs.get(relative_svg)
            if prior_owner is not None:
                failures.append(
                    f"{relative_svg}: coverage.duplicate: claimed by {prior_owner} "
                    f"and {topic_spec['id']}"
                )
                continue
            claimed_svgs[relative_svg] = topic_spec["id"]
            svg_content = svg_path.read_text(encoding="utf-8")
            label = f"{spec_path.relative_to(ROOT)}::{relative_svg}"
            if args.stage in {"svg", "all"}:
                failures.extend(
                    f"{label}: {issue}"
                    for issue in inspect_direct_svg(topic_spec, relative_svg, svg_content)
                )
            if args.stage in {"artifacts", "all"}:
                failures.extend(
                    f"{label}: {issue}"
                    for issue in inspect_png(svg_path.with_suffix(".png"), svg_content)
                )

    all_svgs = {path.relative_to(ROOT) for path in (ROOT / "graphs").glob("**/*.svg")}
    for unclaimed in sorted(all_svgs - set(claimed_svgs)):
        failures.append(f"{unclaimed}: coverage.unclaimed: no topic spec owns this SVG")
    for unclaimed in sorted(all_svgs - set(kernel_claimed_svgs)):
        failures.append(
            f"{unclaimed}: reconstruction.unclaimed: no kernel spec or collection record owns this SVG"
        )

    if failures:
        print("Kernel graph QA failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        raise SystemExit(1)

    print(
        "graph QA passed · "
        f"{checked_direct_svgs} direct SVG(s) · "
        f"{checked_kernel_views} reconstruction view(s) · stage={args.stage}"
    )


if __name__ == "__main__":
    main()
