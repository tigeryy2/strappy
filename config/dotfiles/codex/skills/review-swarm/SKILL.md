---
name: review-swarm
description: Review open code changes with an independent multi-agent swarm, history-aware repeat-review modes, and independent validation. Use for first-pass exhaustive reviews, moved-head rechecks, same-head variance reviews, or supplied-finding evaluation before commit or merge.
---

# Review Swarm

## Overview

Run a read-only, evidence-backed review of the exact assigned change set. Preserve
independent discovery for the first exhaustive review. On later reviews, let the
primary agent reuse compact prior review receipts while keeping blind discovery
reviewers free from prior conclusions.

To validate your findings, you are explicitly allowed to:
1. read from production or preview data (if preview exists and is populated) to validate the current real state
2. write and run temporary scripts or tests (do not mutate prod data)

Choose one mode before spawning agents:

- **Full review:** first review of the exact head, an explicitly requested fresh
  exhaustive re-review, or a moved head whose delta materially changes the
  reviewed surface.
- **Moved-head delta:** a prior full review exists and the new delta is bounded
  enough to revalidate prior findings plus inspect the repair safely.
- **Same-head variance:** the exact head already received a complete full review.
  Re-attest scope and run only limited blind variance coverage unless the user
  explicitly requests another exhaustive review.
- **Supplied-finding evaluation:** the user provides concrete findings and asks
  whether they are real. Use one batch validator rather than a discovery swarm.

Read [references/review-history.md](references/review-history.md) before a
same-head, moved-head, or supplied-finding review. A first review with no relevant
receipt does not need that reference.

## Coordinator preflight

The primary agent owns setup, history lookup, mode selection, and consolidation.
Do not make every reviewer repeat this work.

1. Resolve the exact review root, base ref, head ref, immutable base/head SHAs,
   diff expression, and changed files.
2. For working-tree review, include staged, unstaged, and untracked files. Stop
   if there are no open changes.
3. For a PR, use an isolated worktree and verify the actual target branch.
4. Search only for compact prior review receipts matching this repository and
   head, or a directly preceding head. Do not broadly load raw prior transcripts.
5. Select the review mode using the rules above. State the mode and why before
   spawning reviewers.
6. Keep the review read-only. Do not edit files, stage changes, or run destructive
   git commands.
7. The primary reads applicable AGENTS instructions, skills, memories, and
   historical context. Reviewers receive compact briefs and do not repeat that
   discovery unless their assigned lens explicitly requires it.

## Scope contract

Define and pass:

- `reviewRoot`: absolute checkout/worktree path
- `baseRef` and immutable `baseSha`
- `headRef` and immutable `headSha`
- `diffExpr`: exact comparison
- `changedFiles`: exact in-scope file list

Each reviewer performs one bounded scope attestation:

- verify the repository root and base/head SHAs;
- verify the changed-file list or its supplied fingerprint;
- stop with `scope mismatch` if the contract differs.

Do not ask every reviewer to refetch PR metadata, search memories, reconstruct the
target branch, install dependencies, or rediscover the review history. The
coordinator supplies those facts. For isolated reviews, use `git -C <reviewRoot>`
or set `workdir=<reviewRoot>`; never rely on ambient cwd.

Findings must have their primary defect in `changedFiles`. Unchanged files may be
cited only as supporting evidence for a changed-file bug.

## Independence and history

History is coordinator context, not shared discovery context.

- Blind discovery reviewers receive the immutable scope, role, and raw repository
  evidence needed for that role—but no prior findings, reviewer votes, or earlier
  conclusions.
- A designated continuity reviewer may receive the compact prior receipt. It
  checks moved-head repairs, surviving findings, regressions, and coverage gaps.
- Validators receive candidate evidence for and against a finding, but not
  reviewer identity, vote count, or the coordinator's desired conclusion.
- Never ask delegated reviewers to load complete prior sessions. If the compact
  receipt is insufficient, the coordinator extracts only the missing fact.

This separation preserves reviewer variance while preventing every child agent
from paying for and anchoring on the same historical context.

## Mode-specific agent layout

Every spawn must set `fork_turns: "none"`. Use the same base model as the primary
unless a role below explicitly requires Sol xhigh.

### Full review

Preserve the exhaustive first-review layout:

1. Two independent standard reviewers.
2. One complexity-fit reviewer.
3. Two target-branch deep reviewers.
4. One parallel `gpt-5.6-sol` xhigh second opinion.

All six remain blind to prior conclusions. Keep prompts short and independent.
If a relevant earlier receipt exists for an ancestor head, add one continuity
reviewer only when the moved history materially affects correctness; do not make
the six blind reviewers history-aware.

### Moved-head delta

Use the smallest review that preserves the original coverage contract:

1. One continuity reviewer receives the prior receipt and exact old-head-to-new-
   head delta. It classifies prior findings as fixed, surviving, regressed, or
   uncertain and checks whether fixes introduced new defects.
2. One blind delta reviewer independently inspects the same delta without prior
   findings.
3. Add a specialized blind reviewer only when the delta touches security,
   authorization, migrations, destructive data behavior, or another distinct
   high-risk boundary.

Escalate to a full review when the delta changes ownership, architecture,
permissions, schema shape, deployment topology, or enough files/flows that the
old coverage no longer represents the current change.

### Same-head variance

Do not repeat the complete swarm automatically.

1. Re-attest the immutable head, base, changed files, CI, and current comments.
2. Reuse the earlier receipt and completed validation results.
3. Run one blind variance reviewer by default; use two for security,
   authorization, migrations, destructive data behavior, or when the previous
   receipt records a meaningful coverage gap.
4. Assign a lens not already duplicated at the same model/effort. Do not rerun an
   identical Sol second-opinion lane merely because a new task was opened.
5. Run another full swarm only when the user explicitly requests a fresh
   exhaustive re-review or the prior receipt is incomplete/untrustworthy.

Negative prior results remain evidence, not proof. Limited blind variance exists
specifically to catch reviewer stochasticity and previously missed findings.

### Supplied-finding evaluation

This is validation, not discovery.

1. Give one fresh independent validator the complete ordinary finding batch.
2. Ask for `real`, `not real`, or `caveated` verdicts with execution path,
   conditions, consequence, severity, and smallest remedy.
3. Use a dedicated additional validator only for an individual P0/P1 involving
   security, authorization, destructive data changes, or similarly high-
   consequence behavior.
4. Do not launch the full six-agent discovery swarm unless the user separately
   requests a full review.

## Full-review lenses

### Standard reviewers

Focus on bugs, regressions, risky edge cases, missing tests, incorrect
assumptions, and whether the direction itself is sound. Include staged,
unstaged, and untracked files where applicable. Return prioritized findings only,
with file/line references when possible.

### Complexity-fit reviewer

Judge whether the implementation is overbuilt, underbuilt, or right-sized.
Identify speculative abstractions, missing simplifications, bolted-on special
cases, duplicated concepts, and missing structure only when concrete. Return only
actionable findings.

### Target-branch deep reviewers

Map touched flows, data paths, functions, callers, and target-branch behavior.
Look for missed updates, integration gaps, hidden side effects, and behavior
drift. State the target-branch assumption and inspect the nearest existing entry
points for new files.

### Sol xhigh second opinion

Spawn in parallel with `model: "gpt-5.6-sol"`,
`reasoning_effort: "xhigh"`, and `fork_turns: "none"`. Keep it blind,
read-only, and scoped to the same immutable contract. Ask for prioritized bugs,
regressions, permission/security problems, migration risks, missing tests, and
performance-shape problems.

## Design and code standards

### Tests

- Keep only intentional tests that guard important behavior.
- Reject coverage that merely locks in implementation details.
- Check asymmetry, absence, error paths, and the real integration boundary.

### UI

- Use visual hierarchy and a consistent spacing scale.
- Reject unnecessary nested cards, eyebrows, subtitles, and arbitrary spacing.
- Ensure hierarchy and primary actions remain inferable without reading labels.

### Obvious solution and erasure

- Check that the change solves a demonstrated problem.
- Prefer established project patterns and the simplest complete solution.
- Flag speculative infrastructure, extension points, and fallback behavior.
- Identify duplicated concepts, dead code, obsolete branches, compatibility
  paths, stale comments, completed TODOs, and superseded tests/docs.
- For every `X -> Y` replacement, verify `X` is fully removed unless explicitly
  retained.
- Ask: what did this change make obsolete, and was all of it removed?

## Consolidation

After the selected mode's reviewers finish:

1. Merge duplicates and separate genuinely independent agreement from repeated
   restatement.
2. Re-rank by execution consequence, severity, and confidence—not reviewer
   identity or vote count.
3. Drop weak, stylistic, speculative, and out-of-scope findings.
4. Record disagreements and negative coverage that materially affect confidence.
5. Create the candidate list. Do not report it as final before validation.

When an agent is interrupted or blocked, preserve its completed evidence before
retrying. Prefer a follow-up to the same agent when possible. If replacement is
required, give the replacement the usable raw evidence but not the interrupted
agent's conclusion. Never pay for a complete restart merely because the first
agent failed to format a final verdict.

## Validation

For a full, moved-head, or same-head review:

1. Batch all ordinary candidates into one fresh independent validator.
2. Add a dedicated validator only for an individual high-consequence P0/P1 as
   defined above.
3. Drop failed candidates and narrow severity/scope when evidence requires it.
4. If no candidates exist, skip validation and report the residual coverage.

Do not add a second validation round merely because the review mode reused prior
history. Reuse a prior validation result only when the exact head and relevant
code are unchanged.

## Review receipt

At completion, emit the compact receipt described in
[references/review-history.md](references/review-history.md). Do not write it
into the reviewed repository. Persist it through task history or memory only when
the surrounding environment authorizes that write.

The receipt is the cross-task deduplication boundary. It must be sufficient for a
future coordinator to identify the exact reviewed head, completed coverage,
surviving/dropped findings, validation status, and known gaps without loading raw
review transcripts.

## Output contract

Use:

- `Findings`
- `Open questions / assumptions`
- `Coverage`
- `Review receipt`

Each finding includes severity, concise defect, triggering conditions,
consequence, smallest proportionate remedy, file reference, and independent
agreement status.

Coverage includes:

- selected mode and why;
- receipt reused, if any;
- exact base/head and changed-file scope;
- reviewers run, skipped, interrupted, or replaced;
- validation performed and candidates dropped/narrowed;
- tests or live verification inspected;
- residual gaps.

If subagents are unavailable, perform the best available review and state the
reduced coverage precisely.
