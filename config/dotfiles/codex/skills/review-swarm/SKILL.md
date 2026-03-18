---
name: review-swarm
description: Review open code changes with an independent multi-agent swarm and a consolidation pass. Use when Codex needs to review staged, unstaged, and untracked changes before commit or PR; when the user wants prioritized findings from multiple review angles; or when changes should be checked against the likely merge target and the current implementation on that target branch.
---

# Review Swarm

## Overview

Run a read-only swarm review of the current working tree. Cover staged, unstaged, and untracked files; use independent subagents with different review angles; then consolidate overlap, disagreement, and severity into one report.

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

## Agent Layout

Spawn exactly five subagents. Keep the prompts short and independent. Give each agent the task and raw repo context it needs, but not your conclusions.

Use the same base model as the main agent for every subagent in the swarm. Do not mix model families within one review. Example: if the main agent is running on `gpt-5.4`, spawn all review subagents on `gpt-5.4` as well.

Keep reasoning effort flexible, but favor the active setting from the main agent. Only raise or lower it when a specific review angle clearly benefits, and keep that choice intentional rather than using model variation as a review tactic.

### Agents 1-2: Standard Review

Ask each agent to review the current uncommitted changes and return prioritized findings only.

Require:
- include staged, unstaged, and untracked files
- focus on bugs, regressions, risky edge cases, missing tests, and incorrect assumptions
- cite file/line references when possible
- keep the summary brief

Example prompt:

`Review the current staged, unstaged, and untracked code changes in this repo. Read-only only. Return prioritized findings with file/line refs where possible. Focus on bugs, regressions, missing tests, and risky assumptions.`

### Agent 3: Complexity Fit Review

Ask the agent to judge whether the implementation complexity fits the problem and the codebase.

Require:
- identify overbuilt and underbuilt areas
- distinguish necessary complexity from speculative abstraction
- call out missing simplifications or missing structure only when concrete
- report only actionable findings

Example prompt:

`Assess whether the current uncommitted implementation is overbuilt, underbuilt, or right-sized for this project. Return only actionable findings.`

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

`Infer the likely merge target branch for the current branch, map the flows touched by the current uncommitted changes, understand how those flows work on the target branch, then review the changes in that context. Return prioritized findings with file/line refs and state your target-branch assumption.`

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

After all five agents finish:

1. Combine all findings into one list.
2. Merge duplicates.
3. Track agreement:
   - note when multiple agents independently found the same issue
   - note when a finding came from only one angle
   - note material disagreement or uncertainty
4. Re-rank by severity and confidence, not by which agent found it.
5. Drop weak or purely stylistic comments unless they expose a real risk.
6. Keep the final answer in code-review form: findings first, then open questions or assumptions, then a short coverage summary.
7. If there are no findings, say so explicitly and mention residual risk or unreviewed areas.

## Output Contract

Use this structure:

- `Findings`
- `Open questions / assumptions`
- `Coverage`

In `Findings`, each item should include:

- severity
- concise problem statement
- why it matters
- file reference
- whether it had multi-agent agreement

In `Coverage`, include:

- whether the full 5-agent swarm ran
- which angles ran: standard x2, complexity x1, target-branch x2
- any fallback or missing pass

If subagents are unavailable, fall back to a single-agent review and state that coverage was reduced.

## Example Requests

- `Use $review-swarm to review the current uncommitted changes before I commit.`
- `Use $review-swarm and tell me if these open changes are missing anything against develop.`
- `Use $review-swarm to review my working tree and flag overbuilt parts.`
