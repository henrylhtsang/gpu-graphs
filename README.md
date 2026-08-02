# GPU Graphs

Visual explanations of GPU architecture, kernels, scheduling, memory movement,
and performance. The goal is to make difficult GPU topics easier to understand
with diagrams like execution timelines, dependency graphs, and data-flow maps.

SVG is the source format. Each SVG also has a same-named PNG export so diagrams
work in places that do not render SVG reliably.

## Repository layout

All topics live under `graphs/` so the repository root stays small:

```text
graphs/
  <topic>/
    README.md                    # optional collection context
    <content-name>/
      <graph-name>.svg           # editable source of truth
      <graph-name>.png           # generated from the SVG
scripts/
  qa-kernel-graphs.py
  render-svg.sh
schema/
  kernel.schema.json
specs/
  kernels/<topic>/<kernel>.json
src/gpu_graph/
  model.py              # loading and lifecycle resolution
  validation.py         # causal, loop-residency, and storage checks
  qa.py                 # generic and layout-profile SVG artifact QA
design/
  authoring-workflow.md # code-derived spec and LLM SVG authoring workflow
  llm-svg-authoring.md  # direct-SVG contract and semantic ID requirements
  qa-workflow.md        # spec -> LLM-authored SVG -> QA -> PNG loop
templates/
  kernel-spec.template.jsonc # starter semantic specification
  kernel-svg.template.svg    # starter semantic SVG structure, not a fixed layout
```

Use lowercase kebab-case for topic directories and graph filenames. A topic can
contain several related graphs; create subdirectories inside a topic if it grows
large. Prefer self-contained SVGs with embedded styles and fonts that have
reasonable system fallbacks.

## Add or update a graph

1. Create or choose a topic directory under `graphs/`, then give each content
   unit its own mini-directory when a topic contains multiple diagrams.
2. Add the SVG and, when useful, a short topic `README.md` explaining what it
   shows and linking to relevant sources.
3. Run `make png` to generate the PNG companion.
4. Commit the SVG and PNG together.

New reconstruction-oriented kernel diagrams must be backed by a versioned
specification under `specs/kernels/`. The AI/LLM derives that specification by
reading the target kernel implementation and relevant helpers, then authors the
SVG directly from the validated semantic model. Scripts validate and rasterize
the SVG; they do not generate its composition or markup. See
[`design/authoring-workflow.md`](design/authoring-workflow.md) and
[`design/llm-svg-authoring.md`](design/llm-svg-authoring.md) before adding one.

Before committing a specification-backed graph, run `make qa`. It executes the
ordered spec → LLM-authored SVG → automated layout QA → PNG parity loop. The QA
profiles and visual-review checklist are in
[`design/qa-workflow.md`](design/qa-workflow.md).

```text
read kernel implementation
    → evidence-backed specification
    → semantic validation
    → LLM authors SVG directly
    → generic + layout-profile SVG QA
    → PNG rendering
    → SVG/PNG artifact parity
    → visual review
    ↺ fix the spec or SVG and repeat
```

`make generate` exists only for older, non-specification diagram collections.
Do not use it to author a specification-backed kernel SVG.

The PNG must be regenerated after **every** SVG change. `make png` only rebuilds
PNG files whose SVG sources are newer; use `make png-force` to regenerate all of
them.

## Rendering prerequisites

The render script uses the first available command from `rsvg-convert`, `resvg`,
Inkscape, ImageMagick, or macOS `sips`. macOS works without additional setup;
for the most faithful CSS and font rendering, install librsvg:

```sh
brew install librsvg
make png
```

On Debian or Ubuntu, `sudo apt install librsvg2-bin` provides `rsvg-convert`.
See [`AGENTS.md`](AGENTS.md) for repository-specific editing rules.
