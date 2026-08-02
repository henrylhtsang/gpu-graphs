# Kernel graph information policy

The primary graph must answer eight questions:

1. Which warp role performs each major operation?
2. What data moves between GMEM, SMEM, TMEM, and registers?
3. Which event makes data ready for another role?
4. Which event releases a physical allocation for reuse?
5. Which operations repeat, and what persists across the loop?
6. Where is each important logical resource live over the event sequence?
7. Which logical resources share one physical allocation?
8. Which configuration decision makes a likely alias present or absent?

## Required semantic facts

Every reconstruction-oriented specification declares:

- a concrete kernel configuration with machine-readable parameter IDs;
- active warp roles and the major operations they own;
- repeated loop scopes and whether one representative iteration is shown;
- logical on-chip resources referenced by operation `reads` and `writes`;
- lifecycle endpoints that reference operations, loop boundaries, or named events;
- physical SMEM/TMEM allocations and intentional sequential reuse;
- explicit alias or separation assertions for configuration-sensitive layouts;
- source evidence for loop residency, reuse, and storage-layout decisions.

## Phase-local iteration names

Keep bootstrap indices and steady-state indices separate. A prologue uses
concrete seed names such as `K0` and `V0` because it shows what is loaded before
the loop begins. A representative mainloop uses its declared iterator, such as
`Kj` and `Vj`, plus only the adjacent iteration that explains overlap (`j+1` for
prefetch or `j-1` for a lagging consumer).

Do not carry `K0` or `V0` labels into a symbolic mainloop. Instead, declare the
prologue operations as the loop's `seed`, the consumed operands as `current`,
and any overlapped producer work as `next` or `previous`. On the first loop
entry, the seed supplies the current operands with `j=0`; subsequent entries
receive them from the adjacent iteration. This keeps one representative loop
iteration readable without pretending that the bootstrap happens every time.

Do not enter independent numeric lifetime bars. A resource lifetime is derived
from semantic references such as `load-q0:start`, `q-loop-release`, or
`kv-loop:end`. This keeps the operation graph and memory graph consistent.

## What belongs in the primary graph

Always show role ownership, major ordered operations, cross-role
synchronization, loop-carried data, pipeline stages, and SMEM/TMEM physical
lifetimes. Include shapes, layouts, instruction variants, barrier mechanisms,
and address or column formulas only when changing them would change correctness
or prevent reconstruction.

Do not collapse stage-indexed operations when they produce distinct objects or
have distinct consumers. If `Q0K -> S0` wakes softmax stage 0 and `Q1K -> S1`
wakes softmax stage 1, both MMA issues and both handoffs belong in the primary
timeline.

## What stays out

Do not put host launch plumbing, pointer arithmetic, every arithmetic
instruction, unmeasured cycle durations, speculative performance claims, or
every repeated loop iteration in the primary graph. Keep source locations,
variant alternatives, and longer rationale in the specification or topic
README unless they change how the displayed configuration must be read.

Unknown or conditional facts must not be silently guessed. Select one concrete
configuration, record its decision, and describe the alternate condition in a
storage relation or supporting note.
