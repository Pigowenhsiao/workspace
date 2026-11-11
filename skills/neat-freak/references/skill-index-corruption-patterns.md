# Skill_Index.md 腐蝕圖譜

## 已知腐敗模式（A–U）

1. **Pattern A** — Dangling rows：刪 skill 不更新 index
2. **Pattern B** — Purpose cell `\\` 腐蝕：description 含 `|` 未逸出
3. **Pattern C** — Summary header drift
4. **Pattern D** — Category count drift
5. **Pattern E** — Rebase conflict resolution 方向錯誤
6. **Pattern F** — YAML multi-line description 取不到內容
7. **Pattern G** — 修復後 pipe 未轉義導致重新錯位
8. **Pattern H** — 路徑解析基底搞錯
9. **Pattern I** — Per-section header drift
10. **Pattern J** — check_per_section_drift 的 dict 被 int 覆蓋（script logic bug）
11. **Pattern K** — `git status --short` 不顯示 staged deletion
12. **Pattern L** — Python 3.13 `re` 模組語法迴歸導致 script crash
13. **Pattern M** — 上游內容與 workspace HEAD 不一致（雙向：落後/領先皆為腐蝕訊號）
14. **Pattern N** — Merge conflict resolution 方向選錯導致 counts 錯誤
15. **Pattern O** — Branch divergence + `git stash` 的危險組合
16. **Pattern P** — 檔案已被 commit 刪除但磁碟上仍存在（orphan resurrect）
17. **Pattern Q** — `git show origin/main:<file>` 假陰性：origin 無 vs canonical 無 是不同訊號
18. **Pattern R** — Dangling 路徑靜態清單可能已過時（skill 目錄搬家後路徑改變）
19. **Pattern S** — sync-check.py 報告 `EXTRA in workspace: agents/` 不一定是污染
20. **Pattern T** — Merge conflict 同時衝擊 Summary + 多個 per-section header 是複雜度確定信號
21. **Pattern U** — 口徑修復順序不對導致二次修正迴圈

---

## Pattern Q：`git show origin/main:<file>` 假陰性

**觸發**：用 `diff <(git show origin/main:<file>) <file>` 驗證時，`<file>` 若不存在於 HEAD，diff 全部標為「刪除」，看起來像截斷，實際是檔案根本不在 HEAD。

**三種 origin 訊息的判斷徑（2026-05-17 實測）**：

| `git show origin/main:<file>` 輸出 | 意義 | 行動 |
|---|---|---|
| `fatal: path '...' exists on disk, but not in 'origin/main'` | canonical 有，origin/main 沒有（從未上傳或已刪除） | 從 canonical restore，視為正當 sync |
| `fatal: path '...' does not exist in repository path` | 檔案不在 origin/main 且不在 canonical | 檢查磁碟版＋對照 HEAD，確認是否為 workspace 污染 |
| 有內容（lines count） | 檔案在 origin/main 有內容 | 繼續 Pattern M 的行數比對流程 |

**預防**：每次做 `diff <(git show X:<file>) <file>` 前，先單獨確認 `git show X:<file> > /dev/null 2>&1` 來源端存在，再比對行數，最後才 diff 內容。

---

## Pattern A：Dangling rows

**觸發**：刪除 skill 目錄後只 `git rm`，不更新 index row。

**重要**：static pattern list 可能已過時（skill 目錄會搬家）。`darwin-skill` 真實路徑是 `../openclaw-imports/darwin-skill/`，而清單裡的 `../skills/darwin-skill/` 匹配不到。

**動態修復流程**（每次都要跑）：
```python
import os
import re, subprocess

idx_path = os.path.expanduser('~/Documents/Agent/docs/Skill_Index.md')
workspace = os.path.expanduser('~/Documents/Agent')

# 1. 從 index 抽出所有 path cells
with open(idx_path) as f:
    content = f.read()
paths = re.findall(r'\|\s*\[.+\]\(([^)]+SKILL\.md\)\)', content)

# 2. 對每個 path，檢查磁碟上是否存在
dangling = []
for p in paths:
    # p 是相對於 docs/ 的路徑，如 ../openclaw-imports/darwin-skill/SKILL.md
    full = f"{workspace}/{p}"
    if not subprocess.run(['test', '-e', full]).returncode == 0:
        dangling.append(p)

print(f"Dangling: {len(dangling)}")
for d in dangling:
    print(f"  {d}")
```

**靜態清單**（已知的已知，會過時）：
```python
dangling_patterns = [
    '../skills/mattpocock-skills/skills/productivity/caveman/',
    '../skills/mattpocock-skills/skills/productivity/grill-me/',
    '../skills/mattpocock-skills/skills/engineering/grill-with-docs/',
    '../skills/mattpocock-skills/skills/engineering/setup-matt-pocock-skills/',
    '../skills/mattpocock-skills/skills/engineering/to-issues/',
    '../skills/mattpocock-skills/skills/engineering/to-prd/',
    '../skills/mattpocock-skills/skills/engineering/triage/',
    '../skills/mattpocock-skills/skills/productivity/write-a-skill/',
    '../skills/darwin-skill/',      # 已失效！真實路徑在 openclaw-imports/
    '../skills/mattpocock-skills/skills/personal/obsidian-vault/',
    '../skills/mattpocock-skills/skills/misc/git-guardrails-claude-code/',
    '../skills/mattpocock-skills/skills/misc/setup-pre-commit/',
    '../skills/mattpocock-skills/skills/deprecated/design-an-interface/',
    '../skills/mattpocock-skills/skills/engineering/diagnose/',
    '../skills/mattpocock-skills/skills/engineering/improve-codebase-architecture/',
    '../skills/mattpocock-skills/skills/misc/migrate-to-shoehorn/',
    '../skills/mattpocock-skills/skills/deprecated/qa/',
    '../skills/mattpocock-skills/skills/deprecated/request-refactor-plan/',
    '../skills/mattpocock-skills/skills/engineering/tdd/',
    '../skills/mattpocock-skills/skills/engineering/zoom-out/',
    '../skills/mattpocock-skills/skills/personal/edit-article/',
    '../skills/mattpocock-skills/skills/misc/scaffold-exercises/',
    '../learning-assistant/',
    '../neat-freak/',
    '../skills/mattpocock-skills/skills/deprecated/ubiquitous-language/',
]
```

**驗證口徑命令**（Skill_Index.md 格式：pipe-table，Bold 數字）：
```python
import os
import re
c=open(os.path.expanduser('~/Documents/Agent/docs/Skill_Index.md')).read()
rows=[l for l in c.split('\n') if l.startswith('| ') and 'SKILL.md' in l
      and 'Root-level Skills (standalone)' not in l and 'Category | Count |' not in l]
actual=len(rows)
m=re.search(r'- Active Skills:\s*\*{2,3}(\d+)\*{2,3}', c)
header=int(m.group(1)) if m else 0
print(f'Header={header}, Actual={actual}, Match={header==actual}')
```

**預防**：Skill_Index.md 必須在 skill 目錄結構任何變更後（搬家、刪除、新增）立即重新掃描磁碟重建，不能只靠增刪 row。

---

## Pattern B：Purpose cell `\\` 腐蝕

**觸發**：SKILL.md 的 description 含 `|` 但寫入 index 時未轉義。

**修復**：用 Python 逐行置換，不能用 patch（多列有完全相同的 `\\`）。

---

## Pattern C：Summary header drift

**觸發**：增刪 skill 後只改 Summary 數字，忘了更新 row 本身。

**症狀**：`Active Skills: 585 ← 落後（實際 569）`

---

## Pattern D：Category count drift

**觸發**：Skill_Category.md 的 per-category 加總落後於 actual rows。

---

## Pattern E：Rebase 衝突導致腐敗復發

**觸發**：`git pull --rebase` 發生 conflict，resolve 時選了含腐敗內容的 remote 版本。

**修復**：`git rebase --abort`，在乾淨 branch 做修復後再 push。

---

## Pattern F：YAML multi-line description 取不到內容

**觸發**：SKILL.md 的 description 是 YAML multi-line 流水線格式，直接 `split('description:')[1].strip()` 得到空字串。

---

## Pattern G：修復後 pipe 未轉義導致重新錯位

**觸發**：description 含 `|` 寫入時未轉義，`split('|')` 再次錯位成 7 cells 而非 6。

---

## Pattern H：路徑解析基底搞錯

**觸發**：index 中路徑相對於 `docs/`，但技能本體在 Agent 根目錄。

---

## Pattern I：Per-section header drift

**觸發**：每次增刪 skill 時，只更新 Summary 數字，14 個 section header 數字全落後。

---

## Pattern J：check_per_section_drift 的 dict 被 int 覆蓋

**觸發**：dict 被 int 覆蓋，最後一個 section 才爆（`TypeError: 'int' object is not subscriptable`）。

---

## Pattern K：`git status --short` 不顯示 staged deletion

**觸發**：`rm -rf` 自動 staged 了刪除，但 `--short` 格式不明顯，誤判工作樹乾淨。

---

## Pattern L：Python 3.13 `re` 模組語法迴歸導致 script crash

**觸發**：Python 3.13.9 的 `re` 模組對 `.+` 在 character class 後的 subpattern 做嚴格語法檢查，`re.PatternError` crash。

**受影響函式**：`check_dangling()` 中的 `paths = re.findall(r'\|\\s*\[.+\]\(([^)]+SKILL\.md\))', idx_content)`

**修復**：用 `[^\]]+` 取代 `.+`，用 lookahead `(?=\))` 而非吃掉 `)`。

---

## Pattern M：上游內容與 workspace HEAD 不一致

**觸發**：`<file>` 在 HEAD 與 origin/main 行數不同，但 `git status` 乾淨（差異已被 commit）。可能是 workspace 落後 origin（截斷），也可能是 workspace 領先 origin（新增）。

**兩種方向的檢測流程**：
```bash
# Step 1：確認 HEAD 與 origin/main 各自有多少行
wc -l <file>
git show origin/main:<file> | wc -l

# Step 2：確認檔案在雙方都存在（避免 Pattern Q 假陰性）
git show HEAD:<file> > /dev/null 2>&1 && echo "IN HEAD" || echo "NOT IN HEAD"
git show origin/main:<file> > /dev/null 2>&1 && echo "IN origin/main" || echo "NOT IN origin/main"

# Step 3：確定方向
# HEAD 行數 < origin 行數 → workspace 截斷（Pattern M-A）
# HEAD 行數 > origin 行數 → workspace 領先（Pattern M-B）

# Step 4：若為 Pattern M-A（workspace 落後）
git diff origin/main -- <file>
git checkout origin/main -- <file>
wc -l <file>  # 確認還原後與 origin 一致

# Step 5：若為 Pattern M-B（workspace 領先）
# 先確認領先內容是否為使用者意圖（可能是本地實驗 commit）
# 若確認是 upstream 應有的內容 → 考慮 merge/rebase 後 push
# 若確認是本地實驗 → 視情況 revert 或保留
```

**實測案例**：
- Pattern M-A（落後）：llm-wiki/SKILL.md workspace 251 行，origin 419 行（2026-05-15 初發現）
- Pattern M-B（領先）：llm-wiki/SKILL.md HEAD 419 行，origin 407 行（2026-05-17）— workspace 在 vault 路徑更新後領先，diff 顯示 `Pigo_Obsidian` → `PigoVault` 更新

**修復口徑**：Pattern M 指的是「雙方有差距且差距已被 commit」，**不是「落後才叫問題」**。領先時以同樣流程診斷意圖。

---

## Pattern N：Merge conflict resolution 方向選錯導致 counts 錯誤

**觸發**：`git merge origin/main` 產生 conflict，隨便選一邊導致 drift。

**修復**：以 actual row count 為準，不能選 conflict 側。

---

## Pattern O：Branch divergence + `git stash` 的危險組合

**觸發**：`Your branch and 'origin/main' have diverged` 且有 staged-only 檔案時執行 `git stash`。

**修復**：先解決 divergence，再 stash。

---

## Pattern P：檔案已被 commit 刪除但磁碟上仍存在（orphan resurrect）

**觸發**：upstream commit 刪除 `<file>`，但 local branch 落後，磁碟上的檔案與 HEAD IDENTICAL，`git status` 乾淨。

**正確檢測流程**：
```bash
git show HEAD:<file> > /dev/null 2>&1 && echo "IN HEAD" || echo "NOT IN HEAD"
diff <(git show HEAD:<file>) <file> && echo "IDENTICAL — warning!"
git show origin/main:<file> > /dev/null 2>&1 && echo "IN origin/main" || echo "NOT IN origin/main"
```

---

## Pattern R（2026-05-18）：Dangling 路徑可能已過時

**觸發**：腐蝕圖譜記錄的 dangling paths 是在某個時間點驗證過的，但 skill 目錄會搬家、重命名。`darwin-skill` 的真實路徑是 `../openclaw-imports/darwin-skill/`，而腐蝕圖譜清單裡的路徑是 `../skills/darwin-skill/`——因此該 row 未被移除。

**預防**：在套用 dangling removal 前，先 grep index 找出「index 中有但磁碟上無」的 actual paths，再與腐蝕圖譜清單比對。不要假設清單涵蓋所有 dangling。

## Pattern V（2026-07-03 初發現）：Full Rebuild 後仍有 Invalid Path Survivor

**觀察**：2026-06-29 執行了 Skill_Index.md 完整重建，但重建後仍殘留無效路徑 `skills/browser-web-social/aihot/SKILL.md`（`browser-web-social/` 為 scatter dir，非 `aihot/` 的父目錄）。此 row 在重建前即存在，視為 dangling 移除後才等於 actual count。

**腐蝕機制**：重建時的磁碟掃描若只驗證「路徑是否存在於磁碟」，而不驗證「路徑結構是否合理」（如 `browser-web-social/aihot/` 是否為有效巢狀結構），則無效路徑可通過掃描。另一可能是重建 source data 已被污染。

**修復**：獨立驗證每個 section 的 actual count，與 header 比對。

**預防**：重建後除口徑驗證外，須對照磁碟抽查 section boundary 是否正確——例如 Root-level Skills 內的 skill 是否真的都沒有父目錄。

---

## Pattern S（2026-05-18）：sync-check.py 報告 `EXTRA in workspace: agents/` 不一定是污染

當 canonical 的 `agents/` 目錄從未定義，但 origin/main 自己擴充了 `agents/openai.yaml` 時，sync-check.py 會把 workspace copy 裡的 `agents/` 標記為 drift（多了），但這是 upstream 的正常內容，不是 workspace 污染。

**標準確診步驟**：
```bash
ls ~/.hermes/skills/neat-freak/agents/ 2>&1
ls ~/Documents/Agent/skills/neat-freak/agents/ 2>&1
git -C $WORKSPACE ls-files -- "skills/neat-freak/agents/*"
# 若有輸出 → 正當 tracked content，保留
```

---

## Pattern T（2026-05-18）：Merge conflict 複雜度即時信號

**觸發**：`git pull --no-rebase` 產生 Skill_Index.md conflict，且 conflict 波及範圍包含 **Summary count + ≥3 per-section count**——說明雙方都在墊高 counts，隨便選任一側都會遺漏另一側的更新。

**判斷徑**：
```
只有 Summary count conflict → 可嘗試 resolve
Summary count + ≥3 per-section count 同時 conflict → 立即 abort
只有內容行 conflict，header 沒動 → 可嘗試 resolve
```

**修復**：abort，等人工處理。

---

## Pattern U（2026-05-18）：口徑修復順序不對導致二次修正

**觸發**：若先修 Summary header 再 count actual rows，會因為 dangling 未移除而得到錯誤的 correct value。典型案例：Summary 修到 580 後，Learning header 才暴露 actual=21 vs header=20。

**正確順序**：
1. 移除 dangling rows
2. 重新 count actual rows
3. 以 actual 值為準修正 Summary header
4. 修正 per-section headers
5. **重跑 skill-index-check.py 確認全面乾淨**

口徑 drift 是連鎖反應，修完一項**必須重跑 script** 確認，不能只修一項就結束。

---

## 驗證腳本

```bash
python3 ~/.hermes/skills/neat-freak/scripts/skill-index-check.py
```

檢查五項：Summary drift、Per-section drift、Dangling references、Purpose cell `\\` 腐蝕、Skill_Category.md 對齊。

---

## 修復順序

1. 移除 dangling rows（Pattern A + Pattern R 動態驗證）
2. **重新 count actual rows**（用 `re.findall` 或 `grep -c SKILL.md` 確認新基線）
3. 以 actual 值為準修正 Summary header drift（Pattern C）
4. 修正 per-section header drift（Pattern I）
5. 修 Purpose cell `\\`（Pattern B）
6. 最後修 Skill_Category.md 對齊（Pattern D）
7. **重跑 skill-index-check.py 確認全面乾淨**——口徑 drift 是連鎖反應，修完一項必須重跑 script 確認

**不要**在修復腐敗的同一個 commit 裡做 rebase。
