---
name: simplicity-review
description: Review a completed change in hindsight or audit a codebase for high-leverage simplification using Rich Hickey's distinction between simple and easy. Use when asked to step back after implementation, identify complected concerns, surface design unease, or stack-rank simplification opportunities. This is an analysis workflow; do not refactor unless the user separately asks.
---

# Simplicity Review

Judge the artifact now visible, not how pleasant it was to write. Seek simplicity
in Rich Hickey's sense: concerns that can be understood, changed, tested, and
operated independently. Complexity is complecting—interleaving things that do not
have to move together. Easy means familiar or near at hand; it is not evidence of
simplicity. Fewer lines, files, types, or components are not inherently simpler.

Use the smallest applicable scope:

- **Change retrospective:** compare a completed change with its baseline.
- **Codebase audit:** map the codebase, explore each meaningful area, evaluate
  the strongest simplification candidates, and stack-rank them.
- **Combined review:** run both when the request covers the change and its wider
  design context.

Remain read-only unless the user explicitly asks for implementation.

## Establish the evidence

Resolve the repository root and the exact scope before judging it. For a change,
identify the baseline, current state, changed files, original intent, and any
available plan or decision record. For a codebase audit, identify architectural
areas by responsibility and runtime boundary rather than mechanically assigning
one directory per area.

Build a compact map of:

- responsibilities and owners;
- state and data flow;
- public interfaces and dependency direction;
- policy, mechanism, timing, and deployment boundaries;
- areas with high change frequency, incident history, duplicated decisions, or
  expensive tests.

Do not confuse unfamiliar code, personal taste, file size, or style violations
with complexity. Require a concrete braid: two or more concerns forced to vary,
fail, deploy, test, or be understood together without a domain reason.

## Change retrospective

Take a step back once the whole implementation is visible.

1. Reconstruct where the design started and what the change intended to improve.
2. Classify the result:
   - **Improved the design:** removed an entanglement or made boundaries clearer.
   - **Fit the design:** delivered the behavior without materially improving or
     degrading the surrounding structure.
   - **Degraded the design:** added coupling, duplicated authority, widened state,
     or made future change harder.
3. Ask what became obsolete. Find superseded branches, compatibility paths,
   abstractions, tests, comments, TODOs, docs, state, and configuration that the
   change should have erased.
4. Separate:
   - problems introduced by this change;
   - pre-existing problems exposed by this change;
   - deliberate tradeoffs that remain justified.
5. Name hindsight pushback. Where did the reasoning, sequencing, scope, or
   execution take a wrong turn, even if the final code is acceptable?
6. Surface hunches. Label them as unproven, state the observation that prompted
   the unease, and name the cheapest evidence that would confirm or dismiss it.

Do not invent criticism to make the retrospective look balanced. A sound change
may simply fit or improve the design.

## Codebase audit

Fan out read-only explorer agents across the mapped areas. Give each agent a
compact brief containing the repository root, its bounded area, the simplicity
definition above, and the output contract below. Do not make agents repeat global
setup or history discovery.

Each explorer returns its single best simplification recommendation, plus at most
one labeled hunch. Require:

- the concerns currently complected;
- concrete files, symbols, flows, or change evidence;
- why the concerns need not move together;
- the smallest structural move that separates them;
- what can be deleted as a result;
- expected benefit, implementation cost, migration risk, and uncertainty;
- whether the issue was introduced by the current change or merely exposed by it.

Agents should return `no strong candidate` when the evidence is weak. Coverage is
more valuable than manufacturing a recommendation for every area.

Merge duplicates into candidate themes. Then explore and evaluate every retained
candidate against its actual callers, data flow, tests, ownership, and deployment
boundary. Reject candidates that merely:

- replace familiar code with fashionable machinery;
- move complexity behind another layer without removing an entanglement;
- optimize line count, DRYness, or aesthetic symmetry;
- introduce a framework, generic abstraction, or compatibility path without a
  present requirement;
- split things that must change atomically because of a real domain invariant;
- offer benefits too speculative to justify migration and regression risk.

Use focused follow-up exploration when evidence is missing. Do not let the first
agent's confidence determine the verdict.

## Rank by leverage

Stack-rank validated candidates by judgment, not a decorative numeric score.
Weigh:

1. strength and breadth of the entanglement removed;
2. frequency and cost of changes through the area;
3. correctness, reliability, security, and operability gains;
4. amount of obsolete code, state, or policy erased;
5. implementation and migration effort;
6. regression risk and reversibility;
7. confidence in both the diagnosis and the proposed boundary.

Prefer a smaller, well-evidenced separation with a clear deletion path over a
grand redesign whose benefits depend on future needs. Call out prerequisites
when they materially change ranking.

## Output

Lead with the overall design judgment. Then provide:

1. **Retrospective** — better, fitted, or worse; introduced vs exposed problems;
   hindsight pushback; obsolete pieces still present.
2. **Stack-ranked simplifications** — for each: target, complected concerns,
   evidence, smallest separating move, deletion unlocked, leverage, cost/risk,
   confidence, and why it ranks there.
3. **Hunches** — unproven unease, trigger, and next evidence to collect.
4. **Rejected candidates** — appealing ideas that did not survive evaluation and
   why.
5. **Coverage** — areas explored, agents completed or blocked, scope gaps, and
   verification performed.

If only one review mode applies, omit irrelevant sections. Keep observations,
inferences, and recommendations distinguishable. Never present a hunch as a
finding.
