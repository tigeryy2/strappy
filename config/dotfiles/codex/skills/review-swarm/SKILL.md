---
name: review-swarm
description: Review open code changes with an independent multi-agent swarm and a consolidation pass. Use when Codex needs to review staged, unstaged, and untracked changes before commit or PR; when the user wants prioritized findings from multiple review angles; or when changes should be checked against the likely merge target and the current implementation on that target branch.
---

# Review Swarm

## Overview

Run a read-only swarm review of the current working tree. Cover staged, unstaged, and untracked files; use independent subagents with different review angles plus one parallel Sol xhigh second-opinion subagent; then consolidate overlap, disagreement, and severity into one report.

## Preflight

1. Confirm there are open changes with `git status --short`.
2. Capture the review scope with:
   - `git branch --show-current`
   - `git diff --stat --staged`
   - `git diff --stat`
   - `git ls-files --others --exclude-standard`
3. If there are no open changes, stop and say there is nothing to review.
4. Keep the entire swarm read-only. Do not edit files, stage changes, or run destructive git commands.
5. Use fresh subagent threads. Do not share one agent's conclusions with another before consolidation.
6. The primary agent reads applicable AGENTS instructions, skills, memories, and historical context. Give reviewers a compact, self-contained scope brief; do not ask them to reread those sources unless the assigned review specifically depends on them.

## Scope Contract

Before spawning reviewers, define the exact review root and diff scope:

- `reviewRoot`: absolute path of the checkout/worktree being reviewed
- `baseRef`: the merge target ref, such as `origin/main`, `github/main`, or `develop`
- `headRef`: the reviewed ref, usually `HEAD`
- `diffExpr`: the exact comparison, such as `<baseRef>...<headRef>`
- `changedFiles`: output of `git -C <reviewRoot> diff --name-only <diffExpr>` plus any staged/unstaged/untracked files in scope

Pass these values to every subagent. Instruct reviewers to verify
`git -C <reviewRoot> rev-parse --show-toplevel`, `git -C <reviewRoot> rev-parse <baseRef>`,
`git -C <reviewRoot> rev-parse <headRef>`, and the changed-file list before
reviewing. If the check does not match the assigned scope, the reviewer should
stop and report `scope mismatch`.

For PR reviews from an isolated clone/worktree, all shell commands in reviewer
prompts must use `git -C <reviewRoot>` or run with `workdir` set to
`reviewRoot`. Do not rely on ambient cwd.

Findings should be limited to files in `changedFiles`. A reviewer may cite an
unchanged file only as supporting evidence for a bug caused by a changed file.
Drop findings whose primary defect is outside the assigned diff.

## Design & Code Guidelines

### Tests

- Ensure that tests are intentional and provide real value. It is important to avoid tests that don't provide useful coverage or simply lock in unimportant implementation details
- Tests commited to the codebase should be selected carefully with extreme selectivity & intetionality.
- Tests should validate and guard core logic and flows.

### UI

- Ensure that UI uses visual hierarchy, reject over use of nested cards or boxes
- Avoid overuse of eyebrows, overlines, and subtitles
- Ensure that a consistent spacing scale is used, no arbitrary spacing unless a specific constraint requires it
- Ensure that even if the UI was in a different language that the user couldn't read, the spacing & context would allow them to infer the primary actions & interactions

### Obvious Solution Checklist

- Check that the change solves a demonstrated problem, not a hypothetical future need.
- Flag speculative abstractions, configuration, extension points, and fallback behavior.
- Look for a simpler solution that still provides the required functionality and performance.
- Prefer established project patterns over clever or novel machinery.
- Challenge indirection that does not reduce meaningful complexity.
- Flag bolted-on special cases that suggest the underlying design is wrong.
- Confirm complexity is justified by an actual constraint, requirement, or measured bottleneck.
- Ensure simplification does not trade away correctness, functionality, performance, or maintainability.
- Push back when the implementation overlooks a more direct and obvious approach.
- Final question: **Is this the simplest complete solution to the problem we actually have?**

### Erasure Review Checklist

- Identify duplicated concepts, logic, abstractions, or sources of truth that should be unified.
- Flag dead code, unused files, obsolete branches, stale compatibility paths, and redundant configuration.
- Prefer reuse of existing code over introducing parallel helpers or abstractions.
- Challenge additions that solve no demonstrated requirement.
- Flag tangled or surprising code; confusion often indicates a poor abstraction.
- Check whether the change fixes the root cause or merely shields the symptom with a special case.
- For every `X → Y` replacement, verify `X` is fully removed unless compatibility was explicitly required.
- Confirm obsolete syntax, behavior, APIs, flags, and data shapes are removed from:
  - Implementation
  - Tests and fixtures
  - Documentation and examples
  - Configuration and migrations
- Ensure tests for superseded behavior were deleted or rewritten—not retained, skipped, or weakened.
- Remove stale comments; rewrite only those still needed to explain intent.
- Remove completed TODOs and references to resolved work.
- Check for documentation describing decommissioned systems, retired workflows, or obsolete rules.
- Verify links and references to deleted or renamed material were updated.
- Prefer compression: fewer concepts, branches, files, and rules while preserving required behavior.
- Treat deletion and simplification as valuable outcomes, not incidental cleanup.
- Final question: **What did this change make obsolete, and was all of it removed?**

## Agent Layout

Spawn exactly five primary review subagents and, in parallel, one read-only Sol xhigh second-opinion subagent. Keep prompts short and independent. Give each reviewer the task and raw repo context it needs, but not your conclusions or another reviewer's output.

Every spawn must set `fork_turns: "none"`; the scope contract in the prompt replaces conversation inheritance. Never rely on the full-history default.

Use the same base model as the main agent for the five primary reviewers. The designated Sol xhigh second-opinion reviewer is the intentional model exception; do not introduce other model variation.

Keep reasoning effort flexible, but favor the active setting from the main agent. Only raise or lower it when a specific review angle clearly benefits, and keep that choice intentional rather than using model variation as a review tactic.

### Agents 1-2: Standard Review

Ask each agent to review the current uncommitted changes and return prioritized findings only.

Require:
- include staged, unstaged, and untracked files
- focus on bugs, regressions, risky edge cases, missing tests, and incorrect assumptions
- cite file/line references when possible
- keep the summary brief
- consider not only issues in the implementation but the direction/high level design chosen itself

Example prompt:

`Review only this scope: reviewRoot=<absolute path>, diffExpr=<baseRef>...HEAD, changedFiles=<list>. First verify the root, base/head SHAs, and changed-file list. If they do not match, stop with scope mismatch. Read-only only. Return prioritized findings with file/line refs where possible. Focus on bugs, regressions, missing tests, and risky assumptions. Do not report primary findings outside changedFiles unless citing unchanged support for a changed-file bug.`

### Agent 3: Complexity Fit Review

Ask the agent to judge whether the implementation complexity fits the problem and the codebase.

Require:
- identify overbuilt and underbuilt areas
- distinguish necessary complexity from speculative abstraction
- call out missing simplifications or missing structure only when concrete
- report only actionable findings

Example prompt:

`Assess only this scope: reviewRoot=<absolute path>, diffExpr=<baseRef>...HEAD, changedFiles=<list>. First verify the root, base/head SHAs, and changed-file list. Judge whether the changed implementation is overbuilt, underbuilt, or right-sized for this project. Return only actionable findings whose primary defect is in changedFiles.`

### Agents 4-5: Target-Branch Deep Review

Ask each agent to:

1. infer the most likely merge target branch
2. identify touched flows, data paths, functions, and call sites
3. understand how those flows work on the target branch
4. review the working tree changes in that context

Require:
- state the exact target branch assumption and why
- compare changed behavior against target-branch behavior
- look for missed updates, integration gaps, hidden side effects, and behavior drift
- include file/line references when possible
- for new files, inspect the nearest existing entry points and callers on the target branch

Example prompt:

`Review only this scope: reviewRoot=<absolute path>, diffExpr=<baseRef>...HEAD, changedFiles=<list>. First verify the root, base/head SHAs, and changed-file list. State the target branch assumption. Map the flows touched by changedFiles, inspect target behavior with git -C <reviewRoot> show <baseRef>:path as needed, then review the changes in that context. Return prioritized findings with file/line refs. Do not report primary findings outside changedFiles unless citing unchanged support for a changed-file bug.`

### Parallel Sol xhigh Second Opinion

Run the second-opinion subagent at the same time as the five primary reviewers, not after the initial swarm finishes.

- Spawn with `model: "gpt-5.6-sol"`, `reasoning_effort: "xhigh"`, and `fork_turns: "none"`.
- Keep it read-only and tightly scoped to the same immutable review contract.
- Require exact root, base/head SHA, diff, and changed-file verification before review; stop with `scope mismatch` on any mismatch.
- Ask it to inspect only the assigned diff, untracked files in scope, and directly relevant tests or subsystems at risk.
- Do not share primary-reviewer findings, candidates, or conclusions; preserve independence.
- Return prioritized findings only, with file/line references where possible.

Default prompt:

`Review only this assigned scope: reviewRoot=<absolute path>, baseRef=<baseRef>, headRef=<headRef>, diffExpr=<diffExpr>, changedFiles=<list>. First verify the review root, base/head SHAs, and changed-file list; stop with scope mismatch if they differ. Read-only. Focus on bugs, regressions, permissions/security, migrations, missing tests, and performance-shape issues in changedFiles. Do not report primary findings outside changedFiles unless citing unchanged support for a changed-file bug. Return prioritized findings only with file/line refs where possible.`

## Target Branch Heuristics

Use the smallest reliable heuristic set:

1. Start with `git branch --show-current`.
2. Check whether `develop`, `main`, or `master` exist locally or on `origin`.
3. Default rules:
   - if the current branch is `develop`, target `main` when it exists
   - if the current branch is a feature or topic branch, target `develop` when it exists
   - otherwise target `main` when it exists, then `master`
4. If the repo state suggests something else, state the assumption explicitly instead of pretending certainty.

When agents need target-branch file contents, prefer direct inspection such as `git show <target>:path/to/file` plus local call-site reads. Do not rely only on the current working tree.

## Consolidation

After all five primary reviewers and the parallel Sol xhigh second opinion finish:

1. Combine all findings into one list.
2. Merge duplicates.
3. Track agreement:
   - note when multiple agents independently found the same issue
   - note when a finding came from only one angle
   - note material disagreement or uncertainty
4. Re-rank by severity and confidence, not by which agent found it.
5. Drop weak or purely stylistic comments unless they expose a real risk.
   Also drop out-of-scope findings whose primary defect is outside the assigned
   `changedFiles`, even if a reviewer found a real issue elsewhere.
6. Create a candidate findings list. Do not send the final review yet.
7. Track which findings came from the Sol xhigh second opinion alone versus from the five primary reviewers.
8. If there are no candidate findings, skip the validation round and say there
   are no findings.

## Validation Round

After consolidation and before the final answer, independently validate every candidate finding that may appear in the final review.

1. Spawn one fresh independent validation subagent for the complete ordinary candidate list, with `fork_turns: "none"` and a compact brief containing for each candidate:
   - where to look
   - the suspected issue
   - suspected severity / scope
   - a request to confirm whether the issue is real, not real, or needs caveats
2. Spawn a dedicated independent validator for an individual P0/P1 only when it involves security, authorization, destructive data changes, or similarly high-consequence behavior.
3. Do not share reviewer identities, vote counts, or conclusions with validators; provide only the candidate evidence that needs checking.
4. Drop findings that fail validation.
5. Adjust severity, scope, and wording when validation narrows or expands the issue.
6. Keep the final answer in code-review form: findings first, then open questions or assumptions, then a short coverage summary.
7. If no findings survive validation, say so explicitly and mention residual risk or unreviewed areas.

## Output Contract

Use this structure:

- `Findings`
- `Open questions / assumptions`
- `Coverage`

In `Findings`, each item should include:

- severity
- concise problem statement
- why it matters
- when/in what situations would the problem occur
- file reference
- whether it had multi-agent agreement

In `Coverage`, include:

- whether the full 5-agent swarm ran
- whether the Sol xhigh second-opinion subagent ran in parallel with the swarm
- which angles ran: standard x2, complexity x1, target-branch x2
- whether ordinary findings were batch-validated and which high-consequence findings received dedicated validation
- any findings dropped or materially changed after validation
- any fallback or missing pass

If subagents are unavailable for either the initial swarm or the validation
round, fall back to the best available review and state exactly which coverage
was reduced.

## Example Requests

- `Use $review-swarm to review the current uncommitted changes before I commit.`
- `Use $review-swarm and tell me if these open changes are missing anything against develop.`
- `Use $review-swarm to review my working tree and flag overbuilt parts.`
