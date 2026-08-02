# Repository instructions

## Purpose and organization

- This repository explains GPU concepts through diagrams.
- Treat the warp / warp-group role timeline as a primary design artifact. It is
  critical for understanding how a kernel assigns work and overlaps producer,
  MMA, epilogue, and auxiliary roles; show role ownership and synchronization
  over time whenever the kernel uses warp specialization.
- When the kernel uses shared memory (SMEM) or tensor memory (TMEM), include a
  clearly labeled sub-figure showing the applicable memory partition: operands,
  pipeline stages, accumulators, scale factors, epilogue buffers, and any
  intentional aliasing or reuse. State explicitly when TMEM is not available.
- Make diagrams large enough for role and memory labels to remain legible when
  opened directly; prefer a canvas at least 2400 pixels wide for new or redrawn
  timeline figures.
- Put graph topics under `graphs/<topic>/`; do not add topic directories at the
  repository root.
- When a topic contains multiple diagrams, put each SVG/PNG pair in its own
  `graphs/<topic>/<content-name>/` mini-directory.
- Use lowercase kebab-case for directory and file names.
- For hand-authored graphs, SVG is the editable source of truth. For
  specification-backed graphs, the kernel spec is the semantic source and the
  renderer is the presentation source; their SVG and PNG files are generated
  artifacts. Never edit a PNG independently.

## SVG and PNG pairs

- Every committed SVG should have a same-named PNG beside it, for example
  `attention/forward-pass.svg` and `attention/forward-pass.png`.
- After every SVG change, run `make png` and commit the regenerated PNG in the
  same change. If timestamps are unreliable or the PNG is not updated, run
  `make png-force`.
- Before finishing work that changes SVGs, confirm `git status` includes the
  expected PNG changes.
- When finishing work that modifies an SVG and its PNG companion, always list
  the absolute paths to both files as clickable links so the user can open them.
  Put each absolute path on its own line; do not place SVG and PNG links on the
  same line.
- Keep SVG text as text when practical, embed required styles, include a
  meaningful `<title>` and `<desc>`, and use a `viewBox` so the graph scales.

## Required AI/LLM workflow for specification-backed graphs

AI agents must use this production loop for every generated kernel graph:

```text
inspect repository + evidence
    → edit semantic specification or reusable renderer
    → validate schema + kernel invariants
    → generate deterministic SVG
    → run generic + renderer-specific SVG QA
    → render PNG + verify SVG/PNG parity
    → visually inspect full graph and dense crops
    ↺ classify failures, fix the correct layer, and repeat
```

Follow these steps in order:

1. Inspect before editing.
   - Read this file, the topic README, the kernel spec, and the relevant files
     under `design/`.
   - Run `git status --short` and preserve unrelated user changes.
   - Identify whether the graph is hand-authored or specification-backed.
2. Put each change in its owning layer.
   - Kernel facts, role ownership, operations, synchronization, and memory
     lifetimes belong in `specs/kernels/**/*.json`.
   - Reusable layout, wrapping, routing, and visual encoding belong in a
     renderer under `src/gpu_graph/`.
   - Cross-graph semantic invariants belong in `validation.py` and the schema.
   - Generated SVG and PNG files must not receive hand patches.
3. Preserve evidence and uncertainty.
   - Prefer primary implementation sources. Record source IDs, locators, and
     concise factual notes in the spec.
   - Do not invent cycle timing, storage aliasing, synchronization, or operation
     order. Make unknown or configuration-dependent facts explicit.
4. Use the fast feedback loop while authoring.

   ```sh
   make check
   make generate
   make svg-qa
   ```

5. Run the full pre-completion gate.

   ```sh
   make qa
   ```

   It must pass semantic validation, deterministic generation, renderer-specific
   collision and coverage checks, PNG rendering, and SVG/PNG dimension parity.
6. Perform visual QA even when automation passes.
   - Open the generated PNG at full-graph scale and at 100% scale.
   - Inspect dense timeline, synchronization, and memory regions separately.
   - Confirm that text does not overlap or clip, connectors remain traceable,
     phases are distinct, and the reconstruction story is understandable.
   - Do not declare completion based only on `make qa`.
7. Turn repeatable visual failures into system checks.
   - Add a renderer QA rule and a deliberately broken regression test for any
     collision, clipping, stale-artifact, or semantic-coverage failure that can
     recur.
   - Do not solve a renderer problem by nudging one generated graph.
8. Finish with artifact verification.
   - Run `git diff --check` and confirm the expected SVG and PNG both changed.
   - Report the checks run and link the absolute SVG and PNG paths on separate
     lines.

Classify failures before editing:

| Failure | Fix here |
| --- | --- |
| Missing or incorrect kernel fact | Kernel spec |
| Invalid reference, lifetime, loop scope, or alias claim | Spec, schema, or semantic validator |
| Fact exists but is absent from the graph | Renderer semantic coverage |
| Text, boxes, annotations, or arrows collide | Reusable renderer layout and SVG QA |
| Label is unnecessarily verbose | Spec label, while preserving detail/evidence elsewhere |
| SVG is stale | Regenerate; do not hand-edit it |
| PNG is stale or mismatched | Re-render from SVG; do not hand-edit it |

## Topic documentation

- Add `graphs/<topic>/README.md` when a graph needs background, terminology,
  citations, or interpretation notes.
- Keep explanations concise and link to primary sources where possible.
