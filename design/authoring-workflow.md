# Kernel graph authoring workflow

Use this order for every reconstruction-oriented kernel graph. It separates
source facts from presentation and lets validation catch causal mistakes before
rendering.

## 1. Freeze one concrete configuration

Give every configuration field a stable ID, label, and typed value. Include all
parameters that can change warp roles, pipeline depth, memory layout, or aliasing.
Create another specification for a materially different variant rather than
combining incompatible layouts in one timeline.

## 2. Build the evidence ledger

Register primary sources once under `sources`. Attach source ID, locator, and a
short factual note to every loop-residency claim, intentional physical reuse,
and configuration-sensitive storage relation. Evidence remains in the spec and
does not need to clutter the primary graph.

## 3. Define the semantic axis and loops

Create exactly three top-level sections: prologue, mainloop, and epilogue. Put
bootstrap work in prologue, repeated work and loop-tail/drain events inside
mainloop, and final publication in epilogue.
Declare repeated loops separately from visual sections, including the iterator
and whether the figure shows every iteration or one representative iteration.
For a representative iteration, declare its indexing contract: the concrete
prologue seed, the symbolic current iterator, and whether overlap is expressed
with the previous or next iteration. Tag seed/current/adjacent operations with
structured iteration metadata; labels are presentation, not the source of this
phase relationship.

## 4. Inventory roles and operations

Add one lane per active role. Keep only operations that change a logical
resource, create a cross-role dependency, release storage, or are necessary to
reconstruct the datapath. Preserve multiple readiness points when a consumer can
start on a partial operand and later waits on a final fragment. Mark repeated
operations with their loop scope and frequency.

## 5. Define logical resources

Use stable IDs in operation `reads` and `writes`. Give every SMEM/TMEM resource:

- one physical allocation ID;
- a lifecycle start and end that reference operations, events, or loop bounds;
- a loop-residency assertion when it survives every iteration;
- a next-iteration carry marker when it is prefetched for the following iteration.

Register-only temporaries and GMEM operands can remain in operation labels when
their lifetimes are not part of the on-chip allocation story.

For large collections of related kernels, a `collection-0.1` catalog may record
one compact reconstruction per SVG. Each record must retain a concrete source
and code locator, the source-specific role/operation path, and its
synchronization plus memory-lifetime consequence. Use a full `0.3` kernel spec
when the graph claims exact operations, handoffs, allocation IDs, or lifetimes.

## 6. Define physical allocations and relationships

Create one allocation record per physical row. When several logical resources
share it, declare `sequential-alias` with source evidence. Add a storage relation
for relationships readers are likely to ask about, especially configuration-
dependent aliasing such as Q/O buffers. Validated storage relations are added to
the graph notes automatically; do not duplicate them in free-form notes. Encode
the selected relation's applicability as typed configuration predicates, not a
prose condition, so changing a variant invalidates stale storage claims.

## 7. Validate, author the SVG, and inspect

Declare one or more views of the same semantic model. Exactly one view is
primary. Choose the composition according to the kernel's structure: a cycle for
a repeated pipeline, a timeline for overlap, a floorplan for physical placement,
a dependency graph for synchronization, or a custom composition when those
forms are insufficient. Assign the applicable automated `qa_profile`. Width,
height, orientation, and panel count are not schema constraints.

Secondary views may expose denser reconstruction detail without forcing it into
the primary infographic. View declarations select QA profiles and output paths;
they do not duplicate operations, resources, lifetimes, or storage decisions.

The AI/LLM authors each SVG directly from the validated spec and this
repository's visual grammar. Do not build or invoke a script, renderer, plotting
library, or template engine that emits the SVG. The SVG is an editable
presentation source, not a generated projection. Keep stable semantic classes
and `data-*` IDs on important marks so automated QA can relate geometry back to
spec records. Follow [`llm-svg-authoring.md`](llm-svg-authoring.md) for the
authoring packet, direct-SVG rules, semantic join contract, and completion
standard.

Run the complete production loop:

```sh
make qa
```

This validates the spec, inspects the existing LLM-authored SVG with generic and
layout-profile QA, renders PNG companions, and verifies SVG/PNG dimension
parity. It does not create or rewrite the SVG. See
[`qa-workflow.md`](qa-workflow.md) for the gate contracts, failure routing, and
manual visual-review checklist.

The validator enforces these invariants:

| Invariant | Prevents |
| --- | --- |
| Every operation access references a declared resource | Orphan data appearing from nowhere |
| Every access lies inside the resource lifetime | Bars ending before their last consumer |
| Loop-resident resources cover the whole loop and end at a scoped release | Q ending after only the first displayed QK |
| Next-iteration resources reach the loop boundary | Prefetches leaking into the epilogue or disappearing early |
| Multiple resources in one allocation require documented reuse | Accidental aliasing |
| Resources sharing an allocation cannot overlap | Impossible physical reuse |
| Alias/distinct assertions match allocation IDs | Incorrect configuration-dependent memory claims |
| Evidence references registered primary sources | Untraceable reconstruction assumptions |
| Seed/current/adjacent operations stay in their declared phases | `K0`/`V0` leaking into a symbolic mainloop |

Automated SVG QA catches supported collision, coverage, containment, and canvas
failures. Visual inspection remains necessary for information density and the
overall reconstruction story, but repeatable layout failures should become QA
regressions rather than recurring manual fixes.
