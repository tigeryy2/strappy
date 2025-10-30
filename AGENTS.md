# Repository Guidelines

- Delete unused or obsolete files when your changes make them irrelevant (refactors, feature removals, etc.), and revert files only when the change is yours or explicitly requested. If a git operation leaves you unsure about other agents' in-flight work, stop and coordinate instead of deleting.
- Before attempting to delete a file to resolve a local type/lint failure, stop and ask the user. Other agents are often editing adjacent files; deleting their work to silence an error is never acceptable without explicit approval.
- NEVER edit .env or any environment variable files—only the user may change them.
- Coordinate with other agents before removing their in-progress edits—don't revert or delete work you didn't author unless everyone agrees.
- Moving/renaming and restoring files is allowed.
- ABSOLUTELY NEVER run destructive git operations (e.g., git reset --hard, rm, git checkout/git restore to an older commit) unless the user gives an explicit, written instruction in this conversation. Treat these commands as catastrophic; if you are even slightly unsure, stop and ask before touching them. (When working within Cursor or Codex Web, these git limitations do not apply; use the tooling's capabilities as needed.)
- Never use git restore (or similar commands) to revert files you didn't author—coordinate with other agents instead so their in-progress work stays intact.
- Always double-check git status before any commit
- Keep commits atomic: commit only the files you touched and list each path explicitly. For tracked files run git commit -m "<scoped message>" -- path/to/file1 path/to/file2. For brand-new files, use the one-liner git restore --staged :/ && git add "path/to/file1" "path/to/file2" && git commit -m "<scoped message>" -- path/to/file1 path/to/file2.
- Quote any git paths containing brackets or parentheses (e.g., src/app/[candidate]/**) when staging or committing so the shell does not treat them as globs or subshells.
- When running git rebase, avoid opening editors—export GIT_EDITOR=: and GIT_SEQUENCE_EDITOR=: (or pass --no-edit) so the default messages are used automatically.
- Never amend commits unless you have explicit written approval in the task thread.
- This codebase keeps a short `README.md` in each major directory. These files share a common structure so humans and LLMs can easily navigate the repository.

---

## README Format

```markdown
# Directory Title

Brief one or two sentence overview.

## Contents
- bullet points describing key files or subfolders
````

When you add (or update) directories or significant files, include (or update) a README following this pattern. Keep descriptions concise.

---

## Contributing

* **Backend tests**

  ```bash
  uv run pytest
  ```

  (Run this within `/backend`)

* **Frontend tests**

  ```bash
  npx vitest
  ```

  (Run this within `/frontend`)

* **Backend formatting**

  ```bash
  uv run ruff format
  uv run ruff check --fix
  ```

---

## Docs

Project docs live in `backend/docs`. This includes:

* Project roadmap & planning
* Developer docs & miscellaneous notes

---

## Tools

### Backend

* Use `uv` instead of `pip`. Prefix commands with `uv run`.
* Prefer Python `dataclasses` over manually written `__init__` methods.
* Prefer Pydantic `BaseModel` for complex data structures, especially those related to the database or API.

### Frontend

* Strongly prefer **shadcn/ui** components.

---

## Updating the Frontend API Client

1. Ensure the backend FastAPI server is running.
2. From the `/frontend` directory, run:

   ```bash
   npm run generate:podmocks
   ```

   This will regenerate the API client based on the running backend.

---

## Task Updates

After completing a task, write a short explanation summarizing what changed and why.
Include code snippets from the modified files when they help illustrate the update.
This summary should appear at the end of your response or pull request description.

---
