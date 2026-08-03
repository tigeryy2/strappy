---
name: review-test-suites
description: Review and clean up tests for durable, high-value behavioral coverage. Use during pull-request, branch, commit, working-tree, or code reviews to assess only tests and coverage relevant to the change; when asked to improve, simplify, consolidate, relocate, or remove tests; or when the user explicitly requests a full-repository test-suite audit. Never expand a change-focused review into a repository-wide test sweep without an explicit request.
---

# Review Test Suites

## Set the scope

Choose the narrowest scope supported by the request:

- For a PR, branch, commit, patch, or working-tree review, inspect changed tests and the tests needed to protect changed behavior. Respect any pinned base, head, diff, and changed-file contract from the parent review. Read nearby unchanged tests only as supporting context.
- For a named path or subsystem, stay within that behavior and its directly related tests.
- Audit the overall test suite only when the user explicitly requests a full, overall, entire-repository, or equivalent sweep. Do not initiate one merely because broader cleanup opportunities exist.

If this skill is one lane in a broader review, return test-specific findings to that review. Do not duplicate production-code findings except where necessary to explain a coverage defect.

## Establish the contract

1. Read repository guidance, test configuration, and documented test commands.
2. Identify canonical test locations and intended unit, integration, and end-to-end boundaries.
3. Trace the relevant production behavior before judging its tests. Determine the user-visible outcome, business rule, invariant, and failure modes.
4. Run focused tests or perform read-only checks needed to validate each suspected problem. Treat a passing test as evidence of execution, not evidence that it protects the right contract.

## Judge test value

Prefer tests that are:

- **Contract-focused:** protect outcomes and invariants rather than implementation shape.
- **Boundary-driven:** exercise real executors, persistence, transforms, routes, and other consequential boundaries.
- **Composed:** cover interactions where individually correct components can conflict.
- **Realistic and failure-oriented:** include ambiguity, retries, conflicts, partial writes, stale state, identity mismatches, and representative false positives or negatives.
- **Selective and economical:** keep only assertions and cases that guard meaningful regressions; delete weaker cases once stronger coverage subsumes them.
- **Stable:** tolerate harmless wording, styling, ordering, formatting, and refactoring changes.
- **Minimally mocked:** fake true external boundaries while keeping internal collaboration real.
- **Table-driven:** consolidate equivalent cases so edge coverage is visible.
- **User-visible where appropriate:** assert accessibility, navigation, decisions, and essential language rather than CSS or generated markup.
- **Clear and canonical:** make the business rule legible through the name, fixture, action, and expected result; place tests where maintainers expect to find and run them.

Treat these as warning signs:

- Assertions against graph node names, private helpers, call order, exact skeleton counts, CSS classes, generated HTML, or other implementation details.
- Large sets of prompt, message, or copy substring assertions that lock prose without protecting a required language contract.
- Mock-heavy wiring tests that prove calls occurred while bypassing real component collaboration.
- Overlapping positive and negative assertion shotguns where a few durable contracts would suffice.
- Thorough helper tests with no coverage of the real execution, write, or persistence boundary.
- Happy-path-only fixtures that omit plausible ambiguity, conflicts, and false matches.
- Repetitive standalone cases that obscure an equivalent table-driven rule.
- Exact ordering, counts, formatting, markup, or intermediate values treated as requirements without product evidence.
- Independently tested components with no composed coverage at their conflict points.
- Tests outside the repository's canonical test tree without a documented reason.
- Tests that preserve obsolete assumptions, codify a defect, or pass while the real behavior remains broken.

Confirm whether precision is intentional before criticizing it. Exact copy, order, markup, call sequence, or counts can be valid contracts when accessibility, protocols, compliance, snapshots, migrations, or explicit product requirements depend on them.

## Review or clean up

For a review-only request:

1. Report only concrete, actionable findings.
2. For each finding, cite the test and relevant production boundary, explain the regression that can escape or the false confidence created, and describe when it matters.
3. Rank behavior gaps above maintainability smells. Do not report taste-only rewrites.
4. Recommend deletion only when the test is redundant or obsolete, or when stronger replacement coverage is specified.

For an implementation or cleanup request:

1. Add or strengthen the behavioral, boundary, or composed test first when removing a weaker test would create a gap.
2. Consolidate duplicated cases and assertions; remove obsolete fixtures, mocks, helpers, snapshots, and tests made redundant by the stronger contract.
3. Relocate tests only after confirming the canonical tree and updating imports, discovery configuration, and documentation that actually requires the old location.
4. Keep changes focused. Do not redesign production code merely to make testing easier unless the user requested that work and the design defect is demonstrated.
5. Run the smallest relevant test command, then the broader affected suite when practical. Report commands and anything not verified.

## Output

Lead with findings, highest severity first. Use file and line references where possible. State explicitly when no actionable findings remain. Finish with a short scope and verification summary; for cleanup work, include what was consolidated or deleted and why.
