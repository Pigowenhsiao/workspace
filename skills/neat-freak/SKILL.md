---
name: neat-freak
description: >
  會話結束後的知識庫終極大整理——用龜毛級的標準審視專案檔案（CLAUDE.md、README.md、docs/）
  和 Agent 記憶，確保專案知識不會隨著時間腐爛。當使用者說：
  "sync up"、"tidy up docs"、"update memory"、"clean up docs"、"整理文件"、"整理一下"、
  "更新記憶"、"同步一下"、"收尾"、"這階段做完了"、"新人能直接上手"、
  或任何暗示開發里程碑需要知識同步的句子，就觸發這個 Skill。
  使用者反映檔案過期、記憶衝突、或需要交接給隊友或接手 Agent 時也觸發。
  單獨說「整理」或「tidy」但有開發上下文也算——不要漏觸發。
  跨平台通用：Claude Code、OpenAI Codex、OpenCode、OpenClaw 皆可使用。
---

# 龜毛工程師 — 知識庫整頓 Skill

## Description

會話結束後對專案文件與 Agent 記憶進行全面審查與同步，確保專案知識不會過期或遺漏。
適用於：使用者在開發現場說「同步一下」、「整理文件」、「更新記憶」、「收尾」等階段性整理指令時；
或文件出現過期、記憶衝突、需交接給隊友或接手 Agent 的情境。
核心價值：讓知識體系每一層（記憶、CLAUDE.md/AGENTS.md、docs/）都跟得上程式碼變化。

> **跨平台 Agent Skill** — Claude Code · OpenAI Codex · OpenCode · OpenClaw 通用。
> 遵循開放 Agent Skill 規範。

## Cron 調用方式

**正確路徑：`neat-freak`**（bare name，無前綴）

> ⚠️ 2026-07-17 教訓：cron 錯誤配置 `skills=[hermes/neat-freak]`（錯誤前綴）導致 skill 載入失敗，出現「Skill(s) not found and skipped」警告後直接跳過。`~/.hermes/skills/` 下沒有 `hermes/` 子目錄。正確值是 `skills=[neat-freak]`。

**路徑衝突已解除（2026-10-26 修復）**：過去 bare name `neat-freak` 同時匹配 `~/.hermes/skills/neat-freak/`（canonical）與 `~/.hermes/skills/productivity/neat-freak/`（過期副本），`skill_view(name='neat-freak')` 直接回 `Ambiguous skill name`，導致 cron 每次都報「Skill(s) not found and skipped」。**過期副本已移除**（內容與 canonical byte-identical，備份於 `/home/x/.hermes/cache/scratch/removed_prod_neatfreek_20261026_2350`），bare name 現在正確解析到 canonical。

驗證方式：
```bash
python3 -c "
import sys; sys.path.insert(0,'/home/x/.local/share/uv/tools/hermes-agent/lib/python3.12/site-packages')
from tools.skills_tool import skill_view
print(skill_view(name='neat-freak')[:120])
"
```

⚠️ 但 `~/.hermes/skills/productivity/` 下還有 15 個與 top-level 同名的重複 skill（aihot, brave-search, weather, vault-knowledge, obsidian-cli 等），同樣會造成該 15 個名稱的 ambiguity。**若哪個名稱報 ambiguous，重複來源就是 `productivity/<name>`。**

## 腐蝕圖譜（Corruption Map）

維護過程中發現的陷阱，按發現日期編號。**每次執行 Skill 都必須重讀這份圖譜**，不能只靠記憶。

### Pattern A–G：Skill_Index.md 腐敗（2026-05-12 初發現）

1. **YAML multi-line description（`description: |`）split 取不到內容**
2. **修復後 pipe 未轉義導致 cell 再次錯位**（7 cells 而非 6）
3. **路徑基底搞錯**（index 路徑相對於 `docs/`，但技能本體在 Agent 根目錄）
4. **Per-section header drift**（每增刪 skill 只更新 Summary 數字，14 個 section header 全落後）
5. **check_per_section_drift 的 dict 被 int 覆蓋**（script logic bug，每次最後一個 section 才爆）
6. **`git status --short` 不顯示 staged deletion**，workspace pollution 移除後誤判工作樹為乾淨
7. **Python 3.13 `re` 模組語法迴歸**：`\\.+` subpattern 在 character class 後導致 `re.PatternError`，crash 而非只給錯誤結果（2026-05-13）

### Pattern N（2026-05-18）：Dangling 路徑可能已過時

26. **靜態 dangling 清單與 index 實際路徑可能不一致**。腐蝕圖譜記錄的 dangling paths 是在某個時間點驗證過的，但 skill 目錄會搬家、重命名。`darwin-skill` 的真實路徑是 `../openclaw-imports/darwin-skill/`，而腐蝕圖譜清單裡的路徑是 `../skills/darwin-skill/`——因此該 row 未被移除。

    **預防**：在套用 dangling removal 前，先 grep index 找出「index 中有但磁碟上無」的 actual paths，再與腐蝕圖譜清單比對。不要假設清單涵蓋所有 dangling。

27. **口徑修復順序不對會導致二次修正**。若先修 Summary header 再 count actual rows，會因為 dangling 未移除而得到錯誤的 correct value，導致要重新修正。**正確順序**：移除 dangling rows → 重新 count actual rows → 以 actual 值為準修正 Summary → 修正 per-section headers。口徑 drift 是連鎖反應，修完一項必須重跑 script 確認全面乾淨。典型案例：Summary 修到 580 後，Learning header 才暴露 actual=21 vs header=20 的問題。

### Pattern H：雙軌結構混淆（2026-05-14）

8. **Skill 的雙軌結構混淆**：當 `neat-freak` 同時存在於 `~/.hermes/skills/neat-freak/`（canonical）和 `~/Documents/Agent/skills/neat-freak/`（workspace sync copy）時，`git diff` 顯示 `create mode` 的檔案可能是**正常 sync restore**，不是 workspace pollution。誤判會導致錯誤地刪除正當的 restore commit。

   **完整判斷徑（已實戰驗證）**：
   ```bash
   # Step 1：確認 canonical 和 workspace sync copy 的完整目錄結構
   ls ~/.hermes/skills/neat-freak/
   ls ~/Documents/Agent/skills/neat-freak/

   # Step 2：每個 subdirectory 獨立比較
   # references/ — 逐檔比對
   # scripts/ — 逐檔比對（注意：script 不在 linked_files 清單裡，需主動檢查）
   # agents/ — workspace 有但 canonical 無 → 確認 origin 再決定是否刪除

   # Step 3：應用修復
   # 少於 canonical 的目錄 → 從 canonical 拷回
   # 多於 canonical 的目錄 → 逐檔問：是 legitimate workspace addition 還是 script 誤寫入？
   ```

   **實測案例（2026-05-14）**：
   - `skills/neat-freak/scripts/` 在 workspace 為空 → 從 canonical 還原 `skill-index-check.py`
   - `skills/neat-freak/agents/openai.yaml` 在 workspace 有但 canonical 無 → 確認 origin/main 有後接受，不砍
   - **不要**因為 `git diff --stat` 看到 `create mode 100644` 就說「這是污染」——這可能是正常 restore

9. **`sync-check.py` 只測目錄存在，不測內容一致**（2026-05-17）— `sync-check.py` 只比對「workspace 多了哪些檔案 / 少了哪些檔案」，但**不比較既有檔案的內容差異**。若 canonical 的 script 已被修改（ 如增加 Pattern L 修復），workspace copy 的同名檔案會被當成「存在」而通過檢查，但內容已落後。**每次 restore 都必須人工 `diff` 確認**：
   ```bash
   diff ~/.hermes/skills/neat-freak/scripts/<file> ~/Documents/Agent/skills/neat-freak/scripts/<file>
   ```
   若有差異，以 canonical 為準覆蓋 workspace copy。

### Pattern I：Git 操作陷阱

10. **Branch divergence + `git stash` 組合陷阱**（2026-05-14）— 當 `Your branch and 'origin/main' have diverged` 且有 staged-only 檔案時，`git stash` 會把 staged commit 節點和 stash 棧都搞亂；`git stash pop` 如果有 conflict 會把 WIP 狀態留在分支上。症狀：`git status --short` 乾淨但 `git stash list` 有東西。正确做法：先解決 divergence 再做 stash。

11. **`git ls-files --error-unmatch` 的虛假信心陷阱**（2026-05-14）
12. **`git checkout --theirs` 會同時抹掉 conflict markers 和 stashed 內容**（2026-05-14）
13. **`git add -A` 在大型 workspace 的沉默 staging 陷阱**（2026-05-14）— 在包含數百個 skills 的 workspace（如 `~/Documents/Agent/`）中，`git add -A` 會把所有 unstaged 變更包含進 staging area。若直接以為工作樹乾淨就跳過 commit 會丟失刪除。正確：先 `git status`（非 `--short`）確認 staging 狀態。
14. **`git ls-tree` vs `ls` 路徑不一致陷阱**（2026-05-15）— `git ls-tree origin/main:docs/article-notes/` 輸出空白，但 `ls docs/article-notes/` 有內容且 git 有追蹤。诊断时使用 `git ls-files -- "article-notes/*"` 而非 `git ls-tree`。

### Pattern J：上游截斷覆寫（2026-05-15）

15. **上游內容被 workspace 截斷覆寫** — upstream 版本被截斷後 commit，`git status` 乾淨，需用 `wc -l` 行數比對才能發現。

    **典型案例**：llm-wiki/SKILL.md workspace 版本 251 行，origin 版本 419 行。Workspace 版本缺少 `version: 2.4.1`、完整 vault 路徑、和大部分內容主體。

    **修復**：用 `git checkout origin/main -- <file>` 還原，但**要先 `git diff origin/main -- <file>` 確認差距內容**。

    **驗證**：`wc -l` 比對行數 + `diff <(git show origin/main:<file>) <file>` 確認完全一致。

    **特別注意：Branch divergence 時的 restore 原則**
    - restore 後若 branch 仍與 origin divergence，**不要在解決 divergence 前單獨 commit** 這個 restore——會把 origin 的 canonical 內容「重新引入」到落後的分支
    - **正確順序**：先 merge/rebase 解決 divergence，再一併 commit restore

16. **`diff <(git show X:<file>) <file>` 假性信心陷阱**（2026-05-16）— 當 `<file>` 不存在於 HEAD 時，process substitution 輸出空，diff 全部標為「刪除」，看起來像截斷，實際是檔案根本不在 HEAD。預防：每次 diff 前先 `git show HEAD:<file> > /dev/null` 確認來源端存在。

### Pattern K：Merge / Conflict 陷阱

17. **Merge conflict resolution 方向選錯導致 counts 錯誤**（2026-05-15）— `git merge origin/main` 產生 conflict 後，雙方 Summary counts 都落後於 actual rows，隨便選一邊都導致 drift。修復：先用 script count actual rows，再以實際值為準重算 header，不能選任一 conflict 側。

18. **Skill_Index.md counts drift 會因 branch divergence 累積加速**（2026-05-16）— workspace Summary counts 568，origin 586，落差 18。**在 divergence 未解決前，skill-index-check.py 的口徑只能對 workspace 內部，不能對 origin 比對**。修復順序：先 merge/rebase，再跑 script，最後重算 header。

### Pattern L：Workspace 結構陷阱

19. **`article-notes/` 孤兒目錄陷阱**（2026-05-15）— workspace 根目錄下發現 `article-notes/` 目錄，但 git 中記錄為 `docs/article-notes/`。這是目錄結構與 git 路徑不一致的孤立案例。**不屬於 workspace pollution**（git 有追蹤），但位置混亂會誤導閱讀者。需人工裁決是否正規化。

### Pattern M：Branch Divergence 處置流程缺失（2026-05-17）

23. **Branch divergence 缺乏處置流程** — 腐蝕圖譜記錄了「不要在 divergence 未解決前 stash」，但**沒有說怎麼解決**。這導致執行者只能停住等人工，完全失去了 neat-freak 的自主性。

    **Divergence 分類與處置徑**：
    ```
    git status
    │
    ├─ "Your branch and 'origin/main' have diverged, and have X and Y different commits"
    │   │
    │   ├─ X > Y 且 commit log 顯示架構調整（skill 搬家、跨專案重組）
    │   │   → 傾向 merge --no-ff（保留分支結構）
    │   │
    │   ├─ X > Y 但 commit log 顯示零散修補
    │   │   → 傾向 rebase（拉平歷史）
    │   │
    │   ├─ Y >> X（落後很多）且 origin 有近期大範圍變更
    │   │   → 先 fetch，再 rebase 或 merge（取決於是否在意本地 commits）
    │   │
    │   └─ X 和 Y 都相對少，log 顯示各自獨立事實變更
    │       → merge（或 rebase -i 拆分本地 commits）
    │
    └─ "Your branch is ahead of 'origin/main' by X commit(s)"
        → push 或 rebase -i  squash，取決於是否要保留顆粒度
    ```

    **修復完成後才能繼續 Step 3 的任何 git 操作**（restore、commit 等）。實戰複雜度評估、決策樹、和 abort 後正確重新拉齊流程，詳見 [references/divergence-resolution-workflow.md](references/divergence-resolution-workflow.md)。
    
    **特別注意**：解決 divergence 後，skill-index-check.py 的口徑比對**只對 workspace 內部**，不能對 origin 比對（因為 origin 的 canonical 內容可能已被 upstream 階段性重構）。真正需要拉齊的是 workspace 與 origin 的差距，必須在 divergence 解決後再以 `git pull` 拉齊，並重跑 skill-index-check.py 驗證口徑。

20. **Canonical skill 的 `scripts/__pycache__` 自我污染**（2026-05-15）— canonical `~/.hermes/skills/neat-freak/scripts/` 必須保持乾淨。workspace sync copy 裡的 `__pycache__/` 是執行驗證時產生的 side effect，**不應該 commit 回 upstream**。

21. **`agents/openai.yaml` 存在於 origin/main 但不在 canonical**（2026-05-16）— workspace sync copy 的 `agents/` 目錄裡有 `openai.yaml`（canonical 從未定義 agents/），但 `git show origin/main:skills/neat-freak/agents/openai.yaml` 有內容，這是 origin/main 自己擴充的，不是 workspace pollution。**不能直接刪除**，必須先確認 origin 有無。

22. **OPENSPEC block 陳屍陷阱**（2026-05-16）— `Readme.md` 包含 `<!-- OPENSPEC:START -->` block，引用 `@/openspec/AGENTS.md`，但 `openspec/` 目錄**從未存在於 workspace**（不在 git history、不在磁碟）。跡象：grep "openspec" 有結果但 `ls openspec/` 回 `No such file or directory`。修復：直接刪除該 block。預防：任何 `<!-- XXX:START -->` managed block 都應在刪除前確認 target 目錄是否存在。

### Pattern S：反向干擾——sync-check.py 的「多餘檔案」可能是正當的 tracked content（2026-05-18）

24. **`sync-check.py` 報告 `EXTRA in workspace: agents/` 不一定是污染——可能是 origin/main 的正當擴充**。當 canonical 的 `agents/` 目錄從未定義，但 origin/main 自己擴充了 `agents/openai.yaml` 時，sync-check.py 會把 workspace copy 裡的 `agents/` 標記為 drift（多了），但這是 upstream 的正常內容，不是 workspace 污染。Pattern H 只說「workspace 有但 canonical 無 → 確認 origin」，**但沒有說怎麼確認**。

    **標準確診步驟**：
    ```bash
    # 先確認 canonical 和 workspace 的 agents/ 內容
    ls ~/.hermes/skills/neat-freak/agents/ 2>&1
    ls ~/Documents/Agent/skills/neat-freak/agents/ 2>&1

    # 確認 workspace 的 extra 是否 origin/main 有追蹤
    git -C $WORKSPACE ls-files -- "skills/neat-freak/agents/*"
    # 若有輸出 → 正當 tracked content，保留
    # 若無輸出 → 可能是 script 誤寫入，需進一步確認
    ```
    當 `git ls-files` 確認有輸出，視為正當 sync copy addition，**不要刪除**。

### Pattern Z（2026-05-22 初發現）：三種常見 EXTRA 組合幾乎全是正當 sync content

**觸發**：`sync-check.py` 報告 workspace 比 canonical 多三項：
- `EXTRA in workspace: agents/`
- `EXTRA in workspace: references/Readme.md`
- `EXTRA in workspace: scripts/Readme.md`

**2026-05-20 實戰確診結果**：
- `agents/` — `git ls-files` 確認 origin/main 有追蹤 `openai.yaml` 和 `Readme.md` → **正當，保留**
- `references/Readme.md` — `git ls-files` 確認 origin/main 有追蹤 → **正當，保留**
- `scripts/Readme.md` — `git ls-files` 確認 origin/main 有追蹤 → **正當，保留**

**原則**：當 workspace copy 的 EXTRA 剛好是 `agents/`、`references/Readme.md`、`scripts/Readme.md` 這三者組合時，幾乎可以確定是 origin/main 在 canonical 未定義的時間點之後擴充的內容，**不要刪除**。用 `git ls-files` 二次確認即可。

**真正需要刪除的 workspace EXTRA** 是那種 `git ls-files` 查不到、磁碟上卻存在的目錄/檔案——這才是 script 誤寫入或殘留的污染。

## Pattern T：Merge conflict 複雜度即時信號——多層同時衝突（2026-05-18）

25. **Merge 時 Summary header + 多個 per-section header 同時 conflict 是複雜度的確定信號**...

---

### Pattern V（2026-05-19 初發現，2026-05-20 已修復）：script regex 導致 uniform +14 drift

**2026-05-19 觀察**：每個 section header 的數字比實際多 1，14 sections × 1 = Summary 多 14（header 說 595，實際 581）。

**2026-05-20 確認的錯誤機制**：`check_per_section_drift()` 中的 regex `.+` greedy，在短路徑時導致整個 match 失敗。

**2026-05-20 已修復**：`skill-index-check.py` 當前版本已使用非 greedy regex：
- `re.findall(r'\|\s*\[.+?\]\(.+?SKILL\.md\)', idx_content, re.IGNORECASE)`（header drift）
- `re.match(r'\|\s*\[.+?\]\(.+?SKILL\.md\)', line, re.IGNORECASE)`（per-section）

**驗證方法**：
```python
# 獨立計數（不走 script 的 regex）
import re
content = open(os.path.expanduser('~/Documents/Agent/docs/Skill_Index.md')).read()
actual = re.findall(r'\`\[([^\]]+SKILL\.md)\]\`', content, re.IGNORECASE)
print(f'Actual rows: {len(actual)}')
# 比對 script 口徑：若兩者差 14×N 且所有 section 均勻偏離 → script bug（已修復）
```

**預防**：任何修改 regex 後必須用獨立計數驗證，不能只依賴 script 自己的輸出。

**2026-05-21 session 確認**：script 當前口徑 = 578 actual skills。Skill_Category.md 口徑 = 581（14 categories 加總）。兩者不同是預期的，因為計算邏輯不同，不算 drift 腐敗。

### Pattern AA（2026-05-21 初發現）：Script format vs actual file format 不一致（backtick vs pipe-bracket）

**觸發**：`skill-index-check.py` 的三個函式使用 `\|\s*\[.+?\]\(.+?SKILL\.md\)`（pipe + bracket link 格式），但 workspace 的 `docs/Skill_Index.md` 實際使用 `` `[skills/.../SKILL.md]` ``（backtick-enclosed 格式）。結果：script 回報 `Actual rows: 0` 却同時 `✓ ALL CLEAN`，給予虛假的乾淨信號。

**修復（2026-05-21）**：
- `check_header_drift()`：`\|\s*\[.+?\]\(.+?SKILL\.md\)` → `` r'\`\[([^\]]+SKILL\.md)\]\`' ``
- `check_per_section_drift()`：row matching regex 同時修復；`^###` → `^##`（檔案用 H2 而非 H3）
- `check_dangling()`：`\|\s*...` → `` r'\`\[([^\]]+SKILL\.md)\]\`' ``
- `check_category_counts()`：`^###` → `^##`

**驗證**：已在 `scripts/verify-patch.py` 確認，修復後口徑 = 578 actual rows，header = 578，drift = 0。

**⚠️ Pattern AA 修復可能已部分迴歸（2026-07-24 觀察）**：
- Header-level 口徑（460 vs 469）仍準確捕獲 +9 drift
- 但 per-section drift 仍有 4 個 section 報錯（script 顯示 `header=N, actual=N+1` 的差異）
- 研判：2026-07-23 rebuild 後，Skill_Index.md 變為 pipe-table format（`| name | path | description |`），但 script 的 per-section regex 仍用 backtick 格式比對，導致在 pipe format sections 無法正確 count
- **獨立驗證法**（不走 script）：`grep -c 'SKILL\.md' docs/Skill_Index.md` 比對各 section 內實際行數
- **根因修復**：需要將 `check_per_section_drift()` 的 row regex 從 backtick 改回 pipe format（`| name | path |`），並對 header line（如 `| adaptyv | skills/...`）單獨處理

### Pattern AB（2026-05-22 初發現）：三個 script bug 導致虛假 DRIFT

**發現經過**：cron job 執行 neat-freak 時，sync-check.py 報告 DRIFT（workspace 少了 verify-patch.py，多了 agents/ 等三項），而 skill-index-check.py 報告「578 dangling」（全部 Skills 都被誤判為 dangling）和「39 category mismatches」（全部 mismatch）。

**三個 root cause**（詳見 [references/skill-index-script-bugs-2026-05-22.md](references/skill-index-script-bugs-2026-05-22.md)）：

1. **`check_dangling()` 路徑拼接錯誤（Bug 1）**
   - 錯誤：`os.path.join(docs_base, sp)` 其中 `docs_base = docs/`
   - 結果：所有路徑變成 `docs/skills/...`，全部 578 筆誤判為 dangling
   - 修復：直接以 `AGENT_ROOT` 為基底，不多拼接 `docs/`

2. **`check_header_drift()` regex 與檔案格式不符（Bug 2）**
   - 錯誤：regex 找 `Active Skills:\s*(\d+)`，但檔案格式是 `Auto-generated from disk scan:\s*(\d+)`
   - 結果：header 永遠是 0，drift 顯示 -578
   - 修復：改為正確的 regex

3. **`check_category_counts()` 比較兩套不同命名系統（Bug 3）**
   - 錯誤：Skill_Index.md 用目錄名（`agent-workflows`），Skill_Category.md 用功能性分類名（`Agent, Workflow & Skill Operations`），名稱完全不同
   - 結果：39 項全部 mismatch（false alarm）
   - 修復：移除逐項比對，改為只報告 total sum（578 vs 581）


**附帶發現**：verify-patch.py 也用了 `Active Skills:` regex，導致自我驗證失敗——script 有 bug，驗證它的 script 也有相同 bug，兩個假的湊在一起看起來正常。

**預防**：
- 修改 `skill-index-check.py` 的 regex 後，必須跑 `verify-patch.py` 確認口徑正確
- 任何格式變更（Skill_Index.md header 行、row 格式）都必須同步檢查三個 regex
- 發現 drift 時，先用獨立 Python 重新 count，不依賴 script 輸出（Pattern W 原則）

    **判斷徑**：
    ```
    git pull --no-rebase
    → Skill_Index.md 產生 conflict
    → 檢查 conflict 區塊：
       ├─ 只有 Summary count conflict（其餘 section 內容未動）→ 可嘗試 resolve
       ├─ Summary count + ≥3 per-section count 同時 conflict → 立即 abort
       └─ 只有內容行 conflict，header 沒動 → 可嘗試 resolve
    ```

    **為什麼這個組合是麻煩的**：Summary count 和 per-section count 是獨立的數字，雙方各自更新了不同的數字，resolve 時若只選一側，會同時留下另一側的錯誤 count。手工校準又要重新 count 所有 actual rows，性價比極低。Abort 等人工是正確選擇。

### Pattern II（2026-06-05 初發現）：Readme.md UTF-8 mojibake corruption——double-encoding 導致亂碼

**觀察**：`Agent/Readme.md` 第 93-111 行（Communication / 執行策略 / 執行環境 三區段）全部變成亂碼：
```
Line 94: èˆ‡ä½¿ç"¨è€æºå‹æ™æ™æ´¿ä½¿ç"¨ç¹é"ä¸æ"æè³ã€‚
Line 101: ## åŸ·è¡Œç­–ç•¥
```
其餘內容正常，只有這 18 行損壞。

**腐蝕機制**：UTF-8 編碼的中文文字被錯誤地以 Latin-1 解讀後再次編碼為 UTF-8，產生 mojibake。`file` 命令仍報告 `UTF-8 text`，BOM 存在所以看不出來。

**為什麼舊檢查找不到**：
- `grep -E "今天|昨天|最近"` 只測相對時間殘留，對 mojibake 完全無效
- `file` 命令報告正確編碼（因為確實是有效的 UTF-8，只是內容是雙重編碼的結果）
- 只有**視覺檢查**或**與乾淨參照比對**才能發現

**檢測方法**：
```python
# Step 1：Python bytecode 直接檢查（唯一可靠方法）
data = open('Readme.md', 'rb').read()
lines = data.split(b'\n')
# 壞掉的行顯示為 \xe8\x88\x85... 這類位元組序列（合法 UTF-8 但為 double-encoded）
# 乾淨的行顯示為正確中文（如 b'\xe8\x88\x87\xe4\xbd\xbf...' = "與使用"）

# Step 2：git show HEAD:<file> | cat -v 檢查 git 歷史是否也腐敗
# Step 3：若 git 版本也已損壞，用視覺推断 + 語意猜測重建
```

**為什麼 `cat -v` 和 `file` 不可靠**：
- `cat -v` 的輸出被**終端 encoding 設置**影響——在某些終端設定下，合法 UTF-8 也會被錯誤渲染成 mojibake 外觀，給假信號
- `file` 命令報告「UTF-8 text」是對的——double-encoded 的位元組序列在技術上確實是有效的 UTF-8，file 只測編碼類型不測內容語意
- **正確流程**：用 Python 讀 raw bytes，直接看指定行的位元組序列是否為預期的 UTF-8 中文字元

**修復方法**：
1. 確認破壞範圍（哪些行是乱碼）
2. 用 `git show HEAD:<file>` 取得 origin 版本比對
3. 若 git 版本也已損壞，用視覺推断 + 語意猜測重建
4. 以正確內容 patch 覆蓋損壞行

**預防**：
- 任何來自非 UTF-8 環境（Windows、舊版 Codex、其他 Agent）的 text 寫入，都應立即檢視是否正常顯示
- 跨平台 repo（曾有 Windows 寫入歷史）要特別注意

## Pattern U：「Ahead Only」 divergence 的慣性停滯陷阱（2026-05-18）

28. **Branch 只 ahead 不 behind 時，直覺是「遲早 push 就好」，導致慣性停滯**。症狀：workspace 落後 origin/main 0 個 commit，領先 2+ 個 commit，長期不 push。危險：累積的 housekeeping commit（Skill_Index cleanup、STATUS 追加）與 upstream 其他變更日益脫節，未來 merge 痛苦增加。

    **Pattern M 的「ahead → push 或 rebase -i squash」只給了方向，沒給觸發時機**。實戰經驗：
    - 若 ahead commits 主要是 **Skill_Index 口徑修正、dangling cleanup** 等已知生命週期很短的操作 → **優先 push**，這類 commit 拖越久越容易與 upstream 的 Skill_Index 重構產生衝突
    - 若 ahead commits 摻雜了實驗性變更（未測試的草稿）→ 先在本地 squash 或 rebase -i 拆分乾淨再 push
    - 若不確定 → 先 push（相對安全，因為沒有破壞性conflict風險）

    **驗證口徑**：每次 neat-freak 跑完，若處於「ahead by N」狀態，**立即評估這 N 個 commit 的性質**，不要只是「記錄下來等下次」。口徑修復類 commit 應在同次 session 立即 push。

    **特別記錄**：`git log --oneline origin/main..HEAD` 可快速窺見 ahead commits 的性質。

## Pattern X（2026-05-20）：Stash 遮蔽 branch divergence 真相

**觸發**：`git stash list` 有內容時，`git status` 和 `git diff` 的輸出都基於 stash 層而非真實分支狀態。症狀：branch 看似 clean（ahead of origin/main by 1），但 `git stash list` 有 WIP stash；更危險的是 stash pop 可能帶來 conflict，把 WIP 狀態留在分支上。

**實戰案例（2026-05-20）**：
- `git stash list` → `stash@{0}: WIP on main: c9337eb2`
- `git status` → `ahead of 'origin/main' by 1 commit`（掩蓋了 stash 的存在）
- 分析到一半 stash pop：衝突把 3 個額外 commits（efccf9bd, f071dc0a）帶入分支
- 這 3 個 commits 把 Skill_Index.md 的 counts 從 581（真實）改為 595（加了 script bug 的 +14）

**防範原則**：
1. **任何分析工作開始前，先查 `git stash list`**——stash 不出現在任何 `git status` 輸出裡，是隱藏狀態
2. 若 stash 有內容，先 `git stash pop` 或 `git stash drop` 再繼續
3. Stash pop 時的 conflict 會把 WIP commit 節點留在分支上，導致 `git log --oneline origin/main..HEAD` 多出非預期的 commits

## Pattern Z（2026-05-22 初發現）：git index 與 HEAD 不同步導致虛假 modified

**觸發**：`git status` 顯示 `modified: skills/neat-freak/scripts/skill-index-check.py`，但 `diff ~/.hermes/skills/neat-freak/scripts/skill-index-check.py ~/Documents/Agent/skills/neat-freak/scripts/skill-index-check.py` 輸出空白（兩檔案內容完全相同）。

**根本原因**：git index（staging area）與 HEAD commit 的 metadata 不同步，導致 git 認為一個內容未變的檔案是 modified。通常是因為：
- 之前有 `git checkout` 或 `git restore` 中斷
- 裸檔案被 copy 覆蓋但 timestamp 改變
- `.git/index` 損壞

**正確診斷徑**：
```bash
# 步驟 1：diff 內容是否真的相同
diff ~/.hermes/skills/neat-freak/scripts/<file> ~/Documents/Agent/skills/neat-freak/scripts/<file>

# 步驟 2：若 diff 空白但 git status 仍顯示 modified → index 不同步
# 用以下任一方式修復
git -C ~/Documents/Agent update-index --refresh
# 或
git -C ~/Documents/Agent checkout HEAD -- skills/neat-freak/scripts/<file>
# 或（破壞性，會丟失 staged 內容）
git -C ~/Documents/Agent reset HEAD -- skills/neat-freak/scripts/<file>
```

**為什麼不要跳過診斷直接 commit**：
若直接 `git add + commit` 一個「內容與 HEAD 相同但 index 不同步」的檔案，會產生一個幾乎為空的 commit（只改變檔案 mode/timestamp），汙染歷史。Pattern G 提到的 `git add -A` 也可能同時 staging 大量預期外的刪除。

**Pattern Y（2026-05-20）：Branch divergence 時 `git diff origin/main -- file` 的誤導性輸出

**觸發**：當 workspace 和 origin/main 都有各自的口徑修正 commit（各自把 counts 改為不同錯誤值）時，用 `git diff origin/main -- docs/Skill_Index.md` 會顯示「old: 610, new: 595」——但 595 反而是正確的（真實 581），610 是包含大量 dangling 的錯誤巊值。

**為什麼會誤導**：
- origin/main 的 Skill_Index.md 有 610 個 rows（包含已搬家 skill 的 dangling entries）
- workspace 修正後的 Skill_Index.md 有 595 個 rows（-14 script bug + -X dangling removal）
- diff 顯示 595 比 610 少，看起來像「刪除」，實際上是**口徑修正**

**判斷原則**：
```
口徑對不對 → 用 script（skill-index-check.py）+ 獨立 list filter 驗證
不要用 `git diff origin/main -- file` 的行數增減來判斷是否「正確」
git diff 只告訴你「兩個版本差多少」，不告訴你「哪個版本更接近真實」
```

**實戰流程**：
1. Branch divergence 且雙方都有 Skill_Index.md 修改 → 進入 Pattern M 的處置流程
2. 解決 divergence（merge/rebase）後，用 script count actual rows
3. 以 script 的 actual 值為準，**忽略** diff 顯示的增減數字

## Pattern AA（2026-05-20）：474 dangling rows 的真實性質——下游重構遺毒，非本次workspace問題

**觀察**：skill-index-check.py 報告 474 dangling rows，幾乎覆蓋所有 `gsd-*`、`ce-*`、`superpowers/*`、`openclaw-imports/*` 等整類 skill。

**根因**：這不是 workspace 的事實錯誤，而是 **upstream（origin/main）的 Skill_Index.md 落後於磁碟上已刪除的 skill 目錄**。Upstream 做了大規模 skill 搬家/刪除後，index 從未同步清理，累積了 474 個 dangling entries。

**為什麼 script 口徑（581）是對的**：獨立 Python count `re.findall(r'\|\s*\[.+?\]\(.+?SKILL\.md\)', ...)` 得出 581，與修復後的 header 581 完全吻合。474 個 dangling 是「index 引用了但磁碟上沒有」的 SKILL.md，並非事實 skill rows。

**與 upstream 的關係**：
```
origin/main Skill_Index.md: ~709 行（包含 474 dangling + 581 actual = ~1055 理論總和，但有截斷/重疊）
HEAD Skill_Index.md: 581 actual rows（已經過 upstream + 本次口徑修正，dangling 已移除到 0）
```
HEAD 的口徑比 origin/main 的 raw 行數更接近真實——因為 HEAD 已經過多次 dangling cleanup，origin/main 的 raw 行數摻雜了 upstream 的腐敗。

**處置結論**：
- **不要在本次 session 試圖清除 474 個 dangling**——Pattern N 警告靜態清單不可靠，每個路徑都需逐一核實磁碟
- 這是 upstream 的鍋，應在 upstream 解決，透過 `git pull --no-rebase` 或 merge 把 workspace 的乾淨口徑同步回 upstream
- **下次 upstream乾淨做完重構之後**，再在 workspace 跑一次 dangling removal，才能確保不再產生新的 dangling

**預防**（給 upstream 的建議，非本次 workspace）：
每次刪除 skill 目錄後，立即更新 Skill_Index.md 移除對應 row，不要留到下次同步才處理。

你是**知識庫編輯**，不是打字員。打字員只會一直往後面追加，編輯會審視全局、
合併重複、更新過期、砍掉廢棄。你的工作是讓整個專案的知識體系始終保持在
**整潔、準確、對新人友好**的狀態——像個龜毛工程師一樣。

## 為什麼這件事重要

在 AI 協作開發中，程式碼可以隨時重寫，但**文件和記憶是跨會話、跨 Agent 的唯一橋梁**。
如果記憶裡有過期資訊，下一個 Agent（無論它是 Claude、Codex 還是別的）會基於錯誤前提做決策。
如果 docs/ 混亂或缺漏，接手的人（尤其是下游專案的同事）會浪費大量時間搞懂這套系統怎麼用。

這個 Skill 的價值就在於：**讓知識體系的每一層都跟得上程式碼的變化。**

## 核心概念：三類知識，三種受眾

**必須先理解這件事，否則你只改 CLAUDE.md 就結束，把下游同事和其他 Agent 晾在那邊。**

| 位置 | 受眾 | 職責 | 不同步的代價 |
|------|------|------|-------------|
| **Agent 記憶系統**（若有的話） | Agent 自己跨會話復用 | 個人偏好、不明顯的專案事实、跨專案 reference | 下次會話 Agent 忘記歷史決策 |
| 專案根 `CLAUDE.md` / `AGENTS.md` | 這個專案裡的 AI（下次會話的自己） | 專案約定、架構、紅線、環境變數、路由清單 | 下次 AI 在這個專案裡走歪路 |
| 專案 `docs/` + `README.md` | **其他人**（人類同事、下游開發者、未來接手的 AI） | 接入指南、架構圖、維運手冊、交接說明、API 參考 | **其他人或系統無法正確接入或維運** |

這三層**受眾不同，職責不重疊**。CLAUDE.md 裡寫「新增了 device flow 五個路由」≠
docs/integration-guide.md 裡「下游怎麼接這套 flow」——前者是提醒自己，後者是教別人。
**兩份都要寫。**

> **Agent 記憶系統的實際位置因平台而異**（Claude Code 在 `~/.claude/projects/<...>/memory/`，
> Codex 用 `AGENTS.md`，OpenCode 用 `.opencode/`，OpenClaw 用 `~/.openclaw/`）。
> 完整路徑速查見 [references/agent-paths.md](references/agent-paths.md)。
> 如果當前 Agent 沒有獨立的記憶系統，直接跳過這層，把功夫全花在 docs 和專案根 markdown 上。

## 執行流程

### 第一步：盤點現況（強制機械式列舉，不能跳過）

**先做 ls，再做判斷。**

0. **先驗證 canonical skill 自己沒有腐敗**（完全獨立，不依賴 session history）：

   ```bash
   # 這兩個腳本是 canonical self-check，與 workspace 無關，可隨時運行
   python3 ~/.hermes/skills/neat-freak/scripts/sync-check.py
   python3 ~/.hermes/skills/neat-freak/scripts/skill-index-check.py
   ```

   若在互動式 session，可立即跟進：
   ```bash
   skill_view(name='hermes-agent')   # 取得 workspace 根目錄路徑、工具設定
   ```

   若為 cron job（無 session history）：hermes-agent 資訊需從上次保存的記憶或 `~/.openclaw/` 現況取得，優先依賴本次執行的磁碟實際狀態而非假設。

   **Ahead-only 評估 + Competing-commit guard**（branch ahead of origin/main 但不 behind）：
   ```bash
   git log --oneline origin/main..HEAD   # 快速窺見 ahead commits 性質
   ```
   若 ahead commits 主要是口徑修正（Skill_Index cleanup、dangling removal），**立即 push**；若摻雜實驗性變更，先 squash 再 push。詳見 Pattern U。

   **Compensate-commit guard**（在 ahead-only 評估之後、任何 git 操作之前）：
   ```bash
   LATEST=$(git ls-remote --refs origin main | awk '{print $1}' | head -1)
   PREV=$(git rev-parse HEAD)
   if [ "$LATEST" != "$PREV" ]; then
     git log --oneline origin/main..HEAD | grep -qi "drift\|fix.*Skill_Index" && \
       echo "WARNING: Remote may have competing fix. Pull before continuing."
   fi
   ```
   詳見 Pattern LL。

   `references/` 下的 `.md` 檔案在 linked_files 清單裡有承諾，缺檔案是 self-integrity failure。
   **`scripts/` 不在 linked_files 清單中，必須獨立檢查**——本維護（2026-05-14）和上次（2026-05-16）都漏掉過 restore。

**但 `sync-check.py` 只測目錄存在，不測內容一致**。即使報告 `All clean`，每個既有檔案都必須 diff 一次：
  ```bash
  for f in ~/.hermes/skills/neat-freak/references/*.md; do
    diff "$f" ~/Documents/Agent/skills/neat-freak/references/$(basename "$f") 2>&1
  done
  for f in ~/.hermes/skills/neat-freak/scripts/*.py; do
    diff "$f" ~/Documents/Agent/skills/neat-freak/scripts/$(basename "$f") 2>&1
  done
  ```
  - `diff` exit code 0 = 完全一致
  - `diff` exit code 1 = 內容不同（常見：canonical 已更新，workspace copy 落後）
  - 以 canonical 為準覆蓋 workspace copy

  **典型案例（2026-05-17）**：`sync-check.py` 報告 `All clean`，但 diff 發現 4/4 reference 檔案全部內容落後（canonical 為雙語完整版，workspace copy 為截斷英文版）。若不做 diff 就跳過，restore 會漏掉。

  **Pattern S 注意**：`sync-check.py` 報告 `EXTRA in workspace: agents/` 不一定是污染。需確認 origin/main 有無該內容再決定（詳見 `references/macos-case-insensitive-pitfalls.md` Pattern S）。

  **Missing canonical reference（每次都漏的反模式）**：當 sync-check.py 報告 `MISSING in workspace` 時，必須立即 restore，不能跳過：
  ```bash
  # 例：skill-index-script-bugs-2026-05-22.md 在 canonical 有、workspace 無
  cp ~/.hermes/skills/neat-freak/references/skill-index-script-bugs-2026-05-22.md \
     ~/Documents/Agent/skills/neat-freak/references/
  git -C ~/Documents/Agent add skills/neat-freak/references/skill-index-script-bugs-2026-05-22.md
  git -C ~/Documents/Agent commit -m "restore missing <file> from canonical"
  # 立即 push（口徑修復類 commit 不要累積）
  git -C ~/Documents/Agent push
  ```
  2026-05-22 session 確認：繼 `skill-index-2026-05-21-session.md`（上次 restore）之後，本次又發現 `skill-index-script-bugs-2026-05-22.md` 漏 restore。**每次 DRIFT 都有潛在 missing，要逐一確認**。

  **然後立即載入 hermes-agent**（`skill_view(name='hermes-agent')`），用它的內容來理解當前執行環境的 workspace 根目錄路徑、可用工具、和設定慣例。**每個 cron job 都從這步開始**，不要假設這次會話的環境跟上次一樣。hermes-agent 的設定會隨安裝、更新、或平台遷移而改變。

1. 列出 Agent 的記憶檔案（如有的話）：
   - Claude Code：`ls ~/.claude/projects/<...>/memory/` 並讀 `MEMORY.md` 及所有被引用的 `.md`
   - Codex / OpenCode / 其他：找該 Agent 的等價位置（見 references/agent-paths.md）
   - **hermes-agent / OpenClaw**：`~/.openclaw/workspace/`（`MEMORY.md` + `memory/` 子目錄）
2. 對本次對話涉及的**每一個專案**：
   - `ls <project-root>/` → 確認根目錄結構
   - `ls <project-root>/docs/ 2>/dev/null` → **列舉所有 docs**（沒有的也要確認）
   - `find <project-root> -maxdepth 2 -name "*.md" -not -path "*/node_modules/*" -not -path "*/.git/*"` → 兜底抓散落的 .md
   - 讀 `README.md`、`CLAUDE.md` / `AGENTS.md`、每一個 `docs/*.md`
3. 讀全域 Agent 設定（如有的話，例如 `~/.claude/CLAUDE.md`、`~/.codex/AGENTS.md`）
4. 回顧本次對話全部內容

**輸出一張檔案清單**（內部用，不用給使用者看），每個檔案標：「評估過 / 要改 / 不用改」。
**漏一個不行**——這是這個 Skill 最容易翻車的地方。

**附帶檢查：孤立檔案**（非技能、非文件但出現在 workspace 根目錄的 .md）：
在列舉 `find <project-root> -maxdepth 2 -name "*.md"` 時，會發現一些不在任何文件引用中的 `.md` 檔案（如 `Agent.md`、`Agents_2.md`）。這些孤兒可能：
- 被某個流程意外建立但從未引用
- 曾是文件但引用已移除
用 `grep -r "Agent\.md\|Agents_2\.md" . --include="*.md"` 確認無引用後，視為孤立候選，留「未處理」待人工裁決。

### 第二步：識別變更——用「變更影響矩陣」思考

**不要只看對話增量有什麼新事實，要看新事實會波及哪些文件層級。**

常見模式速覽：
- 新增 API / 路由 → CLAUDE.md 路由清單 + integration-guide + architecture 的 Routes
- 新增 / 改名 環境變數 → CLAUDE.md 環境變數表 + runbook + 下游 integration-guide
- 新增資料庫表格 → CLAUDE.md + architecture 的 Data Model
- 新增大特性（跨多檔案）→ 以上全部 + architecture 新章節 + handoff 已完成清單
- 跨專案改動 → 上下游兩邊的 docs **都要對齊**（最常見的漏改場景）
- 記憶層面：相對時間→絕對日期、過期事實→改、重複→合併、已完成待辦→砍

完整映射表（覆蓋更多變更類型與對應文件）見 **[references/sync-matrix.md](references/sync-matrix.md)**——遇到不确定的改動先查這張表。

**關鍵檢查**：這次對話是不是**跨專案**的？如果改了專案 A 且專案 B 依賴它
（透過 SDK、API、子網域、環境變數），**專案 B 的 docs 也要改**。
這是歷次同步最常翻車的場景。

### 第三步：實際修改（用工具，不只是描述）

你必須**真的用 Edit 修改既有檔案、用 Write 建立新檔案、用刪除指令清理廢棄檔案**。
「我會怎麼改」的描述不算完成。

**順序建議**：先改 docs/（改錯影響外部）→ 再改 CLAUDE.md/AGENTS.md → 最後理記憶。
先動外部優先順序最高的，即使中途被打斷，讀者看到的也是對齊的最新狀態。

**編輯原則**：

- **合併優於追加**：新資訊是對舊資訊的更新，改舊條目，不要再加一條
- **刪除優於保留**：完成的臨時計畫、推翻的決策、過期的上下文，砍掉
- **精確優於冗長**：一條記憶說清楚一件事，別塞三件
- **絕對時間**：永遠 `2026-04-29`，不寫「今天」、「最近」
- **metadata 一併更新**：修改任何文件時，若有 `Last updated`、`Updated:`、日期 version 欄位，**在同一次 commit 裡一併更新**。漏了會導致日後多一次無價值的口徑修正 commit（2026-05-19 教訓）
- **面向讀者**：docs/ 的讀者是「第一次接觸這個專案的外部人」，寫的時候想像對方只有 5 分鐘能看完
- **受眾不混**：CLAUDE.md 裡不抄 docs/ 的全文，docs/ 裡不寫「我記得上次……」——這是記憶的事

**Pitfall — `patch` 無法處理唯一性不足的多重匹配**：當多個 rows 內容完全相同（如多個 session 記錄都有相同的 description）時，`patch` 的 `old_string` 會同時匹配到多個位置，導致 `Found N matches for old_string` 而拒絕替換。症狀：明明只有一個需要改，卻被阻擋。

**修復**：換 `execute_code` 處理：
```python
content = open('/path/to/file.md').read()
old = 'exact string to replace'
new = 'replacement'
if old in content:
    content = content.replace(old, new, 1)   # 1 = 只換第一個
    open('/path/to/file.md', 'w').write(content)
    print("Fixed")
```

**實戰案例（2026-07-02）**：`memory/index.md` 有 6 個完全相同的 session row，試圖 patch 唯一的時間戳差異但因 row 完全相同而被阻擋。`execute_code` 一次成功。

**Pitfall — 廢棄參考文件陳屍磁碟**：正文說「已取代舊的 X」≠ X 已從磁碟刪除。跡象：`references/` 目錄裡有 md 檔案，但正文「## 參考資料」章節已無該檔案 link。修復：直接 `rm` 並 commit。驗證：`ls references/` 與正文 link 列表交叉比對，兩者必須完全一致。

**Pitfall — 版本範例陳屍不走**：

`Skill_Index.md` 有三種已知的腐敗模式，會反覆出現，每次 sync 都要檢查：
1. **Dangling rows** — 刪除 skill 目錄後 row 未移除（如 mattpocock-skills）
2. **Purpose cell `\\` 腐蝕** — 含 pipe 的 description 未轉義，cell 變成 `\\`
3. **Header/category drift** — header 數字、口徑加總與 actual rows 不符

完整修復流程（驗證腳本、Pattern 說明、修補順序）見 **[references/skill-index-corruption-patterns.md](references/skill-index-corruption-patterns.md)**。

**驗證脚本**：
- `python3 ~/.hermes/skills/neat-freak/scripts/sync-check.py` — 全面檢查 canonical vs workspace sync copy 結構（目錄、檔案、__pycache__）；注意只測存在性，不測內容
- `python3 ~/.hermes/skills/neat-freak/scripts/skill-index-check.py` — Skill_Index.md 口徑 drift、dangling、corruption 三項檢查

**Pitfall — 版本範例陳屍不走**：
版本升級後，`grep -E` 相對時間檢查會清零，但文件裡的「版本範例」——例如 `> GBrain v0.5.0 is available (you're on v0.4.0)` 或 `// Added in v0.6` 這類嵌入在範例訊息、註釋、範例代碼中的版本號——**grep 抓不到**，因為它們不是「今天/昨天」這類相對時間詞。
每次同步必須同時跑：
```bash
grep -rnE 'v[0-9]\\.[0-9]+\\.[0-9]+' <project>/docs/
```
並將結果與 `VERSION` / `CHANGELOG.md` 比對——凡文件裡的版本號比實際落後一個以上 major/minor patch 的，就是待更新的範例陳屍。

**Pitfall — Dated STATUS 檔案實為 active history orphan**：若 `docs/STATUS_YYYY-MM-DD-*.md` 含實質工作記錄（而非狀態截圖），應合併進 `STATUS_ALL.md` 後刪除原文。詳見 `references/status-file-consolidation-pattern.md`。

在所有檔案修改完之後（不是之前），給使用者簡潔摘要：

```
## 同步完成

### 記憶變更
- 更新：xxx（原因）
- 新增：xxx
- 刪除：xxx（原因）

### 文件變更（按專案分組，每個專案列全改動的檔案）
- <專案 A>/CLAUDE.md — xxx
- <專案 A>/docs/integration-guide.md — xxx
- <專案 A>/docs/architecture.md — xxx
- <專案 B>/docs/<integration>.md — xxx

### 未處理
- xxx（為什麼沒處理，例如需要使用者確認）
```

只列有實際變更的條目。沒改的不寫。

## Pattern OO（2026-07-07 初發現）：Skill_Index.md 格式從 link-style 變為 table-style——腐蝕圖譜 regex 全數過期

**觀察**：2026-06-29 完整重建後，`docs/Skill_Index.md` 的 row 格式已從 pipe-bracket link 格式（`\| [name](../path/SKILL.md)`）改為**純文字 pipe table 格式**（`\| name \| path \| description \| api_key \|`）。

但腐蝕圖譜中所有涉及口徑驗證的 regex 仍指向舊格式：

| 位置 | 過期 regex | 當前正確 regex |
|------|-----------|----------------|
| Pattern AA 驗證命令 | `re.findall(r'^\| \[([^\]]+\.md)\]', c, re.M)` | `re.findall(r'^\| [a-z]', l) and 'SKILL.md' in l` |
| Pattern NN 三口徑驗證 | `re.match(r'^\| \[', l)` | `re.match(r'^\| [A-Za-z0-9]', l) and 'SKILL.md' in l` |
| Pattern V 驗證命令 | `re.findall(r'\`\[([^\]]+SKILL\.md)\]\`', ...)` | 不適用（新格式不用 backtick link） |

**為什麼舊檢查找不到**：腐蝕圖譜上次更新時（2026-06-29 rebuild）口徑對齊，沒有驅使重新檢驗 regex 正確性。本次 drift 修復時重新 count 才發現 actual=0 而非預期的 600+。

**當前 Skill_Index.md row 格式識別符**：
```python
# 正確的口徑 count（pipe table 格式）
actual = [l for l in lines if re.match(r'^\| [A-Za-z0-9]', l) and 'SKILL.md' in l]

# 錯誤的口徑 count（舊 link 格式，2026-07-07 已不適用）
actual = re.findall(r'^\| \[([^\]]+\.md)\]', c, re.M)  # 永遠返回 0
```

**三口徑驗證命令（更新版，2026-07-07 起強制）**：
```python
import re
c = open(os.path.expanduser('~/Documents/Agent/docs/Skill_Index.md')).read()
lines = c.split('\n')

# 1. Count actual rows（pipe table format）
actual = [l for l in lines if re.match(r'^\| [A-Za-z0-9]', l) and 'SKILL.md' in l]
print(f'Actual rows: {len(actual)}')

# 2. Summary header
m = re.search(r'- Active Skills:\s*\*{2,3}(\d+)\*{2,3}', c)
summary = int(m.group(1)) if m else None
print(f'Summary header: {summary} (diff={abs(len(actual) - summary)})')

# 3. Category Map sum
cm_lines = [l for l in lines if re.match(r'^\| [^|]+\| \d+ \|', l)]
cm_sum = sum(int(re.search(r'\| (\d+) \|', l).group(1)) for l in cm_lines)
print(f'Category Map sum: {cm_sum} (diff={abs(len(actual) - cm_sum)})')

# 4. Per-section
section_headers = [(i, l) for i,l in enumerate(lines) if re.match(r'^## [^#]', l)]
all_ok = True
for num, line in section_headers:
    hm = re.match(r'^## [^#].+\((\d+)\)', line)
    if not hm: continue
    expected = int(hm.group(1))
    rows = sum(1 for l in lines[num+1:] if re.match(r'^\| [A-Za-z0-9]', l) and 'SKILL.md' in l and not re.match(r'^## [^#]', l))
    # stop at next section
    for j in range(num+1, len(lines)):
        if re.match(r'^## [^#]', lines[j]):
            rows = sum(1 for l in lines[num+1:j] if re.match(r'^\| [A-Za-z0-9]', l) and 'SKILL.md' in l)
            break
    status = '✓' if expected == rows else f'✗(expected={expected}, actual={rows})'
    if '✗' in status: all_ok = False
print(f'All sections OK: {all_ok}')
```

**預防**：每次 rebuild Skill_Index.md 後，獨立驗證口徑命令必須重新測試——不只是確認數字對，也要確認 regex 能抓到 rows（actual count > 0）。若 actual=0，regex 格式100%有問題。

### Pattern CC（2026-05-29 初發現）：路徑參照衝突——cross-document path inconsistency

**觀察**：`AGENTS.md` 的 Vault 路徑紀錄為 `~/Documents/Obsidian`，但磁碟上的實際目錄名是 `~/Documents/Pigo_Obsidian`。記憶系統（`memory/P0-core.md`）已正確，但 `AGENTS.md` 錯誤。兩個文件來自同一個 repo，彼此同步了外層結構但未同步路徑事實。

**為什麼舊檢查抓不到**：
- Step 1 的 `find -name "*.md"` 只列舉檔案，不比對檔案間的內容邏輯一致性
- 舊的相對時間 / 版本號 grep、dangling entries 檢查都不涉及路徑字串的 cross-document 驗證

**修復**：
在 Step 1 末段（列舉完所有 md 檔案之後）新增**路徑參照交叉檢查**：
```bash
# 對每個聲稱某路徑存在的文件，驗證該路徑是否在磁碟上真的存在
grep -rh "~/Documents/" --include="*.md" | sort -u | grep -v "^#" | while read line; do
  echo "$line" | grep -oE "~/[^ \)\"']+" | sort -u
done | while read path; do
  expanded="${path/#~\/$HOME}"
  if [ ! -e "$expanded" ]; then
    echo "WARN: $path (from docs) does not exist on disk"
  fi
done
```
**只報 warning，不自動修改**——路徑衝突可能有多個合理的時間點（如 vault 搬家），需要人工裁決。

**預防**：任何「路徑變更」都必須同時更新記憶 + AGENTS.md + 任何其他參照該路徑的文件，不能只改一處。

你是**知識庫編輯**，不是打字員。

`neat-freak` 同時存在於兩個位置：
- **Canonical**：`~/.hermes/skills/neat-freak/`（上游 skill 本體，永遠視為正確來源）
- **Workspace sync copy**：`~/Documents/Agent/skills/neat-freak/`（從 canonical 同步過來的副本，會出現在 git diff 和 workspace ls 裡）

這不是污染，是正常架構。但 Step 0 自檢、`git status`、和「workspace pollution」檢查如果沒考慮這個雙軌結構，會把**正常的 sync 文件**誤判成污染或 dangling。

**正確的判斷邏輯**：
```bash
# canonical 位置的所有 reference 檔案
ls ~/.hermes/skills/neat-freak/references/

# workspace sync copy 的所有 reference 檔案
ls ~/Documents/Agent/skills/neat-freak/references/ 2>/dev/null

# 如果 workspace copy 少了 canonical 有的檔案 → 正常（需要 sync 回 workspace）
# 如果 workspace copy 比 canonical 多了檔案 → 需要評估是 sync 還是新增
```

**修復方式**：
- 缺少的檔案：從 canonical 拷到 workspace，git add + commit（視為 restore）
- 多的檔案：檢查是否為 legitimate workspace addition（如果是從其他流程同步過來的合法檔案，保留；如果是 script 誤寫入的，移除）
- **不要**因為 `git diff --stat` 顯示 `create mode` 就判定是污染——這可能是正常的 sync restore

**驗證**：restore 完成後，`git diff origin/main --stat` 不應該顯示 `skills/neat-freak/references/` 有不預期的 create/delete。

**為什麼相對時間 grep 抓不到**：版本範例是「`> GBrain v0.8.0 is available (you're on v0.7.0)`」這類嵌入在 markdown 程式碼區塊或 blockquote 裡的文字。`grep -E "今天|昨天|recently"` 對這種「相對版本號」完全盲眼。**每次 sync 都必須跑版本號 grep**，不能只靠相對時間檢查。

**全域設定極度節制**：`~/.claude/CLAUDE.md` / `~/.codex/AGENTS.md`
只有在使用者在對話中明確表達了**跨專案的核心原則**才能動。日常專案細節絕不進全域。

**docs/ 編輯要點**——新增一個能力的文件變更通常要四處都補：
1. **integration-guide** 或對應「外部視角」文件：加**怎麼用**（curl / SDK 範例 / 錯誤碼表）
2. **architecture**：加**怎麼工作**（資料流、狀態機、設計取捨）
3. **runbook**：加**怎麼維運**（冒煙指令、故障排除、環境變數）
4. **handoff** 或 CHANGELOG：加**已完成**

- **[references/skill-index-2026-05-19-session.md](references/skill-index-2026-05-19-session.md)** — Pattern V/W/X/Y from 2026-05-19 session (uniform +1 per-section drift, execute_code vs terminal, patch after sibling, metadata atomicity)

## 附：2026-05-21 session 新增參考

- **[references/skill-index-2026-05-20-session.md](references/skill-index-2026-05-20-session.md)** — Skill_Index vs Skill_Category 兩套口徑差異的正確解讀
- **[references/skill-index-script-bug.md](references/skill-index-script-bug.md)** — Pattern V regex 錯誤機制（.+ greedy 吃掉 SKILL.md 終止符）、驗證方法、Pattern J vs V 區分
- **[references/skill-index-2026-05-19-session.md](references/skill-index-2026-05-19-session.md)** — Pattern V/W/X/Y from 2026-05-19 session
- **[references/skill-index-2026-05-22-session.md](references/skill-index-2026-05-22-session.md)** — Pattern Z2 missing canonical reference 再現；restore 後 push，ALL CLEAN

## 參考資料

- **[references/skill-index-corruption-patterns.md](references/skill-index-corruption-patterns.md)** — Skill_Index.md 三種常態腐敗

- [ ] 第一步列出的每個檔案，都判斷了「不用改」或「已改」
- [ ] 記憶索引（若有的話）裡的每個連結指向存在的檔案
- [ ] 每個記憶檔案的 description 和內容對得上
- [ ] 記憶之間沒有互相矛盾
- [ ] CLAUDE.md / AGENTS.md 裡提到的路徑 / 指令 / 工具 / 環境變數在程式碼中真實存在
- [ ] README 的安裝 / 執行步驟跟程式碼一致
- [ ] 新增 API 路由：**在 integration-guide 和 architecture 都出現了**
- [ ] 新增環境變數：**在 runbook 和專案根 markdown 都出現了**
- [ ] 新增資料庫表格：**在 architecture 的 Data Model 和專案根 markdown 都出現了**
- [ ] 跨專案影響：下游專案的 docs 也跟著改了
- [ ] 沒有相對時間殘留（`grep -E "今天|昨天|剛剛|最近|上週|today|yesterday|recently"` 清零）——**注意**：`recently` 出現在 SKILL.md 的 `description` 或 `Purpose` 欄位（如 `Document a recently solved problem`）時，是**功能描述性文字**，並非相對時間殘留，不需要修改。只有出現在敘述「上次什麼時候做」這類時間參照上下文時才需要處理（2026-05-14）
- [ ] **無 UTF-8 mojibake 腐蝕**（Pattern II 擴充，2026-10-22）——相對時間 grep 對 mojibake 100% 盲眼，`file` 只測編碼類型，唯一可靠偵測是逐檔算 badness：
      ```bash
      /usr/bin/python3 -c "
      import os,sys
      from ftfy.badness import badness
      for root,d,f in os.walk(sys.argv[1]):
          if '.git' in root: continue
          for fn in f:
              if fn.endswith('.md'):
                  p=os.path.join(root,fn)
                  b=badness(open(p,encoding='utf-8',errors='replace').read())
                  if b>50: print(round(b,1),p)
      " <path>
      ```
      `ftfy` 裝在 `/usr/bin/python3`（3.12），Hermes venv 與 `~/.hermes/tools/python-3.14.7` **沒有**。修復用 `fix_encoding()`（不是 `fix_text()`，後者會改全形標點），且必須**逐行**套用 + ASCII 骨架比對。
      ⚠️ `badness > 0` **不等於** mojibake——中英混排標點也會給非零分數。確認時必須跑 `fix_encoding(content) == content`；`fix_text()` 會改動 19 行正常中文（它在做全形標點轉換），`fix_encoding()` 0 行改動 = 全部假陽性（Pattern OOO 附錄）。
- [ ] **所有 skill 的 YAML frontmatter 可解析**（Pattern OOO/PPP，2026-10-26）——canonical 與 workspace **兩棵樹都要掃**，且通用 YAML 解析通過 **≠** Hermes 能載入：
      ```bash
      /usr/bin/python3 -c "
      import os, yaml
      SKIP={'references','examples','scripts','agents','assets','templates','.archive','.git','__pycache__'}
      for root in ('/home/x/.hermes/skills','/home/x/Documents/Agent/skills'):
          bad=0; tot=0
          for dp,dirs,files in os.walk(root):
              dirs[:]=[d for d in dirs if d not in SKIP]
              if 'SKILL.md' not in files: continue
              tot+=1
              raw=open(os.path.join(dp,'SKILL.md'),'rb').read()
              try: yaml.safe_load(raw.split(b'---',2)[1].decode('utf-8','replace'))
              except Exception as e: bad+=1; print('INVALID',dp,str(e)[:70])
          print(root,'total',tot,'invalid',bad)
      "
      ```
      最終裁決用 Hermes 自己的 parser（**必須**）：
      ```python
      import sys; sys.path.insert(0,'/home/x/.local/share/uv/tools/hermes-agent/lib/python3.12/site-packages')
      from agent.skill_utils import parse_frontmatter
      from agent.skill_commands import scan_skill_commands
      ```
      批次改寫 frontmatter 一律用 `bytes.replace(old, new, 1)` 精確取代，**不要用「切出→修→拼回」重建**（會吃掉 fence 後的空行，見 Pattern PPP）。
- [ ] **`Skill_Index.md` 口徑分類驗證**（Pattern QQQ，2026-10-26）——「磁碟比 index 多」不自動等於 drift。先把差額按目錄性質分類（現行 / `*_revived` 歷史復原 / `*.bak` / `test/fixtures`），分類完再判斷。直接重建會把歷史版 skill 誤標為 active。
- [ ] Git 工作樹是乾淨的（**先用 `git status`（非 `--short`）確認沒有隱藏的 staged 檔案，再視需要用 `git status --short`**——後者不顯示 staged deletion；更危險的是 stash 之後 `git stash list` 不會出現在任何 `git status` 輸出裡，容易被忽略）；如果看到差異，先 `git diff` 確認內容再決定是否 commit 或 rollback
- [ ] Branch 與 upstream 同步狀態（`git status` 會顯示 `ahead/by X commit(s)`，落後錨點或落後 origin 都是訊號；ahead 不 push 只是落後，behind 不 pull 會造成未來的 merge 痛苦）
- [ ] Branch divergence（`Your branch and 'origin/main' have diverged`）— 立刻評估是架構調整（skill 搬家）還是錯誤的 merge，絕對不要在 divergence 未解決前做 `git stash`
- [ ] Ahead-only 評估：若 `ahead by N` 且 N 的 commits 主要是口徑修正 / dangling cleanup → **立即 push**，不要累積（Pattern U）
- [ ] `git stash` 在 staged-only 檔案時的危險：stash 棧不會在 `git status --short` 顯示出來，但 `git stash list` 裡有；更危險的是 `git stash pop` 如果有 conflict 會把已 staged 的 commit 節點留在 WIP 狀態。**正確流程**：懷疑有 staged 變更時，先 `git status`（非 `--short`），確認工作樹狀態後再決定是否 stash
- [ ] **`git add -A` 在大型 workspace 的沉默風險**：在包含數百個 skills 的 workspace（如 `~/Documents/Agent/`）中，`git add -A` 會把所有 unstaged 變更包含進 staging area，**包含大量預期中的刪除檔案**（如已搬家到別處的 skill 目錄）。此時 `git status`（預設）會顯示「Changes to be committed」而非「nothing to commit」，若直接以為工作樹乾淨就跳過 commit 會丟失這些刪除。**正確做法**：先 `git status`（非 `--short`）確認 staging 狀態，再決定是否 commit；若 staging 內容是預期的 workspace 清理，直接 commit 並在 log 說明原因
- [ ] Skill 自己的 references/ 沒有被汙染進 workspace（`~/Documents/Agent/neat-freak/` 如果存在，必須是 canonical 的正當 sync copy，而非 script 誤寫入；參見「雙軌結構」pitfall）
- [ ] Step 0 雙軌結構檢查通過（跑 `python3 ~/.hermes/skills/neat-freak/scripts/sync-check.py`）：
  `[1]` references/ 無 missing/extra drift、`[2]` scripts/ 無 missing/extra drift、`[3]` 無 `__pycache__` 污染
- [ ] Step 0 內容一致性確認：`diff ~/.hermes/skills/neat-freak/scripts/<file> ~/Documents/Agent/skills/neat-freak/scripts/<file>` 確認每個既有檔案完全一致
- [ ] Skill_Index.md 通過全部五項檢查（跑 `python3 ~/.hermes/skills/neat-freak/scripts/skill-index-check.py` — **用絕對路徑，不要用相對路徑**，相對路徑在 workspace sync copy 裡會指向錯誤位置）：
  `[1]` Summary drift、`[2]` per-section drift、`[3]` dangling、`[4]` Purpose cell `\\` 腐蝕、`[5]` Skill_Category.md 對齊
  **注意**：若 Python 3.13 環境下 script crash（`re.PatternError`），參見 Pattern G（腐蝕圖譜第 7 條）

  **Skill_Category.md 與 Skill_Index.md 口徑不一致的判斷原則**：
  - `Skill_Index.md` 的 section header 數 = 磁碟上實際 SKILL.md 數（用 `-\s+\*\*[^*]+\*\*\s+—` regex 計）
  - `Skill_Category.md` 的 category 總和 = 另一套 14 類功能分類，允許與 Skill_Index.md 數字不同（因為分類邏輯不同、計數重疊）
  - **兩者數字不同 ≠ drift腐敗**，只要各自內部 count 一致即可
  - 若懷疑是腐敗，用獨立 Python 重新 count Skill_Index.md：`python3 -c "import re; print(len(re.findall(r'\-\s+\*\*[^*]+\*\*\s+—', open('docs/Skill_Index.md').read())))"`

  **注意**：若 Python 3.13 環境下 script crash（`re.PatternError`），參見 Pattern G（腐蝕圖譜第 7 條）

## Pattern W（2026-05-19）：驗證 drift 性質時的獨立計數原則

**原則**：判斷一個 drift 到底是「index 真的錯了」還是「checker 的口徑錯了」，
必須用**獨立於 checker 的方法**重新計數一次，不能只信 checker 的自我報告。

**方法**：
1. 先用獨立 Python count 出 actual rows（regex 見 Pattern NN 的三口徑驗證命令）
2. 再跑 `skill-index-check.py` 比對兩組數字
3. 若 script 報 `Actual rows: 0` 卻同時給 `✓ ALL CLEAN` → 是 script 的 regex 失效（Pattern AA / Pattern V），不是 index 乾淨
4. 若兩組數字一致但都錯（如 header 說 760、actual 說 759）→ 是**第三個數字**沒跟著更新（Pattern XXX）

**預防**：
- 發現 drift 時，先用獨立 Python 重新 count，不依賴 script 輸出
- script 的「✓ ALL CLEAN」只代表**被驗的那幾項**一致，不代表文件內部自洽（Pattern XXX / Pattern YYY）
- 修改 `skill-index-check.py` 的 regex 後，除了獨立 count 驗證口徑，還要跑一次**負向測試**（故意改壞一個值 → 確認它會報錯）

## 特殊情況

**專案還沒有 README 或 CLAUDE.md/AGENTS.md**：判斷專案是不是到了「有可執行程式碼」的階段。
是 → 建立。還在 vibe 階段 → 跳過，但在摘要裡提一句。

**對話沒有產生新事實**：審查現有記憶和文件有沒有過期 / 衝突 / 相對時間——審查本身就有價值。

**記憶之間出現無法自動判斷的矛盾**：列在「未處理」讓使用者決定。
**這是唯一需要使用者介入的情況**，其他都自己拍板。

**跨專案改動**：本次對話改了多個專案，每個專案都要跑一次完整的第一步（ls + 讀 docs）。
不要假設一個專案的 docs 改了，另一個就不用。
尤其是上游-下游對接文件（集成指南 / SDK 說明 / API 協定），兩邊都要對齊。

- **發現之前的同步漏了東西**：修掉。不要說「那不是這次對話的事」——
  你就是這個專案的持續編輯，過去的漏洞也歸你管。

- **macOS case-insensitive 陷阱**：刪檔案前必先用 `git ls-files -- "<exact-name>"` 確認沒被追蹤；`rm` 大寫檔名可能同時刪掉 git 追蹤的小寫版本（詳見 `references/macos-case-insensitive-pitfalls.md` Pattern R）

**Stale skill（引用已移除專案的技能）**：當你發現 workspace 裡的某個 SKILL.md 引用了一個已被移除的系統（如 GBrain），不要直接刪除該 SKILL.md——因為 Skill_Index.md（如果有）會因此產生懸空引用，正確做法是將該技能的 `description` 或內容標記為 `DEPRECATED` 並說明原因，讓下游查閱者知道去處而非面對斷裂的索引。若不確定是否已被移除，先 grep 整個 workspace 確認。完整流程見 **[references/gbrain-deprecation-workflow.md](references/gbrain-deprecation-workflow.md)**。

**Cron job / 無使用者會話**：當你以排程任務執行 neat-freak 而沒有即時使用者，可以且應該自主判斷。你的上下文資訊只有（1）session history（2）磁碟上的實際檔案。判斷不了的果斷留「未處理」，但不要因為「沒有使用者確認」就放棄所有修改——有足夠資訊依據的維護動作，直接做。

**Vault 側的 audit 報告要直接修，不要只回報選單**：當報告對象是 `~/Documents/Pigo_Obsidian`
（不是 Agent repo 的 `Skill_Index.md`）時，發現的通常是機械式可修項——缺少 `00-Inbox/`、
active intake 放錯分類目錄、外部 vault 連結已失效、目錄命名不一致。這些不是需要裁決的
架構決策，列出「發現」就等於授權修。Pigo 的回應通常是「請逐一修復」，不是「給我優先級
選單」；把可修項列成待辦再回頭問一次，是把決策負擔丟回給使用者。

**但要區分「機械式修復」與「需要裁決」**：
- 機械式 → 直接做：建目錄、搬移錯放筆記、移除已失效的外部連結、統一命名
- 需裁決 → 留「未處理」：刪除 archive/歷史資料、合併重複筆記、動到 Chroma DB / git log

**外部連結失效的判定標準**：修完後全 vault 搜尋殘留字串，剩下的命中要逐一確認不是可點擊的
wikilink。落在 archive log、git log、Chroma DB 或歷史報告裡的字串是歷史資料，**不要為了讓
數字歸零而改寫 archive**。詳細流程見 `vault/vault-management` skill。

## 參考資料

- **[references/skill-index-corruption-patterns.md](references/skill-index-corruption-patterns.md)** — Skill_Index.md 三種常態腐敗（Dangling rows、Purpose cell `\\` 化、Header drift）與完整修復順序；取代舊的 mattpocock-corruption-patterns.md
- **[references/skill-index-verification.md](references/skill-index-verification.md)** — 路徑解析基準與 drift 口徑交叉檢查（已整合進腐蝕圖譜，保留供參）
- **[scripts/skill-index-check.py](scripts/skill-index-check.py)** — 單一命令完成口徑 drift、dangling、corruption 三項檢查
- **[scripts/sync-check.py](scripts/sync-check.py)** — canonical vs workspace sync copy 結構全面檢查（目錄、檔案、__pycache__）；注意只測存在性，不測內容
- **[references/sync-matrix.md](references/sync-matrix.md)** — 變更類型 → 文件層級映射表
- **[references/agent-paths.md](references/agent-paths.md)** — 各 Agent 平台的記憶與設定路徑速查
- **[references/workspace-snapshot.md](references/workspace-snapshot.md)** — Workspace 拓撲快照（hermes-agent、gbrain、Agent 三專案現況）
- **[references/gbrain-deprecation-workflow.md](references/gbrain-deprecation-workflow.md)** — GBrain 移除後的 stale skill 處理流程
- **[references/skill-index-2026-05-19-session.md](references/skill-index-2026-05-19-session.md)** — Pattern V/W/X/Y from 2026-05-19 session
- **[references/skill-index-2026-05-20-session.md](references/skill-index-2026-05-20-session.md)** — Skill_Index vs Skill_Category 兩套口徑差異的正確解讀
- **[references/skill-index-script-bugs-2026-05-22.md](references/skill-index-script-bugs-2026-05-22.md)** — 2026-05-22 發現的三個 script bug（dangling path錯誤、header regex錯誤、category命名系統混淆）與修復方法
- **[references/skill-index-2026-05-21-session.md](references/skill-index-2026-05-21-session.md)** — 口徑驗證命令、Pattern S+Z EXTRA 組合確診流程、578 vs 581 口徑說明
- **[references/skill-index-2026-05-29-session.md](references/skill-index-2026-05-29-session.md)** — 路徑參照衝突修復（~/Documents/Obsidian vs ~/Documents/Pigo_Obsidian）、Pattern CC 新增、Skill 重複內容清理
- **[references/skill-index-2026-05-30-session.md](references/skill-index-2026-05-30-session.md)** — Dated backup files in AGENT/; Pattern Z extra diagnosis confirmed; branch sync verified clean
- **[references/skill-index-2026-05-31-session.md](references/skill-index-2026-05-31-session.md)** — 口徑 486 = header，口徑完全乾淨；script `Actual rows: 0` CRITICAL bug 仍存在，SKILL.md 已強化警告；Pattern EE 新增（全部 486 路徑 dangling，磁碟實有 597 skills）

## 附：2026-06-05 session 新增參考

- **[references/skill-index-2026-06-05-session.md](references/skill-index-2026-06-05-session.md)** — Pattern II 新增（Readme.md UTF-8 mojibake corruption）；口徑 517 = header，口徑差 82 個 skills；branch 乾淨

## 附：2026-06-02 session 新增參考

- **[references/skill-index-2026-06-05-session.md](references/skill-index-2026-06-05-session.md)** — Pattern II（Readme.md mojibake）；口徑 517=header，口徑差 82
- **[references/skill-index-2026-06-02-session.md](references/skill-index-2026-06-02-session.md)** — Pi-AGENTS.md 路徑遷移；sync-check.py DRIFT 確診正當；Pattern HH
- **[references/skill-index-2026-06-01-session.md](references/skill-index-2026-06-01-session.md)** — 口徑 486 = header，磁碟 600 skills，落後 114；sync-check.py DRIFT 已確診正當；Pi-AGENTS.md OPENSPEC block 為條件式描述非陳屍；AGENT/Readme.md dated backup 列表符合 Pattern GG（已確認非引用問題）
- **[references/status-file-consolidation-pattern.md](references/status-file-consolidation-pattern.md)** — Dated STATUS_2026-04-*.md 實為 active history orphan，應合併進 STATUS_ALL.md；與 Pattern DD 的區分；已實戰驗證的合併流程

## 附：2026-06-05 session 新增參考（本次）

- **Pattern HH + FF 聯動修復**：root `AGENTS.md` 含 Windows 路徑（`C:\Users\hsi67063\...`）與 `AGENT/AGENTS.md` 含 `~/.codex/docs/STATUS_ALL.md` 為兩起獨立的 cross-document drift，同步修復後各自與 `docs/Pi-AGENTS.md` 口徑一致。
- **Pattern CC false positive 確認**：`docs/Pi-AGENTS.md` 的 `~/Documents/Pigo_Obsidian` 為**正確路徑**，非過期；2026-06-01 已修復，Pattern CC 的 Path V 追蹤終結。
- **`func.md` 非 orphan**：被根 `Readme.md` lines 24, 60, 103, 104 多處引用，是 active Function Registry，維護狀態良好。

## 附：2026-06-10 session 新增參考

- **[references/skill-index-2026-06-10-session.md](references/skill-index-2026-06-10-session.md)** — 口徑 518 = header（+1 from 2026-06-05）；Pattern S/Z 三項 EXTRA 組合再確診為正當 origin 擴充；611 disk vs 518 indexed（落後 93 個 upstream 重構遺留）；workspace branch 與 origin 完全同步；口徑修復 commit 同次 session push（Pattern U）

- **[references/skill-index-false-clean-pattern.md](references/skill-index-false-clean-pattern.md)** — skill-index-check.py persistent false-clean bug: script reports ✓ ALL CLEAN with 0 dangling while verified scan finds 482 dangling paths; always verify with independent Python count

## 附：2026-06-29 session 新增參考

- **[references/skill-index-2026-06-29-session.md](references/skill-index-2026-06-29-session.md)** — 完整重建 Skill_Index.md (520 → 605)；A2-改2 分類決策；max_concurrent_children=3 hard cap 踩坑；merge script column-header tolerance；Pattern II 確認生效

## 附：2026-06-30 session 新增參考

- **[references/skill-index-false-clean-pattern.md](references/skill-index-false-clean-pattern.md)** — 更新：發現 `check_per_section_drift()` 有第二層 structural bug（dict key collision，導致所有 8 sections 全部 report actual=0）；獨立 Python count 確認口徑 605 = header = 全 8 sections 正確（並非真正的 drift）；更新驗證命令

## 附：2026-07-01 session 新增參考

- **[references/skill-index-2026-07-01-session.md](references/skill-index-2026-07-01-session.md)** — 口徑 605 = header，口徑正確；Path drift 新範圍（`/home/pigo/文件/` 擴及 skill docs，不只 AGENTS.md）；Pattern S/Z drift 再次確診正當；4 項 EXTRA 全部 origin/main tracked content

## 附：2026-07-02 session 新增參考

- **[references/skill-index-2026-07-02-session.md](references/skill-index-2026-07-02-session.md)** — Pattern JJ 新增（docs/Readme.md Primary Read Targets 雙反斜線路徑腐敗 `article-notes\` → 修復為 `article-notes/`）；口徑 605 = 606 actual，口徑正確；10 個 Skill 重複名稱為不同子目錄合法同名skill，非腐敗；sync-check DRIFT 4 項 EXTRA 全部 origin/main tracked content；**`patch` vs `execute_code` 多重匹配處理差異**（記憶 index.md 同一 row 出現 6 次，只有 execute_code 能處理）

## 附：2026-07-04 session 新增參考

- **[references/skill-index-2026-07-04-session.md](references/skill-index-2026-07-04-session.md)** — 口徑 drift 再現（605 header vs 585 actual）；Root-level drift 14（header=64, actual=50）；Pattern MM 新增（subagent merge 後 header drift 系統性重現）；Readme.md 幽靈目錄修復；restore canonical frontmatter-corruption-bug.md

## 附：2026-07-07 session 新增參考

- **[references/skill-index-2026-07-07-session.md](references/skill-index-2026-07-07-session.md)** — 口徑 603 = actual，口徑正確；三口徑 drift（Summary=606, Category=604, Section=603）；Pattern NN 新增（三層口徑可分層落後，需各自獨立驗證）；Pi-AGENTS.md openspec 條件式描述非陳屍；sync-check DRIFT 確診正當 upstream 擴充；canonical reference 同步（workspace→canonical）

口徑 drift 只有 1（actual=595, 三口徑全 594）；三口徑獨立驗證 + execute_code 批次修復；`execute_code` f-string 反斜槓限制（Python 3.11+ 嚴格限制）；Pattern Z EXTRA 再次確診正當；restore missing canonical reference

## Pattern MM（2026-07-04 初發現）：Subagent Merge 後 header drift 系統性重現

- **[references/skill-index-2026-07-08-session.md](references/skill-index-2026-07-08-session.md)** — 口徑 drift 只有 1（actual=595, 三口徑全 594）；三口徑獨立驗證 + execute_code 批次修復；`execute_code` f-string 反斜槓限制（Python 3.11+ 嚴格限制）；Pattern Z EXTRA 再次確診正當；restore missing canonical reference（skill-index-2026-07-07-session.md）

## 附：2026-07-09 session 新增參考

- **[references/skill-index-2026-07-09-session.md](references/skill-index-2026-07-09-session.md)** — 口徑 plateau（3→3，policy mismatch，非腐敗）；Pattern PP 新增（vault frontmatter FAIL plateau，00-Inbox intake stub exemption gap）；4 檔修復（x-note-fxtwitter-troubleshoot、x-note-fallback-gaps、templates/index、歡迎）；status note 已寫入 00-Inbox/

## 附：2026-10-22 session 新增參考

- **[references/skill-index-2026-10-22-session.md](references/skill-index-2026-10-22-session.md)** — 跨三層（canonical ~/.hermes/skills、Agent repo、vault）系統性 mojibake 腐蝕修復（60 檔）；Pattern II 擴充（ftfy badness 掃描為唯一可靠偵測手段、fix_encoding 而非 fix_text、逐行 ASCII 骨架比對）

## Pattern MM（2026-07-04 初發現）：Subagent Merge 後 header drift 系統性重現

**觀察**：2026-06-29 完整重建後，本次（2026-07-04）和下一次（2026-07-04 即本次）都發現重建後的口徑 drift：
- 2026-06-29 重建：header=605，actual=585（差 20），Root-level header=64 vs actual=50（差 14）
- 本次（2026-07-04）同樣 pattern：Root-level header=64 vs actual=50

**根因**：subagent 在生成 `03-rows-G*.md` 時，已經在 section header 寫入「預期 count」（如 Root-level 64）而非重新 count actual rows。merge script 直接串接這些 header，保持了錯誤數字。

**修復**：用 execute_code 批次替換（不能依賴 patch，4 個 drift 需同時修）：
```python
content = open('docs/Skill_Index.md').read()
for old, new in [
    ('## media-documents (66)', '## media-documents (64)'),
    ('## engineering..., (91)', '## engineering..., (88)'),
    ('## manual-review..., (36)', '## manual-review..., (35)'),
    ('## Root-level Skills (64)', '## Root-level Skills (50)'),
    ('| Root-level Skills (standalone) | 64 |', '| Root-level Skills (standalone) | 50 |'),
    ('| Media, Documents & Writing | 66 |', '| Media, Documents & Writing | 64 |'),
    ('| Engineering..., | 91 |', '| Engineering..., | 88 |'),
    ('| Manual Review..., | 36 |', '| Manual Review..., | 35 |'),
]:
    content = content.replace(old, new, 1)
open('docs/Skill_Index.md', 'w').write(content)
```

**預防**：
1. merge script 必須在串接後重新 count 每個 section 的 actual rows，並用 actual 值重寫 header
2. 獨立 Python 驗證是唯一可靠的 drift 檢測方式，script 的 `actual=0` 是已知虛假信號

## Pattern QQ（2026-10-23 第三 run 初發現）：Purpose cell 三型腐蝕 + checker 漏判單一反斜線

**發現**：`skill-index-check.py` 回報 `✓ ALL CLEAN`，但 index 內實際有 14 個 row 的
purpose cell 是 `\|`、57 個是佔位字串 `Agent workflow skill for <name>.`、1 個含字面量 `\n`。

**根因（兩個 bug 疊加）**：

1. `check_purpose_corruption()` 用 `line.split('|')` 切 cell — `\|` 的 `|` 也被當分隔符，
   row 被切成 5 段，`cells[2]` 取到的不是 purpose cell。
2. 判定集合只含 2 個 / 4 個反斜線（`'\\\\'`），**單一 `\` 不在集合內**，`startswith` 也不成立 → 漏判。

**修復**（canonical `scripts/skill-index-check.py`）：

```python
def _split_row(line):
    parts = re.split(r'(?<!\\)\|', line)   # 只在未被 escape 的 pipe 上切分
    return [p.strip() for p in parts[1:-1]]
```
判定條件擴充為三型：`backslash` / `placeholder`（`^Agent workflow skill for .+\.$`）/
`literal-newline`（purpose 含 `\n` 兩字元）。

**預防**：
- 任何 pipe table 的 cell 切分都要用 `re.split(r'(?<!\\)\|', ...)`，不可用 naive `split('|')`
- 新增腐蝕型別後，必須用**舊版 index** 餵新版 checker 驗證「能抓到」（本次：舊 72 → 新 0）
- 用 grep 數 `\|` 的次數**不能**當這個數字的驗證 — purpose 裡合法逸出的 pipe 會混進來
- 佔位描述的 row 可能對應到**沒有 YAML frontmatter** 的 SKILL.md（只有 `## Purpose` 區段），
  這種得人工補 description，或回頭把 frontmatter 補齊

### Pattern RRR-2（2026-11-05 第二十四 run）：語意不同步是「常態檢查」，不是修一次就結案的歷史債

2026-10-28 修完 27 檔後，11-05 又抓到 4 檔，且**全部由 upstream 事件引入**：
1. 上游 job 改寫 SKILL.md frontmatter（x-agent 轉 Agent-native、x-agent-qa 改英文、
   x-note 加 KAW 路由），index row 沒跟著改 → 3 檔陳舊。
2. 上游新增 index row 時 purpose cell 寫的是**手寫摘要**而非 frontmatter 原文
   （`chinese-novelist`，upstream `592ee39a`）→ 1 檔不同步。

**任何動到 frontmatter 或新增 row 的 upstream job（x-agent 批次、weekly skills update、
手動新增）都不觸發 purpose cell 同步**，checker 7 項也全部結構性。
→ RRR 補測腳本**每次 run 都要重跑**；merge upstream 後**必須立即重跑一次**
（本次 merge 後才暴露 chinese-novelist 那筆）。詳見
[references/skill-index-2026-11-05-session.md](references/skill-index-2026-11-05-session.md)。

## Pattern RRR（2026-10-28 第十五 run 初發現）：Purpose cell 與 frontmatter 敘述「語意不同步」— checker 的結構性盲區

**發現**：`skill-index-check.py` 回報 `✓ ALL CLEAN`，但 `Skill_Index.md` 有 **27 個 row 的 purpose cell
與該 SKILL.md 的 frontmatter `description` 對不上**。兩類退化：

1. **陳舊**：index 記的是舊版 description。例：`executing-plans` index 寫「execute in a separate session」，
   檔案 frontmatter 已是「in the current session as the implementer yourself」。
2. **退化為非描述文字**（Pattern OOO-2 的 downstream 症狀）：
   - `llm-wiki` 三個副本的 purpose cell = `Path to the active vault root`
   - `web-access` = `# web-access Skill`
   - `Paper-Read` = `# Skill Definition: Academic-Omni-Router`

**為什麼舊檢查抓不到**：`skill-index-check.py` 的五項檢查覆蓋
口徑 drift / dangling / purpose cell 的三型**結構性**腐蝕（backslash、placeholder、literal-newline），
**完全不驗 purpose cell 與 frontmatter 敘述的語意一致性**。
一句寫得通順的陳舊描述，在結構上無從與「格式壞掉」區分。

**補測腳本**（用 `/usr/bin/python3`——Hermes venv 與 `~/.hermes/tools/python-3.14.7` **沒有** `yaml`）：

```python
import os, re, yaml
idx = open('docs/Skill_Index.md').read()
rows = re.findall(r'^\|\s*([^|]*?)\s*\|\s*(skills/[^\s|]*SKILL\.md)\s*\|\s*([^|]*?)\s*\|', idx, re.M)
mism = []
for name, path, purpose in rows:
    if not os.path.exists(path): continue
    raw = open(path, 'rb').read()
    parts = raw.split(b'---', 2)
    if len(parts) < 3: continue
    try: fm = yaml.safe_load(parts[1].decode('utf-8', 'replace'))
    except Exception: continue
    if not isinstance(fm, dict): continue
    d = fm.get('description', '')
    if not isinstance(d, str) or len(d) < 25: continue
    d = re.sub(r'\s+', ' ', d).strip()
    if d.startswith('#') or d.startswith('Path to the active'):
        continue          # 退化值 → 人工補 frontmatter，不自動改寫
    p = re.sub(r'\s+', ' ', purpose).strip()
    if d[:60] != p[:60]:
        mism.append((path, p, d))
```

**修復**：以 frontmatter 為準重寫 purpose cell（**合併優於追加**，不要新增第二列）。
改寫後口徑不變（760），8 個 section header 全對，`skill-index-check.py` 仍 `✓ ALL CLEAN`。

**預防**：
1. `skill-index-check.py` 的「✓ ALL CLEAN」**只代表結構一致**，不代表內容正確——
   每次同步都要獨立跑一次語意比對
2. purpose cell 若等於 `# ...` 開頭 → 是 Pattern OOO-2（frontmatter 缺 fence）的 downstream 症狀，
   要回去補 frontmatter，不是改 index
3. 改寫 purpose cell 必須保留 `|` 的跳脫（`\|`），且不能動到 name / path / api_key 三欄

## 附：2026-10-23 第三 run 新增參考

- **[references/skill-index-2026-10-23c-session.md](references/skill-index-2026-10-23c-session.md)** — Pattern QQ 新增（Purpose cell 三型腐蝕：backslash / placeholder / literal-newline）；checker 漏判單一反斜線 bug 已修（`_split_row()` 用 `re.split(r'(?<!\\)\|')`）；70 個 degraded purpose cell 已從 frontmatter 修復

## Pattern RR（2026-10-23 第四 run 初發現）：Bulk rewrite 掉 frontmatter key 首字元

**發現**：Vault working tree 有 2,672 檔未 commit 的批次修改（tag 小寫化 + quote 正規化 +
wikilink 路徑更新），其中 **655 檔的 YAML frontmatter key 被掉了第一個字元**：
`sources:`→`ources:`、`type:`→`ype:`、`status:`→`tatus:`、`score:`→`core:`、
`date:`→`ate:`、`rating:`→`ating:`、`created:`→`reated:`、`source:`→`ource:`、
`category:`→`ategory:`、`categories:`→`ategories:`、`classification_path:`、
`related_to:`。

**為什麼舊檢查抓不到**：
1. `git diff` 顯示為 `-sources:` / `+ources:` — 看似兩行合理變更，不會意識到「掉字元」
2. **YAML 解析不會報錯** — `ources:` 是合法 YAML key，只是名稱錯了
3. `file` / grep / 相對時間檢查全部無效

**偵測法**（可靠）：比對 HEAD 與 working tree 的 frontmatter **key 序列**。
若 `len(ko) == len(kn)` 且存在 `kn[i] == ko[i][1:]` → 首字元遺失。
位置對齊（zip）僅在 key 序列長度相同時安全。

**修復**：只補 key 名首字元，**不動 value**（value 的變化如 tag 小寫化是預期變更）。

**驗證（必做兩次量測）**：
| 檢查 | 修復前 | 修復後 |
|---|---|---|
| frontmatter key mismatch | 655 檔 | 0 |
| YAML invalid 檔數 | 1,024 | 1,024（相等 → 既有問題，非本次引入） |

**關鍵**：修復前後**都要量一次 YAML invalid 數**。只檢查「修復後是否 0 invalid」會誤判——
本次 Vault 既有 1,024 檔 YAML 本來就 invalid（value 內含未引號 `:` 等），與批次改寫無關。

**預防**：
- 批次重寫 frontmatter 優先用「解析 → 改 value → 重新序列化」，不要 regex 取代整行
- 批次改寫後必須驗證 key 名逐檔比對 HEAD
- 批次改寫後跑 YAML 解析，並**同時**比對修復前後 invalid 數以區分既有問題

**詳見 [references/skill-index-2026-10-23d-session.md](references/skill-index-2026-10-23d-session.md)**

## 附：2026-10-23 第四 run 新增參考

- **[references/skill-index-2026-10-23d-session.md](references/skill-index-2026-10-23d-session.md)** — Pattern RR 新增（bulk rewrite 掉 frontmatter key 首字元，655 檔已修復）；LLM-Wiki-Index.md merge conflict 處置（root-relative vs file-relative，以主流慣例為準）；Vault 1,024 檔既有 YAML invalid 問題記錄待處理

## Pattern SS（2026-10-23 第五 run 初發現）：批次改寫用文字模式會吃掉 CRLF 行尾

**觀察**：對 Vault 10 檔 x-note 做 regex 批次改寫（`[[待補充]]` → `待補充`）後，
`git diff --stat` 顯示**每檔 142–224 行全變**，而非預期的 1 行。

**根因**：Python `open(p, encoding='utf-8').read()` 走 **universal newlines**——
讀入時把 `\r\n` 正規化成 `\n`，寫出時用 `\n`。
**CRLF 檔案的行尾被無聲改成 LF**，整檔在 git 眼中全變。
Vault 內 x-note 多為 CRLF（Windows 來源），每次批次改寫都會踩到。

**修復**：改用 **binary 模式**做 regex 替換，不經過 newline 正規化：

```python
import re, subprocess
out = subprocess.run(['git','grep','-z','-l','-E',r'\[\[待補充','--','*.md'],
                     capture_output=True)
files = [f for f in out.stdout.decode('utf-8').split('\0') if f]
pat = re.compile(r'\[\[(待補充(?::[^\]]*)?)\]\]'.encode('utf-8'))
for f in files:
    b = open(f, 'rb').read()
    nb = pat.sub(lambda m: m.group(1), b)   # bytes pattern
    if nb != b:
        open(f, 'wb').write(nb)
```

**驗證**：修復前 890 insertions / 890 deletions → 修復後 10 / 10 ✅

**預防**：
1. **Vault 內批次改寫一律用 binary 模式**（`rb`/`wb`），不要用文字模式
2. 改寫後**立刻看 `git diff --stat` 的行數**——遠超預期就是行尾被吃掉
3. 已誤改且無其他變更 → `git checkout -- .` 後用 binary 模式重做

> ⚠️ 與 Pattern RR 同屬「批次改寫靜默破壞」家族，但成因不同：
> RR 是 regex 本身吃掉字元，本 Pattern 是 I/O 層的 newline 正規化。

## Pattern TT（2026-10-23 第五 run 初發現）：wikilink checker 的 basename 比對 bug — 假斷鏈 22,418

**觀察**：`check_wikilinks.py` 回報 **22,418 個斷鏈目標**，
包含 `[[AI agents]]`、`[[Claude Code]]`、`[[OpenAI]]` 等**確實存在**的筆記。

**根因（三個缺陷疊加）**：

1. **basename 集合比對失敗**（主因）
   ```python
   base_lower = {p.rsplit("/", 1)[-1].lower() for p in paths}   # {"ai agents.md", ...} 帶副檔名
   ...
   base = target.rsplit("/", 1)[-1]
   if base.endswith(".md"): base = base[:-3]                     # "ai agents" 已剝副檔名
   ok = base.lower() in base_lower                               # → 永遠 False
   ```
   集合存「帶副檔名」形式，比對時卻用「去副檔名」形式 → **所有短名 wikilink 全被誤判**。
   修法：集合同時收 stem 與含副檔名兩種形式。

2. **範本佔位符被當成真連結**：`note-name`（x-note 改寫範本的格式說明，LLM 照抄進正文）、
   `...`、`topic:*`、`待補充` / `TODO` / `TBD`。修法：新增 `is_placeholder()` 排除。

3. **目錄型連結未解析**：`[[00-Inbox/]]`（Obsidian 允許連資料夾）與 `[[00-Inbox]]`
   （解析到該目錄 `index.md`）。修法：加入目錄前綴比對 + `<dir>/index.md` 比對。

**效果**：22,418 → 17,302（basename 修正）→ **17,288**（+ placeholder + 目錄連結）。
剩餘為真實斷鏈（多為 archive 舊連結），屬既有積壓，非本次引入。

**預防**：任何「集合比對 basename」的程式，**建集合與比對時的 key 形式必須一致**。
自我檢查：故意挑一個確定存在的短名筆記，跑 checker 看是否被報成斷鏈。

## Pattern UU（2026-10-23 第五 run 初發現）：repo 根 scripts/ 與 skill 內 scripts/ 重複實作

**發現**：`~/Documents/Agent/scripts/check_wikilinks.py` 與
`~/Documents/Agent/skills/x-agent/scripts/check_wikilinks.py` 是同名不同實作，
兩者都被 git 追蹤，且 grep 不到任何文件引用——只能靠人肉記憶知道該跑哪個。

**處置**：repo 根版本改為薄 wrapper，轉呼叫 canonical
（`sys.path.insert` + `import check_wikilinks`），消除雙軌漂移。

**預防**：
- 新增工具腳本時，**canonical 放在 `skills/<name>/scripts/`**，
  repo 根 `scripts/` 只放 wrapper 或不放
- 定期 `grep -rn "<script-name>"` 確認有文件指向 canonical

## 附：2026-10-23 第五 run 新增參考

- **[references/skill-index-2026-10-23e-session.md](references/skill-index-2026-10-23e-session.md)** — Pattern SS 新增（文字模式批次改寫吃掉 CRLF 行尾，890→10 diff）；Pattern TT 新增（wikilink checker basename 比對 bug，假斷鏈 22,418→17,288）；Pattern UU 新增（repo 根 scripts/ 重複實作改 wrapper）；upstream force-push sanitized 版本的 merge conflict 判斷準則（採 theirs）；Vault 剩餘 17,264 條真實斷鏈待裁決

## 附：2026-10-24 第七 run 新增參考

- **[references/skill-index-2026-10-24a-session.md](references/skill-index-2026-10-24a-session.md)** — Pattern WW 新增（origin/main 與 local 的 88/88 分歧其實是 upstream sanitized rewrite，判定準則：訊息相同 + tree 不同 → 衝突採 theirs，不可 reset）；Pattern XX 新增（upstream 的 security fix 只存在於 remote，本地 merge 後才補上；本地所有 commit 的 tree 都含硬編碼 key → 絕不可 force-push）；Pattern YY 新增（sanitize 移除「本機絕對路徑」時會讓 sanitized 版在來源機以外不可用，補回 `os.path.expanduser()` 相對路徑）；Pattern ZZ 新增（程式讀 `.env` 但 `.gitignore` 未忽略 `.env`）；Vault 423 檔 `<think>` 殘留機械式清理完成（YAML/mojibake/frontmatter 全部 0 regression）

## 附：2026-10-24 第八 run 新增參考

- **[references/skill-index-2026-10-24b-session.md](references/skill-index-2026-10-24b-session.md)** — Pattern AAA 新增（雙軌差距同時出現在「檔案」與「索引行」兩層：`sync-check.py` 只比檔案存在性，`SKILL.md` 內容需獨立 diff；restore 時必須兩層一起做，否則 workspace 出現 dead link）；Pattern AAAA 新增（Agent repo ahead N commits 不一定是待清理積壓——若 local-only commits 的 tree 含 live API key，即使 fast-forward 也**不可 push**；取 key 必須 `grep -m1` + 去引號，否則 `.env` 兩行串接成 251 字元雜訊使 `-S` 搜尋失真）


- **[references/skill-index-2026-10-24e-session.md](references/skill-index-2026-10-24e-session.md)** — Pattern GGG 新增（口徑 count regex 只認小寫開頭的 row，10 個大寫開頭的 skill 被漏算：749 vs 759）；Pattern HHH 新增（canonical skill 內 macOS 絕對路徑在 Linux 機器上失效，改用 ~ + os.path.expanduser()）；Vault 落後 10 commits 已 pull 同步；直接反應其實施檔案選成 UTF-8
## 附：2026-10-24 第十 run 新增參考

- **[references/skill-index-2026-10-24d-session.md](references/skill-index-2026-10-24d-session.md)** — Pattern EEE 新增（dangling **tree** 可用 `git reflog expire --expire=now --all && git gc --prune=now` 完全清除，不需要 `--aggressive`；過去多次記為「無害殘留」是錯過，`git fsck --full` 驗證須完全無輸出）；附帶修正 live key 傳播範圍的過度概括（只有 3 個 ancestor commit 含 key，HEAD tree 不含，量詞須用實測數字）

## 附：2026-10-24 第九 run 新增參考

- **[references/skill-index-2026-10-24c-session.md](references/skill-index-2026-10-24c-session.md)** — Pattern BBB 新增（skill 名稱在「同名但內容分歧」時會被 loader 判定 ambiguous 並在 cron 預載入時被 skip，`provably_same_skill()` 需所有候選 sha256 完全相同；`~/.hermes/skills/` 內部的 category 雙軌不在 `sync-check.py` 覆蓋範圍，必須以 `resolve_skill_catalog()` 掃描）；Pattern CCC 新增（`git fsck --unreachable` 的「無法取得」是 dangling tree 的子物件已被 gc 的正常後果，非 repo 損毀；判定要用 `git fsck` exit code + `cat-file` 交叉驗證）；Pattern DDD 新增（scratch 目錄裡的 linked worktree 持有過期實驗分支，比對「獨有檔案」必須用 blob hash 而非路徑 basename，否則把「改寫前舊版」誤判為資料遺失）

## Pattern EEE（2026-10-24 初發現）：dangling tree 可以清掉——過去多次記為「無害殘留」是錯過

**觀察**：2026-10-24a/b/c 三次 session 都把 Vault 的 4 個 dangling **tree** 記為
「無害殘留，不處理」。本次實測發現**可以完全清掉**：

```bash
cd ~/Documents/Pigo_Obsidian
git reflog expire --expire=now --all
git gc --prune=now          # ← 不需要 --aggressive
git fsck --full             # → 完全無輸出
git count-objects -v        # → count: 0, size: 0
```

**為什麼過去判定「清不掉」**：`references/dangling-objects.md` 的歷史觀察只涵蓋
**dangling commit**，並記錄「`git gc` aggressive=0 無法清除，必須搭配 reflog expire」。
但 **dangling tree** 是另一類物件——它是某個被 gc 掉的 commit/tree 的殘留容器，
其子 blob 早已不可達。`reflog expire` 清掉 reflog 對這些 tree 的引用後，
普通 `gc --prune=now` 就能回收。

**成本**：`scripts/git-dangling-cleanup.sh` 內建 `--aggressive`，對 1.1G repo 會做完整
repack（數分鐘、大量 I/O）。日常 housekeeping 用 `reflog expire + gc --prune=now` 已足夠；
`--aggressive` 只留給「發布乾淨 tarball / docker image」等一次性場景。

**預防**：Phase 1 報「N 個 dangling tree」時，應實際跑一次清理並用 `git fsck --full`
驗證（期望完全無輸出），而不是直接歸類為「無害殘留」留到下個 session。
詳見 `references/skill-index-2026-10-24d-session.md`。

## Pattern FFF（2026-10-24 初發現）：安全斷言的量詞必須用實測數字，不可過度概括

**觀察**：2026-10-24b 寫入 P0-core.md 的斷言是「89 個 local-only commits **全部**含
硬編碼 live API key」。本次逐 commit 掃描（`git grep -l -F <key> <commit>` 跑遍全部 92 個
ahead commit）後的**實際**結果是：

- 只有 **3 個** commit 的 tree 含 key：`b861b654`、`9477a6ae`、`18eb1284`
- **HEAD 的 tree 本身不含 key**（`git grep -F <key> HEAD` = 0 命中）
- 這 3 個 commit 是 local-only 分支的 **ancestor** → `git push`（即使 fast-forward）
  仍會把帶 key 的 blob 物件一併上傳 → **「不可 push」結論不變**

**為什麼這是問題**：過度概括會讓後人誤判風險範圍，也會讓清理方案選錯
（以為要處理 92 個 commit，實際只有 3 個）。

**預防**：
1. 寫「N 個 X 全部含 Y」之前，先逐個掃描取證
2. 同時驗證**當前 tree**（`git grep <pattern> HEAD`）與**歷史**（`git log -S<pattern>`）——
   兩者結論可能相反（tree 已清理但 ancestor 還帶著）
3. remote 端用 `git ls-remote --refs origin` 列出全部 refs 逐個掃描，不只掃 main

## Pattern GGG（2026-10-24 第十一 run 初發現）：口徑 count regex 只認小寫開頭的 row — 大寫開頭的 skill 全部被漏算

**觀察**：`skill-index-check.py` 回報 `✓ ALL CLEAN`（759 = header = 8 sections），
但用 SKILL.md 自己記載的「三口徑驗證命令」獨立重跑，卻得到 **749 actual**，
差 header 759 整整 **10 個**。

**根因**：SKILL.md 正文（Pattern OO / Pattern NN 兩節）記載的驗證 regex 是
`re.match(r'^\| [a-z0-9]', l)` — 只匹配**小寫字母或數字**開頭的 row。
但 Skill_Index.md 有 10 個 row 的 skill 名稱以**大寫字母**開頭：

```
| Skill-Develop | ... | | Remotion | ... | | Scholar Evaluation | ...
| Slide Deck (幻燈片簡報) | ... | | X-note | ... | | AutoIt v3 | ...
| Paper-Read | ... | | GordenImage2PPTX | ... | | GordenImagePPTGen | ...
| GordenSuperPPTSkill | ... |
```

**為什麼 script 沒抓到**：`scripts/skill-index-check.py` 用的是
`^\| [^|]+\| [^\s|]+\.md\s+\|`（不限定首字元），所以它算 759 是**正確**的。
壞掉的是 **SKILL.md 正文記載的驗證命令**，不是 script。兩邊口徑不一致 → 任何
未來照著 SKILL.md 跑「獨立驗證」的人，都會得到 749 ≠ 759 的假 drift，
然後可能「修壞」一個其實乾淨的 index。

**修復**（2026-10-24）：
- SKILL.md 內所有 `^\| [a-z]` / `^\| [a-z0-9]` 的驗證 regex 改為 `^\| [A-Za-z0-9]`
- 同步檢查 `references/skill-index-verification.md`、
  `references/skill-index-corruption-patterns.md`、
  `references/skill-index-false-clean-pattern.md`、
  `references/workspace-snapshot.md`

**預防**：
1. **口徑 count regex 不要用首字元 class 假設**。skill 名稱大小寫不受控
   （使用者自訂名），首字元必須用 `[A-Za-z0-9]` 或 `[^|]`
2. **SKILL.md 記載的驗證命令與 script 的 regex 必須定期對齊**——
   SKILL.md 是給未來 agent 看的「權威口徑」，它錯了比 script 錯更危險
3. 每次獨立驗證時，若 count 與 checker 差一個小數（10/759 ≈ 1.3%），
   先檢查是不是「少數大寫開頭的 row 被漏算」而不是 index 真的 drift

## Pattern IIII（2026-10-24 第十二 run 初發現）：量詞要分「引入點」與「繼承點」——同一個 key 有兩個不同的數字

**觀察**：記憶裡寫「確認含 key 的 3 個 commit」。實測發現這句話**兩個數字都對，但用途不同**，
不區分會導致錯誤的清理範圍估算。

**實測**：
- **3 個 commit「引入」key**（`git log -S<key>`，差異比對）：`b861b654` / `9477a6ae` / `18eb1284`
- **88 個 commit 的 tree「含」key**（`git grep -E 'sk-(cp|CMM)-[A-Za-z0-9_-]{60,}' <commit> --`）

**差異機制**：key 一旦進入某個 commit 的 tree，**所有後續 descendant commit 的 tree 都會繼承它**，
直到某個 commit 把它 sanitize 掉。所以「引入點」數（3）≠「繼承點」數（88）。

**用途對應**：

| 數字 | 意義 | 用途 |
|---|---|---|
| 3 | 污染源頭 | rewrite 時需要重寫的**最小** commit 集合 |
| 88 | 會被 push 出去的**物件範圍** | 決定「push 是否會帶 key 上遠端」 |

**預防**：
1. 寫「N 個 commit 含 X」之前，先問是**引入**（`-S`）還是**包含**（tree 比對）
2. `git grep -E <pattern> <commit> --` 中 **commit 必須放在 `--` 之前**；
   寫成 `git grep -E <pat> -E <commit> --` 會讓第二個 `-E` 把 commit 當成 pattern 吃掉，
   **靜默回傳 0 命中**（本次第一次掃描就栽在這裡，得出「沒有 key」的錯誤結論）
3. 驗證 key 是否 live：比對 `sk-` token 的 sha256 與 `~/.hermes/.env` 生效值

**註**：本次另確認 repo visibility = **PRIVATE**（`gh repo view`）→ 洩漏面僅限協作者。

### Pattern FFF-2（2026-10-27 實測）：安全規則的「結論」會過期——理由失效時禁令也要跟著失效

**背景**：記憶裡寫「remote 全部 9 refs 不含 live key → **禁止 `git push`**（即使 fast-forward）」。
2026-10-26 的 job 已經 push 過一次，**該規則被自己的 push 打破**，但規則文字還留在記憶裡。

**本次實測**：
- `git merge-base --is-ancestor b861b654 origin/main` → exit 0 → **live key 已在遠端歷史**
- key 的 sha256 與 `~/.hermes/.env` 生效值相同；對 MiniMax API 實測 HTTP 200（對照組偽造 key = 401）
- 但 `git rev-list --objects origin/main..HEAD` 的**每一個**新 blob 對 live key regex = 0 命中
  → **現在 push 乾淨的前向 commit 不會擴大接觸面**

**結論**：
- 有效緩解手段 = **旋轉 MiniMax key**（撤銷舊 key），不是 git 歷史 rewrite（後者只清除表面）
- 禁止 push 的**理由**（怕帶 key 上遠端）已失效 → 恢復正常 push 流程（Pattern U：ahead commit 不累積）
- 仍禁止 force-push rewrite（破壞性，需 Pigo 口頭授權）

**預防**：
1. 安全規則要寫「**理由**」而非只有「結論」——理由失效時結論也要跟著失效
2. 否則會留下過期的禁令，讓未來的 agent 拒絕做本來安全的事
3. 每次清理安全記憶時，用**實測**覆寫過期事實（`is-ancestor` / sha256 比對 / API 實測），
   不要只把「未確認」改成「已確認」

## Pattern JJJ（2026-10-24 第十二 run 初發現）：backup script 的自我參照競態——`cp -r` 複製正在被寫入的目錄

**觀察**：Hermes Backup cron 某日輸出出現 `[WARN] 複製失敗: /home/x/.hermes/cron`，
但同一行又印「備份成功」——矛盾訊號。

**根因**：backup script 把 `~/.hermes/cron` 整包納入備份，但 **cron job 自己的執行紀錄
就寫在 `~/.hermes/cron/output/<job_id>/`**。執行 backup 的當下，
該日誌檔正被寫入 → `cp -r` 讀到「檔案大小在讀取期間改變」→ 回傳非 0 → 印 WARN。
**這是 backup 複製自己輸出目錄造成的自我參照競態**，不是權限或磁碟問題。

**實際影響（實測）**：該次 tarball 缺 14 個 cron 檔案（4 個當天 `output/*`、
2 個 `external-workers/*.stderr`、2 個 `admissions/*.json`）；
config.yaml / auth.json / skills / memories / AGENTS.md / kanban.db **完整無缺**。

**修復**：複製步驟從 `cp -r` 改為 `tar` pipe
```bash
tar -cf - -C "$(dirname "$item")" --ignore-failed-read "$(basename "$item")" 2>/dev/null \
    | tar -xf - -C "$BACKUP_DIR" 2>/dev/null
if [ ${PIPESTATUS[0]} -ne 0 ]; then
```
- `--ignore-failed-read`：讀取中變動的檔案只發警告，不中止整個 archive
- **`PIPESTATUS[0]` 取的是左側 tar（producer）**，不是管線最後一段；用 `$?` 會判斷錯對象

**預防**：
1. 任何「把某目錄整包備份」的 script，若該目錄會被執行中的 job 寫入 → 必然自我參照競態
2. 複製目錄用 `tar` pipe 優於 `cp -r`：前者對檔案變動具容錯，後者整個指令失敗
3. 判斷管線成功要看 **producer**（`PIPESTATUS[0]`）

## Pattern KKK（2026-10-24 第十二 run 確認）：Pattern EEE（dangling tree 可清）跨 repo 通用

**觀察**：Agent repo `git fsck --full` 回報 3 個 dangling tree（每個 ~40,000 entry）。

**處置**（與 Vault 完全相同）：
```bash
git reflog expire --expire=now --all
git gc --prune=now      # 不需要 --aggressive
git fsck --full         # → 完全無輸出
git count-objects -v    # → count: 0, size: 0
```
結果：3 個 dangling tree 全清，packs 2 → 1，fsck 全無輸出。

**預防**：Pattern EEE 不只適用於 Vault，**任何 repo 都適用**。
Phase 1/3 報 dangling tree 時應直接實際清理並用 `git fsck --full` 驗證，
不要歸類為「無害殘留」留到下個 session。

## 附：2026-10-24 第十二 run 新增參考

- **[references/skill-index-2026-10-24f-session.md](references/skill-index-2026-10-24f-session.md)** — Pattern IIII 新增（量詞分「引入點」3 vs「繼承點」88；`git grep -E` 重複 `-E` 靜默回傳 0 命中的坑）；Pattern JJJ 新增（backup script 自我參照競態，`cp -r` → `tar` pipe 修復，132/132 全收錄）；Pattern KKK 新增（dangling tree 可清跨 repo 通用，Agent repo 3 個全清）；repo visibility = PRIVATE 確認

## 附：2026-10-24 第十三 run 新增參考

- **[references/skill-index-2026-10-24g-session.md](references/skill-index-2026-10-24g-session.md)** — Pattern MMM 新增（自我修復 loop 只 patch 非 canonical 路徑＝patch 進黑洞；loader 以 `skill_candidate_rank` 淺路徑勝出，「較新」不等於「會被載入」）；Pattern NNN 新增（文件記載的驗證命令必須實際執行過——header regex `\*\*` 抓不到實際的 `***759***` 三星號格式，script 是對的文件是錯的；口徑 count 漏 `'SKILL.md' in l` 造成假 drift 9）；8 檔 17 處殘留 macOS/舊主機絕對路徑修正（含巢狀引號無效 Python 陷阱）；repo 根 `neat-freak/SKILL.md` 確認為正當 sync copy 並同步

## 附：2026-10-27 run 新增參考

- **[references/skill-index-2026-10-27-session.md](references/skill-index-2026-10-27-session.md)** — Pattern OOO-2 新增（SKILL.md **根本沒有** frontmatter fence，`parse_frontmatter` 回傳 `({}, body)` 不拋例外 → 靜默降級而非載入失敗；通用 YAML 掃描報 `list index out of range`）；Pattern LL-2 新增（concurrent cron job 留下**未完成的 rebase**，診斷要看 `.git/rebase-merge/{done,git-rebase-todo,stopped-sha,onto,orig-head}`，append 衝突要合併保留兩側）；Pattern FFF-2 新增（安全規則的結論會過期——理由失效時禁令也要跟著失效；live key 已在 origin/main 歷史 → 有效緩解是旋轉 key，不是 git rewrite）；Pattern QQQ-2 新增（index 漏列來自 weekly update job，`skill-index-check.py` 只驗 index 內部一致性不做磁碟↔index 雙向比對 → 必須獨立做雙向比對）

- **[references/skill-index-2026-10-27b-session.md](references/skill-index-2026-10-27b-session.md)** — **Phase 2 / Phase 3 的「事實來源」方向規則寫反了**：SKILL.md 原本寫死「canonical 為準、單向同步到 workspace」，但 2026-10-27 實測 canonical 與 workspace **輪流出現領先者**（本次 workspace 領先：P0 記憶 6,503 B vs 5,424 B、SKILL.md 2,083 行 vs 1,992 行，`diff | grep -c '^<'` = 0 → workspace 為嚴格超集）→ 照原規則會回退 2026-10-27 的安全修正並刪掉 4 個 Pattern。**新規則：方向由 mtime + 內容 superset 實測決定**（`'<'` = 0 → workspace→canonical；兩側皆 > 0 → 停止覆寫、回報交接）。附帶解掉每小時健康度 job `33f50df6ac6b` 長期紅燈（`sync-check.py` 的 EXTRA 有兩義性：污染 vs workspace 領先，補齊 canonical 後轉 exit 0）。另記：Agent repo `.git` 已 868M，日常 dangling 清理**只用 `reflog expire --expire=now --all` + `git gc --prune=now`**（`--aggressive` 只留給一次性發布場景）

## Pattern SSS（2026-10-28 第十六 run 初發現）：canonical 樹的同名 skill 讓 `skill_view` 完全無法解析

**觀察**：`sync-check.py`、`skill-index-check.py`、frontmatter 掃描全部綠，
但 `skill_view(name='weather')` 回傳 `{"success": false, "error": "Ambiguous skill name..."}`。
canonical 樹 `~/.hermes/skills/` 有 **151 個 name 對應多個目錄**。

**為什麼舊檢查抓不到**：
- `sync-check.py` 只比 canonical ↔ workspace 的 **neat-freak 單一 skill**，不掃整棵樹
- `skill-index-check.py` 只驗 Agent repo 的 `docs/Skill_Index.md`，不碰 canonical 樹
- frontmatter 掃描只驗 YAML 可解析 + `name` 存在 — 重複 name 是**合法 YAML**
- `scan_skill_commands()` 回報 `dups: 0` — 它用 **slash command 名**當 key，
  而 slash command 由目錄 basename 推導，與 frontmatter `name` 不同

**關鍵方法論**：比對「重複」**必須比全部檔案，不能只比 SKILL.md**。
本次先只比 SKILL.md sha256 → 82 個「可刪」候選；
逐檔比對後發現 **45 個候選的其他檔案有內容差異**
（`openclaw-imports/baoyu-cover-image` 有 17 個 reference 檔案與 top-level 版本不同）。
照第一份清單刪會**靜默丟失差異版本**。

**三條件全過才可刪**（loser c、winner w = 最淺路徑）：
1. c 的每個檔案 f 必須在 w 存在（無 only-in-loser）
2. 且 sha256 完全相同（無 content-diff）

**canonical 樹沒有 git** → 刪除不可逆，唯一還原路徑是 `~/Documents/Backup/hermes/` 的 tarball。
刪前必須先做 tarball 備份（用相對路徑 + `-czf`）。

**union 合併陷阱**：合併時若手列檔案清單，會漏掉只存在於 loser 的
`assets/`、`references/` 內的檔（若 SKIP 集合把它們排除在 tree 比對之外）。
→ **用程式枚舉 loser 全部檔案自動搬移**，不要手列。

**「最淺路徑勝出」≠「內容最新」**：loader 的 `skill_candidate_rank` 是路徑深度優先，
但實測 93 個殘餘重複中 **59 個的勝出者 mtime 比 sibling 還舊**。保留哪份不能只看路徑。

**殘餘 88 個「多版本並存」型**（gstack 三軌 / 上游 bundle vs 本地 fork / 備份目錄）
**不能機械式刪**，列為「未處理」待人工裁決。

**預防**：
1. Phase 3 應加「canonical 樹重複 name 掃描」（見 session reference 的完整腳本）
2. `scan_skill_commands()` 的 `dups: 0` **不代表沒有 name 衝突**
3. canonical 樹任何刪除前先備份

## 附：2026-10-28 run 新增參考

- **[references/skill-index-2026-10-28d-session.md](references/skill-index-2026-10-28d-session.md)** — Pattern SSS 新增（canonical 樹 151 個同名 skill 造成 `skill_view` ambiguity；比對必須涵蓋全部檔案不能只比 SKILL.md；78 個 byte-identical 重複已刪、6 個 union 合併、88 個留待裁決；canonical 樹無 git → 刪前必備份）
- **[references/skill-name-collision-false-positive.md](references/skill-name-collision-false-positive.md)** — **跨樹比對的 key 必須是「相對路徑」，絕對不能用 frontmatter `name`**：canonical 技能樹是多軌並存（`weather` 同時存在 `weather/`、`weather/weather/`、`productivity/weather/`），name-based 比對會把不同目錄樹的同名 skill 配成一對並誤覆寫（本次污染 7 個 canonical 檔案，從 backup tarball 還原）。**且 canonical 樹沒有 git** → 覆寫後唯一還原路徑是 `~/Documents/Backup/hermes/` 的 tarball，覆寫前必須先確認備份涵蓋該檔
- **[references/skill-index-2026-10-28-session.md](references/skill-index-2026-10-28-session.md)** — 五 Phase 全綠（Vault audit report commit+push、memory 三檔 byte-identical、三項 checker 全綠、cron output 全 < 500、backup 排程今日已跑）；記錄 name-based 比對事故與回滾流程；`.gitignore` 含 `12-Meta/reports/` 但檔案已被追蹤 → `git add -f` 必要
- **[references/skill-index-2026-10-28c-session.md](references/skill-index-2026-10-28c-session.md)** — 15th run：`Skill_Index.md` 的 **purpose cell 與 frontmatter 敘述語意不同步**（27 個，`skill-index-check.py` 抓不到——它只驗口徑/dangling/三型腐蝕，不驗語意一致性）；canonical `vault-check`/`vault-GPS` 的 Windows vault 路徑遷移至 `~/Documents/Pigo_Obsidian`；`Agents_2.md`/`Agents_3.md` 的 OPENSPEC 陳屍依 Pattern 22 機械式修復

## 附：2026-10-28 第十八 run 新增參考

- **[references/skill-index-2026-10-28e-session.md](references/skill-index-2026-10-28e-session.md)** — Pattern TTT 新增（canonical ↔ workspace 31 個內容分歧檔案，**mtime 不是可靠的同步方向指標**——本次 5 檔方向相反；可靠判定是 superset 測試：canonical 每個非空行都出現在 workspace → workspace 為嚴格超集 → 可安全單向同步；雙向都有獨有內容 → 真分歧需人工裁決。本次僅 2 檔可機械同步，29 檔留待裁決；`Readme.md` 類差異是「Codex 自動生成目錄說明 vs skill 自身說明」用途不同，**不是 drift**，硬同步會破壞語意；`x-note/config_loader.py` 差異是 Windows vs Ubuntu 平台遷移，兩邊都對，不可合併）

## Pattern TTT（2026-10-28 第十八 run 初發現）：內容分歧的同步方向由「superset 測試」決定，不是 mtime

### 觀察

canonical（`~/.hermes/skills/`）與 workspace（`~/Documents/Agent/skills/`）之間
31 個檔案內容不同。`diff -rq` 只告訴你「哪些不同」，**不告訴你該往哪個方向同步**。

mtime 與內容豐富度**方向相反**的有 5 檔（`x-note/bin/config_loader.py` canonical 新但 workspace 較完整；
`Article-writer/references/*.md` workspace 新但 canonical 較完整）→ mtime 不可信（與 Pattern SSS 一致）。

### 可靠判定法（superset 測試）

```python
cl = [l for l in canon_text.splitlines() if l.strip()]
wl = set(l for l in ws_text.splitlines() if l.strip())
is_superset = all(l in wl for l in cl)
```

- `is_superset == True` → workspace 是 canonical 的嚴格超集 → **可安全單向同步 workspace→canonical**
- 兩方向都 False → **真分歧**（兩邊各有獨有內容）→ **不可自動同步**，留待人工裁決

### 同步前的強制前置

canonical 樹**沒有 git** → 覆寫不可逆（P0 硬規則 1）：
1. `tar -tzf ~/Documents/Backup/hermes/<最新>.tar.gz ./skills/<path>` 確認備份涵蓋該檔
2. `grep -E "sk-[A-Za-z0-9_-]{20,}"` 掃描無憑證外洩
3. 同步後 `cmp` 驗證 byte-identical

### 預防

1. 「兩棵樹有差異」不等於「該同步」——先問方向，再問能不能機械處理
2. `Readme.md` 差異多半是**用途不同**（自動生成的目錄說明 vs skill 自身說明），不是 drift
3. 平台遷移（Windows↔Ubuntu）造成的差異是「兩邊都對」，不是版本落後

## Pattern WWW（2026-10-29 第二十 run 新發現）：backup script 遺漏所有 `.env` 憑證檔 — 備份範圍要從「憑證實際存放位置」反推

**觀察**：`~/.hermes/scripts/hermes-backup.sh` 的 `ITEMS` 陣列備份了 `config.yaml`、`auth.json`、
`credentials/`，但**沒有備份任何 `.env`**。而 `config.yaml` 裡 provider 宣告 `key_env: MINIMAX_API_KEY`
—— 那指的是**環境變數名**，環境變數的**實際值來源**是 `~/.hermes/profiles/analysis/.env`。
備份了 config 卻沒備份 .env = **還原後 Telegram bot 完全失效、minimax/strata provider 拿不到 key**。

**為什麼舊檢查抓不到**：`tar -tzf` 抽查只問「關鍵檔案在不在」→ `config.yaml` 在就回報 ✅；
`references/hermes-backup-protocol.md` 的「備份範圍」表格**照抄腳本的 ITEMS**，
文件與腳本一致，但**都錯**（Pattern LLL 家族：文件描述的是一套合理但從未實作的流程）。

**修復**（三個 .env 全部補入）：
- `ITEMS` 加 `"$HOME/.hermes/.env"`
- profile 內的 `.env` 走新的 `EXTRA_ITEMS` 迴圈，**保留相對路徑**

**關鍵陷阱 — 多個同名 `.env` 會互相覆蓋**：複製邏輯是
`tar -C "$(dirname "$item")" "$(basename "$item")"` → **只取 basename 平鋪到 backup 根**。
若把兩個 `profiles/*/.env` 直接塞進 `ITEMS`，兩者都會被寫成 `$BACKUP_DIR/.env` → 後者覆蓋前者 → 只留一份 key。
必須另走保留相對路徑的路徑：

```bash
EXTRA_ITEMS=(
    "$HOME/.hermes/profiles/analysis/.env::profiles/analysis/.env"
    "$HOME/.hermes/profiles/strata/.env::profiles/strata/.env"
    "$HOME/Documents/.env::Documents/.env"
)
for entry in "${EXTRA_ITEMS[@]}"; do
    src="${entry%%::*}"; rel="${entry##*::}"
    if [ -e "$src" ]; then
        mkdir -p "$BACKUP_DIR/$(dirname "$rel")"
        tar -cf - -C "$(dirname "$src")" --ignore-failed-read "$(basename "$src")" 2>/dev/null \
            | tar -xf - -C "$BACKUP_DIR/$(dirname "$rel")" 2>/dev/null
        if [ ${PIPESTATUS[0]} -ne 0 ]; then
            echo "[WARN] 複製失敗: $src"; FAILED=1
        fi
    fi
done
```

**憑證檔不只在 `~/.hermes/`**：第二 run 追查時發現 `~/Documents/.env`（skills / shell script
實際使用的憑證來源，含 `MINIMAX_API_KEY` / `STRATA_API_KEY` / `GITHUB_TOKEN` / `HF_TOKEN` /
`BRAVE_API_KEY` / `TWITTER_AUTH_TOKEN` / `OPENROUTER_API_KEY` 等）**位於 `.hermes` 之外**，
同樣沒被備份。→ `EXTRA_ITEMS` 的 `src::rel` 格式就是為了同時處理「同名不同路徑」與
「來源在 tree 外」兩種情況。

**預防**：
1. 備份清單要從「憑證實際存放位置」反推，不能只看 config 宣告
2. tar 平鋪 basename 的副作用：任何同名的第二層檔案都會覆蓋第一層
3. 備份腳本改動後**立刻手動重跑 + `tar -tzf` 抽查**，不要等隔天 cron
4. 兩套 backup 策略（Hermes 內建 `hermes_cli/backup.py` 把 `.env` 列為刻意排除的 secret
   vs 自製 `hermes-backup.sh`）不一致時，以自製腳本為準並同步更新 protocol 文件

詳見 [references/skill-index-2026-10-29b-session.md](references/skill-index-2026-10-29b-session.md)

## 附：2026-10-29 第二十 run 新增參考

- **[references/skill-index-2026-10-29b-session.md](references/skill-index-2026-10-29b-session.md)** — Pattern WWW 新增（backup script 遺漏全部三個 `.env` 憑證檔；tar 平鋪 basename 導致同名 `.env` 互相覆蓋 → 需 `EXTRA_ITEMS` 保留相對路徑）；repo 根 `neat-freak/SKILL.md` **第二次**因 `sync-check.py` 不涵蓋 repo 根副本而落後 canonical（superset 測試判定 canonical 為嚴格超集 → 單向同步安全）；canonical 樹同名群組 SAFE-to-delete = **0**（Pattern VVV 復現：可安全刪數很小是常態）；29 檔 canonical↔workspace 真分歧狀態未變（平台遷移 / 用途不同，非 drift）

## Pattern UUU（2026-10-29 第十九 run 初發現）：工作樹批次改寫要先量測「修復 vs 污染」再 commit

**觀察**：Vault working tree 有 60 檔 uncommitted 修改。照 Phase 1 指示直接 `git add -A` + commit，
就是**未經驗證就接受上游的批次改寫**——這正是 Pattern RR（批次改寫掉 frontmatter key 首字元）的入口。

**正確做法**：commit 前做**修復前後對照量測**（Pattern RR 的預防手段）：

```python
def parse(text):
    lines = text.split('\n')
    if not lines or lines[0].strip() != '---': return None, 'NOFENCE'
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            try: return yaml.safe_load('\n'.join(lines[1:i])), None
            except Exception as e: return None, str(e)[:90]
    return None, 'NOCLOSE'

# 對每個 changed file：解析 worktree 版本 + `git show HEAD:<file>` 版本
# → FIXED（HEAD invalid → worktree valid）/ REGRESSED / UNCHANGED
```

實測：**head invalid = 60、worktree invalid = 0、regressions = 0** → 判定為上游
quote-fixer 的修復成果，可安全 commit。

**預防**：Phase 1 的「若有 uncommitted 則 commit」必須加一道前置量測。
批次改寫檔案數越大，越要先確認它是修復還是破壞；量測成本（數秒）遠低於事後回滾成本。

## Pattern VVV（2026-10-29 第十九 run 初發現）：canonical 樹同名重複——「只有 1 個可安全刪」是常態

**觀察**：canonical 樹（`~/.hermes/skills/`，排除 `.archive/` 與巢狀 `.hermes/skills/`）有
**803 個 name、93 個 name 對應多個目錄**。套用 Pattern SSS 三條件安全刪除檢查後：

- **SAFE-to-delete：只有 1 個**（`yao-tutorial-skill/yao-tutorial-skill`，3 檔 byte-identical）
- **UNSAFE：138 個**

逐一檢查後發現三種「不可刪」型態，多半其實是**兩邊都對**的並行版本：

1. **巢狀自我複本**（`weather/weather`、`mail-triage/mail-triage`）— 只有 SKILL.md 不同。
   `mail-triage/mail-triage` 是 2026-04-29 dedupe 後的 canonical 英文版，
   外層 `mail-triage/` 是後來重寫的中文詳細版（含 vault 路徑已遷 `~/Documents/Pigo_Obsidian`）
   → **刪任一邊都會丟失資訊**
2. **category 化 richer 副本**（`productivity/pdf` 21 個 unique 檔、`productivity/docx` 12 個）
3. **上游 bundle vs 本地 fork**（`openclaw-imports/*` vs top-level）

**預防**：

1. 跑「canonical 樹重複 name 掃描」時，**預期「可安全刪除數」會很小**。
   若算出 90+ 可刪，先懷疑比對邏輯錯了（應比對**全部檔案**而非只有 SKILL.md）
2. canonical 樹無 git → 刪前必須備份覆蓋
3. 刪除收益應以「`skill_view` 由 ambiguous 轉 success」衡量，而非刪除數量

## 附：2026-10-29 第二十一 run 新增參考

- **[references/skill-index-2026-10-29c-session.md](references/skill-index-2026-10-29c-session.md)** — Pattern XXX 新增（checker 只驗「被驗的那幾項」：Summary 分解 subtotal 不在覆蓋範圍，32+193+534=759≠760）；Pattern YYY 新增（跨文件口徑矛盾無標明：Skill_Category 581 是 dated snapshot，live census 是 Skill_Index 的 760）；Pattern ZZZ 新增（heading-based 區塊切片沒排除 code fence 內 heading → 刪掉 1455 行，已從 workspace copy 還原）；checker 加 check [6] API-key breakdown、[7] Skill_Category table self-consistency（皆以負向測試驗證）

## 附：2026-10-29 第十九 run 新增參考

- **[references/skill-index-2026-10-29-session.md](references/skill-index-2026-10-29-session.md)** — Pattern UUU 新增（**工作樹批次改寫要先量測「修復 vs 污染」再 commit**：60 檔 HEAD 全部 YAML invalid → worktree 全部 valid、0 regression → 判定為上游 quote-fixer 成果才可 commit）；Pattern VVV 新增（canonical 樹 93 個同名群組，套用三條件安全刪除後**只有 1 個可安全刪**，其餘多為「兩邊都對」的並行版本——巢狀自我複本 `X/X`、category 化 richer 副本 `productivity/pdf`（21 unique 檔）、上游 bundle vs 本地 fork；**可安全刪除數很小是常態**，算出 90+ 先懷疑比對邏輯只比了 SKILL.md）

## 附：2026-10-26 run 新增參考

- **[references/skill-index-2026-10-26-session.md](references/skill-index-2026-10-26-session.md)** — Pattern OOO 新增（YAML frontmatter 內混入 Markdown 指令 → Hermes loader 整個跳過該 skill；13 檔 canonical + 5 檔 workspace；必須用 `agent.skill_utils.parse_frontmatter` / `agent.skill_commands.scan_skill_commands` 驗證，通用 YAML 解析通過不等於能被載入）；Pattern PPP 新增（canonical 與 workspace 是兩份獨立內容，frontmatter 損壞各修各的；批次改寫 frontmatter 一律用 `bytes.replace()` 精確取代，**不要用「切出→修→拼回」重建**，會吃掉 fence 後的空行）；Pattern QQQ 新增（磁碟 1,209 vs index 759 的差額 = 414 個 `*_revived` 歷史復原 + 36 個 `*.bak`/fixtures → 759 才是正確口徑，不是 drift）；`ftfy badness > 0` 對中英混排標點是假陽性，判斷真 mojibake 必須用 `fix_encoding()`（`fix_text()` 會做全形標點轉換，那是副作用）

## Pattern OOO（2026-10-26 初發現）：YAML frontmatter 內混入 Markdown 指令 → Hermes loader 整個跳過該 skill

**觀察**：canonical `~/.hermes/skills/` 有 13 個 `SKILL.md` 的 YAML frontmatter 無效。
被塞在 `---` fence **之間**的 `**重要：所有輸出內容必須使用繁體中文。**`
讓 YAML parser 看到 `key: **重要...**` → 語法錯誤 → `parse_frontmatter` 失敗 →
loader 記 `Skipping invalid skill` → 該 skill 從未進入 command catalog。

**為什麼舊檢查抓不到**：
- `skill-index-check.py` 只掃 `~/Documents/Agent/docs/Skill_Index.md`，不碰 canonical skill 檔
- `sync-check.py` 只比 canonical vs workspace 的**目錄結構**，不比 frontmatter
- 檔案在磁碟上存在、內容完整，只是 YAML 解析失敗 → 沒有任何「檔案遺失」訊號

**修復**：binary 模式（Pattern SS）把注入的 Markdown 指令**移到 fence 之外的 body**
（不可刪除：會改變 skill 行為），順帶修 trailing comma 與巢狀 key 縮排。

**驗證（通用 YAML 解析不足夠）**：
```python
import sys; sys.path.insert(0, '/home/x/.local/share/uv/tools/hermes-agent/lib/python3.12/site-packages')
from agent.skill_utils import parse_frontmatter
from agent.skill_commands import scan_skill_commands
```
`parse_frontmatter` 全部回傳合法 metadata + `scan_skill_commands()` 能發現 12 個 active skill
（`.archive/` 底下的正確被排除）。

**預防**：
1. frontmatter 掃描必須**同時覆蓋 canonical skill 樹**（`~/.hermes/skills/**/SKILL.md`）與 workspace
2. 通用 YAML 解析通過 **≠** Hermes 能載入 → 必須用 Hermes 自己的 parser 驗證
3. 任何「在 frontmatter 裡加一句話」的動作都要用 binary 模式，加完立刻跑 `parse_frontmatter`
4. `.archive/` 底下的 skill 也要修 YAML（只是不進 active command catalog）

### Pattern OOO-2（2026-10-27 初發現）：SKILL.md **根本沒有** frontmatter fence ≠ frontmatter 損壞

**觀察**：4 檔 `SKILL.md` 開頭直接是 `# Title`，**沒有 `---` fence**（Pattern OOO 是 fence 內混入指令，
型態不同，處置也不同）。症狀：通用 YAML 掃描報 `list index out of range`
（`raw.split(b'---',2)[1]` 找不到第 2 個 fence）。

**為什麼舊檢查抓不到**：`parse_frontmatter()` **不會拋例外**，回傳 `({}, body)` → `name=None`。
Hermes loader fallback：`name = frontmatter.get('name', skill_md.parent.name)` → **skill 仍可載入**
（用目錄名當 name），`description` 從 body 第一個非 `#` 開頭行抓。
→ 這是**靜默降級**，只看 `scan_skill_commands()` 會誤判為正常。

**downstream 症狀**：Skill_Index.md 的 purpose cell 變成 `# Skill Definition: Academic-Omni-Router`
這類髒資料（本次 `learning-personas/Paper-Read` 即如此）。

**修復**：在檔案開頭 **bytes 前插** frontmatter（不動 body 其餘位元組）。
**驗證**：通用 YAML 掃描 4 → 0 invalid；`parse_frontmatter()` 回傳正確 name/description。

**預防**：
1. YAML 掃描遇到 `list index out of range` → 是**根本沒有 fence**，不是 fence 內混入指令
2. 檢查 SKILL.md 品質要看 `parse_frontmatter(...).get('name')` 是否為 None，
   不能只看 `scan_skill_commands()` 有沒有註冊該 command
3. Skill_Index.md 的 purpose cell 若等於 `# ...` 開頭 → 是這個問題的 downstream 症狀

## Pattern PPP（2026-10-26 初發現）：canonical 與 workspace 各有各的 frontmatter 損壞 — 兩邊都要掃

**觀察**：修完 canonical 13 檔後，掃 workspace（1,209 檔）又發現 **5 檔**獨有的無效
frontmatter（`learning-recap-to-x` ×2 巢狀 key 縮排、`hv-analysis` list 缺 `- ` marker、
`xiaocui-skill` 引號內尾隨散文、`guizang-material-illustration_revived` 未加引號含 `: `），
canonical 沒這問題。

**為什麼重要**：canonical 與 workspace 是**兩份獨立內容**，修一邊不等於修好另一邊。
「同步」是流程，不是保證。

**陷阱 — 重寫 frontmatter 會吃掉 fence 後的空白行**：
用 `raw[start:idx] + b'\n---' + body` 重建時，若 body 開頭原本是 `\n`，
會變成 `---\n# Title`（少一個空行）→ diff 雜訊。
**修復方式：不要重建**，改用**精確 bytes 取代**（`raw.replace(old, new, 1)`），
其他位元組完全不動，diff 最小。

## Pattern QQQ（2026-10-26 實測確認）：「磁碟比 index 多」不自動等於 drift — 先分類差額

本次獨立掃描：磁碟 1,209 / index 759，差額 450 = **414 個 `*_revived/`**（上游 sync 復原的
歷史版 skill，canonical 樹完全沒有 `_revived` 目錄）+ **36 個 `gstack.v1.1.0.bak/` 與
`test/fixtures/`**。→ **index 的 759 是正確口徑**，不是落後。

**教訓**：把差額按**目錄性質**分類（現行 / 歷史復原 / 備份 / 測試 fixture）後再判斷。
若直接「重建 index 把 1,209 全部列進去」，會把 414 個歷史版 skill 誤標為 active。

### Pattern QQQ-2（2026-10-27 實測）：index 漏列的 skill 來自 weekly update job，`skill-index-check.py` 抓不到

**觀察**：`skills/agent-workflows/superpowers/diagnosing-superpowers/` 由 weekly update job
（`14592b91 chore(skills): superpowers refresh 2026-10-26`）加入磁碟，但 Skill_Index.md 沒收錄
→ 磁碟 760 / index 759。

**為什麼舊檢查抓不到**：`skill-index-check.py` 只驗 **index 內部一致性**
（Summary / per-section / dangling / purpose cell），**不做「磁碟 vs index」雙向比對**。
少一筆時 header 也一致 → 回報 `✓ ALL CLEAN`。

**預防**：獨立驗證腳本必須做雙向比對：
```python
listed = set(re.findall(r'^\| [A-Za-z0-9].*?\|\s*(skills/[^\s|]*SKILL\.md)\s*\|', idx, re.M))
disk   = {磁碟掃描結果，排除 _dead-skills / *_revived / *.bak / test fixtures}
assert listed == disk   # 少一筆或多一筆都要抓
```
修復順序（Pattern NN）：補 row → per-section header → Summary → Category Map。

## Pattern MMM（2026-10-24 第十三 run 初發現）：自我修復 loop 只 patch 非 canonical 路徑＝patch 進黑洞

**觀察**：`~/.hermes/skills/` 下存在兩個 `neat-freak`：

```
~/.hermes/skills/neat-freak/                 ← canonical（loader 實際載入這個）
~/.hermes/skills/productivity/neat-freak/    ← 較舊的結構化副本
```

`SKILL.md` sha256 完全相同、`scripts/` 與 `agents/` 也完全一致，
**但 `references/` 有 2 個檔案分歧**（`cron-output-retention.md`、`hermes-backup-protocol.md`）。

**根因**：journal 顯示某次自我修復 review 對 `productivity/neat-freak` 執行了
`patched (references/...)`，但**沒有同步到 canonical**。

**loader 實際載入哪一份（實測，不是猜測）**：

```python
from agent.skill_utils import provably_same_skill, skill_candidate_rank
provably_same_skill([a, b])            # True
skill_candidate_rank(a, root)          # (False, 2)  ← canonical 勝出
skill_candidate_rank(b, root)          # (False, 3)  ← productivity
```

rank 較淺者勝出 → canonical 勝出 → **「較新的內容」實際沒有生效**。

**預防**：
1. `~/.hermes/skills/` **內部**的 category 雙軌不在 `sync-check.py` 覆蓋範圍
   （它只比 canonical vs workspace），必須另外 `diff -rq` 或 `resolve_skill_catalog()`
2. **「比較新」不等於「會被載入」**——先確認 loader 的 rank 規則
3. 自我修復 loop 若 patch 了非 canonical 路徑，等於 patch 進黑洞

## Pattern NNN（2026-10-24 第十三 run 初發現）：文件記載的驗證命令必須「實際執行過」——regex 看起來對 ≠ 跑得出來

**觀察**：SKILL.md 與 4 份 live reference 記載的 header 驗證 regex 是：

```python
re.search(r'Active Skills:\s*\*\*(\d+)\*\*', c)
```

但 `Skill_Index.md` 的實際格式是 `- Active Skills: ***759***`——**三個星號**。
實測：

| regex | 對 `- Active Skills: ***759***` 的結果 |
|-------|---------------------------------------|
| `Active Skills:\s*\*\*(\d+)\*\*` | **NO MATCH** → header=None → 假 drift |
| `Active Skills:\s*(\d+)` | **NO MATCH** → header=None → 假 drift |
| `- Active Skills:\s*\*{2,3}(\d+)\*{2,3}` | **759** ✓ |

canonical `scripts/skill-index-check.py` 早就是對的（第 80 行用 `\*{2,3}`）。
**即：script 是對的，文件是錯的。** 照文件跑的人會拿到 `header=None` → 誤判 drift
→ 可能「修壞」一個其實乾淨的 index。

**延伸**：Pattern GGG 家族的口徑 count 還會因**條件不完整**出錯——
`references/skill-index-false-drift-2026-07-22.md` 漏了 `'SKILL.md' in l`，
把 Category Map 的數字列也算進去 → 768 vs header 759 → **假 drift 9**。

**預防**：
1. **SKILL.md 記載的驗證命令必須實際執行並貼出輸出**，不能只靠「regex 看起來對」
2. 寫 regex 前先 `head -3` 看實際檔案長什麼樣
3. script 與文件口徑不一致時，**script 通常是對的**（script 有人跑過，文件是抄的）
4. 口徑 count 的**每個條件都要有理由**；缺一個 filter 就是幾個假 drift
5. 批次取代字串後必須跑 `ast.parse()` 驗證每個 python code block
   ——巢狀引號（`"'os.path.expanduser('~/x')'"`）會產生語法錯誤的無效 Python
6. `python3 -c "` 殼層區塊裡的 `import os` 要插在**每個區塊內部**，
   且只在真的用到 `os.path` 時才插

**詳見 [references/skill-index-2026-10-24g-session.md](references/skill-index-2026-10-24g-session.md)**

## Pattern LLL（2026-10-24 第十二 run 初發現）：文件描述的是一套「合理但從未實作」的流程——比「過期」更隱蔽的腐敗

**觀察**：`references/hermes-backup-protocol.md` 描述的備份系統與磁碟實況**完全不同**：

| 項目 | 文件寫的 | 實際 |
|------|---------|------|
| 目的地 | `~/Documents/Agent/backups/hermes/` | `~/Documents/Backup/hermes/`（**該目錄根本不存在**） |
| 產物 | `memory_<TS>/` 散檔 | `hermes_<TS>.tar.gz` |
| 排程 | `0 0 * * *` | `0 3 * * *` |
| 流程 | `git commit` + **`git push`** | 沒有任何 git 步驟 |
| Cron output | 「**不備份**」 | 整個 `~/.hermes/cron` 都備份 |
| Skills | `cd ~/.hermes/skills && git status` | `~/.hermes/skills` **不是 git repo** |

**為什麼舊檢查抓不到**：這是**另一套設計方案**，不是過期版本——從未被實作。
每條指令單獨看都合理，沒有相對時間詞，grep 全漏。
只有「逐條驗證文件宣稱的每個路徑/指令真的存在」才會發現。

**預防**：
1. 文件宣稱的每個路徑與指令都要實際跑一次
2. 特別檢查文件裡的 `git push` 步驟——照著做可能洩漏憑證
3. `cd <dir> && git status` 這類假設該目錄是 repo 的指令，先驗證 `.git` 存在

## Pattern HHH（2026-10-24 第十一 run 初發現）：SKILL.md / references 內 macOS 絕對路徑 `/Users/pigo` 在 Linux 機器上全部失效

**觀察**：canonical `~/.hermes/skills/neat-freak/` 的 SKILL.md 與多個 references
仍寫著 `/Users/pigo/Documents/Agent/...`。這台機器是 Linux（`/home/x`），
那些路徑**不存在**——照著文件跑腳本會直接 `FileNotFoundError`。

**受影響檔案**：`SKILL.md`（5 處）、`references/skill-index-verification.md`（6 處）、
`references/skill-index-corruption-patterns.md`（3 處）、
`references/skill-index-false-clean-pattern.md`（4 處）、
`references/workspace-snapshot.md`（2 處）、`references/skill-index-script-bugs-2026-07-13.md`（1 處）。

**修復**：
- 純文件敘述中的路徑 → `~/Documents/Agent`
- **Python 程式碼片段中的路徑 → `os.path.expanduser('~/Documents/Agent/...')`**
  （`~` 在 Python 字串裡不會自動展開，必須顯式 expanduser）

**預防**：
- canonical skill 內的路徑一律用 `~` + `os.path.expanduser()`，
  不可寫死任何使用者的家目錄
- 批次取代時注意括號平衡：`open('~/X')` → `open(os.path.expanduser('~/X'))`
  需補上收尾括號；用 regex 一次性取代比逐個字串 replace 安全
- 平台遷移（macOS → Linux）時應把 skill 內的路徑納入 migration checklist

## Pattern PP（2026-07-09 初發現）：Vault frontmatter FAIL plateau — 00-Inbox intake stub policy gap

**觀察**：2026-07-09 cron job — 3 turns of fixing reduced FAIL count from 3 to 3（沒有改善）。剩餘的 FAIL 全是 `00-Inbox/` 的 intake stubs。

**根因**：`verify-vault-ingest.py` 對所有檔案強制執行完整 frontmatter，但 vault 自己的 intake workflow（`00-Inbox/`）故意建立不帶 source_url / status / classification_path 的檔案。Verifier 從未設定 exempt inbox 檔案。

**檢測**：FAIL count 在 ≥2 個連續 turn 後停止下降（plateau）。

**處置**：取決於 intended policy：
1. **若 inbox 檔案應該 exempt**：更新 `verify-vault-ingest.py` 跳过 `00-Inbox/` 目錄，或加入 `inbox: true` 欄位作為 exemption flag
2. **若 inbox 檔案需要完整 frontmatter**：對所有 inbox 檔案批量新增 stub frontmatter，並修復 template 檔案

**不要**：持續對同一類檔案 try fix——plateau signal 表示 policy gap，不是 fix 次數不夠。

**驗證**：確認剩餘 FAIL 屬於 `00-Inbox/` 或其他已知 intentional exemption 類別後，視為已修復，停止 further iteration。

詳見 [references/skill-index-2026-07-09-session.md](references/skill-index-2026-07-09-session.md)。

## Pattern LL（2026-07-03 初發現）：Concurrent cron race 導致雙重 competing commits

### Pattern LL-2（2026-10-27 實測）：concurrent cron job 留下**未完成的 rebase**——不是未完成的 merge

**觀察**：另一個 neat-freak job 在 10:36 執行 `git pull --rebase`，在 `docs/STATUS_ALL.md` 的
append 衝突處停下，**沒有任何 git 程序存活**，rebase 狀態留在磁碟上。

**診斷**（rebase 狀態檔是唯一真相來源，`git status` 只說「互動式重定基底動作正在進行中」
但不會告訴你這是 rebase 而非 merge，容易誤判）：
```bash
cat .git/rebase-merge/done            # 已套用
cat .git/rebase-merge/git-rebase-todo # 剩餘
cat .git/rebase-merge/stopped-sha     # 卡在哪一筆
cat .git/rebase-merge/onto            # rebase 目標
cat .git/rebase-merge/orig-head       # rebase 前的 HEAD
ps aux | grep -E "git (rebase|pull|commit)"   # 確認沒有活著的程序
```

**處置**：
1. 確認無存活 git 程序（有的話是別人正在跑 → 不要動）
2. 衝突若為**兩邊各自 append 新段落** → **合併保留兩側**，不要 `git checkout --theirs/--ours`
3. `git add <file>` + `GIT_EDITOR=true git rebase --continue`（避免開 editor 卡住）

**預防**：兩個 neat-freak job 排程重疊（本次 `539040a91ad2` 與 `b27de85df4a3` 都是每 120 分鐘）
→ 必然互相踩。建議錯開 interval，或在 job 開頭加 repo lock。

**觀察**：兩個 cron neat-freak job 同時在 `main` branch 對同一份 `Skill_Index.md` 做口徑修正，產生兩個 competing commits。push rejection 觸發 `git commit --amend` 產生新 commit object 而非覆寫，最終需 merge 解決。

**正確處置徑**：
```
push rejection → git pull --no-rebase → resolve conflict → commit → push
```
**不要 `git commit --amend`**——在已有 remote commit 的 branch 上 amend 會產生新 commit object 而非覆寫。

**預防：cron job 的 competing-commit guard**（在 Step 0 的 ahead-only 評估之後、任何 git 操作之前）：
```bash
LATEST=$(git ls-remote --refs origin main | awk '{print $1}' | head -1)
PREV=$(git rev-parse HEAD)
if [ "$LATEST" != "$PREV" ]; then
  git log --oneline origin/main..HEAD | grep -qi "drift\|fix.*Skill_Index" && \
    echo "WARNING: Remote may have competing fix. Pull before continuing."
fi
```

## Pattern KK（2026-07-02 初發現）：`patch` 與 `execute_code` 對「唯一性不足的多重匹配」的處理差異

## Pattern KK（2026-07-02 初發現）：`patch` 與 `execute_code` 對「唯一性不足的多重匹配」的處理差異

**觀察**：`memory/index.md` 的 session 記錄 table 中，同日期有多個檔案（如 `2026-06-05-0004.md` 和 `2026-06-05-0404.md`）時，嘗試修正其中一個 row 的時間戳會被 `patch` 阻擋：`Found 6 matches for old_string`。

**根因**：`patch` tool 設計上要求 `old_string` 在檔案內唯一。當多個 rows 內容完全相同時（如多個 session row 都帶相同的 description），`old_string` 會同時匹配所有 rows，`replace_all=false` 的約束讓 tool 直接拒绝執行。

**為什麼舊檢查抓不到**：這不是 drift，是「編輯器阻塞」——patch tool 的 guard 機制，沒有任何 error message 或提示。

**正確解法**：使用 `execute_code` 的 Python 字串替換（`str.replace(old, new, 1)`），可在多重匹配中精確替換第一個（或第 N 個）：
```python
content = open('/path/to/file.md').read()
old = 'exact string to replace'
new = 'replacement'
if old in content:
    content = content.replace(old, new, 1)   # 1 = 只換第一個出現
    open('/path/to/file.md', 'w').write(content)
```

**預防**：當需要修改的 row 是「看起來相同但位置不同」的 table row 時，優先用 `execute_code` 而非 `patch`。若已知 row 內有足夠 unique substring 可以區分，給 `patch` 提供更多 surrounding context 也能解決。

## Pattern II（2026-06-29 更新）：完整重建的觸發條件與分類決策 A2-改2

**觸發**：當 Pattern EE 達到嚴重程度（>50% row 結構腐敗，dangling + unlisted 合計 >1000），incremental 修復已不可行，必須**完整重建**。

**Pigo 觸發語**：當他說「一次完整重建才能解決」、「不適合在單次 session 修補」、「歷史證明單次修補無效」這類話時，這是觸發信號。

**完整重建流程**（2026-06-29 實戰驗證）：

1. **備份**：先 `cp docs/Skill_Index.md docs/Skill_Index.md.bak-$(date +%Y%m%d-%H%M%S)`，備份檔 commit 進去供回溯
2. **磁碟盤點**：用 `find skills -name SKILL.md` 排除 `SKILL.merged.md`、`references/`、`examples/`，得「事實清單」JSON
3. **分類政策決策**：
   - **A1**：沿用舊 14 類口徑，只補缺漏（最小變動，分類口徑穩定）
   - **A2**：磁碟一級目錄作分類（高層口徑，反映事實結構）
   - **A2-改2**（推薦）：A2 為主 + 散落型 skill 統一進「Root-level Skills」最後一段，按字母序排
   - **A3**：完全照磁碟一級目錄（最暴力，跟舊 index 政策打架）
   - **A4**：全部平鋪按字母序（最穩，但失去分類導航）
4. **平行 dispatch**：8 組（每組 60-110 條）用 subagent 生成 row files，每組產出 `03-rows-G*.md` 帶 section header
5. **合併腳本**：主線程跑 `merge_index.py` 串接 8 組，過濾 subagent 可能誤加的 column header / separator，計算 Summary 數字
   **CRITICAL（Pattern MM）**：subagent 寫入的 section header count（如 `## Root-level Skills (64)`）可能與 actual row count 不符。merge script 必須在串接後對每個 section 重新 count actual rows，並用 actual 值覆寫 header，不能直接採用 subagent 提供的數字。
6. **驗證**：0 dangling, 0 unlisted, 0 duplicates, header 數字跟 actual rows 一致
7. **commit**：單一 commit「docs: full rebuild Skill_Index.md from disk inventory (520 → N)」，不 push

**A2-改2 為何優於純 A2**：Agent repo 結構是混合的——有目錄的（如 `agent-workflows/`、`science-data/`）和散落型（如 `aihot/`、`x-note/`、`yao-*`）。純 A2 會把 73 個不同 category name 平鋪（其中 18% 是「一個 skill 一個資料夾」的裸型），可讀性差。A2-改2 把 13 個大目錄保留為主分類，63 個散落型統一進 Root-level Skills，可讀性最好。

**A2-改2 為何優於 A4**：完全平鋪失去分類導航價值。docs/Skill_Index.md 的主要受眾是「第一次找 skill 的人」，分類能給快速導航。

**merge script 必備的三個 column-header tolerance**（subagent 容易多加）：
- `| name | path | description | api_key |` — column header
- `| --- | --- | --- | --- |` — markdown separator
- Category Map 區段的 3 欄表格（`| Category | Count | Skills From |`）

**commit 內容決策**：
- ✅ commit：`docs/Skill_Index.md`（主成品）、`docs/Skill_Index.md.bak-YYYYMMDD-HHMMSS`（回溯保險）、`docs/.index-rebuild/`（事實快照 `01-disk-inventory.json` + 8 組 input + 8 組 row + merge script）
- ❌ gitignore：ad-hoc audit report（`docs/.index-audit-report.md`）——regenerable 的診斷輸出不入庫

**Pigo 數字估計常偏低**：他說「134 個落後」，實測 484 dangling + 584 unlisted = 1068 落差。**永遠先驗證再動作**。

## Pattern HH（2026-06-02 初發現）：Pi-AGENTS.md 與根 AGENTS.md 的 path drift

**觀察**：`docs/Pi-AGENTS.md`（Pi 全域指令）含過期 Windows 路徑，而根目錄 `AGENTS.md` 已為正確 macOS 路徑。兩層來自同一 repo 但各自維護，之間沒有自動同步。

**為什麼舊檢查抓不到**：
- Step 1 的 `find -name "*.md"` 只列舉檔案，不交叉比對同類文件（如所有 AGENTS.md）之間的路徑事實一致性
- 過去的路徑檢查主要針對記憶和單一文件，未擴展到同層 multiple copies

**修復**：在 Step 1 末段新增 AGENTS.md 規範一致性交叉檢查（已見 Pattern FF），但需注意：
- `docs/Pi-AGENTS.md` 是 Pi 的全域疊加，**不是**根 AGENTS.md 的 copy
- 兩者受眾不同，各自維護各自的路徑事實
- 發現 drift 時，檢查磁碟實際路徑，以正確的為準，各自更新

**預防**：每次平台遷移後（Windows→macOS、換 vault 路徑），對所有 AGENTS.md 層級檔案**和 skill docs** 做路徑 cross-check，不要只檢查根目錄。

**2026-07-01 發現**：過去修復只針對根目錄 AGENTS.md，但 `skills/transcript-cleaner/README.md`、`skills/transcript-cleaner/SKILL.md`、`skills/xiaocui-skill/references/research/03-expression-dna.md`、`skills/xiaocui-skill/references/research/04-topic-spectrum.md` 也含 `/home/pigo/文件/Agent` 路徑。vendor/ 內 3 處不修（外部 bundle）。

**標準修復命令**：
```bash
sed -i '' 's|/home/pigo/文件/Agent|~/Documents/Agent|g' \
  ~/Documents/Agent/skills/transcript-cleaner/README.md \
  ~/Documents/Agent/skills/transcript-cleaner/SKILL.md \
  ~/Documents/Agent/skills/xiaocui-skill/references/research/03-expression-dna.md \
  ~/Documents/Agent/skills/xiaocui-skill/references/research/04-topic-spectrum.md
```

### Pattern EE（2026-05-31 初發現，2026-06-01 更新）：Skill_Index 整體結構腐敗——全部路徑 dangling + 口徑落後磁碟 114 個

**觀察（2026-06-01）**：獨立驗證口徑：
- Skill_Index.md header: **486**（drift=0，header 數對得上自己的 rows）
- 磁碟上實際 SKILL.md: **600 個**（不含 vendor/archive/.system/，2026-05-31 為 597）
- Skill_Index.md 內**所有 486 個路徑全部 dangling**
- 差額: 600 - 486 = **114 個** skills 完全沒被列入

**腐敗機制**：Index 的路徑格式為 `../skills/mattpocock-skills/skills/productivity/caveman/SKILL`（三層巢狀），但實際磁碟為 `skills/<name>/SKILL.md`（兩層）。`mattpocock-skills/skills/...` 目錄在磁碟上**根本不存在**。

**為什麼 script 沒抓到**：`check_dangling()` 正確偵測到所有路徑都不存在並回報「578 dangling」，但 `check_header_drift()` 的 `Actual rows: 0` 虛假信號讓整體判斷變成 `✓ ALL CLEAN`（false positive）。兩層 bug 互相抵消。

**修復方向**：
1. 用 `find ~/Documents/Agent/skills -name SKILL.md` 重新掃描磁碟（600 個）
2. 產生新的 row 格式：`skills/<dirname>/SKILL.md`（相對於 `docs/` 即 `../skills/<dirname>/SKILL.md`）
3. 以 actual 600 重新設定 Summary header

**預防**：Skill_Index.md 必須在 skill 目錄結構任何變更後（搬家、刪除、新增）立即重新掃描磁碟重建，不能只靠增刪 row。

## Pattern FF（2026-05-31 初發現）：Subdirectory AGENTS.md 規範漂移

**觀察**：`Agent/AGENTS.md` 的 Requirement #5 仍要求寫入 `STATUS_*.md`，但根目錄 `AGENTS.md` 已改為 `STATUS_ALL.md`。兩份文件存在於同一 repo 但規範不同步。

**為什麼舊檢查找不到**：
- Step 1 的 `ls + find` 只列舉檔案，不比對同一類別檔案之間的內容邏輯一致性
- 相對時間 / dangling / 路徑 grep 都只測單檔，不測 cross-file 規範衝突

**修復**：
1. 在 Step 1 末段（列舉完所有 `.md` 後）新增 **AGENTS.md 規範一致性交叉檢查**：
   ```bash
   # 找出所有 AGENTS.md 檔案，檢查同一關鍵條款是否一致
   for f in $(find ~/Documents/Agent -name "AGENTS.md" -not -path "*/node_modules/*" -not -path "*/.git/*"); do
     echo "=== $f ==="
     grep -n "STATUS_\|STATUS_ALL\|STATUS_2026" "$f" | head -5
   done
   ```
2. 若發現不一致，以根目錄 `AGENTS.md` 為準，同步更新所有 subdirectory copy

**預防**：每次修改根目錄 `AGENTS.md` 的規範後，立即用上述指令檢查所有 subdirectory copy 是否需要同步。

## Skill Library Maintenance（Skill_Index.md 專用）

當需要審計、診斷或重建 Agent repo 的 `Skill_Index.md` 時使用本流程。觸發條件包括：`clean up Agent index`、`rebuild skill index`、`fix Skill_Index.md`、`skill index broken`、`regenerate index`、`audit skills`。

### Step 1: 先審計再動手

```bash
cd ~/Documents/Agent

# 取得磁碟上所有 skill
find . -name "SKILL.md" | grep -v ".git" | sort > /tmp/all_skills.txt

# 取出目前 index 引用的路徑（index 的路徑相對於 docs/，使用 ../ 前綴）
rg "\]\([^)]+\.md\)" docs/Skill_Index.md | rg -o "\]\([^)]+\.md\)" | sed 's/]//g; s/(//g; s/)//g' | sort -u > /tmp/indexed_paths.txt
```

### Step 2: 確認磁碟實際結構

```python
import os
disk_skills = set()
for root, dirs, files in os.walk("skills"):
    if "SKILL.md" in files:
        rel = os.path.relpath(root, ".")
        disk_skills.add(rel)
```

### Step 3: 識別問題類型

- **路徑漂移**：Index 用 `../X/SKILL.md` 但磁碟是 `skills/X/SKILL.md`
- **Index 漏掉**：磁碟上有但 index 沒列
- **Index 多餘**：index 引用但磁碟上不存在（dangling rows）
- **大小寫衝突**：`Skill.md` vs `SKILL.md` 在大小寫不敏感系統差異

### Step 4: 重建 Skill_Index.md

產出格式為 markdown 表格，含：
- Skill 名稱（取 frontmatter）
- 路徑（相對於 Agent 根目錄，`docs/` 的 index 使用 `../` 前綴）
- 用途說明（取 frontmatter description）
- API Key 需求（自動偵測）
- 備註

按功能分類（目錄 namespace）分組。

### Step 5: 修復後驗證

```bash
git status --short
# 只應顯示 docs/Skill_Index.md 的變更
```

### 常見陷阱

- **不要相信 index 的 summary counts** — 一定要用磁碟掃描驗證
- **不要一個一個修路徑** — 從磁碟掃描重建最快最乾淨
- **Vendor skills**（`vendor/`）是外部 bundle 匯入，不是 canonical，不加入 active index
- **Runtime skills**（`.agents/`、`.system/`）是系統專用，原則上不暴露在 main index
- **大小寫更名**：在大小寫不敏感系統（macOS）上，`SKILL.md` vs `Skill.md`  rename 不會衝突，先用 `ls -la` 確認磁碟上的實際大小寫
- **路徑漂移模式**：若 400+ 個「壞掉」的路徑都共享同樣的前綴問題（如 `../skills/X/SKILL.md` vs `../X/SKILL.md`），問題是 index 格式漂移，不是檔案遺失

### 參考：目前 Repo 結構（2026-05-20）

- `skills/` — canonical skill 層（~577 skills）
- `vendor/` — 外部 bundle 匯入（60 skills，不加入 main index）
- `.agents/skills/` — runtime skill mirrors（6，系統專用）
- `.system/` — 系統 skill（5，系統專用）
- `archive/` — 已歸檔/重複候選（1）
- `shared-skills/` — 共享 skill 副本（5）

`docs/Skill_Index.md` 的路徑格式為相對於 `docs/` 的 `../` 前綴（如 `../skills/agent-browser/SKILL.md`）。

## Pattern JJ（2026-07-04 初發現）：Readme.md Primary Read Targets 雙重腐敗——雙反斜線 + 幽靈目錄

**觀察**：`Agent/Readme.md` 的 `Primary Read Targets` 含 8 個 DOS-style trailing backslash 路徑（`.agents\`、`.baoyu-skills\`、`.github\`、`.system\`、`AGENT\`、`archive\`、`browser-use-lab\`、`docs\`），且列出 5 個**磁碟上不存在的目錄**（`browser-use-lab`、`document-skills`、`macm1bot-migration-pack`、`pptx-posters`、`scripts`）。

**腐敗機制**：這是同一來源的兩種不同症狀：
1. **雙反斜線腐敗**：Windows 環境寫入或路徑轉義殘留，`grep` 和 `cat` 皆看不出（單 `\` 在 markdown 中外觀正常）
2. **幽靈目錄列舉腐爛**：目錄在磁碟上被刪除或從未建立，但 `Readme.md` 的 `Primary Read Targets` 和 `Immediate Child Directories` 章節未同步清理

**為什麼舊檢查找不到**：
- `grep -E "今天|昨天|最近"` 對雙反斜線無效
- `file` 命令報告 UTF-8（編碼本身沒問題，是內容語意錯誤）
- 過去的路徑檢查主要針對 `~/Documents/` 絕對路徑，不涉及 workspace 內部目錄列舉

**檢測方法**（雙軌並進）：
```python
# 軌跡 1：雙反斜線
c = open('Readme.md').read()
for i, l in enumerate(c.split('\n')):
    if '\\\\' in l:
        print(f'Line {i+1}: trailing backslash — {repr(l[:60])}')

# 軌跡 2：幽靈目錄
import os
workspace = os.path.expanduser('~/Documents/Agent')
with open('Readme.md') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    stripped = l.strip()
    if stripped.startswith('- `') and (stripped.endswith('/`') or stripped.endswith('\\`')):
        dirname = stripped[3:-2]
        if not os.path.exists(os.path.join(workspace, dirname)):
            print(f'Line {i+1}: phantom directory — {dirname} does not exist on disk')
```

**修復方法**：
```python
c = open('Readme.md').read()
# 修雙反斜線
for old, new in [
    ('.agents\\', '.agents/'), ('.baoyu-skills\\', '.baoyu-skills/'),
    ('.github\\', '.github/'), ('.system\\', '.system/'),
    ('AGENT\\', 'AGENT/'), ('archive\\', 'archive/'),
    ('browser-use-lab\\', 'browser-use-lab/'), ('docs\\', 'docs/'),
]:
    c = c.replace(old, new)

# 移除幽靈目錄
phantom = {'browser-use-lab', 'document-skills', 'macm1bot-migration-pack', 'pptx-posters', 'scripts'}
lines = c.split('\n')
new_lines = []
for l in lines:
    stripped = l.strip()
    is_phantom = stripped.startswith('- `') and any(
        stripped[3:-2] in phantom
        for x in [stripped[3:-2]]
        if stripped.endswith('/`') or stripped.endswith('\\`')
    )
    if not is_phantom:
        new_lines.append(l)
open('Readme.md', 'w').write('\n'.join(new_lines))
```

**預防**：
- 每次刪除 workspace 根目錄的目錄後，同步更新 `Readme.md` 的 `Primary Read Targets` 和 `Immediate Child Directories`
- 建議對 `Readme.md` 內所有 `- \`xxx/\`` 格式的目錄行定期做磁碟存在性抽查

## Pattern GG（2026-05-31 初發現）：Readme.md Primary Read Targets 包含已封存備份檔

**觀察**：`Agent/Readme.md` 的 `Primary Read Targets` 包含 `AGENTS_2026-05-02.md`，但這是含日期後綴的已封存備份檔（Pattern DD），不應作為主動閱讀目標。

**修復**：
1. `ls <subdir>/` 檢查是否有用戶端未預期的 dated backup 檔案
2. 確認後同步更新 Readme.md 的 `Primary Read Targets` 或 `## 參考資料` 章節

**預防**：每次發現 dated backup 檔案時，同時檢查相關 Readme.md 是否將其列為 active reference。

## Pattern DD（2026-05-30 初發現）：Dated backup files in AGENT/ subdirectory — 不修改已封存的歷史備份

**觀察**：在 `~/Documents/Agent/AGENT/` 子目錄下發現含日期後綴的備份檔：
- `AGENTS_2026-05-02.md`（387 行，含過期路徑 `~/Documents/Obsidian`）
- `AGENTs.md.20260501`
- `AGENTS.md.20260430`

這些檔案含有過期的 Vault 路徑引用，但檔名含日期後綴明確標記為已封存歷史。

**為什麼不修改**：
- 備份檔案保留歷史狀態，不應因今日路徑變更而回頭修改歷史備份
- HEAD 的 `AGENT/AGENTS.md` 已為正確版本（路徑已修正）
- `git log` 顯示這些是常規備份 commit，不是 active 文件

**判斷徑**：
```
ls AGENT/*.md
→ 發現含日期後綴的 AGENTS backup 檔案（如 AGENTS_2026-05-02.md）
→ 檢查檔名是否為明確的 dated backup（YYYY-MM-DD 或 YYYYMMDD 後綴）
→ 若是：視為已封存，不active維護，不修改
→ 若否（如 AGENTS.md 而非 AGENTS_2026-05-02.md）：視為 active 文件，需檢查並同步路徑
```

**注意**：`AGENTS_2026-05-02.md` 被 `AGENT/Readme.md` 引用——若需要刪除備份檔，需同步移除 Readme.md 中的 reference，否則留「未處理」待人工裁決。

## Pattern CC（2026-05-29 初發現）：路徑參照衝突——cross-document path inconsistency

### Script 驗證工具

- **[scripts/sync-to-workspace.sh](scripts/sync-to-workspace.sh)** — canonical → workspace sync helper（拷貝 SKILL.md + 所有 references/ + scripts/ 到 workspace copy，之後 git add + commit + push）
- **[scripts/verify-patch.py](scripts/verify-patch.py)** — 快速驗證 skill-index-check.py 的 regex 口徑是否與實際 Skill_Index.md 一致（修復 Pattern AA 後必跑）

### 已知持久性問題（2026-05-31 仍存在）

**CRITICAL — `check_header_drift()` 的 regex 仍無法抓到大陸式 dash-prefix header**：
script 的 `check_header_drift()` 用 `Active Skills:\s*(\d+)` 對 Summary 行比對，但 Skill_Index.md 格式是 `- Active Skills: N`（前有 dash），導致永遠抓不到數字，回報 `Actual rows: 0` 却同時給出 `✓ ALL CLEAN`——這是**虛假乾淨信號**。

**2026-05-31 cron job 驗證**：口徑實際為 486 rows（獨立 Python 確認），但 script 報告 0。

**每次驗證口徑的標準流程**（不能跳過）：
```python
# Step 1：獨立計數（不走 script 的 regex）
python3 -c "
import re
c=open(os.path.expanduser('~/Documents/Agent/docs/Skill_Index.md')).read()
rows=re.findall(r'^\| \[([^\]]+)\]\([^)]+\.md\)', c, re.M)
print(f'Actual rows: {len(rows)}')
m=re.search(r'- Active Skills:\s*\*{2,3}(\d+)\*{2,3}', c)
print(f'Header: {m.group(1) if m else \"not found\"}')
"
# Step 2：比對兩者是否一致
# Step 3：若一致，script 報告的 0 是已知虛假信號，可忽略
#         若不一致，script 有 bug，需盡快修補 SKILL.md + script
```

**為什麼不能依賴 script 的 `Actual rows` 欄位**：
`check_header_drift()` 內部呼叫的口徑 count 和 `check_dangling()` 共用同一套 regex，而那套 regex 匹配不到 `- Active Skills: N` 格式，導致 `Actual rows` 永遠是 0。**已知虛假，勿信**。

**長期修復方向**：`skill-index-check.py` 的 `check_header_drift()` 函式需要一次全函式重構，把口徑計數與 drift 檢查解耦，詳見 `references/skill-index-script-bugs-2026-05-22.md`。

## Pattern NN（2026-07-07 初發現）：三口徑各自 drift——Summary / Category Map / Section Header 可以分層落後

**觀察**：本次（2026-07-07）發現三層數字各自落後於 actual rows：
- Summary header: **606**（落後 actual=603，差 3）
- Category Map sum: **604**（落後 actual=603，差 1；engineering entry 92 實際應為 91）
- Section Header sum: **603**（對 actual=603 ✓；但 engineering header 為 91 仍需单独驗證）

**根因**：三口徑由不同維護動作產生，各自独立漂移：
- Summary 来自「每次 rebuild 時人工估算或 subagent 報數」
- Category Map 来 自「每次增刪 row 時的 column 加總」
- Section Header 来自「每次 merge 時 subagent 寫入的預期值」

**為什麼舊檢查找不到**：
- 舊的 Pattern AA 口徑驗證流程只要求「確認 Summary 與 actual rows 一致」
- 沒有要求分別驗證 Category Map sum 和 per-section header 與 actual rows 的對齊

**三口徑驗證標準流程（2026-07-07 起強制）**：

```python
import re
c = open(os.path.expanduser('~/Documents/Agent/docs/Skill_Index.md')).read()

# 1. Count actual rows
lines = c.split('\n')
actual_rows = len([l for l in lines if re.match(r'^\| [A-Za-z0-9]', l)])
print(f'Actual rows: {actual_rows}')

# 2. Summary header
m = re.search(r'- Active Skills:\s*\*{2,3}(\d+)\*{2,3}', c)
summary = int(m.group(1)) if m else None
print(f'Summary header: {summary} (diff={abs(actual_rows - summary) if summary else "N/A"})')

# 3. Category Map sum
cm_lines = [l for l in lines if re.match(r'^\| [^|]+\| \d+ \|', l)]
cm_sum = sum(int(re.search(r'\| (\d+) \|', l).group(1)) for l in cm_lines)
print(f'Category Map sum: {cm_sum} (diff={abs(actual_rows - cm_sum)})')

# 4. Section header sums
section_headers = [(i+1, l) for i,l in enumerate(lines) if re.match(r'^## [^#](.+)\((\d+)\)', l)]
section_sum = sum(int(re.match(r'^## [^#](.+)\((\d+)\)', l).group(2)) for _,l in section_headers)
print(f'Section header sum: {section_sum} (diff={abs(actual_rows - section_sum)})')

# 5. Per-section validation
print('\nPer-section:')
all_ok = True
for num, line in section_headers:
    expected = int(re.match(r'^## [^#](.+)\((\d+)\)', line).group(2))
    start = num
    end = len(lines)
    for j in range(num, len(lines)):
        if re.match(r'^## [^#]', lines[j]) and j > num:
            end = j; break
    rows = [l for l in lines[start:end] if re.match(r'^\| [A-Za-z0-9]', l)]
    status = '✓' if expected == len(rows) else f'✗(expected={expected}, actual={len(rows)})'
    if '✗' in status: all_ok = False
    print(f'  {line[:55]} => {len(rows)} rows {status}')
print(f'All sections OK: {all_ok}')
```

**三口徑修復優先順序**：
1. 先修 per-section header（對 actual rows 最精準）
2. 再以 actual rows 為準重算 Summary header
3. 最後重算 Category Map sum（允許與 actual 差 ±1，但 drift 超過 2 就要修）

**預防**：
- 任何 Skill_Index.md rebuild 後，必須跑完整三口徑驗證，不能只修 Summary
- 口徑 drift 超過 5 就要懷疑是 subagent merge bug（Pattern MM），而非普通遺漏

## Pattern XXX（2026-10-29 第二十一 run 初發現）：checker 只驗「被驗的那幾項」——Summary 分解 subtotal 不在覆蓋範圍

**發現**：`skill-index-check.py` 回報 `✓ ALL CLEAN`，但 `docs/Skill_Index.md` 的 Summary 段落
宣稱 API key 需求分布為 `32 需要 / 193 可能需要 / 534 不需要`，
**32 + 193 + 534 = 759 ≠ 760**（Active Skills 實際為 760）。

**追查**：三個 subtotal 的 cell 內容與表格實際統計完全一致——真正壞掉的是
**Summary 段的分解數字**，不是任何一列的 cell。checker 的五項檢查覆蓋
口徑 drift / per-section drift / dangling / purpose cell 三型腐蝕 / Skill_Category 對齊，
**全部只檢查「表格 ↔ 表格」的一致性，沒有任何一項檢查「Summary 的分解數字 ↔ 表格 cell 的加總」**。

**根因**：2026-10-24 新增 `diagnosing-superpowers` 使 Active Skills 從 759 → 760。
當時只更新了 Active Skills 總數與該 skill 自己的 row，**沒有人記得「不需要 API key」
這個 subtotal 也要跟著 +1**。三個數字各自都「看起來合理」，加起來才發現對不上。

**修復**：
1. `docs/Skill_Index.md` 的 `不需要` 由 534 改為 535（32 + 193 + 535 = 760 ✓）
2. checker 新增 check `[6] API key breakdown drift (Summary vs actual cells)`：
   解析 Summary 的三個 subtotal，直接對表格 cell 做加總比對
3. 負向測試：把 `不需要` 改成 999 → checker 回報 `[('不需要', 999, 535)]` ✓

**預防**：
1. **加總類數字必須獨立驗證**——單一數字合理不代表它們的和不合理
2. 任何「新增一個 skill」的操作，都要檢查文件裡**所有**依賴該計數的衍生數字
   （total / subtotal / percentage / section header / category map）
3. checker 的「✓ ALL CLEAN」只代表**它驗的那幾項**一致，不代表文件整體自洽（Pattern YYY）

## Pattern YYY（2026-10-29 第二十一 run 初發現）：跨文件引用同一個計數 — 兩份文件各自「對」但合起來矛盾

**發現**：`docs/Skill_Category.md` 的 14 類功能分類表合計 **581**，
而 `docs/Skill_Index.md` 的 Active Skills 是 **760**。兩者相差 179。

**為什麼不是 drift 腐敗**：
- `Skill_Category.md` 用的是**功能分類**（`Agent, Workflow & Skill Operations` 等 14 類），
  由 2026-05-20 的 rebuild 產生
- `Skill_Index.md` 用的是**目錄分類**（8 個 directory-based categories）
- 兩套分類維度不同、計數重疊規則不同 → 數字不同是**預期的**

**真正的問題**：兩份文件都沒有說明自己的口徑與對方不同，讀者只會看到「581 vs 760」
然後懷疑其中一份壞了。這是 Pattern LLL 家族（文件描述的是一套合理但從未實作的流程）
的輕量版——不是內容錯，是**語意缺失**。

**修復**：
1. `docs/Skill_Category.md` 的 `Current Verification Notes` 明確聲明 581 是
   **2026-05-20 的 dated functional-placement snapshot（lower bound）**，
   指定的 live census 是 `docs/Skill_Index.md` → `Category Map` 的 760
2. header 改為 `Generated: 2026-05-20 · Counts refreshed: 2026-10-29`，
   count 欄位標為 snapshot
3. checker 新增 check `[7] Skill_Category.md table self-consistency`：
   驗證表內各列加總 == 文件自己宣稱的 claim（`Sum of category counts:` 或 `Table row sum:`）
   —— 驗的是**文件內部自洽**，不是跨文件口徑相同
4. 負向測試：把 claim 改成 777 → checker 回報 `table_sum 581 claim 777 rows 14` ✓

**預防**：
1. **口徑不同的兩份文件，必須各自標明口徑**——不等於要求它們數字相同
2. checker 的跨文件檢查應該驗「**各自內部自洽**」，不是「兩者數字相同」
3. 兩份文件的口徑差異要寫在**被引用次數少的那一份**上（通常是舊的那份）

## Pattern ZZZ（2026-10-29 第二十一 run 初發現）：headings 位於 code fence 內時，heading-based 區塊切片會誤刪內容

**發現**：整理 `SKILL.md` 的重複 heading 時，用「找下一個 heading 當作區塊結尾」的
helper 切片。該 helper **沒有排除 code fence 內的 heading** ——
`SKILL.md` 的「同步完成」摘要範例是放在 ``` fence 裡的，
其中的 `## 同步完成` / `### 記憶變更` / `### 文件變更` 都被當成真 heading，
於是區塊結尾比預期早數百行，**刪掉了 1455 行有效內容**。

**傷害範圍**：canonical `SKILL.md`（`~/.hermes/skills/neat-freak/SKILL.md`）被截斷。
canonical 樹**沒有 git**，唯一還原路徑是 `~/Documents/Backup/hermes/` 的 tarball 或
workspace copy。

**還原**：從 workspace copy（git HEAD，2336 行）覆蓋回 canonical，內容完全一致。

**修復（正確的 fence-aware 版本）**：
```python
def fence_prefix(lines, idx):
    """True if line idx is inside a ``` code fence."""
    st = False
    for i in range(idx):
        if lines[i].lstrip().startswith('```'):
            st = not st
    return st

def real_headings(lines):
    return [i for i, l in enumerate(lines)
            if l.startswith('#') and not fence_prefix(lines, i)]

def endof(lines, s):
    """Index of next REAL heading after s."""
    for j in range(s + 1, len(lines)):
        if lines[j].startswith('#') and not fence_prefix(lines, j):
            return j
    return len(lines)
```

**預防**：
1. **任何用 heading 當區塊邊界的編輯，一律要 fence-aware**
2. 大規模刪改前**先備份**（canonical 樹無 git → 用 tarball 或 workspace copy）
3. 刪改後用**多集比對**驗證內容沒丟：
   ```bash
   grep -v '^#' old.md | grep -v '^$' | sort | uniq -c > a.txt
   grep -v '^#' new.md | grep -v '^$' | sort | uniq -c > b.txt
   diff a.txt b.txt   # 只應顯示「重複項減少」與「新增項」
   ```
   ——只比 `diff` 的行數增減會漏掉「內容被刪掉但同時新增了等量行數」的情況
4. **刪除前先寫下每個 anchor 的 assert**（`assert len(x) == 2`），
   讓 anchor 數量不符時**立即失敗**而不是靜默刪錯區塊
5. canonical 樹的任何內容破壞都可由 workspace copy 還原 → **改動前先確認 workspace copy 是完整的**


## Pattern XXXX（2026-10-29 第二十二 run 初發現）：checker 的覆蓋範圍是它「以為」的範圍——repo-root 副本第三次落後

**觀察**：`~/Documents/Agent/neat-freak/SKILL.md`（**repo 根的第三份副本**）再次落後 canonical
（2,336 行 vs 2,435 行）。前兩次（2026-10-27、2026-10-29b）都是**手動 `cp` 修好**，
沒有人去修導致它反覆落後的根因 → 同一個坑第三次踩。

**三份副本，只有兩份在檢查範圍內**：
```
canonical    ~/.hermes/skills/neat-freak/SKILL.md         ← 真正的來源
copy A       ~/Documents/Agent/skills/neat-freak/SKILL.md  ← sync-check.py 只比這份
copy B       ~/Documents/Agent/neat-freak/SKILL.md         ← 沒有任何檢查看它 ← 問題所在
```

**更深的層次**：`sync-check.py` **從不比較內容**，只比對檔案**存在性**。
即使 copy A 的 `SKILL.md` 內容過期，舊版 checker 仍回報 `RESULT: CLEAN`。
（Pattern H item 9、Pattern AAA 早就指出這點，但歷次都只寫在正文，沒人實作進 checker。）

**修復**（canonical `scripts/sync-check.py`）：
1. **Content consistency** — 對 canonical 樹下每個檔案做 `read_bytes()` 比對
2. **Repo-root copy** — 比對 `<WORKSPACE_ROOT>/neat-freak/SKILL.md`，過期時顯示兩者行數
3. 新增 `WORKSPACE_ROOT` 環境變數（預設 `~/Documents/Agent`）

**驗證（負向測試必做，Pattern QQ）**：

| 測試 | 期望 | 實測 |
|------|------|------|
| 乾淨狀態 | `RESULT: CLEAN`, exit 0 | ✓ |
| canonical 改動未同步 | CONTENT DIFFERS, exit 1 | ✓ |
| repo-root 副本注入 2 行 | STALE + exit 1 | ✓ `canonical 2435 lines vs repo-root copy 2437 lines` |

**預防**：
1. **checker 的覆蓋範圍要靠「故意破壞」來證明**——negative test 是唯一能證明檢查有效的手段
2. **同一份內容有多份副本時，先列出所有副本位置**，逐一納入比對基準
3. **發現「同一問題第 N 次出現」時，不要只做第 N 次手動修復**——修根因，
   否則會有第 N+1 次。本次修的是 checker 覆蓋範圍，不是再一次 `cp`
4. `sync-check.py` 的比對基準是兩個 `*_dir()` 函式的回傳值；新增 skill 副本位置要同步擴充基準

詳見 [references/skill-index-2026-10-29d-session.md](references/skill-index-2026-10-29d-session.md)

## Pattern NNN-2（2026-10-29 第二十三 run）：批次修路徑注入 `fos.` typo——reference 內的 Python 片段也要 `ast.parse()`

**觀察**：canonical `references/openclaw-exec-allowlist-fix.md` 第 77–78 行是
`fos.path.expanduser('~/.nvm/.../bin/{runtime}')`——`fos` 未定義（typo）＋字串缺
`f` prefix（`{runtime}` 不會展開）。這是某個 10-29 run 做 Pattern HHH 修復
（`/home/pigo/` → `expanduser`）時批次取代注入的新腐敗。

**為什麼抓不到**：grep 對 `fos.` 無感（它長得像正常變數）；`sync-check.py`
只比 canonical↔workspace 一致性，兩邊一起錯就會綠燈。

**修復 + 預防**：
1. 批次改寫任何含 Python code block 的 `.md` 後，**逐 block 跑 `ast.parse()`**：
   ```python
   import re, ast
   blocks = re.findall(r'```python\n(.*?)```', open(f).read(), re.S)
   for i, b in enumerate(blocks): ast.parse(b)
   ```
2. reference 文件裡的 Python 片段是「會被未來 agent 照抄的代碼」，
   品質標準與可執行 script 相同（Pattern NNN 延伸）
3. 詳見 [references/skill-index-2026-10-29e-session.md](references/skill-index-2026-10-29e-session.md)

## 附：2026-10-29 第二十二 run 新增參考

- **[references/skill-index-2026-10-29d-session.md](references/skill-index-2026-10-29d-session.md)** — Pattern XXXX 新增（repo-root 副本第三次落後，根因是 `sync-check.py` 覆蓋範圍不含該路徑且從不比較內容；已實作 content-consistency + repo-root 兩項檢查並以負向測試證明有效）；Vault 914 檔 tag 去重（HEAD/worktree YAML invalid 皆 0 → 判定為修復成果後才 commit）；Phase 1–5 全綠


## 附：2026-11-02 run 新增參考

- **[references/skill-index-2026-11-02-session.md](references/skill-index-2026-11-02-session.md)** — 五 Phase 全綠；canonical 樹 5 個 `__pycache__` 清理；canonical↔workspace 真分歧 29→34（全部 Pattern TTT 不可機械同步：x-note 平台遷移 / Readme.md 用途不同 / inbox-check 規格版 vs 精簡版）；`.env`×4 備份覆蓋持續有效

## Pattern CCCC（2026-11-03 初發現）：cron watchdog 的「雙目標」是假的——script 不吃 argv

**發現經過**：cron job `33f50df6ac6b`（Neat-freak 每日四次雙目標掃描）連續紅燈逾 30 次，每次錯誤都是 `sync-check FAILED`。追查發現 `neat-freak-hourly.sh` 的 `check_target()` 以 **argv** 傳目標路徑（`python3 sync-check.py "$path"`），但：

- `sync-check.py` **不讀 argv**，只讀 `WORKSPACE_DIR`（預設 `~/Documents/Agent/skills/neat-freak`）與 `WORKSPACE_ROOT`
- `skill-index-check.py` **不讀 argv**，只讀 `AGENT_ROOT`（預設 `~/Documents/Agent`）

→ 「Vault」與「Agent」兩輪檢查跑的是**同一份 Agent workspace**，Vault 從未被檢查過。證據：`/tmp/neat-freak-Vault.log` 與 `/tmp/neat-freak-Agent.log` 逐 byte 相同。而 Vault 根本沒有 `skills/neat-freak`、也沒有 `docs/Skill_Index.md` → 對 Vault 跑 skill-index-check 本身就是無效操作。

**修法**：watchdog 一律用 **env** 指定路徑（`WORKSPACE_DIR=` / `WORKSPACE_ROOT=` / `AGENT_ROOT=`），不要傳 argv。Vault 目標改成只做「目錄存在 + git 狀態」。

- **預防**：新增 watchdog script 時，先讀目標 script 的 `os.environ.get(...)` 宣告，確認參數介面。傳了 script 不吃的參數 ≠ 有做檢查。
- **預防**：多目標 watchdog 應寫成「每目標一個明確 env 組合」，並在日誌檔名上區分；用 `diff` 兩個 log 就能立刻發現假檢查。

## Pattern DDDD（2026-11-03 初發現）：session 產物只寫 workspace、沒進 canonical

**這是 no_agent cron 連續 DRIFT 的常見根因**。neat-freak 維護 session 新寫的 `references/*.md` 若只落在 workspace sync copy（`~/Documents/Agent/skills/neat-freak/references/`），`sync-check.py` 每 tick 報 `EXTRA in workspace` → cron `failure_streak` 無限累積。

- **修復方向**：把這些檔 **copy 回 canonical** `~/.hermes/skills/neat-freak/references/`（它們是正當學習產物，canonical 才是權威源），**不是**刪 workspace 副本。
- **修完必做**：(1) 跑 `sync-check.py` 確認 `RESULT: CLEAN`；(2) 整個 cron watchdog 腳本手動跑一次確認 exit 0；(3) **負向測試**——故意在 workspace 加一個檔、故意讓 canonical 落後，兩種 drift 都必須讓 watchdog exit 1，否則只是把警報關掉而不是修好。
- **預防**：新增 references 檔一律先寫 canonical，再用 `scripts/sync-to-workspace.sh` 同步到 workspace。

## 附：2026-11-03 run 新增參考

- **[references/skill-index-2026-11-03-session.md](references/skill-index-2026-11-03-session.md)** — cron `33f50df6ac6b` 連續紅燈根因（Pattern CCCC 假雙目標 + Pattern DDDD session 產物只寫 workspace）；canonical 由 2085 → 2504 行（補回 7 個 session reference + 4 個內容落後 reference + workspace 較新 script）；watchdog 改用 env 介面並以兩種負向測試證明偵測機制仍有效
- **[references/skill-index-2026-11-03b-session.md](references/skill-index-2026-11-03b-session.md)** — ⚠️ 本檔「canonical↔workspace 真分歧首次歸零（34→0）」的斷言已被 11-04 run 實測推翻（filecmp 逐檔比對 34 檔分歧原樣存在、mtime 佐證從未同步過 → 11-03 是量測錯誤）。該 run 其他結論（Vault 再生 race、`sk-` sha256 裁決法）仍有效
- **[references/skill-index-2026-11-04-session.md](references/skill-index-2026-11-04-session.md)** — 「歸零」斷言必須附可複現命令＋輸出，測到與宣稱相反的狀態時先查 mtime 分辨「新腐敗」vs「上次量測錯」；ftfy 掃描範圍要標明（vendor/ 與 skill-backups/ 有 24 檔真實 mojibake，屬封存區不修，skills/ 兩樹才是攔截區）

## 附：2026-11-05 run 新增參考

- **[references/skill-index-2026-11-05-session.md](references/skill-index-2026-11-05-session.md)** — Pattern RRR-2 新增（purpose cell 語意不同步由 upstream 事件持續引入：frontmatter 改寫 3 檔 + 新增 row 手寫摘要 1 檔；RRR 補測必須每次 run 重跑、merge upstream 後立即重跑）；四檔 purpose cell 已同步並 push（761 三口徑一致、雙向比對 761=761、兩樹 frontmatter invalid 0）

## Pattern EEEE（2026-11-12 初發現）：watchdog 用 `pipe + grep -q` 判斷存在性 → pipefail 讓 SIGPIPE 翻轉成 false negative

**症狀**：`neat-freak-hourly.sh` 對 Vault repo 回報「✅ Vault git status clean」，但 `git status --short` 實際有 **483 筆**變更。Agent repo 的 clean 是真的，所以整體看起來正常。

**根因**：
```bash
set -uo pipefail
if git -C "$path" status --short | grep -q .; then
    echo "有未 commit 的變更"
else
    echo "git status clean"     # ← 錯誤分支
fi
```
`grep -q .` 找到第一個 match 就 exit(0) 並關管 → 上游 `git status` 收到 **SIGPIPE (141)**。`set -o pipefail` 規則是「pipeline exit code 取最右邊非零碼」，git 的 141 是非零 → pipeline 整體非零 → `if` 走 **else** → **有變更卻報 clean**。

實測：`set -uo pipefail; git status --short | grep -q .; echo $?` → **141**。
把輸出收進變數再判斷 → 正確回報 NONEMPTY。

**修法**：
```bash
CHANGES=$(git -C "$path" status --short)
CHANGE_COUNT=$(printf '%s\n' "$CHANGES" | grep -c . || true)
if [ "$CHANGE_COUNT" -gt 0 ]; then ... fi
```

**為什麼是重要 Pattern**：
1. 這與 **Pattern CCCC**（假雙目標）同源——watchdog 看似在檢查，檢查邏輯實際是壞的。**「watchdog 報綠燈」≠「被監控對象正常」**。
2. 與 **Pattern EEE / FFF** 同屬「量測方法本身會說謊」的類別。
3. 這個 watchdog 是 cron job `33f50df6ac6b` 的執行體，連續回報 ok，**Vault 真實狀態從未被看見**。

**預防**：
1. **不要用 pipe 做存在性判斷**：`cmd | grep -q .` 在 `pipefail` 下不可靠。要收進變數或用 `grep -c` 取數。
2. **watchdog 必須做負向測試**：故意製造一次異常，確認 watchdog 真的會紅。本次：先量到 Vault 483 筆變更 → 看 watchdog 報 clean → 修完 → 報 520 筆。**沒有負向測試的 watchdog 等於沒有 watchdog**（同 Pattern DDDD 的「修完必做負向測試」原則）。
3. 新寫帶 `set -o pipefail` 的 shell script 時，逐一支查 `grep -q` 用法（本次全庫確認 `~/.hermes/scripts/` 只有 `neat-freak-hourly.sh` 命中）。
4. **Summary 語意要區分警告與全綠**：有未 commit 變更時不該印「✅ 檢查通過」，否則 cron 交付文字會讀起來一切正常。

## 附：2026-11-12 run 新增參考

- **[references/skill-index-2026-11-12-session.md](references/skill-index-2026-11-12-session.md)** — Pattern EEEE 新增（watchdog pipefail+SIGPIPE false negative：Vault 483 筆變更卻報 clean，修完正確報 520 筆）；Vault 內 218 筆 ` D` 經逐檔比對確認為 Inbox→08-Learning 搬移（211 檔全等 + 7 檔僅 frontmatter/link 路徑差異，零內容遺失）；Agent repo 與 origin/main 已 0/0 同步（推翻前次「落後 3 commits」結論）；Hermes 備份 `20261112_041319 (2.0G)`；cron output retention 移除 12 檔
- **[references/skill-index-2026-11-12b-session.md](references/skill-index-2026-11-12b-session.md)** — 同日第二次 run（Hermes cron 18:07 CST = 10:07 UTC 推送）：五 Phase 全綠；sync-check DRIFT 為 **workspace 領先 canonical** 的反向形態（Pattern DDDD），以 superset 測試判方向後單向 workspace→canonical；11-03 reference 真分歧由 11-03/11-03b 更名機制拆開、canonical 兩份都收；孤兒 `.keep`（零引用 + cmp byte-identical 確診後 `git rm`）
- **[references/skill-index-2026-11-12c-session.md](references/skill-index-2026-11-12c-session.md)** — 同日第三次 run（OpenClaw cron 16:00 UTC）：**撞上同日第二次 run 的 competing commit**（兩套排程同時寫 `skill-index-2026-11-12-session.md` → add/add conflict）。處置沿用 11-03/11-03b 命名機制：第二 run 版本另存 `11-12b-session.md`（零刪除）、本次留在 `11-12-session.md`；**並查清 3 個週期 cron job 連續 `Connection error.` 的根因＝strata SSH tunnel（`127.0.0.1:8081` → v100）在 2026-11-08 v100 端服務重啟期間 `Connection refused`**（journalctl 佐證），三 job 共用同一 provider 故同時紅，非各自邏輯錯誤；dangling commit `31f037843` 經 `git diff` 驗證 **607 files / +57841 但 0 筆 D**（無檔案只存在於 dangling，無資料遺失）
