# LLM SVG authoring contract

This repository expects an AI/LLM to create each specification-backed kernel
SVG directly. Automation may validate the spec, inspect SVG geometry, and render
the PNG companion; it must not choose the composition or emit SVG markup.

## Authoring packet

Before touching the SVG, load all of the following:

1. `AGENTS.md`;
2. the target kernel implementation and relevant helper/template code;
3. the topic JSON spec and, for a reconstruction view, the kernel JSON spec;
4. the applicable `authoring` brief or briefs;
5. `design/information-policy.md`;
6. `design/visual-grammar.md`;
7. the applicable QA profile in `src/gpu_graph/qa.py`;
8. the topic README and any existing SVG being revised.

The kernel code establishes facts. The topic spec pins code provenance and the
shared communication contract. A kernel spec records reconstruction-level
facts. The authoring brief states what this view must communicate. The visual
grammar guides composition. The QA profile defines machine-checkable SVG
structure.

## Direct-SVG rule

Write literal SVG markup into the declared `views[].output` file. Do not write or
invoke Python, JavaScript, Graphviz, Mermaid, plotting code, a template engine,
or another program that computes the SVG. The LLM owns every layout decision and
may revise any coordinate, path, label, grouping, or style directly.

The starter in `templates/kernel-svg.template.svg` demonstrates the semantic
hooks required by QA without prescribing a graph shape.

Every direct-authored root also carries `data-authoring="llm-direct"`,
`data-authoring-profile`, `data-topic-id`, `data-graph-id`, and
`data-source-id`. Topic QA uses these attributes to prove that all checked-in
SVGs are owned by a code-provenanced authoring contract.

## Semantic join contract

The SVG must be traceable back to the spec:

| SVG element | Required identity |
| --- | --- |
| Root `<svg>` | `data-kernel-id`, `data-view-id`, `data-qa-profile` |
| Phase label | `class="phase" data-section-id="…"` |
| Role label | `class="role" data-role-id="…"` |
| Operation group | `class="operation" data-operation-id="…"` |
| Synchronization path | `class="ready"` or `class="release"` plus `data-handoff-id="…"` |
| Synchronization label group | `class="handoff-annotation" data-handoff-id="…"` |
| Resource lifetime group | `class="resource-lifetime" data-resource-id="…"` |
| Lifetime bar | `class="life-box"` inside its resource group |
| Physical allocation label | `class="memory" data-allocation-id="…"` |

Use spec IDs exactly. Do not create display-only IDs that resemble semantic IDs.
Decorative elements need no semantic identity.

## Authoring sequence

1. Build a coverage ledger before laying out the graph.
   - List every item in `views[].authoring.required_content`.
   - Map each required statement to the operation, handoff, resource, phase, or
     note that will make it visible.
2. Choose the composition.
   - Follow the authoring brief's reading order and composition hint.
   - Treat width and shape as free variables; enlarge the canvas before reducing
     essential information or legibility.
   - Use exactly three top-level timeline phases: prologue, mainloop, and
     epilogue. Keep loop-tail/exit work inside the mainloop phase.
3. Establish large regions first.
   - Title/context, primary execution structure, synchronization, memory, and
     notes should have an explicit reading order.
   - Reserve annotation space before drawing connectors or labels.
4. Add semantic marks with their exact `data-*` identities.
5. Add labels, then route connectors behind labeled marks where practical.
6. Run `make svg-qa`, revise the SVG directly, and repeat until it passes.
7. Run `make qa`, inspect the PNG at fit-to-window and 100%, and inspect dense
   crops separately.

## Completion standard

The graph is complete only when:

- every authoring-brief requirement is visibly answered;
- every relevant semantic ID is represented exactly once where the QA profile
  requires it;
- labels remain legible without overlap or clipping;
- synchronization paths can be followed from producer to consumer;
- SMEM/TMEM lifetime and reuse claims match the spec;
- resource lifetimes are aligned to the same three-phase axis as role work;
- `make qa` passes; and
- manual inspection finds no density or reading-order failure.

If a visual failure can recur, strengthen the QA profile or this contract before
finishing. Do not add a generator to solve layout repetition.
