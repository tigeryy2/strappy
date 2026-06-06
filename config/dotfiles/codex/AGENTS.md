# Guidelines

Tiger owns this computer. Session Start: say hi + 1 motivating line.
Work style: telegraph; noun-phrases ok; drop grammar; min tokens.

- Session Start: Review memories and docs to understand context and intent; Understand existing intent and user asks before coding.
- Need upstream file: stage in /tmp/, then cherry-pick; never overwrite tracked.
- Bugs: add regression test when it fits.
- Keep files <~500 LOC; split/refactor as needed.
- Prefer end-to-end verify; if blocked, say what's missing.
- New deps: quick health check (recent releases/commits, adoption). Be very careful with any dep version <3 days old.
- Web: search early; quote exact errors; prefer 2024-2026 sources
- Style: telegraph. Drop filler/grammar. Min tokens.
- Delete unused or obsolete files when your changes make them irrelevant (refactors, feature removals, etc.), and revert files only when the change is yours or explicitly requested. If a git operation leaves you unsure about other agents' in-flight work, stop and coordinate instead of deleting.
- Before attempting to delete a file to resolve a local type/lint failure, stop and ask the user. Other agents are often editing adjacent files; deleting their work to silence an error is never acceptable without explicit approval.
- As the intent and work in a session changes, update the name of the session.
- Coordinate with other agents before removing their in-progress edits—don't revert or delete work you didn't author unless everyone agrees.
- Moving/renaming and restoring files is allowed.
- ABSOLUTELY NEVER run destructive git operations (e.g., git reset --hard, rm, git checkout/git restore to an older commit) unless the user gives an explicit, written instruction in this conversation. Treat these commands as catastrophic; if you are even slightly unsure, stop and ask before touching them. (When working within Cursor or Codex Web, these git limitations do not apply; use the tooling's capabilities as needed.)
- Never use git restore (or similar commands) to revert files you didn't author—coordinate with other agents instead so their in-progress work stays intact.
- Always double-check git status before any commit
- Keep commits atomic: commit only the files you touched and list each path explicitly. For tracked files run git commit -m "<scoped message>" -- path/to/file1 path/to/file2. For brand-new files, use the one-liner git restore --staged :/ && git add "path/to/file1" "path/to/file2" && git commit -m "<scoped message>" -- path/to/file1 path/to/file2.
- Quote any git paths containing brackets or parentheses (e.g., src/app/[candidate]/**) when staging or committing so the shell does not treat them as globs or subshells.
- When running git rebase, avoid opening editors—export GIT_EDITOR=: and GIT_SEQUENCE_EDITOR=: (or pass --no-edit) so the default messages are used automatically.
- Never amend commits unless you have explicit written approval in the task thread.
- Write code (and comments/docs) that are well understandable by other agents and humans. Explain the intent of things if they are hard to understand or complex.
- As you plan and implement, run temporary tests scripts or test to validate code flows that you aren't 100% sure about.
- Run the available tests, linting, type checks (typescript) to validate your changes, expand the test suite as you go.

---

## Tools

### Python

* Use `uv` instead of `pip`. Prefix commands with `uv run`.
* Prefer Python `dataclasses` over manually written `__init__` methods.
* Prefer Pydantic `BaseModel` for complex data structures, especially those related to the database or API.
* Format code before committing

### Frontend

* Strongly prefer **shadcn/ui** components.
* Use `npx vitest --project unit` to run unit tests, since the storybook tests are blocked (need browser access)
* Run type checks before committing
* For very large changes run build tests before committing
* Remember to escape special characters in *.tsx and other frontend files to avoid `react/no-unescaped-entities`
* We want slim, beautiful UI with excellent UX. Use imagegen to generate UI inspiration when we are designing UIs.
* Generally avoid multi-nested cards/boxes. Prefer using visual hierachy & spatial organization.
* Use spacing, alignment, grouping, and visual hierarchy to make relationships between objects legible and intuitive.

---

## Task Updates

After completing a task, write a short explanation summarizing what changed and why.
Include code snippets from the modified files when they help illustrate the update.
This summary should appear at the end of your response or pull request description.

---

# Memories

Use and organize your memories as a knowledge base.

Guidelines:
- Any missing info you need, search memories. Start with:
  `python3 ~/.codex/memories/list_memories.py --query "<terms>" --show-meta`
- Anything useful you see, dump there `a_very_descriptive_file_name.md`.
- Jot down obstacles and how you solved them.
- Note key design decisions, particular on the intent
- Keep a running list of key issues you repeatedly encounter and how you solved them.
- When asked to commit, you should review the full context (relevant sessions) since the last commit, consider
  a. What issues or obstacles did we run into? Should we expand the knowledge base to cover it?
  b. What articles were very useful? Do we need to update these?

## Memory Knowledge Base Metadata + Listing

Memory files may include simple Markdown metadata fields near the top:

```markdown
usefulness: 0
last_read: 2026-06-06T00:00:00Z
memory_tags: kevork, review, data-plane
scope: when this memory should be considered
keywords: exact symbols, paths, commands, error text
```

Rules:

- Prefer plain Markdown fields over YAML frontmatter for Codex memories.
- Update `last_read` when you consult a human-authored memory article.
- Bump `usefulness` +1 when a memory materially helps; -1 when it misleads.
- Keep `memory_tags` small, concrete, lowercase.
- Generated memory files may not have these fields; use `scope`, `applies_to`, and `keywords` when present.
- Do not hand-edit generated `MEMORY.md`, `memory_summary.md`, `raw_memories.md`, or rollout summaries as the primary control surface. Use ad-hoc notes under `~/.codex/memories/extensions/ad_hoc/notes/` when asked to update memories.

Listing/search script:

```bash
python3 ~/.codex/memories/list_memories.py
python3 ~/.codex/memories/list_memories.py --tags kevork,review --show-meta
python3 ~/.codex/memories/list_memories.py --query "data plane rpc" --show-meta
python3 ~/.codex/memories/list_memories.py --query "siteEnrollmentId" --include-rollouts --limit 10 --show-meta
```

Sort order: tag match, query match, usefulness, last_read, then path.
