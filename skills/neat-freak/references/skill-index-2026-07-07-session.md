# Skill_Index 口徑審查（2026-07-07）

## 口徑狀態

- Actual rows: **594**
- Summary header: **594** ✓
- Category Map: **594** ✓
- Per-section: 8 sections ✓ (all aligned)

## Drift 修復日誌

| 口徑層 | 修復前 | 修復後 |
|--------|--------|--------|
| Summary | 603 | 594 |
| Category Map | 603 | 594 |
| agent-workflows | 136 | 135 |
| science-data | 111 | 110 |
| media-documents | 64 | 62 |
| finance-skill-pack | 65 | 64 |
| knowledge-vault | 39 | 38 |
| engineering (combined) | 91 | 90 |
| manual-review (combined) | 35 | 34 |
| Root-level Skills | 62 | 61 |

## Pattern OO 發現

口徑驗證時發現 skill-index-check.py 回報 `Actual rows: 0`，但 header=603。 Root cause：腐蝕圖譜中所有 regex 仍使用 pipe-bracket link 格式（`\| [name](../SKILL.md)`），但 2026-06-29 rebuild 後已改為 pipe table 格式（`\| name \| path \| description \| api_key \|`）。

正確口徑 count（已驗證）：
```python
actual = [l for l in lines if re.match(r'^\| [a-z]', l) and 'SKILL.md' in l]
# 不再用 re.findall(r'^\| \[([^\]]+\.md)\]', ...)——永遠返回 0
```

## 其他發現

- sync-check.py DRIFT（3 項 EXTRA）→ Pattern S/Z 確診，全部為 origin/main tracked content，非污染
- docs/Readme.md Primary Read Targets：全部目錄存在，無 phantom
- dated STATUS 檔案（`skill-archive-2026-04-29.md` 等）→ 未被引用但 git history 有記錄，依 Pattern GG 為已封存歷史，原則上不主動刪除
- 口徑修復 commit 同次 session push ✓（Pattern U）
