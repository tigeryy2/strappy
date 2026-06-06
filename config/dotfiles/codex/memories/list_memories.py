#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

MEMORY_DIR = Path(__file__).resolve().parent
EXCLUDE_DIRS = {".git"}
DEFAULT_EXCLUDE_DIRS = {"rollout_summaries"}


@dataclass(frozen=True)
class MemoryDoc:
    path: Path
    title: str
    usefulness: int
    last_read_raw: str | None
    last_read: datetime | None
    tags: list[str]
    scope: str
    keywords: list[str]
    tag_match: int
    query_match: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List and search Codex memory Markdown files.",
    )
    parser.add_argument(
        "--root",
        default=str(MEMORY_DIR),
        help="Memory root to scan. Defaults to this script's directory.",
    )
    parser.add_argument(
        "--tags",
        default="",
        help="Comma-separated tags to prefer or filter by.",
    )
    parser.add_argument(
        "--require-all",
        action="store_true",
        help="Require every requested tag to match.",
    )
    parser.add_argument(
        "--query",
        default="",
        help="Case-insensitive text query. All terms must appear.",
    )
    parser.add_argument(
        "--include-rollouts",
        action="store_true",
        help="Also scan rollout_summaries, which can be noisy.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit number of results. 0 means no limit.",
    )
    parser.add_argument(
        "--show-meta",
        action="store_true",
        help="Show usefulness, last_read, tags, and scope.",
    )
    return parser.parse_args()


def iter_markdown(root: Path, include_rollouts: bool) -> Iterable[Path]:
    excluded = set(EXCLUDE_DIRS)
    if not include_rollouts:
        excluded.update(DEFAULT_EXCLUDE_DIRS)

    for path in sorted(root.rglob("*.md")):
        parts = set(path.relative_to(root).parts)
        if parts & excluded:
            continue
        yield path


def parse_doc(
    path: Path,
    root: Path,
    wanted_tags: list[str],
    query_terms: list[str],
    require_all_tags: bool,
) -> MemoryDoc | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    meta = parse_metadata(text)
    tags = normalize_list(meta.get("memory_tags") or meta.get("read_win_tags"))
    keywords = normalize_list(meta.get("keywords"))
    scope = meta.get("scope") or meta.get("applies_to") or ""
    title = extract_title(text) or path.relative_to(root).name
    tag_match = count_tag_matches(
        tags=tags,
        keywords=keywords,
        scope=scope,
        title=title,
        path=path.relative_to(root),
        wanted_tags=wanted_tags,
    )
    query_match = count_query_matches(text, query_terms)

    if wanted_tags:
        if tag_match == 0:
            return None
        if require_all_tags and len({tag.lower() for tag in wanted_tags}) > tag_match:
            return None

    if query_terms and query_match != len(query_terms):
        return None

    rel_path = path.relative_to(root)
    return MemoryDoc(
        path=rel_path,
        title=title,
        usefulness=parse_int(meta.get("usefulness")),
        last_read_raw=meta.get("last_read"),
        last_read=parse_datetime(meta.get("last_read")),
        tags=tags,
        scope=scope,
        keywords=keywords,
        tag_match=tag_match,
        query_match=query_match,
    )


def parse_metadata(text: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    lines = text.splitlines()
    scan_lines = lines[:80]

    if scan_lines and scan_lines[0].strip() == "---":
        for index, line in enumerate(scan_lines[1:], start=1):
            if line.strip() == "---":
                scan_lines = scan_lines[1:index]
                break

    current_key: str | None = None
    list_values: dict[str, list[str]] = {}
    in_fence = False
    for raw in scan_lines:
        line = raw.rstrip()
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not line.strip():
            continue
        if current_key and line.startswith("  - "):
            list_values.setdefault(current_key, []).append(line[4:].strip())
            continue
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        current_key = key if value == "" else None
        meta.setdefault(key, value)

    for key, values in list_values.items():
        meta.setdefault(key, ", ".join(values))
    return meta


def normalize_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in re.split(r"[,;]", value) if item.strip()]


def parse_int(value: str | None) -> int:
    try:
        return int(value or "0")
    except ValueError:
        return 0


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    cleaned = value.strip()
    if cleaned.endswith("Z"):
        cleaned = f"{cleaned[:-1]}+00:00"
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        return None


def extract_title(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def count_tag_matches(
    tags: list[str],
    keywords: list[str],
    scope: str,
    title: str,
    path: Path,
    wanted_tags: list[str],
) -> int:
    if not wanted_tags:
        return 0
    exact = {tag.lower() for tag in [*tags, *keywords]}
    searchable = " ".join([scope, title, str(path), *tags, *keywords]).lower()
    return sum(
        1
        for tag in wanted_tags
        if tag.lower() in exact or tag.lower() in searchable
    )


def count_query_matches(text: str, query_terms: list[str]) -> int:
    if not query_terms:
        return 0
    lower = text.lower()
    return sum(1 for term in query_terms if term.lower() in lower)


def sort_key(doc: MemoryDoc) -> tuple[object, ...]:
    last_read_ts = doc.last_read.timestamp() if doc.last_read else 0.0
    return (
        -doc.tag_match,
        -doc.query_match,
        -doc.usefulness,
        -last_read_ts,
        str(doc.path).lower(),
    )


def format_doc(doc: MemoryDoc, show_meta: bool) -> str:
    if not show_meta:
        return str(doc.path)
    tags = ", ".join(doc.tags) if doc.tags else "none"
    keywords = ", ".join(doc.keywords) if doc.keywords else "none"
    last_read = doc.last_read_raw or "unknown"
    pieces = [
        str(doc.path),
        f"usefulness={doc.usefulness}",
        f"last_read={last_read}",
        f"tags={tags}",
        f"keywords={keywords}",
    ]
    if doc.scope:
        pieces.append(f"scope={doc.scope}")
    return " | ".join(pieces)


def main() -> int:
    args = parse_args()

    root = Path(args.root).expanduser().resolve()
    wanted_tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
    query_terms = [term.strip() for term in args.query.split() if term.strip()]

    docs: list[MemoryDoc] = []
    for path in iter_markdown(root, args.include_rollouts):
        doc = parse_doc(path, root, wanted_tags, query_terms, args.require_all)
        if doc:
            docs.append(doc)

    docs.sort(key=sort_key)
    if args.limit > 0:
        docs = docs[: args.limit]

    for doc in docs:
        print(format_doc(doc, args.show_meta))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
