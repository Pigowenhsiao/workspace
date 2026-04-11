from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


SOURCE_DIR = Path(r"C:\Users\hsi67063\Box\3DS Quality Taiwan\Pigo\Weekly report\SAG Weekly report")
VAULT_DIR = Path(r"C:\Users\hsi67063\Box\00-home-pigo.hsiao\VBA\Pigo_Obsidian")
LUMENTUM_DIR = VAULT_DIR / "Lumentum"
DEST_ROOT = LUMENTUM_DIR / "Weekly Reports"
INDEX_PATH = LUMENTUM_DIR / "index.md"
LOG_PATH = LUMENTUM_DIR / "log.md"

PERIOD_RE = re.compile(r"(?P<kind>CY|FY)\s*(?P<yy>\d{2})\s*W(?:K)?\s*(?P<wk>\d{1,2})", re.IGNORECASE)
WEEKLY_HINT_RE = re.compile(r"(weekly|wk)", re.IGNORECASE)
TITLE_NOISE_RE = re.compile(r"\s+\(\d+\)$")


@dataclass(frozen=True)
class Candidate:
    path: Path
    kind: str
    yy: str
    week: int
    title: str
    team: str

    @property
    def period_slug(self) -> str:
        return f"{self.kind}{self.yy}W{self.week:02d}"

    @property
    def folder_name(self) -> str:
        return f"20{self.yy}" if self.kind == "CY" else f"FY{self.yy}"

    @property
    def note_name(self) -> str:
        return f"{self.period_slug} - {self.title}.md"


def normalize_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_period(text: str) -> tuple[str, str, int] | None:
    match = PERIOD_RE.search(text)
    if not match:
        return None
    return match.group("kind").upper(), match.group("yy"), int(match.group("wk"))


def infer_title_and_team(filename: str) -> tuple[str, str]:
    lower = filename.lower()
    if "weekly sag-ops report" in lower:
        return "Weekly SAG-Ops Report", "SAG Ops"
    if "sag-tak quality weekly update" in lower:
        return "SAG-TAK Quality Weekly Update", "SAG-TAK Quality"
    if "tak quality weekly update" in lower and "sag-tak" not in lower:
        return "TAK Quality Weekly Update", "TAK Quality"
    if "sag quality weekly update" in lower:
        return "SAG Quality Weekly Update", "SAG Quality"
    if re.fullmatch(r"(cy|fy)\d{2}\s*wk\s*\d{1,2}", lower.replace(" ", "")):
        return "SAG Quality Weekly Update", "SAG Quality"
    if re.fullmatch(r"(cy|fy)\d{2}wk\d{1,2}", lower.replace(" ", "")):
        return "SAG Quality Weekly Update", "SAG Quality"
    return "Weekly Report", "General"


def choose_rank(path: Path) -> tuple[int, int, float]:
    size = path.stat().st_size
    suffix = path.suffix.lower()
    if suffix == ".pptx" and size >= 200_000:
        return (3, size, path.stat().st_mtime)
    if suffix == ".pdf":
        return (2, size, path.stat().st_mtime)
    if suffix == ".pptx":
        return (1, size, path.stat().st_mtime)
    return (0, size, path.stat().st_mtime)


def discover_candidates() -> list[Candidate]:
    picked: dict[tuple[str, str, int, str], Candidate] = {}
    ranking: dict[tuple[str, str, int, str], tuple[int, int, float]] = {}
    for path in SOURCE_DIR.iterdir():
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".pptx", ".pdf"}:
            continue
        if not WEEKLY_HINT_RE.search(path.name):
            continue
        period = parse_period(path.name)
        if not period:
            continue
        kind, yy, week = period
        title, team = infer_title_and_team(path.stem)
        key = (kind, yy, week, title)
        rank = choose_rank(path)
        if key not in ranking or rank > ranking[key]:
            picked[key] = Candidate(path=path, kind=kind, yy=yy, week=week, title=title, team=team)
            ranking[key] = rank
    return sorted(picked.values(), key=lambda item: (item.folder_name, item.period_slug, item.title))


def run_markitdown(path: Path) -> tuple[str, str, int]:
    proc = subprocess.run(
        [sys.executable, "-m", "markitdown", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return proc.stdout, proc.stderr.strip(), proc.returncode


def clean_line(line: str) -> str:
    line = line.replace("\u00a0", " ")
    line = re.sub(r"[ \t]+", " ", line)
    line = line.strip(" -\t")
    return normalize_spaces(line)


def meaningful_lines(text: str, source_name: str) -> list[str]:
    lines: list[str] = []
    seen: set[str] = set()
    for raw in text.splitlines():
        line = clean_line(raw)
        if not line:
            continue
        if line in seen:
            continue
        if len(line) < 3 or len(line) > 220:
            continue
        if line == source_name:
            continue
        if line.startswith("<!--") or line.startswith("!["):
            continue
        if re.fullmatch(r"[#*=._/\\|:]+", line):
            continue
        seen.add(line)
        lines.append(line)
    return lines


THEME_KEYWORDS = [
    ("客訴 / RMA", ["rma", "claim", "customer", "field failure", "compensation"]),
    ("內部異常 / 失效", ["failure", "abnormal", "open", "burn-in", "burn in", "trouble", "defect"]),
    ("Audit / Finding closure", ["audit", "finding", "major", "minor"]),
    ("Change control", ["awr", "ccr", "change control"]),
    ("Yield / SPC / 系統改善", ["yield", "spc", "mes", "cpk", "improvement"]),
    ("FA / Root cause", ["root cause", "analysis", "containment", "corrective action", "fa report"]),
]

FOCUS_KEYWORDS = [
    "quality", "yield", "rma", "audit", "failure", "open", "summary", "spc", "customer",
    "abnormal", "action", "improvement", "finding", "root cause", "containment", "issue",
]
RISK_KEYWORDS = [
    "rma", "failure", "open", "abnormal", "audit", "finding", "claim", "scrap", "reject",
    "burn-in", "burn in", "field failure", "trouble", "defect", "risk",
]
FOLLOWUP_KEYWORDS = [
    "action", "plan", "target", "owner", "eta", "due", "review", "pending", "close",
    "closure", "trial", "schedule", "improvement", "next", "follow",
]


def select_lines(lines: list[str], keywords: list[str], limit: int) -> list[str]:
    hits: list[str] = []
    for line in lines:
        lower = line.lower()
        if any(keyword in lower for keyword in keywords):
            hits.append(line)
        if len(hits) >= limit:
            break
    return hits


def infer_title_from_text(text: str, fallback_title: str, fallback_team: str) -> tuple[str, str]:
    if fallback_title in {"SAG-TAK Quality Weekly Update", "TAK Quality Weekly Update", "Weekly SAG-Ops Report"}:
        return fallback_title, fallback_team
    lower = text.lower()
    if "weekly sag-ops report" in lower:
        return "Weekly SAG-Ops Report", "SAG Ops"
    if "sag-tak quality weekly update" in lower:
        return "SAG-TAK Quality Weekly Update", "SAG-TAK Quality"
    if "tak quality weekly update" in lower and "sag-tak" not in lower:
        return "TAK Quality Weekly Update", "TAK Quality"
    if "sag quality weekly update" in lower or "quality update owner" in lower:
        return "SAG Quality Weekly Update", "SAG Quality"
    return fallback_title, fallback_team


def infer_themes(text: str) -> list[str]:
    lower = text.lower()
    themes = [label for label, keywords in THEME_KEYWORDS if any(keyword in lower for keyword in keywords)]
    return themes[:4]


def yaml_quote(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


def tag_for_team(team: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", team.lower()).strip("-")


def parse_frontmatter_value(text: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*'?(.*?)'?\s*$", text, re.MULTILINE)
    return match.group(1) if match else None


def replace_first(pattern: str, replacement: str, text: str) -> str:
    return re.sub(pattern, replacement, text, count=1, flags=re.MULTILINE)


def repair_existing_notes() -> int:
    repaired = 0
    team_tags = {"sag-quality", "sag-tak-quality", "tak-quality", "sag-ops", "general"}
    for note_path in DEST_ROOT.rglob("*.md"):
        text = note_path.read_text(encoding="utf-8")
        source_file = parse_frontmatter_value(text, "source_file")
        if not source_file:
            continue
        desired_title, desired_team = infer_title_and_team(Path(source_file).stem)
        current_title = parse_frontmatter_value(text, "title")
        current_team = parse_frontmatter_value(text, "team")
        if not current_title or not current_team:
            continue
        period_slug = current_title.split(" - ", 1)[0]
        desired_full_title = f"{period_slug} - {desired_title}"
        desired_tag = tag_for_team(desired_team)
        changed = False

        if current_title != desired_full_title:
            text = replace_first(r"^title:\s*.*$", f"title: {yaml_quote(desired_full_title)}", text)
            text = replace_first(r"^# .*$", f"# {desired_full_title}", text)
            changed = True
        if current_team != desired_team:
            text = replace_first(r"^team:\s*.*$", f"team: {yaml_quote(desired_team)}", text)
            changed = True

        lines = text.splitlines()
        updated_lines: list[str] = []
        tag_replaced = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("- "):
                tag_value = stripped[2:].strip()
                if tag_value in team_tags:
                    updated_lines.append(f"  - {desired_tag}")
                    tag_replaced = True
                    continue
            updated_lines.append(line)
        if changed and not tag_replaced:
            updated_lines.insert(updated_lines.index("tags:") + 1, f"  - {desired_tag}")
        if changed:
            text = "\n".join(updated_lines).rstrip() + "\n"
            note_path.write_text(text, encoding="utf-8")
            desired_path = note_path.with_name(f"{desired_full_title}.md")
            if desired_path != note_path:
                if desired_path.exists():
                    desired_path.unlink()
                note_path.rename(desired_path)
            repaired += 1
    return repaired


def build_note(candidate: Candidate, text: str, stderr: str) -> str:
    title, team = infer_title_from_text(text, candidate.title, candidate.team)
    lines = meaningful_lines(text, candidate.path.name)
    themes = infer_themes(text)
    focus = select_lines(lines, FOCUS_KEYWORDS, 6)
    risks = select_lines(lines, RISK_KEYWORDS, 5)
    followups = select_lines(lines, FOLLOWUP_KEYWORDS, 5)

    if not focus:
        focus = lines[:5]
    if not risks:
        risks = ["本份來源沒有明確抽出固定的風險關鍵字，後續可再人工補強。"]
    if not followups:
        followups = ["建議後續人工確認 owner、target date 與是否需要拆成 Issues / Projects 長期追蹤。"]

    summary_parts = themes if themes else ["週報主題已擷取，但需要人工再補強語意摘要"]
    summary = (
        f"本筆記由批次流程從 `{candidate.path.name}` 擷取並整理。"
        f"依可辨識內容判斷，本週主軸集中在：{'、'.join(summary_parts)}。"
        "這份筆記已保留可搜尋的關鍵片段，後續若要做正式週會摘要，可直接在此基礎上補寫。"
    )

    extraction_status = "high" if len(lines) >= 20 else "medium" if len(lines) >= 8 else "low"
    tags = [
        "lumentum",
        "weekly-report",
        tag_for_team(team),
    ]
    if any("rma" in item.lower() for item in lines):
        tags.append("rma")
    if any("audit" in item.lower() for item in lines):
        tags.append("audit")

    note_lines = [
        "---",
        f"title: {yaml_quote(f'{candidate.period_slug} - {title}')}",
        "company: Lumentum",
        "workspace: Lumentum",
        "type: weekly-report",
        f"team: {yaml_quote(team)}",
        f"cycle_year: '{candidate.yy}'",
        f"week: {candidate.week}",
        f"source_file: {yaml_quote(candidate.path.name)}",
        f"source_path: {yaml_quote(str(candidate.path))}",
        f"extraction_confidence: {extraction_status}",
        "tags:",
    ]
    for tag in tags:
        note_lines.append(f"  - {tag}")
    note_lines.extend(
        [
            "---",
            "",
            f"# {candidate.period_slug} - {title}",
            "",
            "## 核心摘要",
            "",
            summary,
            "",
            "## 本週重點",
            "",
        ]
    )
    for item in focus:
        note_lines.append(f"- {item}")
    note_lines.extend(["", "## 風險與異常", ""])
    for item in risks:
        note_lines.append(f"- {item}")
    note_lines.extend(["", "## 待追蹤事項", ""])
    for item in followups:
        note_lines.append(f"- {item}")
    note_lines.extend(
        [
            "",
            "## 我會怎麼用這份週報",
            "",
            "這份筆記可作為後續查詢產品、客戶、RMA、audit 或內部異常的索引入口。若同一議題連續多週出現，建議再拆成 `Lumentum/Issues/` 或 `Lumentum/Projects/` 的長期追蹤筆記。",
            "",
            "## Source",
            "",
            f"- 原始檔：`{candidate.path.name}`",
            f"- 原始路徑：`{candidate.path}`",
            f"- 匯入方式：`python -m markitdown`",
        ]
    )
    if stderr:
        first_warning = stderr.splitlines()[0]
        note_lines.append(f"- 擷取備註：`{first_warning}`")
    return "\n".join(note_lines) + "\n"


def build_failure_note(candidate: Candidate, reason: str) -> str:
    return "\n".join(
        [
            "---",
            f"title: {yaml_quote(f'{candidate.period_slug} - {candidate.title}')}",
            "company: Lumentum",
            "workspace: Lumentum",
            "type: weekly-report",
            f"team: {yaml_quote(candidate.team)}",
            f"cycle_year: '{candidate.yy}'",
            f"week: {candidate.week}",
            f"source_file: {yaml_quote(candidate.path.name)}",
            f"source_path: {yaml_quote(str(candidate.path))}",
            "extraction_confidence: failed",
            "tags:",
            "  - lumentum",
            "  - weekly-report",
            f"  - {tag_for_team(candidate.team)}",
            "  - source-error",
            "---",
            "",
            f"# {candidate.period_slug} - {candidate.title}",
            "",
            "## 核心摘要",
            "",
            "這份週報來源檔在批次匯入時無法正常擷取，因此先建立 placeholder 筆記保留索引位置，避免週次缺口。",
            "",
            "## 本週重點",
            "",
            "- 來源檔目前無法由 `markitdown` 正常讀取。",
            "",
            "## 風險與異常",
            "",
            f"- 擷取失敗原因：`{reason}`",
            "- 若來源檔已損壞或為空檔，需回到原始目錄補上可讀版本。",
            "",
            "## 待追蹤事項",
            "",
            "- 重新取得原始週報檔案後，再次執行 batch ingest 覆寫此筆記。",
            "- 若有同週的 PowerPoint 或其他匯出版，優先以可讀版本替換。",
            "",
            "## 我會怎麼用這份週報",
            "",
            "先把這份 placeholder 當作週次索引，提醒後續補檔，不讓時間線中斷。",
            "",
            "## Source",
            "",
            f"- 原始檔：`{candidate.path.name}`",
            f"- 原始路徑：`{candidate.path}`",
            f"- 擷取備註：`{reason}`",
            "",
        ]
    )


def build_index(note_paths: list[Path]) -> str:
    stats: Counter[str] = Counter()
    grouped: dict[str, list[Path]] = {}
    for path in note_paths:
        grouped.setdefault(path.parent.name, []).append(path)
        text = path.read_text(encoding="utf-8")
        team = parse_frontmatter_value(text, "team") or "General"
        stats[team] += 1

    lines = [
        "---",
        "title: Lumentum Workspace Index",
        "tags:",
        "  - lumentum",
        "  - workspace",
        "  - index",
        "---",
        "",
        "# Lumentum Workspace",
        "",
        "這裡是 Lumentum 相關工作知識的獨立工作區，與 `Learning/` 分開維護。",
        "",
        "## Weekly Reports",
        "",
    ]
    for folder in sorted(grouped):
        lines.append(f"### {folder}")
        lines.append("")
        for note_path in sorted(grouped[folder], key=lambda item: item.name):
            rel = note_path.relative_to(VAULT_DIR).as_posix()
            label = note_path.stem
            lines.append(f"- [[{rel}|{label}]]")
        lines.append("")

    lines.extend(
        [
            "## Meetings",
            "",
            "- 待建立",
            "",
            "## Projects",
            "",
            "- 待建立",
            "",
            "## Issues",
            "",
            "- 待建立",
            "",
            "## Current Focus",
            "",
            f"- 週報筆記總數：`{sum(stats.values())}`",
            f"- SAG Quality：`{stats.get('SAG Quality', 0)}`",
            f"- SAG-TAK Quality：`{stats.get('SAG-TAK Quality', 0)}`",
            f"- TAK Quality：`{stats.get('TAK Quality', 0)}`",
            f"- SAG Ops：`{stats.get('SAG Ops', 0)}`",
        ]
    )
    return "\n".join(lines) + "\n"


def update_log(total_notes: int, placeholder_total: int) -> None:
    lines: list[str] = []
    if LOG_PATH.exists():
        lines = LOG_PATH.read_text(encoding="utf-8").splitlines()
    filtered = [line for line in lines if "batch imported" not in line and "weekly report corpus normalized" not in line]
    entry = f"## [{datetime.now().strftime('%Y-%m-%d')}] ingest | weekly report corpus normalized ({total_notes} notes, {placeholder_total} placeholder)"
    if filtered and filtered[-1] != "":
        filtered.append("")
    filtered.append(entry)
    LOG_PATH.write_text("\n".join(filtered).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    DEST_ROOT.mkdir(parents=True, exist_ok=True)
    candidates = discover_candidates()
    repaired_count = repair_existing_notes()
    imported_count = 0
    skipped_count = 0
    warning_count = 0
    failed: list[str] = []
    placeholder_count = 0

    for candidate in candidates:
        dest_dir = DEST_ROOT / candidate.folder_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        initial_note_path = dest_dir / candidate.note_name
        if initial_note_path.exists():
            skipped_count += 1
            continue

        text, stderr, returncode = run_markitdown(candidate.path)
        title, team = infer_title_from_text(text, candidate.title, candidate.team)
        note_candidate = Candidate(
            path=candidate.path,
            kind=candidate.kind,
            yy=candidate.yy,
            week=candidate.week,
            title=title,
            team=team,
        )
        note_path = dest_dir / note_candidate.note_name

        if returncode != 0 and not text.strip():
            reason = f"markitdown return code {returncode}"
            if candidate.path.exists() and candidate.path.stat().st_size == 0:
                reason += ", source file is 0 bytes"
            note_path.write_text(build_failure_note(note_candidate, reason), encoding="utf-8")
            imported_count += 1
            placeholder_count += 1
            failed.append(f"{candidate.path.name}: {reason}")
            continue

        note_path.write_text(build_note(note_candidate, text, stderr), encoding="utf-8")
        imported_count += 1
        if stderr:
            warning_count += 1

    note_paths = sorted(DEST_ROOT.rglob("*.md"))
    placeholder_total = 0
    for path in note_paths:
        text = path.read_text(encoding="utf-8")
        if "extraction_confidence: failed" in text:
            placeholder_total += 1
    INDEX_PATH.write_text(build_index(note_paths), encoding="utf-8")
    update_log(len(note_paths), placeholder_total)

    print(f"CANDIDATES={len(candidates)}")
    print(f"REPAIRED={repaired_count}")
    print(f"IMPORTED={imported_count}")
    print(f"SKIPPED_EXISTING={skipped_count}")
    print(f"TOTAL_NOTES={len(note_paths)}")
    print(f"WARNINGS={warning_count}")
    print(f"PLACEHOLDERS={placeholder_total}")
    for folder in sorted({path.parent.name for path in note_paths}):
        count = len([path for path in note_paths if path.parent.name == folder])
        print(f"FOLDER_{folder}={count}")
    print(f"FAILED={len(failed)}")
    for item in failed[:20]:
        print(f"FAIL_ITEM={item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
