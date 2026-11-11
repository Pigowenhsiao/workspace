# Skill_Index.md 懸空引用驗證技法

## 核心問題

Skill_Index.md 的路徑解析基準，**不是** Agent 根目錄，而是 `docs/` 目錄。

所有 `../foo/SKILL.md` 形式的路徑，是相對於 `docs/` 所在的目錄來解析的。

## 錯誤做法（浪費 30 分鐘）

```python
import os
# ❌ 以 Agent/ 為基準 —— 所有路徑都 MISSING
base = os.path.expanduser('~/Documents/Agent/')
for sp in skill_paths:
    full = os.path.normpath(os.path.join(base, sp))
    # ../agent-browser/SKILL.md → ~/Documents/agent-browser/SKILL.md
    #                                    ^^^^^^^^ 多了一層
```

## 正確做法

```python
import os
# ✓ 以 docs/ 為基準 —— 所有路徑都 OK
docs_base = os.path.expanduser('~/Documents/Agent/docs/')
for sp in skill_paths:
    full = os.path.normpath(os.path.join(docs_base, sp))
    # ../agent-browser/SKILL.md → ~/Documents/Agent/agent-browser/SKILL.md ✓
```

## 為什麼設計成这样

Skill_Index.md 位於 `Agent/docs/SKILL.md`，在 `docs/` 內引用同層級的 skill 目錄（`../agent-browser/`），語義上是「從 docs 向上看 agent-browser」。

但 Agent 根目錄的 skill 目錄（`Agent/superpowers/brainstorming/SKILL.md`）屬於 Agent repo 本身，不屬於 docs。

## 驗證腳本

```python
import os
import re, os

path = os.path.expanduser('~/Documents/Agent/docs/Skill_Index.md')
with open(path) as f:
    idx = f.read()

skill_paths = re.findall(r'\|\s*\[.+\]\(([^)]+SKILL\.md)\)', idx)
docs_base = os.path.expanduser('~/Documents/Agent/docs/')

dangling = []
for sp in skill_paths:
    full = os.path.normpath(os.path.join(docs_base, sp))
    if not os.path.exists(full):
        dangling.append((sp, full))

print(f"Total: {len(skill_paths)}, Dangling: {len(dangling)}")
if dangling:
    for orig, full in dangling[:5]:
        print(f"  MISSING: {orig} → {full}")
```

## 口徑交叉檢查

驗證 `Skill_Index.md` header drift 時，永遠用 row count 而非 header 數字：

```python
actual = len(re.findall(r'\|\s*\[.+\]\(.+SKILL\.md\)', idx))
header = int(re.search(r'- Active Skills:\s*\*{2,3}(\d+)\*{2,3}', idx).group(1))
# header 會 drift，row count 不會
```

Skill_Category.md 的 per-category 加總落後於 actual rows 時，需要人工 reclassification，無法自動修復。
