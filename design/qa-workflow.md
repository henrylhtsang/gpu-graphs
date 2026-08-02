# Kernel graph QA workflow

Use one repeatable production loop for every specification-backed kernel graph:

```text
edit semantic spec
        ↓
validate schema + kernel invariants
        ↓
generate deterministic SVG
        ↓
run generic + renderer-specific SVG QA
        ↓
render PNG companion and verify artifact parity
        ↓
inspect the graph visually
        ↺ fix the spec or renderer, then run the loop again
```

The canonical command is:

```sh
make qa
```

It deliberately runs the gates in order. A later gate never compensates for a
failure in an earlier one.

## QA gates

| Gate | Automated checks | Correct place to fix a failure |
| --- | --- | --- |
| Spec | Schema, references, operation/resource causality, loop residency, storage reuse, evidence | Kernel spec or semantic validator |
| Generation | Every declared view uses a registered renderer and the checked-in SVG exactly matches deterministic renderer output | Renderer or generated SVG |
| Generic SVG | Parseability, canvas/viewBox agreement, minimum declared width, title, description, accessible root | Shared renderer infrastructure |
| Renderer-specific SVG | Semantic coverage, operation and lifetime box collisions, text containment, handoff annotation collisions, canvas bounds | Renderer layout algorithm; shorten spec text only when meaning is preserved |
| PNG parity | Companion exists and has exactly the SVG canvas dimensions | PNG rendering command or stale artifact |
| Visual review | Information density, arrow routing, phase readability, color/shape clarity, and whether the reconstruction story is understandable | Usually renderer; spec when the semantic story itself is incomplete |

`make svg-qa` runs only generated-SVG checks. `make artifact-qa` checks PNG
companions. These narrower commands are useful while developing a renderer;
`make qa` is the pre-commit gate.

## Feedback rule

Classify the problem before editing:

- Missing or incorrect kernel fact: fix the specification.
- A fact is present but not visible: fix semantic coverage in the renderer.
- Boxes, labels, or arrows collide: fix the renderer's layout policy, not one
  generated SVG.
- One label is needlessly verbose: simplify the spec label while keeping full
  evidence and detail in the spec or README.
- PNG differs from SVG: regenerate the artifact; never edit the PNG directly.

This division keeps kernel knowledge in the spec and presentation policy in the
renderer, so corrections benefit every graph using the same projection.

## Visual review checklist

Open the PNG once fit to the window and once at 100% scale. Confirm:

- prologue, mainloop, and epilogue are visually distinct;
- every important tile has a visible producer, consumer, and stage identity;
- cross-role ready/release events point to the intended operations;
- no text overlaps another label, box, connector, or canvas edge;
- concurrent work uses sublanes rather than overlapping boxes;
- SMEM/TMEM lifetimes align with the same event axis;
- aliases are adjacent in one physical row and do not overlap in time;
- the graph remains understandable without reading reconstruction notes first.

Visual review is the only manual gate. Record a discovered layout failure as an
automated regression whenever it can be expressed as geometry or semantic
coverage.

## Adding another renderer

1. Register it in `src/gpu_graph/renderers.py`.
2. Add its renderer-specific checker to `SVG_QA_CHECKERS` in
   `src/gpu_graph/qa.py`.
3. Give important marks stable classes or `data-*` IDs so QA can connect SVG
   geometry back to semantic IDs.
4. Add a passing reference test and at least one deliberately broken fixture
   that proves the checker detects its main failure mode.

Generation fails when a view names an unknown renderer. SVG QA fails when a
registered renderer lacks a QA contract.
