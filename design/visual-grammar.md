# Kernel graph visual grammar

Kernel diagrams are authored directly as SVG by an AI/LLM after it reconstructs
and validates a semantic specification from implementation code. Coordinates,
colors, and SVG markup belong in the SVG, not in the kernel specification.

## Composition is a projection

The semantic specification does not prescribe graph shape, size, orientation,
or panel count. The authoring LLM chooses the composition that best exposes the
kernel's dominant structure. Multiple coordinated SVG views may be authored from
one specification, with exactly one designated as the primary infographic.

Useful compositions include cyclic mainloops, aligned role timelines,
producer-consumer graphs, physical memory floorplans, phase flows, and combined
multi-panel views. Do not force a cyclic or hierarchical kernel into a linear
timeline merely to reuse a template.

## Common reconstruction composition

1. Kernel identity and the concrete configuration being illustrated.
2. One horizontal lane per active warp or warp-group role.
3. Cross-role readiness and release handoffs.
4. Explicit prologue, repeated-mainloop, loop-tail, and epilogue regions when applicable.
5. SMEM and TMEM physical-allocation lifetimes on the same event axis.
6. A small reconstruction note area for essential formulas or variant decisions.

When a view uses a horizontal axis, it represents semantic event order unless
the graph explicitly states that it is cycle-accurate. A steady-state view may
show one representative iteration, but its loop scope must identify resources
that persist across all iterations and resources carried into the next iteration.

When a timeline includes both bootstrap and representative steady state, use a
phase-local index vocabulary:

| Phase | Index vocabulary |
| --- | --- |
| Prologue | Concrete seed objects: `K0`, `V0` |
| Mainloop | Current symbolic objects: `Kj`, `Vj` |
| Mainloop overlap | One declared neighbor: `Kj+1`, `Vj+1` or `Kj-1`, `Vj-1` |

The phase boundary semantically renames the seed as the current loop value for
the first entry (`j=0`). Keep concrete seed labels on the prologue side of that
boundary.

## Visual meanings

| Concept | Encoding |
| --- | --- |
| Warp role | Horizontal execution lane |
| Operation | Labeled block in its owning role lane |
| Wait | Hatched operation block |
| Data ready | Solid gold cross-role arrow |
| Storage released | Dashed gold return arrow or named lifecycle endpoint |
| Repeated loop | Labeled timeline section with an iterator |
| Physical allocation | One SMEM or TMEM memory row |
| Logical resource lifetime | Colored bar derived from lifecycle references |
| Alias/reuse | Adjacent logical bars in the same physical-allocation row |
| Next-iteration carry | Bar ending at the loop boundary and labeled as carried |
| Split publication | Separate partial-ready and final-ready handoffs to one consumer operation |
| Explicit separation | Different allocation rows plus a validated storage relation |

Color identifies broad data or operation classes. It never carries the only
meaning; every block and lifetime is labeled.

## Operation language

Prefer structured, compact labels:

```text
ACTION · OBJECT
SOURCE → DESTINATION
```

Show instruction families when they determine the datapath, such as TMA,
WGMMA, `tcgen05`, TMEM load, or TMA store. Collapse arithmetic sequences that
do not create a cross-role handoff or change a memory lifetime.

Stage subscripts are causal identity, not decoration. Preserve them from load
through compute, synchronization, and memory lifetime so no role appears to
consume an object that has no visible producer.

## Physical storage rule

A row means one physical allocation, not merely one data category. Multiple
bars may occupy that row only when the allocation declares sequential aliasing
and the validator proves their lifetimes do not overlap. Configuration-sensitive
relationships such as `sQ` versus `sO` must be asserted as `alias` or `distinct`;
row placement alone is not sufficient documentation.
