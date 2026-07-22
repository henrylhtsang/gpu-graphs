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
- Use lowercase kebab-case for directory and file names.
- Treat SVG files as the editable source of truth. Do not edit generated PNGs
  independently.

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

## Topic documentation

- Add `graphs/<topic>/README.md` when a graph needs background, terminology,
  citations, or interpretation notes.
- Keep explanations concise and link to primary sources where possible.
