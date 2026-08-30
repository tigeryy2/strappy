---
last_read: 2026-08-30T00:00:00Z
usefulness: 2
read_win_tags:
  - grok
  - agents
  - bootstrap
---

# Grok Build Global AGENTS.md

Grok getting-started lists `~/.grok/AGENTS.md` as global rules for all projects.

Strappy installs that path as a symlink to `config/dotfiles/codex/AGENTS.md` (same source as `~/.codex/AGENTS.md`).

Grok discovers user skills from `~/.grok/skills/`. Bootstrap links Codex skill directories there, then Claude-only skill directories (currently `make-interfaces-feel-better`). Same-named skills keep the Codex copy.

The more detailed Grok project-rules doc also scans `~/.grok/rules/*.md`. Strappy does not create that directory yet.
