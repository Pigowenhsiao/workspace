# macOS Case-Insensitive Filesystem Pitfalls (Patterns R & S)

## Pattern R：macOS 大小寫混淆導致誤刪 git 追蹤檔（最高危險）

**觸發**：macOS 預設 HFS+/APFS 為 case-insensitive（`README.md` 和 `Readme.md` 視為同一檔案），當 `git` 只追蹤其中一個（如 `Readme.md`）而你嘗試刪除另一個（如 `rm README.md`）時，macOS 會把**已追蹤的檔案**當場刪掉，而不是刪除你想刪的「另一個」檔案。

**典型案例（本 session，2026-05-17）**：
- `git ls-files` 只追蹤 `Readme.md`（小寫）
- `README.md`（大寫）在磁碟上存在但不在 git 追蹤中（或是 orphan）
- 執行 `rm README.md` → macOS 將其解析為 `Readme.md`（同一 inode）→ **git 追蹤的檔案被刪除**
- `git status` 顯示 `deleted: Readme.md`，工作樹變髒

**難以發現的原因**：
- macOS Finder / shell 的 `ls` 顯示兩個不同檔名下，讓你以為它們是分開的
- `stat Readme.md` 和 `stat README.md` 回傳同一個 inode（但 `ls -i` 有時只顯示一個）
- `rm README.md` 在 bash 中**沒有任何警告**

**正確刪除 orphan 副本的流程**：
```bash
# Step 1：確認 git 追蹤哪個大小寫
git ls-files -- "README.md" "Readme.md"

# Step 2：如果只追蹤 Readme.md 且 README.md 也存在，先確認 inode
ls -i README.md Readme.md 2>/dev/null

# Step 3：安全刪除 orphan 副本：用 mv 移到 /tmp 驗證
mv README.md /tmp/README.md.backup

# Step 4：驗證
git status --short
```

**預防**：刪任何 `.md` 檔案前，先 `git ls-files -- "<exact-name>"` 確認是否被追蹤。發現 workspace 有大小寫重複的 `.md` 檔案時，用 `git rm --cached` 從 git 移除不該追蹤的，再用 `rm` 刪除磁碟上的 orphan。

---

## Pattern S：Branch divergence 導致 upstream sync copy 的 agents/ 目錄被誤判為污染

**觸發**：當 workspace sync copy 的 `agents/openai.yaml` 來自 origin/main 的 commit（legitimate upstream addition），但 canonical（`~/.hermes/skills/neat-freak/`）從未定義過 `agents/` 時，sync-check.py 會把 `agents/` 報告為 `EXTRA in workspace`，誤判為 workspace pollution。

**典型案例（本 session，2026-05-17）**：
- `git show origin/main:skills/neat-freak/agents/openai.yaml` 有內容
- `ls ~/.hermes/skills/neat-freak/agents/` → `NO_CANONICAL_AGENTS`
- `sync-check.py` 回報：`EXTRA in workspace (1): + agents`

**正確判斷邏輯**：
```bash
# canonical 有無 agents/？
ls ~/.hermes/skills/neat-freak/agents/ 2>/dev/null || echo "NO_CANONICAL_AGENTS"

# origin/main 有無 agents/？
git -C ~/Documents/Agent show origin/main:skills/neat-freak/agents/openai.yaml 2>/dev/null | wc -l

# 判斷：
# - canonical 無、origin/main 有 → upstream 擴充，保留
# - canonical 無、origin/main 無 → local workspace 新增，評估後決定
# - canonical 有、origin/main 有 → 正常 sync，保留
```

**預防**：當 sync-check.py 報告 `EXTRA in workspace` 時，不要直接刪除。先確認 origin/main 有無該內容，再決定是 upstream 擴充（保留）還是 workspace pollution（刪除）。
