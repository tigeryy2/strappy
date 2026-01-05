---
last_read: 2026-01-05T00:00:00Z
usefulness: 0
read_win_tags:
  - tooling
  - oracle
  - cli
  - ai
  - workflow
---
# Using the Oracle CLI

The Oracle (https://github.com/steipete/oracle) is a CLI helper for delegating complex reasoning to GPT-5 Pro. This repo expects agents to use it whenever a user asks or the problem needs deep guidance.

## Prerequisites
- Ensure the backend/frontend context you want to analyze is saved to disk; the Oracle only operates on real files.
- Fetch the shared OpenAI key once via the macOS keychain:
  ```bash
  security find-generic-password -s oracle_openai_key -w
  ```
  Keep the value handy for the session.

## Basic invocation
```bash
OPENAI_API_KEY=sk-... npx -y @steipete/oracle \
  -p "Describe the thing you need" \
  --file path/to/context.md another/file.ts
```
- `-p` is the prompt/question for GPT-5.
- `--file` accepts one or more file paths on disk. Globs are supported only within the current repo; remote globs fail.
- For complex setups, create a temporary context file (e.g., inside knowledge_base/oracle/) with all relevant snippets, then pass that file.

## Sessions & reattachment
- The CLI launches a background session and prints an ID like `in-my-query`.
- If the run times out or you exit, reattach with:
  ```bash
  OPENAI_API_KEY=sk-... npx -y @steipete/oracle session <session-id>
  ```
- Use `oracle status` to list sessions; `oracle status --clear --hours 168` prunes older runs.

## Tips
- Always gather the minimal-but-complete context before running the Oracle.
- Mention desired output (e.g., "suggest Tailwind utilities").
- Continue adding to this file or another KB file on usage as you learn more.
- You likely need a longer timeout than you think. Start with 5 minutes.
