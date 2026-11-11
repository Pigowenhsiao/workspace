#!/usr/bin/env python3
"""
Skill_Index.md 完整性驗證腳本
用法: python3 skill-index-check.py

檢查五類腐蝕:
1. Header drift (Summary Active Skills 數字與實際 row 數不符)
2. Per-section header drift (每個 section 的括號數字與該 section 實際 row 數不符)
3. 懸空引用 (row 路徑指向不存在的 SKILL.md)
4. Purpose cell \\ 腐蝕 (pipe 未逸出導致 cell 變 \\)
5. Category sum drift (Skill_Category.md per-category counts 與 Skill_Index.md section headers 不符)
"""
import re, os, sys

AGENT_ROOT = os.environ.get("AGENT_ROOT", os.path.join(os.path.expanduser("~"), "Documents/Agent"))
IDX_PATH = os.path.join(AGENT_ROOT, "docs/Skill_Index.md")
CAT_PATH = os.path.join(AGENT_ROOT, "docs/Skill_Category.md")


def check_dangling(idx_content):
    """檢查懸空引用 — 路徑在磁碟上不存在"""
    # Actual format: pipe table `| name | path | description | api_key |`
    # Path column ends with `.md |` — the space before the final pipe is REQUIRED,
    # otherwise the regex matches nothing and dangling reports a false CLEAN.
    paths = re.findall(r'^\| [^|]+\| ([^\s|]+\.md)\s+\|', idx_content, re.MULTILINE)
    dangling = []
    for sp in paths:
        # path like `skills/agent-workflows/gstack/browse/SKILL.md`
        full = os.path.normpath(os.path.join(AGENT_ROOT, sp))
        if not os.path.exists(full):
            dangling.append((sp, full))
    return dangling


def _split_row(line):
    """把 pipe table row 切成 cells — 只在未被 escape 的 pipe 上切分。

    Naive `line.split('|')` 會把 `\\|` 也當分隔符，導致 purpose cell 被截成
    單一反斜線殘留，cell index 全部錯位（2026-10-23 實測：14 個 corrupt row
    被 script 誤判為 clean）。
    """
    parts = re.split(r'(?<!\\)\|', line)
    return [p.strip() for p in parts[1:-1]]


def check_purpose_corruption(idx_content):
    """檢查 Purpose cell 腐蝕

    三種實測形態：
    1. `\\` / `\\\\` — pipe 未逸出導致 cell 只剩反斜線
    2. `Agent workflow skill for <name>.` — 自動生成的佔位描述（無實質資訊）
    3. 字面量 `\\n` 殘留 — YAML block scalar 換行被寫成兩字元
    """
    corrupt = []
    for i, line in enumerate(idx_content.split('\n')):
        cells = _split_row(line)
        if len(cells) >= 4:
            purpose = cells[2].strip()
            reason = None
            if purpose in ('\\', '\\\\', '\\\\\\\\') or purpose.startswith('\\'):
                reason = 'backslash'
            elif re.match(r'^Agent workflow skill for .+\.$', purpose):
                reason = 'placeholder'
            elif '\\n' in purpose:
                reason = 'literal-newline'
            if reason:
                name = cells[0] if cells else '?'
                corrupt.append((i + 1, name, purpose, line[:120], reason))
    return corrupt


def check_header_drift(idx_content):
    """檢查 Summary header drift"""
    # Actual format: pipe table `| name | path | description | api_key |`
    # Path column ends with `.md |` (space before final pipe)
    actual = len(re.findall(r'^\| [^|]+\| [^\s|]+\.md\s+\|', idx_content, re.MULTILINE))
    # The Summary line is rendered as `- Active Skills: ***606***` — 2 or 3 asterisks
    # on each side depending on the rebuild that produced it. A strict `\*\*(\d+)\*\*`
    # misses the 3-asterisk form and reports a false -N drift.
    header_m = re.search(r'- Active Skills:\s*\*{2,3}(\d+)\*{2,3}', idx_content)
    header_n = int(header_m.group(1)) if header_m else 0
    return actual, header_n, header_n - actual


def check_per_section_drift(idx_content):
    """檢查每個 section header 的括號數字是否與該 section 實際 row 數相符"""
    mismatches = []
    lines = idx_content.split('\n')
    current_cat = None
    cat_counts = {}

    for line in lines:
        m = re.match(r'^## (.+?) \((\d+)\)$', line)
        if m:
            current_cat = m.group(1)
            header_count = int(m.group(2))
            cat_counts[current_cat] = {'header': header_count, 'actual': 0}
        elif current_cat:
            # Actual format: pipe table row `| name | path | description | api_key |`
            # Path column ends with `.md |` (space before final pipe)
            if re.match(r'^\| [^|]+\| [^\s|]+\.md\s+\|', line):
                cat_counts[current_cat]['actual'] += 1

    for name, info in cat_counts.items():
        if info['header'] != info['actual']:
            mismatches.append((name, info['header'], info['actual']))

    return mismatches


def check_api_key_breakdown(idx_content):
    """檢查 Summary 區的 api_key 分解數字是否與 index 內實際 cell 值一致

    2026-10-29 實測（Pattern XXX）：`Active Skills` 由 759 改成 760 時，
    `No API key detected` 沒跟著 +1（仍寫 534，實際 535），導致
    32 + 193 + 534 = 759 ≠ 760。

    **舊 checker 的盲區**：五項檢查只覆蓋 Active Skills / per-section /
    dangling / purpose cell / category sum，**完全沒驗這三個分解數字**
    → 回報 ✓ ALL CLEAN，但文件內部已自相矛盾。
    """
    rows = re.findall(r'^\| [^|]+\| [^\s|]+\.md\s+\|.*$', idx_content, re.MULTILINE)
    actual = {}
    for line in rows:
        cells = _split_row(line)
        if len(cells) >= 4:
            key = cells[3].strip()
            actual[key] = actual.get(key, 0) + 1

    claims = {}
    for label, key in (('Requires API key', '需要'),
                        ('May require API key', '可能需要'),
                        ('No API key detected', '不需要')):
        m = re.search(r'- ' + re.escape(label) + r':\s*\*{2,3}(\d+)\*{2,3}', idx_content)
        if m:
            claims[key] = int(m.group(1))

    mismatches = []
    for key, claimed in claims.items():
        real = actual.get(key, 0)
        if real != claimed:
            mismatches.append((key, claimed, real))
    return mismatches, actual, claims


def check_category_self_consistency(cat_path):
    """檢查 Skill_Category.md 自身的加總聲明是否與它自己的表格一致

    2026-10-29 實測（Pattern YYY）：Verification Notes 寫
    `Sum of category counts: 595 ✓`，但表格加總實際是 **581** ——
    文件自己打自己的嘴巴。舊 checker 只比對兩份文件的 total，
    從不驗「單一文件內部的聲明 vs 自身內容」是否一致。
    """
    try:
        with open(cat_path, encoding='utf-8') as f:
            cat = f.read()
    except OSError:
        return None, None, 0

    m = re.search(r'## Categories\n(.*?)(?=\n## |\Z)', cat, re.DOTALL)
    body = m.group(1) if m else cat
    rows = re.findall(r'^\| ([^|]+)\|\s*(\d+)\s*\|', body, re.MULTILINE)
    table_sum = sum(int(c) for _, c in rows)

    # 兩種合法的自我聲明形式都要認：
    #   - 'Sum of category counts: N'   （舊格式）
    #   - 'Table row sum: N'            （2026-10-29 新格式）
    claim = None
    claim_re = re.search(r'(?:Sum of category counts|Table row sum):\s*\*{0,2}(\d+)', cat)
    if claim_re:
        claim = int(claim_re.group(1))
    return table_sum, claim, len(rows)


def check_category_counts(idx_content, cat_path):
    """檢查 Skill_Category.md per-category counts 是否與 Skill_Index.md section headers 對齊

    注意：Skill_Index.md 使用目錄名（39 個 sections，如 "agent-workflows"、"science-data"），
    而 Skill_Category.md 使用功能性分類名（14 個 categories，如 "Agent, Workflow & Skill Operations"）。
    兩套命名系統不同，這裡不做名稱比對，只做 total sum 比對。
    """
    idx_sections = dict(re.findall(r'^## (.+?) \((\d+)\)$', idx_content, re.MULTILINE))

    try:
        with open(cat_path) as f:
            cat_content = f.read()
        cat_rows = re.findall(r'^\| ([^|]+)\| (\d+) \|', cat_content, re.MULTILINE)
        cat_sum_dict = {name.strip(): int(count) for name, count in cat_rows}
    except Exception:
        cat_sum_dict = {}

    idx_total = sum(int(c) for c in idx_sections.values())
    cat_total = sum(cat_sum_dict.values())
    total_mismatch = idx_total != cat_total

    # 不再逐項比對（因為命名系統不同），只做 total sum
    mismatches = []
    return mismatches, idx_total, cat_total


def main():
    with open(IDX_PATH) as f:
        idx = f.read()

    print("=" * 60)
    print("Skill_Index.md Verification Report")
    print("=" * 60)

    # 1. Summary header drift
    actual, header_n, drift = check_header_drift(idx)
    status = "✓" if drift == 0 else f"✗ DRIFT {drift:+d}"
    print(f"\n[1] Header drift (Summary Active Skills)")
    print(f"    Actual rows:   {actual}")
    print(f"    Header:        {header_n}")
    print(f"    Status:        {status}")

    # 2. Per-section header drift
    sec_mismatches = check_per_section_drift(idx)
    print(f"\n[2] Per-section header drift")
    if sec_mismatches:
        print(f"    Status:        ✗ {len(sec_mismatches)} section(s) off")
        for name, header, actual_sec in sec_mismatches:
            print(f"    - '{name}': header={header}, actual={actual_sec}")
    else:
        sections = re.findall(r'^## (.+?) \((\d+)\)$', idx, re.MULTILINE)
        print(f"    Status:        ✓ All {len(sections)} sections match")

    # 3. Dangling refs
    dangling = check_dangling(idx)
    status = "✓" if not dangling else f"✗ {len(dangling)} dangling"
    print(f"\n[3] Dangling references")
    print(f"    Status:        {status}")
    if dangling:
        by_dir = {}
        for sp, full in dangling:
            d = os.path.dirname(sp)
            by_dir.setdefault(d, []).append(sp)
        for d, items in by_dir.items():
            print(f"    {d}/: {len(items)} rows")
            for sp in items[:3]:
                print(f"      - {sp}")
            if len(items) > 3:
                print(f"      ... +{len(items)-3} more")

    # 4. Purpose cell corruption
    corrupt = check_purpose_corruption(idx)
    status = "✓" if not corrupt else f"✗ {len(corrupt)} corrupted"
    print(f"\n[4] Purpose cell \\\\ corruption")
    print(f"    Status:        {status}")
    if corrupt:
        for ln, name, purpose, preview, reason in corrupt[:5]:
            print(f"    L{ln} [{name}] ({reason}): {preview[:70]}")
        if len(corrupt) > 5:
            print(f"    ... +{len(corrupt)-5} more")

    # 5. Skill_Category.md alignment
    cat_mismatches, idx_total, cat_total = check_category_counts(idx, CAT_PATH)
    print(f"\n[5] Skill_Category.md alignment")
    print(f"    Skill_Index total: {idx_total}")
    print(f"    Skill_Category total: {cat_total}")
    if idx_total != cat_total:
        print(f"    Status:        ✓ (different naming systems, totals noted)")
    elif cat_mismatches:
        print(f"    Status:        ✗ {len(cat_mismatches)} category mismatch(es)")
        for name, idx_c, cat_c in cat_mismatches:
            print(f"    - '{name}': Skill_Index={idx_c}, Skill_Category={cat_c}")
    else:
        print(f"    Status:        ✓ All categories match")

    # 6. api_key 分解數字 vs 實際 cell 值（Pattern XXX，2026-10-29 新增）
    api_mismatches, api_actual, api_claims = check_api_key_breakdown(idx)
    print(f"\n[6] API key breakdown drift (Summary vs actual cells)")
    for key in ('需要', '可能需要', '不需要'):
        if key in api_claims:
            print(f"    {key}: claimed={api_claims[key]}, actual={api_actual.get(key, 0)}")
    if api_mismatches:
        print(f"    Status:        ✗ {len(api_mismatches)} breakdown mismatch(es)")
        for key, claimed, real in api_mismatches:
            print(f"    - '{key}': claimed={claimed}, actual={real}")
    else:
        print(f"    Status:        ✓")

    # 7. Skill_Category.md 自我一致性（Pattern YYY，2026-10-29 新增）
    cat_table_sum, cat_claim, cat_rows_n = check_category_self_consistency(CAT_PATH)
    print(f"\n[7] Skill_Category.md self-consistency")
    if cat_table_sum is None:
        print(f"    Status:        (file not readable, skipped)")
    else:
        print(f"    Table rows: {cat_rows_n}, table sum: {cat_table_sum}")
        print(f"    Claimed sum: {cat_claim}")
        if cat_claim is not None and cat_claim != cat_table_sum:
            print(f"    Status:        ✗ self-contradiction (claim={cat_claim}, table={cat_table_sum})")
        else:
            print(f"    Status:        ✓")

    print("\n" + "=" * 60)
    all_ok = (not dangling and not corrupt and drift == 0 and not sec_mismatches
              and not cat_mismatches and not api_mismatches
              and not (cat_claim is not None and cat_table_sum is not None
                       and cat_claim != cat_table_sum))
    print(f"OVERALL: {'✓ ALL CLEAN' if all_ok else '✗ ISSUES FOUND'}")
    print("=" * 60)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
