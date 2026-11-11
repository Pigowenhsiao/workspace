# Skill Index Script Bugs — 2026-05-22 Session

## 觸發情境

Cron job 執行 neat-freak，sync-check.py + skill-index-check.py 輸出異常：
- skill-index-check.py：578 dangling（幾乎全部 skills）、39 category mismatches（幾乎全部 mismatch）
- 輸出「ALL CLEAN」但同時有大量錯誤信號

## Root Cause 分析

### Bug 1：check_dangling() 路徑拼接錯誤

```python
import os
# 錯誤
docs_base = os.path.join(AGENT_ROOT, "docs/")
paths = re.findall(r'\|\s*[^\]]+\]\(([^)]+SKILL\.md)(?=\))', idx_content, re.IGNORECASE)
for sp in paths:
    full = os.path.normpath(os.path.join(docs_base, sp))  # → docs/skills/...
```

Skill_Index.md 的 entry 格式是 `[skills/browser-web-social/aihot/SKILL.md]`（相對於 workspace 根目錄），但代碼拼接了 `docs/`，導致所有路徑變成 `docs/skills/...`，而實際 SKILL.md 在 `skills/` 而非 `docs/skills/`。

**修復**：
```python
import os
paths = re.findall(r'\`\[([^\]]+SKILL\.md)\]\`', idx_content, re.IGNORECASE)
for sp in paths:
    full = os.path.normpath(os.path.join(AGENT_ROOT, sp))  # 直接以 AGENT_ROOT 為基底
```

### Bug 2：check_header_drift() header regex 錯誤

```python
# 錯誤
header_m = re.search(r'- Active Skills:\s*\*{2,3}(\d+)\*{2,3}', idx_content)

# 實際檔案格式
# Auto-generated from disk scan: 578
```

**修復**：改為 `r'Auto-generated from disk scan:\s*(\d+)'`

### Bug 3：check_category_counts() 比較兩套不同命名系統

- Skill_Index.md sections：目錄名（`agent-workflows`、`science-data`）— 39 個
- Skill_Category.md categories：功能性分類（`Agent, Workflow & Skill Operations`）— 14 個

兩套命名完全沒有重疊，逐項比對導致 100% mismatch。

**修復**：移除逐項比對，只報告 total sum。

## 驗證方法

```bash
# 獨立計數（不走 script 的 regex）
python3 -c "
import re
content = open('docs/Skill_Index.md').read()
actual = re.findall(r'\`\[([^\]]+SKILL\.md)\]\`', content, re.IGNORECASE)
print(f'Actual rows: {len(actual)}')
"

# 跑 verify-patch.py 確認口徑
python3 skills/neat-freak/scripts/verify-patch.py
```

## 預防原則

1. **任何修改 regex 後必須跑 verify-patch.py**，不能只依賴 script 自己輸出
2. **任何 drift 都先用獨立 Python 重新 count**（不走 script 的 regex 邏輯）
3. **格式變更時同步檢查所有相關 regex**（header、dangling、per-section、category）