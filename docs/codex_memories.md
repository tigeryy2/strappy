# Codex Memories

Codex memory setup for local agents. Strappy installs the global guidance file and helper script that make memories behave like a searchable knowledge base.

## Installed Files

- `config/dotfiles/codex/AGENTS.md` -> `~/.codex/AGENTS.md`
- `config/dotfiles/codex/memories/list_memories.py` -> `~/.local/bin/codex-memory-search`

Run the bootstrap after cloning or updating strappy:

```bash
uv run --locked python -m strappy.bootstrap
```

## Memory Metadata

Human-authored memory notes can include simple Markdown fields near the top:

```markdown
usefulness: 0
last_read: 2026-06-06T00:00:00Z
memory_tags: kevork, review, data-plane
scope: when this memory should be considered
keywords: exact symbols, paths, commands, error text
```

Use plain Markdown fields instead of YAML frontmatter for Codex memories. Generated Codex memory files may not include these fields, so the helper also searches `scope`, `applies_to`, and `keywords` when present.

## Search

Queries return memories matching any whole search term and rank title, scope,
path, tag, and keyword matches above body-only matches. `--tags` matches exact
`memory_tags` values; use `--require-all` to require every requested tag.

```bash
codex-memory-search
codex-memory-search --tags kevork,review --show-meta
codex-memory-search --query "data plane rpc" --show-meta
codex-memory-search --query "siteEnrollmentId" --include-rollouts --limit 10 --show-meta
```

Sort order is tag match, query match, usefulness, last_read, then path.

## Updating Memories

Do not edit generated `MEMORY.md`, `memory_summary.md`, `raw_memories.md`, or rollout summaries as the primary control surface.

When the user asks to update memories, add a small note under:

```text
~/.codex/memories/extensions/ad_hoc/notes/
```

Those notes should state the reusable fact, the useful search terms, and the intended scope.
