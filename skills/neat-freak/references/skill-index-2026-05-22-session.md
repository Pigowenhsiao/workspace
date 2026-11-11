# Skill Index — 2026-05-22 Session

## 發現：Missing canonical reference 再現

**背景**：上次 session（2026-05-21） restore 了 `skill-index-2026-05-21-session.md`，這次 session 又發現 `skill-index-script-bugs-2026-05-22.md` 同樣在 canonical 有、workspace 無。

**sync-check.py 輸出**：
```
MISSING in workspace (1):
  - references/skill-index-script-bugs-2026-05-22.md
```

**修復動作**：
```bash
cp ~/.hermes/skills/neat-freak/references/skill-index-script-bugs-2026-05-22.md \
   ~/Documents/Agent/skills/neat-freak/references/
git -C ~/Documents/Agent add skills/neat-freak/references/skill-index-script-bugs-2026-05-22.md
git -C ~/Documents/Agent commit -m "restore missing skill-index-script-bugs-2026-05-22.md reference"
git -C ~/Documents/Agent push
```

**驗證**：
- `sync-check.py`：仍報告 DRIFT（agents/, references/Readme.md, scripts/Readme.md 屬於 Pattern Z2 的正當 EXTRA，git ls-files 確認 origin/main 有追蹤）
- `skill-index-check.py`：✓ ALL CLEAN（578 actual, header 578, drift 0）
- Branch ahead by 1 → push 完成

## 口徑確認

| 指標 | 值 | 狀態 |
|------|-----|------|
| Actual rows | 578 | ✓ |
| Header | 578 | ✓ |
| Per-section headers | 39 sections, all match | ✓ |
| Dangling | 0 | ✓ |
| Skill_Category sum | 581 (不同命名系統) | ✓ |

## 結論

Pattern Z2 確認：Missing canonical reference 會在每次 session 反覆出現，已將 restore 步驟直接寫入 Step 0。SKILL.md 已更新。