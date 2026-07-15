# Repository instructions

## Purpose and organization

- This repository explains GPU concepts through diagrams.
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
