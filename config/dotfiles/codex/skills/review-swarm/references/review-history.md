# Review history and receipts

Use this reference only for same-head, moved-head, or supplied-finding review.

## Purpose

A receipt compresses a completed review into the facts needed for safe reuse. It
prevents duplicate swarms without exposing blind discovery agents to previous
conclusions.

The primary coordinator owns receipt lookup and interpretation. Delegated agents
must not search raw sessions or memories independently.

## Lookup

Search the narrowest available history source for:

1. exact repository identity;
2. exact `baseSha` and `headSha`;
3. otherwise, the most recent receipt whose `headSha` is an ancestor of the
   current head and whose base/scope still applies.

Prefer a receipt over a transcript. Open raw history only when one exact missing
fact is required and cannot be verified cheaply from the repository or live PR.
Mutable state—head, base, CI, comments, preview and deployment status—must always
be refreshed live.

## Receipt schema

Keep the receipt concise Markdown. Omit raw reasoning and full reviewer output.

```markdown
### Review receipt

- repository: <owner/repo or canonical root>
- change: <PR/branch/working-tree identity>
- baseSha: <immutable SHA>
- headSha: <immutable SHA>
- diffExpr: <exact expression>
- changedFilesFingerprint: <count plus stable digest, when practical>
- mode: <full|moved-head-delta|same-head-variance|supplied-findings>
- completedAt: <timestamp>
- skill: <name/version or content hash, when available>

Coverage:
- completed: <blind lanes and continuity lanes>
- validation: <ordinary batch and dedicated high-consequence checks>
- missing/interrupted: <anything not completed>
- verification: <tests, CI, runtime or live evidence actually inspected>

Findings:
- <stable id>: <valid|caveated|fixed|surviving|dropped>; <severity>; <location>;
  <trigger and consequence in one sentence>

Dropped candidates:
- <location/claim>: <concrete rejection reason>

Known gaps:
- <unreviewed or unverifiable surface>
```

The changed-files fingerprint is a lookup aid, not a substitute for re-reading
the current changed-file list.

## Mode decision

### Exact same head

Use same-head variance when the receipt proves a complete full review and
validation for the exact immutable head. Refresh mutable delivery state. Reuse
the earlier findings and dropped-candidate reasons. Run limited blind variance;
do not repeat an identical role/model lane automatically.

Use full review instead when:

- the user explicitly requests a fresh exhaustive re-review;
- the receipt is incomplete or lacks trustworthy scope;
- important coverage was interrupted or skipped;
- review instructions materially changed in a way that invalidates coverage.

### Moved head

Compute the exact old-head-to-new-head delta. Use moved-head mode only when that
delta is bounded and the prior coverage still represents the surrounding system.
The continuity reviewer receives the receipt; blind delta reviewers do not.

Escalate to full review when the delta materially changes architecture,
ownership, authorization, schema, migrations, deployment topology, or the set of
touched flows.

### Supplied findings

Treat prior receipts as calibration evidence, not verdicts. One validator checks
the entire ordinary batch against the current exact head. Include concrete prior
rejection evidence when the same candidate was previously dropped, but do not
include reviewer votes or desired conclusions.

## Continuity brief

Give the continuity reviewer:

- current immutable scope contract;
- previous `headSha` and exact delta;
- compact findings/dropped-candidate entries;
- known coverage gaps;
- current task: classify each prior finding as fixed, surviving, regressed, or
  uncertain and find new defects introduced by the delta.

Do not attach the full previous transcript.

## Interrupted agents

Before replacement, capture:

- scope already verified;
- files and paths inspected;
- commands/tests completed;
- raw evidence gathered;
- remaining unanswered question.

Follow up with the same agent when possible. A replacement receives this raw
progress, not a claimed verdict. The receipt records the interrupted lane until a
complete replacement result exists.
