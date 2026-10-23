---
name: review-test-suites
description: Coordinate a small team of test-review subagents, or act as one, to identify low-signal, implementation-coupled, flaky, or disproportionately slow tests and agree on focused cleanup. Use for PR, branch, commit, working-tree, or named-subsystem test reviews and cleanup. Audit the entire repository only when explicitly requested.
---

# Review Test Suites

Use read-only scouts to find candidates, then discuss the evidence with the main agent before removing or changing tests. Optimize for durable behavioral coverage per unit of maintenance and runtime cost, not test count or deletion quotas.

## Roles and scope

**Main agent:** establish the scope and shared context, delegate inspection, reconcile recommendations with the scouts, and own the final cleanup decision and verification.

**Scout subagent:** inspect only the assigned scope, report evidence and recommendations, and participate in follow-up discussion. During inspection, do not edit files or spawn more agents. If this skill is assigned as one lane of a broader review, follow that coordinator's scope and return findings to it; do not start another team.

Choose the narrowest scope supported by the request:

- For a PR, branch, commit, patch, or working-tree review, inspect changed tests and tests protecting changed behavior. Honor the parent's pinned base, head, diff, and changed-file contract. Read nearby unchanged tests and production code as supporting context; do not turn them into an unrelated cleanup backlog.
- For a named path or subsystem, stay within its behavior and directly related tests.
- Audit the whole repository only when explicitly requested.

Keep review-only work read-only. A request to use this skill does not by itself authorize cleanup, commits, or PR publication.

## Delegate inspection

The main agent reads relevant repository guidance, test configuration, canonical test locations, and documented commands once. Give scouts a compact brief with the exact scope, shared guidance, relevant production entrypoints, allowed checks, and review-only or cleanup mode. Scouts verify local details as needed without repeating broad discovery.

Use a small team, usually two or three scouts. Divide by coherent test areas, or use complementary lenses on a small shared scope:

- **Signal and coupling:** tautologies, tests that mirror implementation, mock-only wiring, brittle assertions, and obsolete assumptions.
- **Coverage and redundancy:** duplicated contracts, stronger surviving coverage, missing consequential boundaries, and what each proposed deletion would lose.
- **Reliability and cost:** order dependence, timing races, uncontrolled external dependencies, expensive fixtures, repeated setup, and runtime out of proportion to coverage value.

Scale assignments to the work; do not invent extra scope to occupy agents. When a parent already provides reviewers, use that team for discussion. If delegation is unavailable, perform the same checks directly and disclose that no subagent agreement occurred.

## Inspect and substantiate

Trace the relevant production behavior before judging a test: user-visible outcome, business rule, invariant, execution or persistence boundary, and plausible failure modes. A passing test proves execution, not that it protects the right contract.

Look for:

- Assertions against private helpers, graph nodes, call order, skeleton counts, CSS classes, generated markup, or intermediate values without a product contract.
- Prompt or copy substring shotguns; mocks that bypass the collaboration being tested; expected results computed with the same logic as production.
- Duplicate cases or snapshots that add no distinct regression protection; obsolete behavior; tests that pass while the real boundary remains broken.
- Reliance on wall-clock timing, sleeps, shared mutable state, test order, randomness, network availability, or environment-specific resources.
- Repeated costly setup, broad integration runs for a narrow rule, or large fixtures with little additional coverage.

These are leads, not verdicts. Exact copy, order, counts, markup, and calls can be required by accessibility, protocols, compliance, migrations, or explicit product requirements. Integration tests and large fixtures can justify their cost. Prefer minimally mocked, realistic coverage of meaningful outcomes, composed behavior, and failure paths.

Use focused tests, existing CI history, timings, or read-only code analysis to substantiate candidates. Report what was observed and what remains a hypothesis. Do not call a test flaky because of one failure, or slow solely because of its size or test type. Avoid unbounded reruns or benchmarks.

For each actionable candidate, return:

- Test file/line and relevant production boundary; the contract the test is intended to protect.
- Concrete weakness and when it causes false confidence, maintenance churn, intermittent failure, or excessive cost; include evidence and check results.
- Proposed action: keep, delete, consolidate, or repair. For deletion, identify stronger surviving coverage by reference, explain why the behavior is obsolete, or demonstrate that the test protects no meaningful contract.
- Unique coverage at risk, any prerequisite replacement, related fixtures/mocks/helpers/snapshots that become unused, and uncertainty or counterarguments.

An empty candidate list is valid. Do not manufacture findings, or expand into unrelated production-code review.

## Discuss and decide before editing

The main agent consolidates duplicate candidates and checks recommendations against implementation intent and the actual coverage. Send the proposed dispositions, supporting evidence, and open questions back to the scouts. Ask them to challenge the deletion rationale, identify lost coverage, and confirm or revise the associated cleanup. This is a discussion, not a vote or automatic acceptance of scout output.

Resolve ordinary candidates together in one discussion batch. Investigate further only where a concrete disagreement warrants it. Before a change, the main agent and the relevant scouts must agree on the disposition and any prerequisite coverage or cleanup. Keep or defer unresolved candidates and explain the disagreement; do not force consensus or delete while the decision is pending. Lack of a response is not agreement.

For review-only work, stop with the agreed recommendations and any unresolved candidates. For cleanup work, proceed with the agreed changes within the user's authorized scope; scout consensus does not grant additional authority.

## Clean up and verify

1. Where a candidate protects a meaningful contract that would otherwise be lost, establish stronger behavioral coverage first. Do not add a replacement merely to preserve a tautology, obsolete behavior, or test count.
2. Make the agreed deletions, consolidations, or repairs. Remove fixtures, mocks, helpers, snapshots, and imports made unused by those changes; check for other consumers first. Delegate edits only with explicit, non-overlapping ownership.
3. Prefer fixing a valuable flaky or slow test's cause over deleting its unique coverage, disabling it, adding retries, or inflating timeouts. Consolidate equivalent cases only when the distinct failure paths remain legible.
4. Relocate tests only when needed to follow repository conventions, updating imports and discovery configuration. Do not redesign production code merely to simplify tests unless that work was requested and justified.
5. Run the smallest affected test command, then the broader affected suite when practical. Check that surviving coverage still exercises the intended contract, not merely that fewer tests pass.

## Output

Lead with agreed actionable findings or completed cleanup, most consequential first. Include file references, the triggering conditions, the decision, and surviving or replacement coverage. State explicitly when there are no actionable findings. Finish with concise scope and verification results, any deferred disagreements, and what was removed or consolidated and why. Distinguish measured flakiness or cost from unverified suspicions; do not claim agreement or validation that did not occur.
