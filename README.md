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
    README.md          # optional context, sources, and terminology
    <graph-name>.svg   # editable source of truth
    <graph-name>.png   # generated from the SVG
scripts/
  render-svg.sh
```

Use lowercase kebab-case for topic directories and graph filenames. A topic can
contain several related graphs; create subdirectories inside a topic if it grows
large. Prefer self-contained SVGs with embedded styles and fonts that have
reasonable system fallbacks.

## Add or update a graph

1. Create or choose a topic directory under `graphs/`.
2. Add the SVG and, when useful, a short topic `README.md` explaining what it
   shows and linking to relevant sources.
3. Run `make png` to generate the PNG companion.
4. Commit the SVG and PNG together.

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
