#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

KB_DIR = Path(__file__).resolve().parent
EXCLUDE_NAMES = {"README.md"}


@dataclass(frozen=True)
class Article:
    name: str
    path: Path
    last_read_raw: Optional[str]
    last_read: Optional[datetime]
    usefulness: int
    tags: list[str]
    tag_match: int


def parse_frontmatter(text: str) -> dict[str, object]:
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end_index = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_index = i
            break
    if end_index is None:
        return {}
    return parse_yaml_lines(lines[1:end_index])


def parse_yaml_lines(lines: list[str]) -> dict[str, object]:
    meta: dict[str, object] = {}
    current_key: Optional[str] = None
    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key and isinstance(meta.get(current_key), list):
            meta[current_key].append(line[4:].strip())
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value == "":
                meta[key] = []
                current_key = key
            else:
                meta[key] = value
                current_key = None
    return meta


def parse_last_read(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    cleaned = value.strip()
    if cleaned.endswith("Z"):
        cleaned = f"{cleaned[:-1]}+00:00"
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        return None


def parse_usefulness(value: object) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0


def normalize_tags(tags: object) -> list[str]:
    if isinstance(tags, list):
        return [str(tag).strip() for tag in tags if str(tag).strip()]
    if isinstance(tags, str) and tags.strip():
        return [tags.strip()]
    return []


def load_article(path: Path, required_tags: list[str], require_all: bool) -> Optional[Article]:
    text = path.read_text(encoding="utf-8")
    meta = parse_frontmatter(text)
    last_read_raw = meta.get("last_read")
    usefulness = parse_usefulness(meta.get("usefulness"))
    tags = normalize_tags(meta.get("read_win_tags"))
    tag_match = count_tag_matches(tags, required_tags)
    if required_tags:
        if require_all and tag_match != len(required_tags):
            return None
        if not require_all and tag_match == 0:
            return None
    return Article(
        name=path.name,
        path=path,
        last_read_raw=str(last_read_raw) if last_read_raw else None,
        last_read=parse_last_read(str(last_read_raw)) if last_read_raw else None,
        usefulness=usefulness,
        tags=tags,
        tag_match=tag_match,
    )


def count_tag_matches(tags: list[str], required_tags: list[str]) -> int:
    if not required_tags:
        return 0
    tag_set = {tag.lower() for tag in tags}
    return sum(1 for tag in required_tags if tag.lower() in tag_set)


def sort_key(article: Article) -> tuple:
    last_read_ts = article.last_read.timestamp() if article.last_read else 0.0
    return (-article.tag_match, -article.usefulness, -last_read_ts, article.name.lower())


def format_article(article: Article, show_meta: bool, show_match: bool) -> str:
    if not show_meta:
        return article.name
    last_read = article.last_read_raw or "unknown"
    tags = ", ".join(article.tags) if article.tags else "none"
    parts = [
        article.name,
        f"usefulness={article.usefulness}",
        f"last_read={last_read}",
        f"tags={tags}",
    ]
    if show_match:
        parts.append(f"tag_match={article.tag_match}")
    return " | ".join(parts)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List knowledge base articles sorted by tag match, usefulness, and last_read.",
    )
    parser.add_argument(
        "--tags",
        default="",
        help="Comma-separated read_win_tags filter (any match unless --require-all).",
    )
    parser.add_argument(
        "--require-all",
        action="store_true",
        help="Require all provided tags to match.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit number of results (0 = no limit).",
    )
    parser.add_argument(
        "--show-meta",
        action="store_true",
        help="Show metadata columns alongside filenames.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    required_tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
    articles: list[Article] = []
    for path in sorted(KB_DIR.glob("*.md")):
        if path.name in EXCLUDE_NAMES:
            continue
        article = load_article(path, required_tags, args.require_all)
        if article:
            articles.append(article)
    articles.sort(key=sort_key)
    if args.limit > 0:
        articles = articles[: args.limit]
    show_match = bool(required_tags)
    for article in articles:
        print(format_article(article, args.show_meta, show_match))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
