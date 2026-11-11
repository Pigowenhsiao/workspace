# Skill_Index 2026-07-23 Session

## 口徑狀態
- Actual rows: **460**
- Summary header: **460** ✓（`***460***` format, triple asterisk）
- Section header sum: **460** ✓（全部 7 sections 對齊）
- Category Map sum: **76**（落後，與 actual 差 384；舊格式殘留，見下）

## 本次發現的腐蝕

### Ghost Section Headers — 來自未完成的 partial rebuild
**觀察**：`docs/Skill_Index.md` lines 12-365 包含 14 個 section headers（01-Knowledge-System、agent-workflows 等），但所有這些 sections 下的實際 rows 為 0。Lines 366-1028 才是真實資料（science-data、media-documents 等 7 個 sections）。

**根因**：某次 rebuild 產生了一半的內容（真實資料區段），但另一半（前半部）在完成前被中斷或覆寫，留下了帶錯誤 count 的 section headers，卻沒有對應的實際 rows。

**修復**：刪除 lines 12-365（ghost sections），保留 lines 366-1028（真實內容）。

**驗證命令**：
```python
import re
with open('docs/Skill_Index.md') as f: lines = f.read().split('\n')
sections = [(i, l) for i,l in enumerate(lines) if re.match(r'^## ([^#]+)\s*\((\d+)\)', l)]
for pos, line in sections:
    exp = int(re.match(r'^## ([^#]+)\s*\((\d+)\)', line).group(2))
    start, end = pos+1, next((p for p,_ in sections if p>pos), len(lines))
    actual = len([l for l in lines[start:end] if re.match(r'^\| [a-z0-9]', l) and 'SKILL.md' in l])
    if actual != exp:
        print(f'DRIFT: {line[:50]} expected={exp} actual={actual}')
```

### Orphan Conflict Marker（Line 9）
**觀察**：Summary 區段殘留 `>>>>>>> fe915f5d4b9e6d40bd3ec07815dfe38430438980` artifact。

**根因**：上游 `git pull` 產生 conflict，解決時只移除了 `<<<<<<< HEAD` 和 `=======` 段落，但漏掉了 `>>>>>>>` 行。

### Skill_Index.md Format — Pipe-Table（已確認）
**當前格式**：純文字 pipe table（`\| name \| path \| description \| api_key \|`），非 link format。
**口徑驗證**：使用 `^\| [a-z0-9]` pattern。

### Category Map Sum Drift
**觀察**：Category Map sum = 76，但 actual = 460。差距 384。

**根因**：Category Map 是舊格式殘留（14 個舊 categories，總和 76）。新版 Skill_Index.md 的 7 個 sections 與舊 Category Map 完全不同。Pattern NN（三口徑）告訴我們 Category Map 和 actual rows 允許口徑不一致（不同命名系統），但 drift 超過 2 需要關注。此案 drift = 384，是結構性差異，非普通 drift。

**處置**：不需要在本次修復，未來完整 rebuild Skill_Index.md 時一併重建 Category Map。

## skill-index-check.py 口徑偏差（已知問題）
Script 報告 `Actual rows: 469`，獨立驗證為 `460`。差 9 個。

**根因**：Script 的口徑 regex（`\|\s*\[.+?\]\(.+?SKILL\.md\)`）不匹配當前 pipe-table 格式，永遠返回 0 或錯誤值。這是 Pattern AA 問題在 pipe-table 格式下的延續。

**不要信任 script 的口徑輸出**。使用獨立 Python 驗證：
```python
import re
with open('docs/Skill_Index.md') as f: lines = f.read().split('\n')
actual = [l for l in lines if re.match(r'^\| [a-z0-9]', l) and 'SKILL.md' in l]
print(f'Actual: {len(actual)}')
```

## Cron 調用結論
- `skills=[neat-freak]` bare name 在某些 Hermes 配置下失敗（「Skill(s) not found and skipped」）
- 正確做法：使用完整路徑或確認 Hermes 技能解析順序
- 建議：cron 配置中使用完整 skill 路徑而非 bare name
