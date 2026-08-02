# Repository instructions

## Purpose and organization

- This repository explains GPU concepts through diagrams.
- Treat the warp / warp-group role timeline as a primary design artifact. Every
  primary graph uses exactly three top-level phases: prologue, mainloop, and
  epilogue. Put loop bootstrap in prologue, representative repeated work and
  any loop-tail event inside mainloop, and final publication/drain in epilogue.
  It is
  critical for understanding how a kernel assigns work and overlaps producer,
  MMA, epilogue, and auxiliary roles; show role ownership and synchronization
  over time whenever the kernel uses warp specialization.
- When the kernel uses shared memory (SMEM) or tensor memory (TMEM), include a
  clearly labeled sub-figure showing physical allocations and resource
  lifetimes on the same prologue/mainloop/epilogue event axis: operands,
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
- The kernel spec is the semantic source of truth. The SVG is the presentation
  source of truth and must be authored directly by the AI/LLM from that spec;
  the PNG alone is generated. Never edit a PNG independently.
- Shared architecture topology is not enough to distinguish a kernel view. Each
  graph must visibly integrate its code-derived variant path: the operation or
  role that differs, the synchronization it adds or changes, and the resulting
  memory-lifetime consequence. A filename-specific caption does not satisfy
  this requirement.
- Every SVG must be owned by exactly one `specs/topics/<topic>.json` authoring
  contract and exactly one `specs/kernels/**/*.json` semantic spec or collection
  record. Repository QA rejects missing or duplicate ownership in either layer.
- A large, closely related source collection may use one validated
  `collection-0.1` kernel catalog under `specs/kernels/<topic>/`. It must contain
  exactly one source-derived record per SVG; QA must join the record ID, source
  locator, role path, synchronization, and memory consequence back to visible
  SVG content. Existing labels may be named with `visible_tokens` when the full
  catalog prose would overload the figure. A catalog is not permission to
  generate SVGs from a template.

## SVG and PNG pairs

- Every committed SVG should have a same-named PNG beside it, for example
  `attention/forward-pass.svg` and `attention/forward-pass.png`.
- After every SVG change, run `make png` and commit the regenerated PNG in the
  same change when its rendered pixels change. If timestamps are unreliable or
  the PNG is not updated, run `make png-force`. A semantic-only SVG edit may
  legitimately produce a byte-identical PNG.
- Before finishing work that changes SVGs, confirm the PNG companion was
  regenerated and passes artifact QA, even when `git status` does not show a
  byte-identical PNG.
- When finishing work that modifies an SVG and its PNG companion, always list
  the absolute paths to both files as clickable links so the user can open them.
  Put each absolute path on its own line; do not place SVG and PNG links on the
  same line.
- Keep SVG text as text when practical, embed required styles, include a
  meaningful `<title>` and `<desc>`, and use a `viewBox` so the graph scales.

## Required AI/LLM workflow for every graph

AI agents must use this production loop for every graph. Collection overviews
use a topic spec; reconstruction views use both a topic spec and a kernel spec:

```text
read target kernel code + relevant helpers
    → build an evidence-backed semantic reconstruction
    → write or update the semantic specification
    → validate schema + kernel invariants
    → author the SVG directly as an LLM
    → run generic + layout-profile SVG QA
    → render PNG + verify SVG/PNG parity
    → visually inspect full graph and dense crops
    ↺ classify failures, fix the correct layer, and repeat
```

### Non-negotiable authoring rule

The AI/LLM is the generator. It must reason from the inspected kernel code,
write the semantic spec, choose the composition, and author literal SVG markup
itself. Do not replace any of those steps with a Python or JavaScript program,
Graphviz, Mermaid, a plotting package, a renderer, a template engine, or another
script that computes SVG structure, coordinates, paths, or labels. Repository
automation may validate the spec and SVG, detect omissions or layout failures,
and rasterize the completed SVG to PNG; it may not generate the kernel SVG.

Follow these steps in order:

1. Inspect before editing.
   - Read this file, the topic README, its `specs/topics/<topic>.json` authoring
     spec, any applicable kernel spec, and the relevant files under `design/`.
   - For SVG work, read `design/llm-svg-authoring.md` and the view's structured
     `authoring` brief before choosing a composition.
   - Locate and read the target kernel implementation. Follow the helpers,
     templates, pipeline objects, barriers, and storage definitions needed to
     reconstruct the displayed path; do not infer the spec from the graph or
     kernel name alone.
   - Run `git status --short` and preserve unrelated user changes.
   - Identify whether the graph is hand-authored or specification-backed.
2. Put each change in its owning layer.
   - Topic-wide code provenance, authoring goals, required content, exclusions,
     and minimum visual structure belong in `specs/topics/*.json`.
   - Kernel facts, role ownership, operations, synchronization, and memory
     lifetimes belong in `specs/kernels/**/*.json`.
   - Composition, geometry, wrapping, routing, and visual encoding belong in the
     LLM-authored SVG, guided by `design/visual-grammar.md`.
   - Cross-graph semantic invariants belong in `validation.py` and the schema.
   - Reusable machine-checkable layout rules belong in `qa.py`; reusable
     authoring guidance belongs under `design/` and in this file.
   - The LLM must write and edit SVG markup directly. Do not create or invoke a
     renderer, diagram generator, plotting library, or script that emits the SVG
     for a specification-backed kernel graph.
   - Use `templates/kernel-svg.template.svg` only as a semantic-markup starter;
     it is not a fixed layout. Use `templates/kernel-spec.template.jsonc` when
     starting a new code-derived specification.
   - PNG files are derived artifacts and must not receive hand patches.
3. Derive the kernel spec from code and preserve the evidence.
   - The target implementation code is the primary source for a kernel spec.
     Derive warp roles, operation order, synchronization, pipeline stages,
     memory allocations, lifetimes, and aliasing by reading that code and the
     relevant callees or templates.
   - Record source IDs, precise locators, and concise factual notes in the spec
     for reconstruction-critical claims. The evidence should let another agent
     return to the code and verify the claim.
   - Separate facts directly observed in code from interpretations introduced
     to make one representative timeline. Document the latter as reconstruction
     notes rather than presenting them as measured behavior.
   - Do not invent cycle timing, storage aliasing, synchronization, or operation
     order. Make unknown or configuration-dependent facts explicit.
   - If the required implementation or helper code cannot be inspected, do not
     create or revise an authoritative kernel spec from memory. Report the
     missing source and leave the unsupported facts unresolved.
   - A topic overview may summarize a configuration family, but it must label
     configuration-dependent content as such. Do not promote an archetype
     overview to a reconstruction spec without inspecting and encoding the
     concrete operation, synchronization, and lifetime facts.
4. Use the fast feedback loop while authoring.

   ```sh
   make check
   make svg-qa
   ```

   Edit the SVG directly between QA runs. `make svg-qa` inspects the authored
   SVG; it does not create or rewrite it.

5. Run the full pre-completion gate.

   ```sh
   make qa
   ```

   It must pass semantic validation, layout-profile collision and coverage
   checks, PNG rendering, and SVG/PNG dimension parity.
6. Perform visual QA even when automation passes.
   - Open the generated PNG at full-graph scale and at 100% scale.
   - Inspect dense timeline, synchronization, and memory regions separately.
   - Confirm that text does not overlap or clip, connectors remain traceable,
     phases are distinct, and the reconstruction story is understandable.
   - Do not declare completion based only on `make qa`.
7. Turn repeatable visual failures into system checks.
   - Add an SVG QA rule and a deliberately broken regression test for any
     collision, clipping, stale-artifact, or semantic-coverage failure that can
     recur.
   - Update the visual grammar or AI instructions when a recurring issue cannot
     be expressed as a geometry check.
8. Finish with artifact verification.
   - Run `git diff --check` and confirm the SVG is updated and its PNG companion
     was regenerated; a semantic-only SVG edit may yield a byte-identical PNG.
   - Report the checks run and link the absolute SVG and PNG paths on separate
     lines.

Classify failures before editing:

| Failure | Fix here |
| --- | --- |
| Missing or incorrect kernel fact | Kernel spec |
| Invalid reference, lifetime, loop scope, or alias claim | Spec, schema, or semantic validator |
| Fact exists but is absent from the graph | LLM-authored SVG and semantic-coverage QA |
| Text, boxes, annotations, or arrows collide | LLM-authored SVG plus reusable SVG QA |
| Label is unnecessarily verbose | Spec label, while preserving detail/evidence elsewhere |
| SVG does not match the spec | Revise the SVG directly and strengthen coverage QA |
| PNG is stale or mismatched | Re-render from SVG; do not hand-edit it |

## Topic documentation

- Add `graphs/<topic>/README.md` when a graph needs background, terminology,
  citations, or interpretation notes.
- Keep explanations concise and link to primary sources where possible.
