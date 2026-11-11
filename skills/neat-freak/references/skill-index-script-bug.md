# Skill_Index Script Bug — Pattern V 實錄

## 錯誤機制

`skill-index-check.py` 的 `check_per_section_drift()` 函式用 regex 計算每個 section 的 actual skill rows：

```python
# Line 49（錯誤版本）
re.findall(r'\|\s*\[.+\]\(.+[Ss][Kk][Ii][Ll][Ll]\.[Mm][Dd]\)', idx_content)

# Line 69（錯誤版本）
re.match(r'\|\s*\[.+\]\(.+[Ss][Kk][Ii][Ll][Ll]\.[Mm][Dd]\)', line)
```

問題：`.+` 是 greedy，在短路徑時會過度匹配，把 `SKILL.md` 的結尾字元也吃掉，導致整行匹配失敗。

典型失敗行：
```
| [agent-browser](../agent-browser/SKILL.md) | ... |
```

`../agent-browser/` 只有 16 字元，`.+` greedy 把後面的 `[Ss][Kk][Ii][Ll][Ll]` 也吃進去，導致 `[Ss][Kk][Ii][Ll][Ll]\.[Mm][Dd]` 沒有足夠字符可匹配，regex 回傳空。

結果：每個 section 都少算 1，14 sections × 1 = Summary 多 14。

## 修復後的正確 Regex

```python
# 非 greedy + case-insensitive
re.findall(r'\|\s*\[.+?\]\(.+?SKILL\.md\)', idx_content, re.IGNORECASE)
re.match(r'\|\s*\[.+?\]\(.+?SKILL\.md\)', line, re.IGNORECASE)
```

`.+?` 盡可能少地匹配，確保 `SKILL\.md` 能正確終止。

## 驗證方法

當 `skill-index-check.py` 報告 drift 時，先用獨立的 Python 重新計數，不走 script 的 regex：

```python
import re
content = open('docs/Skill_Index.md').read()
rows = re.findall(r'\|\s*\[.+?\]\(.+?SKILL\.md\)', content, re.IGNORECASE)
print(f'Actual rows: {len(rows)}')

# 也可用 dash-format 交叉驗證
dash_rows = re.findall(r'-\s+\*\*[^*]+\*\*\s+—', content)
print(f'Dash rows: {len(dash_rows)}')
```

若兩者差 `14 × N`（N 為均勻偏移量），且所有 section 均勻偏離 → script bug（Pattern V）。
若 drift 不均勻 → 普通口徑腐敗（Pattern I/IV）。

## Pattern V 與 Pattern J 的區別

| | Pattern J | Pattern V |
|---|---|---|
| 原因 | `dict 被 int 覆蓋`（script logic bug） | `regex greedy`（semantic bug） |
| 表現 | script 直接 crash（TypeError） | script 正常執行但結果錯誤 |
| 口徑偏差 | 最後一個 section 才爆（累計） | 所有 section 均勻偏移 |
| 修復 | 修 script logic | 改 regex 為 non-greedy |

## 為什麼這個區分重要

兩種 bug 都會導致 Skill_Index.md 口徑看起來「不符」，但處置方向完全不同：
- Pattern J：不能相信任何 header count，要重跑 script
- Pattern V：可以用 script跑完後，再對齊 header counts（因為 script 的相對關係是對的，只是絕對值偏移）

Pattern W 的獨立驗證原則就是在這種情況下保護你不會選錯處置方向。