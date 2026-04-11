from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path


VAULT_DIR = Path(r"C:\Users\hsi67063\Box\00-home-pigo.hsiao\VBA\Pigo_Obsidian")
LUMENTUM_DIR = VAULT_DIR / "Lumentum"
WEEKLY_DIR = LUMENTUM_DIR / "Weekly Reports"
ISSUES_DIR = LUMENTUM_DIR / "Issues"
ISSUE_KEYS_DIR = ISSUES_DIR / "RMA Keys"
CUSTOMERS_DIR = LUMENTUM_DIR / "Customers"
CUSTOMER_KEYS_DIR = CUSTOMERS_DIR / "Keys"
INDEX_PATH = LUMENTUM_DIR / "index.md"
LOG_PATH = LUMENTUM_DIR / "log.md"

RMA_SECTION_PATTERNS = (
    "### 一、RMA / PRP / SCAR",
    "### 四、RMA / 內部問題重點",
    "RMA/ PRP/ SCAR",
    "Issue/ RMA/ PRP",
    "RMA Open Status",
    "RMA/ SAG internal Trouble",
)
HEADING_RE = re.compile(r"^#{1,6}\s+")
TABLE_SEPARATOR_RE = re.compile(r"^\|\s*[-:| ]+\|$")
CUSTOMER_MARKER_RE = re.compile(r"(?:客戶|Customer|Custmer)\s*[:：]?\s*", re.IGNORECASE)
ISSUE_SIGNAL_RE = re.compile(
    r"(HL\d|JT\d|OL\d|OD\d|DFB|EML|DML|CW-LD|COB|Driver IC|Gain Chip|"
    r"failure|Failure|Issue|issue|trouble|Trouble|Open|open|Peeling|peeling|"
    r"Crack|crack|Discoloration|Visual|visual|Bubble|bubble|Metal|metal|"
    r"Pick-up|Pick up|WB |Chip |chip )"
)

GENERIC_ISSUE_KEYS = {
    "RMA/ PRP/ SCAR",
    "Issue/ RMA/ PRP",
    "RMA/ SAG internal Trouble",
    "RMA Open Status",
    "Update in red",
    "RMA 狀態",
    "議題 / 專案",
    "變更控制 / 稽核",
    "Other Topics",
    "Other Topics (optional)",
    "Quality Standards",
    "Instruction Memo",
    "Topics",
    "Others",
    "System Improvements",
    "本區未解析到有效資料。",
}

GENERIC_ISSUE_CONTAINS = (
    "AWR/CCR",
    "CCB Chair",
    "Internal QMS Audit",
    "External QMS Audit",
    "PQC",
    "Countermeasure",
    "Activities to prevent",
    "Improvement of",
    "Event of Quality month",
    "Preventive Action for",
    "TAK Quality Update",
    "ORT operation",
    "GC transfer",
)

NON_RMA_TABLE_MARKERS = (
    "AWR/CCB/Audit",
    "Other Topics",
    "Quality Standards",
    "Instruction Memo",
    "議題 / 專案",
    "變更控制 / 稽核",
    "System Improvements",
)

CUSTOMER_ALIASES = {
    "eOptolink": "Eoptolink",
    "Accelionk": "Accelink",
    "Hisence": "Hisense",
    "FBN": "Fabrinet",
}


@dataclass(frozen=True)
class NoteRef:
    vault_rel: str
    title: str


@dataclass(frozen=True)
class Match:
    note: NoteRef
    issue_key: str
    customers: tuple[str, ...]
    excerpt: str


def normalize_space(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text.strip())
    return text


def slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    if slug:
        return slug[:120]
    return "key"


def note_title(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except FileNotFoundError:
        return path.stem
    return path.stem


def relevant_lines(text: str) -> list[str]:
    lines = text.splitlines()
    collected: list[str] = []
    in_rma = False
    in_table_block = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            in_table_block = False
            continue
        if HEADING_RE.match(stripped):
            in_rma = any(pattern in stripped for pattern in RMA_SECTION_PATTERNS)
            in_table_block = False
            continue
        if any(pattern in stripped for pattern in RMA_SECTION_PATTERNS):
            in_rma = True
            if stripped.startswith("|"):
                in_table_block = True
            continue
        if in_rma:
            if stripped.startswith("### ") or stripped.startswith("## "):
                in_rma = False
                in_table_block = False
                continue
            if stripped.startswith("|"):
                if any(marker in stripped for marker in NON_RMA_TABLE_MARKERS):
                    in_rma = False
                    in_table_block = False
                    continue
                in_table_block = True
                if not TABLE_SEPARATOR_RE.match(stripped):
                    collected.append(stripped)
                continue
            if in_table_block and not stripped.startswith("|"):
                in_table_block = False
            if stripped.startswith("- "):
                collected.append(stripped)
    return collected


def split_customers(text: str) -> list[str]:
    text = text.replace(">>", "/").replace("?", "/")
    base = text.split("：", 1)[0]
    base = base.split("|", 1)[0]
    base = base.split("；", 1)[0]
    base = re.sub(r"End customer\s*:\s*", "", base, flags=re.IGNORECASE)
    base = normalize_space(base)
    tokens = re.split(r"[/,&、]| and ", base)
    results: list[str] = []
    for token in tokens:
        token = normalize_space(token)
        if not token:
            continue
        if "(" in token and ")" in token:
            prefix = normalize_space(token.split("(", 1)[0])
            inside = normalize_space(token.split("(", 1)[1].split(")", 1)[0])
            if prefix:
                results.append(prefix)
            if inside:
                results.append(inside)
            continue
        if token == "Innolight Eopto":
            results.extend(["Innolight", "Eoptolink"])
            continue
        results.append(token)
    deduped: list[str] = []
    seen: set[str] = set()
    for token in results:
        token = CUSTOMER_ALIASES.get(token, token)
        if len(token) <= 1:
            continue
        if token.lower() in {"new", "customer"}:
            continue
        if token not in seen:
            deduped.append(token)
            seen.add(token)
    return deduped


def normalize_issue_key(text: str) -> str:
    value = text.replace("�", "").replace("?", "").replace(" ,", ",")
    value = value.strip(" ,;：:")
    value = re.sub(r"\s+", " ", value)
    return value


def looks_like_issue_key(text: str) -> bool:
    if text in GENERIC_ISSUE_KEYS:
        return False
    if any(marker in text for marker in GENERIC_ISSUE_CONTAINS):
        return False
    return bool(ISSUE_SIGNAL_RE.search(text))


def parse_issue_and_customers(raw_line: str) -> tuple[str | None, list[str], str]:
    line = normalize_space(raw_line.strip("- ").strip())
    if line.startswith("|"):
        cells = [normalize_space(cell) for cell in line.strip("|").split("|")]
        cells = [cell for cell in cells if cell]
        if not cells:
            return None, [], line
        if len(cells) >= 1:
            line = cells[0]
    line = normalize_space(line)
    if line in GENERIC_ISSUE_KEYS:
        return None, [], line
    match = CUSTOMER_MARKER_RE.search(line)
    if match:
        issue_part = normalize_issue_key(normalize_space(line[: match.start()]))
        customer_part = normalize_space(line[match.end() :])
        customers = split_customers(customer_part)
        excerpt = line
        if not looks_like_issue_key(issue_part):
            return None, customers, excerpt
        return (issue_part or None), customers, excerpt
    issue_part = normalize_issue_key(normalize_space(line.split("：", 1)[0]))
    if len(issue_part) < 6:
        return None, [], line
    if not looks_like_issue_key(issue_part):
        return None, [], line
    return issue_part, [], line


def render_link(vault_rel: str, label: str) -> str:
    posix_path = vault_rel.replace("\\", "/")
    return f"[[{posix_path}|{label}]]"


def write_customer_pages(customer_map: dict[str, list[Match]], issue_links: dict[str, str]) -> dict[str, str]:
    CUSTOMER_KEYS_DIR.mkdir(parents=True, exist_ok=True)
    customer_page_links: dict[str, str] = {}
    for customer, matches in sorted(customer_map.items(), key=lambda item: (-len(item[1]), item[0].lower())):
        slug = slugify(customer)
        rel = f"Lumentum/Customers/Keys/{slug}.md"
        customer_page_links[customer] = rel
        unique_issue_keys = sorted({match.issue_key for match in matches if match.issue_key})
        lines = [
            "---",
            f"title: '{customer}'",
            "tags:",
            "  - lumentum",
            "  - customer-index",
            "---",
            "",
            f"# {customer}",
            "",
            "## Related Issues",
            "",
        ]
        if unique_issue_keys:
            for issue_key in unique_issue_keys:
                issue_rel = issue_links.get(issue_key)
                if issue_rel:
                    lines.append(f"- {render_link(issue_rel, issue_key)}")
                else:
                    lines.append(f"- `{issue_key}`")
        else:
            lines.append("- 無")
        lines.extend(["", "## Weekly Reports", ""])
        for match in sorted(matches, key=lambda item: item.note.title, reverse=True):
            lines.append(
                f"- {render_link(match.note.vault_rel, match.note.title)} | 議題：`{match.issue_key}` | 摘錄：{match.excerpt}"
            )
        (VAULT_DIR / rel).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return customer_page_links


def write_issue_pages(issue_map: dict[str, list[Match]]) -> dict[str, str]:
    ISSUE_KEYS_DIR.mkdir(parents=True, exist_ok=True)
    issue_page_links: dict[str, str] = {}
    for issue_key, matches in sorted(issue_map.items(), key=lambda item: (-len(item[1]), item[0].lower())):
        slug = slugify(issue_key)
        rel = f"Lumentum/Issues/RMA Keys/{slug}.md"
        issue_page_links[issue_key] = rel
        unique_customers = sorted({customer for match in matches for customer in match.customers})
        lines = [
            "---",
            f"title: '{issue_key}'",
            "tags:",
            "  - lumentum",
            "  - issue-index",
            "  - rma",
            "---",
            "",
            f"# {issue_key}",
            "",
            "## Related Customers",
            "",
        ]
        if unique_customers:
            for customer in unique_customers:
                lines.append(f"- `{customer}`")
        else:
            lines.append("- 無")
        lines.extend(["", "## Weekly Reports", ""])
        for match in sorted(matches, key=lambda item: item.note.title, reverse=True):
            customer_text = ", ".join(match.customers) if match.customers else "無"
            lines.append(
                f"- {render_link(match.note.vault_rel, match.note.title)} | 客戶：{customer_text} | 摘錄：{match.excerpt}"
            )
        (VAULT_DIR / rel).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return issue_page_links


def write_issue_index(issue_map: dict[str, list[Match]], issue_links: dict[str, str]) -> None:
    ISSUES_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        "title: RMA Issue Index",
        "tags:",
        "  - lumentum",
        "  - index",
        "  - rma",
        "---",
        "",
        "# RMA / Issue Index",
        "",
        f"- 總 issue key 數：`{len(issue_map)}`",
        "",
        "## Keys",
        "",
    ]
    for issue_key, matches in sorted(issue_map.items(), key=lambda item: (-len(item[1]), item[0].lower())):
        lines.append(f"- {render_link(issue_links[issue_key], issue_key)} ({len(matches)})")
    (ISSUES_DIR / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_customer_index(customer_map: dict[str, list[Match]], customer_links: dict[str, str]) -> None:
    CUSTOMERS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        "title: Customer Index",
        "tags:",
        "  - lumentum",
        "  - index",
        "  - customer",
        "---",
        "",
        "# Customer Index",
        "",
        f"- 總 customer key 數：`{len(customer_map)}`",
        "",
        "## Keys",
        "",
    ]
    for customer, matches in sorted(customer_map.items(), key=lambda item: (-len(item[1]), item[0].lower())):
        lines.append(f"- {render_link(customer_links[customer], customer)} ({len(matches)})")
    (CUSTOMERS_DIR / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_root_index(issue_count: int, customer_count: int) -> None:
    text = INDEX_PATH.read_text(encoding="utf-8")
    lookup_block = (
        "## Lookup Indexes\n\n"
        f"- [[Lumentum/Issues/index.md|RMA / Issue Index]] (`{issue_count}` keys)\n"
        f"- [[Lumentum/Customers/index.md|Customer Index]] (`{customer_count}` keys)\n"
    )
    if "## Lookup Indexes" in text:
        text = re.sub(r"## Lookup Indexes[\s\S]*?(?=\n## |\Z)", lookup_block.rstrip(), text, count=1)
    else:
        text = text.replace("## Weekly Reports\n", lookup_block + "\n## Weekly Reports\n", 1)
    if "## Issues\n\n- 待建立" in text:
        text = text.replace(
            "## Issues\n\n- 待建立",
            "## Issues\n\n- [[Lumentum/Issues/index.md|RMA / Issue Index]]\n- [[Lumentum/Customers/index.md|Customer Index]]",
        )
    INDEX_PATH.write_text(text, encoding="utf-8")


def update_log(issue_count: int, customer_count: int) -> None:
    entry = (
        f"## [{date.today().isoformat()}] index | rebuilt weekly report relation indexes "
        f"({issue_count} issue keys, {customer_count} customer keys)"
    )
    text = LOG_PATH.read_text(encoding="utf-8").rstrip() + "\n"
    if entry not in text:
        text += entry + "\n"
        LOG_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    issue_map: dict[str, list[Match]] = defaultdict(list)
    customer_map: dict[str, list[Match]] = defaultdict(list)
    weekly_files = sorted(WEEKLY_DIR.rglob("*.md"))
    for path in weekly_files:
        text = path.read_text(encoding="utf-8")
        note = NoteRef(
            vault_rel=str(path.relative_to(VAULT_DIR)).replace("\\", "/"),
            title=note_title(path),
        )
        seen_lines: set[str] = set()
        for raw_line in relevant_lines(text):
            issue_key, customers, excerpt = parse_issue_and_customers(raw_line)
            if not issue_key or issue_key in GENERIC_ISSUE_KEYS:
                continue
            dedupe_key = f"{note.vault_rel}::{issue_key}::{excerpt}"
            if dedupe_key in seen_lines:
                continue
            seen_lines.add(dedupe_key)
            match = Match(note=note, issue_key=issue_key, customers=tuple(customers), excerpt=excerpt)
            issue_map[issue_key].append(match)
            for customer in customers:
                customer_map[customer].append(match)

    issue_links = write_issue_pages(issue_map)
    customer_links = write_customer_pages(customer_map, issue_links)
    write_issue_index(issue_map, issue_links)
    write_customer_index(customer_map, customer_links)
    update_root_index(len(issue_map), len(customer_map))
    update_log(len(issue_map), len(customer_map))

    print(f"WEEKLY_NOTES={len(weekly_files)}")
    print(f"ISSUE_KEYS={len(issue_map)}")
    print(f"CUSTOMER_KEYS={len(customer_map)}")


if __name__ == "__main__":
    main()
