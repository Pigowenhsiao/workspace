# Branch Divergence 實戰處置參考

## 核心判斷徑（基於 2026-05-18 實戰）

### Step 1：量化複雜度

```bash
# 先看雙方 commit 數量比
git log --oneline origin/main -10   # remote 近期走向
git log --oneline HEAD -10          # local 近期走向

# 估算 Skill_Index.md 衝突規模（最常見的衝突源）
grep -c "^|||||||" docs/Skill_Index.md   # 衝突 block 數量
python3 ~/.hermes/skills/neat-freak/scripts/skill-index-check.py 2>/dev/null
# 口徑差距 > 20 行預警，> 50 行建議 abort
```

### Step 2：衝突分類

| 類型 | 跡象 | 處置 |
|------|------|------|
| **簡單編輯衝突** | 衝突 block ≤ 2 處，無大口徑差，git diff 可一眼看懂 | 人工 resolve 後 `git add` + `git rebase --continue` |
| **Skill_Index.md 結構衝突** | 多處衝突（≥ 3 處），口徑 drift 明顯（差 20+ 行），兩邊都更新了同一份 index | 建議 **abort**，手動 merge |
| **跨多檔案分散衝突** | origin 多功能並行落地，local 是 neat-freak 維護記錄 | 傾向 **merge --no-rebase**，保留維護歷史 |

### Step 3：實戰決策樹（2026-05-18 驗證）

```
branch divergence 發生
  │
  ├─ remote 落後 ≤ 5 commits，local 為 neat-freak 微量維護
  │   → git pull --rebase，衝突少則繼續，多則 abort
  │
  ├─ remote 落後 10+ commits 且有大量產品功能落地（ce-work, baoyu-* 等）
  │   → 先 abort，git pull --no-rebase 做 merge
  │   → 衝突時以 actual 行數重算 Skill_Index.md header
  │
  └─ Skill_Index.md 口徑差距 > 50 行
      → 視為「複雜」，abort，等人工裁決
      → 原因是口徑重算容易被任一側錯誤覆蓋
```

### Step 4：Abort 後的正確重新拉齊流程

```bash
# 1. 確認 abort 乾淨
git status  # 確認回到 rebase 前狀態

# 2. 用 merge 而非 rebase（保留 local 維護顆粒度）
git pull --no-rebase

# 3. 若有衝突，解決後：
git add -A
git commit -m "merge: resolve conflict during divergence resolution"

# 4. 口徑重算（在 merge commit 上做，不要在衝突側隨手改）
python3 ~/.hermes/skills/neat-freak/scripts/skill-index-check.py
# 手動重算 Skill_Index.md header counts

# 5. 驗證乾淨
git status && python3 ~/.hermes/skills/neat-freak/scripts/skill-index-check.py
```

## 教訓沉澱

### 為什麼直接 rebase 失敗了

- origin 的 Skill_Index.md 有大量產品功能（poster、baoyu-* 等），每次變更都更新 Summary counts
- local 的 neat-freak 維護記錄也在改 Skill_Index.md counts（remove deprecated skill、sync 等）
- 雙方都在同一個 568 行（當時）的基礎上各自墊高，rebase 時變成四處衝突

### 預防：口徑追蹤

每次執行 neat-freak 時，在 commit log 裡強制標記 Skill_Index.md actual 行數：
```
chore(neat-freak): sync — Skill_Index.md actual=568
```
這樣下次 divergence 時可以一秒看出差距量級。

## 相關腐蝕圖譜 Pattern

- Pattern I（第 10-14 條）：git stash / ls-tree / add -A 陷阱
- Pattern K（第 17-18 條）：conflict resolution 方向選錯導致 counts 錯誤
- Pattern M（第 23 條）：branch divergence 缺乏處置流程（本文補充實戰缺口）
