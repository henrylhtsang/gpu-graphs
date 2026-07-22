# Graph topics

Create one lowercase kebab-case directory per topic in this directory. Keep an
SVG source and its generated, same-named PNG together:

```text
graphs/flash-attention/
  README.md
  blackwell-forward-overlap.svg
  blackwell-forward-overlap.png
```

Related diagrams should share a topic directory. If a topic becomes crowded,
group its graphs into descriptive subdirectories instead of creating more
top-level repository directories.

Current large inventories include
[`cutlass-warp-specialization/`](cutlass-warp-specialization/), whose README
maps every detected CUTLASS example/tutorial source to its role timeline and
documents the pinned-source coverage check.
