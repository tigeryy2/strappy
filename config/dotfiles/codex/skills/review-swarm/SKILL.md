---
name: review-swarm
description: Review open code changes with an independent multi-agent swarm and a consolidation pass. Use when Codex needs to review staged, unstaged, and untracked changes before commit or PR; when the user wants prioritized findings from multiple review angles; or when changes should be checked against the likely merge target and the current implementation on that target branch.
---

# Review Swarm

## Overview

Run a read-only swarm review of the current working tree. Cover staged, unstaged, and untracked files; use independent subagents with different review angles plus one parallel Claude Code second-opinion pass; then consolidate overlap, disagreement, and severity into one report.

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

## Scope Contract

Before spawning reviewers, define the exact review root and diff scope:

- `reviewRoot`: absolute path of the checkout/worktree being reviewed
- `baseRef`: the merge target ref, such as `origin/main`, `github/main`, or `develop`
- `headRef`: the reviewed ref, usually `HEAD`
- `diffExpr`: the exact comparison, such as `<baseRef>...<headRef>`
- `changedFiles`: output of `git -C <reviewRoot> diff --name-only <diffExpr>` plus any staged/unstaged/untracked files in scope

Pass these values to every subagent and Claude. Instruct reviewers to verify
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

## Agent Layout

Spawn exactly five subagents and, in parallel, start exactly one read-only Claude Code second-opinion pass. Keep prompts short and independent. Give each reviewer the task and raw repo context it needs, but not your conclusions or another reviewer's output.

Use the same base model as the main agent for every subagent in the swarm. Do not mix model families within one review. Example: if the main agent is running on `gpt-5.4`, spawn all review subagents on `gpt-5.4` as well.

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

### Parallel Claude Second Opinion

Run the Claude pass at the same time as the five subagents, not after the
initial swarm finishes.

Use the latest Opus model and follow the repo's `AGENTS.md` Claude Review
instructions:

- run `claude -p` outside the sandbox by requesting escalated command
  permissions; ask the user to allow the read-only Claude review command before
  launching it
- put the prompt immediately after `claude -p`, before tool options
- use `--model opus`
- use `--permission-mode dontAsk`
- keep tools read-only and tightly scoped
- ask Claude to verify the exact review root, base/head SHAs, and changed-file
  list before reviewing
- ask Claude to inspect only the assigned diff, untracked files in scope, and
  directly relevant tests or subsystems at risk
- require all Claude `git` commands to use `git -C <reviewRoot>` when reviewing
  an isolated clone/worktree
- tell Claude to stop with `scope mismatch` if its root/ref/diff check does not
  match the assigned scope
- tell Claude not to report primary findings outside `changedFiles`; unchanged
  files may only support a bug caused by a changed file
- do not share any subagent findings, candidate findings, or conclusions;
  preserve independence
- private code and data access for Claude is explicitly approved (as we are using api key w/ zdr)

Default prompt:

`Review only this assigned scope: reviewRoot=<absolute path>, baseRef=<baseRef>, headRef=HEAD, diffExpr=<baseRef>...HEAD, changedFiles=<list>. First run and report git -C <reviewRoot> rev-parse --show-toplevel, git -C <reviewRoot> rev-parse <baseRef>, git -C <reviewRoot> rev-parse HEAD, and git -C <reviewRoot> diff --name-only <diffExpr>. If those do not match this prompt, stop with scope mismatch. Read AGENTS.md first. This is a read-only second opinion for a code review. Focus on bugs, regressions, permissions/security, migrations, missing tests, and perf-shape issues in changedFiles. Do not report primary findings outside changedFiles unless citing unchanged support for a changed-file bug. Return prioritized findings only with file/line refs where possible.`

Default command:

`claude -p "Review only this assigned scope: reviewRoot=<absolute path>, baseRef=<baseRef>, headRef=HEAD, diffExpr=<baseRef>...HEAD, changedFiles=<list>. First run and report git -C <reviewRoot> rev-parse --show-toplevel, git -C <reviewRoot> rev-parse <baseRef>, git -C <reviewRoot> rev-parse HEAD, and git -C <reviewRoot> diff --name-only <diffExpr>. If those do not match this prompt, stop with scope mismatch. Read AGENTS.md first. This is a read-only second opinion for a code review. Focus on bugs, regressions, permissions/security, migrations, missing tests, and perf-shape issues in changedFiles. Do not report primary findings outside changedFiles unless citing unchanged support for a changed-file bug. Return prioritized findings only with file/line refs where possible." --model opus --permission-mode dontAsk --allowedTools "Read,Grep,Glob,Bash(git -C <reviewRoot> *),Bash(rg *),Bash(sed *),Bash(nl *)"`

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

After all five subagents and the parallel Claude pass finish:

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
7. Track which findings came from Claude alone versus from the five-agent swarm.
8. If there are no candidate findings, skip the validation round and say there
   are no findings.

## Validation Round

After consolidation and before the final answer, independently validate every
candidate finding that may appear in the final review.

1. Spawn one fresh independent subagent per candidate finding.
2. Give each validation agent only:
   - where to look
   - the suspected issue
   - suspected severity / scope
   - a request to confirm whether the issue is real, not real, or needs caveats
3. Do not share other agents' conclusions with validators.
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
- whether the single Claude second-opinion pass ran in parallel with the swarm
  and whether it ran with approved outside-sandbox permissions
- which angles ran: standard x2, complexity x1, target-branch x2
- whether one independent validation agent ran for each final finding
- any findings dropped or materially changed after validation
- any fallback or missing pass

If subagents are unavailable for either the initial swarm or the validation
round, fall back to the best available review and state exactly which coverage
was reduced.

## Example Requests

- `Use $review-swarm to review the current uncommitted changes before I commit.`
- `Use $review-swarm and tell me if these open changes are missing anything against develop.`
- `Use $review-swarm to review my working tree and flag overbuilt parts.`
