#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    metadata: dict[str, str] = {}
    if not text.startswith("---\n"):
        return metadata, text

    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return metadata, text

    raw_meta, body = parts
    for line in raw_meta.splitlines()[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return metadata, body


def yaml_list(items: list[str]) -> str:
    if not items:
        return "[]"
    return "[" + ", ".join(json.dumps(item, ensure_ascii=False) for item in items) + "]"


def render_bullets(items: list[str]) -> list[str]:
    if not items:
        return ["- 無"]
    return [f"- {item}" for item in items]


def render_lines(title: str, meta: dict[str, str], spec: dict[str, object], source_md: Path) -> list[str]:
    tags = spec.get("tags", [])
    aliases = spec.get("aliases", [])
    if not isinstance(tags, list):
        tags = []
    if not isinstance(aliases, list):
        aliases = []

    lines: list[str] = []
    lines.append("---")
    lines.append(f"title: {json.dumps(title, ensure_ascii=False)}")
    lines.append(f"aliases: {yaml_list([str(x) for x in aliases])}")
    lines.append(f"tags: {yaml_list([str(x) for x in tags])}")
    if meta.get("url"):
        lines.append(f"source_url: {json.dumps(meta['url'], ensure_ascii=False)}")
    if meta.get("authorName"):
        lines.append(f"source_author: {json.dumps(meta['authorName'], ensure_ascii=False)}")
    if meta.get("publishedAt"):
        lines.append(f"source_published_at: {json.dumps(meta['publishedAt'], ensure_ascii=False)}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {title}")
    lines.append("")

    section_order = [
        ("Summary", "summary", False),
        ("Knowledge Points", "knowledge_points", True),
        ("Methods / Principles", "methods_principles", True),
        ("Why It Matters", "why_it_matters", True),
        ("Related Topics", "related_topics", True),
        ("My Notes", "my_notes", True),
    ]

    for heading, key, as_bullets in section_order:
        lines.append(f"## {heading}")
        value = spec.get(key)
        if as_bullets:
            items = [str(x) for x in value] if isinstance(value, list) else []
            lines.extend(render_bullets(items))
        else:
            text = str(value).strip() if value is not None else ""
            lines.append(text or "待補充。")
        lines.append("")

    lines.append("## Source")
    if meta.get("url"):
        lines.append(f"- Original URL: {meta['url']}")
    if meta.get("author"):
        lines.append(f"- Author: {meta['author']}")
    if meta.get("publishedAt"):
        lines.append(f"- Published: {meta['publishedAt']}")
    lines.append(f"- Source Markdown: `{source_md}`")
    lines.append("")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a structured Obsidian note from source markdown and a JSON spec")
    parser.add_argument("--source-md", required=True)
    parser.add_argument("--spec-json", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    source_md = Path(args.source_md).expanduser()
    spec_json = Path(args.spec_json).expanduser()
    output = Path(args.output).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)

    meta, _ = parse_frontmatter(source_md)
    spec = json.loads(spec_json.read_text(encoding="utf-8"))
    title = str(spec.get("title") or meta.get("title") or source_md.stem)
    lines = render_lines(title, meta, spec, source_md)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
