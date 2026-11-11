# neat-freak session — 2026-10-24 第十三 run

## 摘要

本次 run 的 Phase 3（Skills Consistency）觸發了三個「文件記載的驗證命令實際跑不出正確結果」
的腐敗——全部屬於 **Pattern LLL 家族**（文件描述的流程與實況不符），且互相疊加。

最終結果：Skill_Index.md 口徑 **759 = 759 = 759 = 759**（actual / Summary / Category Map / Section sum），
`skill-index-check.py` 回報 `✓ ALL CLEAN`。

---

## Phase 1 — Vault Git Health

- `git status --short` → 空；`git status` → 「沒有要提交的檔案，工作區為乾淨狀態」
- branch `main`，與 `origin/main` 一致，無 stash，無 ahead/behind
- 推播前安全斷言（Pattern AAAA）：
  - `git grep -cE 'sk-(cp|CMM)-[A-Za-z0-9_-]{60,}' HEAD --` → 0 命中
  - `git show HEAD | grep -cE 'sk-(cp|CMM)-[A-Za-z0-9_-]{60,}'` → 0 命中
- `git push origin main` → fast-forward，`origin/main` 已指向本地 HEAD

## Phase 2 — Memory Sync

`~/.hermes/memory/` 與 `~/Documents/Agent/memory/`：

- 檔案清單 `diff` → 完全相同
- `P0-core.md` / `P1-90days.md` / `P2-30days.md` → 逐檔 `diff -q` 皆 IDENTICAL

無需同步。

## Phase 3 — Skills Consistency（本次主要發現）

### 發現 1 — 自我修復 loop 只寫了一半（Pattern MMM）

`~/.hermes/skills/` 下存在兩個 `neat-freak`：

```
~/.hermes/skills/neat-freak/                 ← canonical（loader 實際載入這個）
~/.hermes/skills/productivity/neat-freak/    ← 較舊的結構化副本
```

兩者的 `SKILL.md` **sha256 完全相同**（`provably_same_skill()` → True），
`scripts/`、`agents/` 也完全一致，**但 `references/` 有 2 個檔案分歧**：

| 檔案 | canonical | productivity |
|------|-----------|--------------|
| `references/cron-output-retention.md` | 舊 | 新（多 25 行 Always-on 規則） |
| `references/hermes-backup-protocol.md` | 舊 | 新（多 8 行 Always-on 規則） |

**根因**：journal 顯示某次自我修復 review 對 `productivity/neat-freak` 執行了
`patched (references/cron-output-retention.md)` 與
`patched (references/hermes-backup-protocol.md)`，但**沒有同步到 canonical**。

**loader 實際載入哪一份**（實測，不是猜測）：

```python
from agent.skill_utils import provably_same_skill, skill_candidate_rank
provably_same_skill([a, b])                      # True
skill_candidate_rank(a, root)   # (False, 2)  ← canonical
skill_candidate_rank(b, root)   # (False, 3)  ← productivity
```

rank 較小者勝出 → **canonical 勝出**。所以「較新的內容」實際上**沒有生效**，
canonical 一直在服務舊內容。

**修復**：將 `productivity/` 的 2 個檔案覆蓋回 canonical，再同步到 workspace copy。
`diff -rq` 三處現已完全一致。

**預防**：
1. `~/.hermes/skills/` 內部的 category 雙軌**不在 `sync-check.py` 覆蓋範圍**
   （它只比 canonical vs workspace），必須另外用 `diff -rq` 或 `resolve_skill_catalog()` 掃
2. loader 遇到同名 skill 時，**rank 較淺的路徑勝出**——「比較新」不等於「會被載入」
3. 自我修復 loop 若 patch 了非 canonical 路徑，等於 patch 進黑洞

### 發現 2 — header regex 抓不到實際格式（Pattern LLL）

`Skill_Index.md` 的 Summary 行實際格式是：

```
- Active Skills: ***759***
```

**三個星號**。但 SKILL.md 與 4 份 live reference 記載的驗證 regex 是：

```python
re.search(r'Active Skills:\s*\*\*(\d+)\*\*', c)     # → NO MATCH
```

實測對照：

| regex | 對 `- Active Skills: ***759***` 的結果 |
|-------|---------------------------------------|
| `Active Skills:\s*\*\*(\d+)\*\*` | **NO MATCH** → header=None → 假 drift |
| `Active Skills:\s*(\d+)` | **NO MATCH** → header=None → 假 drift |
| `- Active Skills:\s*\*{2,3}(\d+)\*{2,3}` | **759** ✓ |

canonical `scripts/skill-index-check.py` 早就是對的（第 80 行）：
`re.search(r'- Active Skills:\s*\*{2,3}(\d+)\*{2,3}', idx_content)`。

**即：script 是對的，文件是錯的。** 任何照著文件跑「獨立驗證」的人都會拿到
`header = None` → 以為 index drift 了 → 可能「修壞」一個其實乾淨的 index。

**修復**：SKILL.md + 5 份 live reference 全部改為 canonical 的 `\*{2,3}` 形式。

**預防**：
1. **SKILL.md 記載的驗證命令必須實際執行過**，不能只靠「regex 看起來對」
2. 寫 regex 前先 `head -3` 看實際檔案長什麼樣（本例是 `- Active Skills: ***759***`，
   既有 dash prefix 又有三個星號）
3. script 與文件口徑不一致時，**script 通常是對的**（script 有人跑過，文件是抄的）

### 發現 3 — 口徑 count 漏掉 `'SKILL.md' in l` 條件（Pattern GGG 延伸）

`references/skill-index-false-drift-2026-07-22.md` 的「獨立驗證命令（當 drift 報告出現時，
必須先跑這個）」寫著：

```python
actual_rows = [l for l in lines if re.match(r'^\| [A-Za-z0-9]', l)]   # 缺 'SKILL.md' in l
```

少了 `'SKILL.md' in l` → Category Map 區段的數字列也被算進來：

| 條件 | 結果 |
|------|------|
| 無 `'SKILL.md' in l` | **768** → 與 header 759 差 9 → **假 drift** |
| 有 `'SKILL.md' in l` | **759** ✓ |

這與 Pattern GGG 是同一族：口徑 count 的**條件不完整**，導致數字對不上。
兩者疊加（`[a-z0-9]` + 缺 filter）會同時製造假 drift 與漏算。

**修復**：該檔的驗證命令重寫為可直接 `bash` 執行的 heredoc 形式，
並補上 `'SKILL.md' in l` filter；實測輸出 759/759/759、8 個 section 全部 ✓。

**預防**：
1. 口徑 count 的**每個條件都要有理由**——`'SKILL.md' in l` 排除的是 Category Map 的數字列
2. 文件裡的驗證命令必須**實際執行並貼出輸出**，不是「看起來對」就寫進去

### 發現 4 — canonical skill 內殘留 macOS/舊主機絕對路徑（Pattern HHH 延伸）

Pattern HHH（2026-10-24 第十一 run）修的是 SKILL.md + 5 份 reference；
本次掃描 code fence 內的路徑，又找到 **8 份檔案、17 處**：

```
/home/pigo/.hermes/cron/output/*/      ← Phase 4 清理腳本
/home/pigo/.hermes/cron/jobs.json      ← cron jobs 讀取
/home/pigo/.openclaw/openclaw.json     ← openclaw 設定
/Users/pigo/Documents/Agent/docs/...   ← 口徑驗證
/home/pigo/Documents/Agent/docs/...    ← 同上
```

**修復**：一律改為 `os.path.expanduser('~/...')`，並在需要時補 `import os`。

**陷阱：批次取代會產生無效 Python**。第一版腳本把
`'/home/pigo/.hermes/cron/jobs.json'` 換成 `'os.path.expanduser('~/.hermes')/cron/jobs.json'`
——巢狀引號 + 字串拼接，語法直接壞掉。**正確做法是取代整個引號字面量**：

```python
LITERAL_RE = re.compile(r"'((?:/Users/pigo|/home/pigo)[^'\n]*)'")
# → "os.path.expanduser('~/.hermes/cron/jobs.json')"
```

**陷阱 2：`python3 -c "` 殼層區塊裡的 `import os` 位置**。該區塊是 shell 不是 python，
頂層加 `import os` 會讓語法檢查失敗；必須插在**每個 `python3 -c "` 區塊內部**，
且只在該區塊真的用到 `os.path` 時才插。

**預防**：
1. 批次取代字串後，**必須跑 `ast.parse()` 驗證每個 python code block**
2. 只在 code fence 內取代，敘述文字的路徑要保留（例如 Pattern GGG 段落刻意引用
   舊的 buggy regex 作為歷史證據——本次誤改過一次，已還原）
3. `import os` 要依 code block 的語境決定位置，不是無腦加在頂端

### 發現 5 — repo 根 `neat-freak/SKILL.md` 三軌殘留

`~/Documents/Agent/neat-freak/SKILL.md`（1724 行）與
`~/Documents/Agent/skills/neat-freak/SKILL.md`（1823 行）內容不同但兩者都被 git 追蹤。

- `Skill_Index.md` 只引用 `skills/neat-freak/SKILL.md`
- `docs/Agent_Organization_Audit.md` 也只引用 `skills/neat-freak/SKILL.md`
- 但 SKILL.md 自身的檢查清單明列：`~/Documents/Agent/neat-freak/` **如果存在**，
  必須是 canonical 的正當 sync copy

→ 屬於「正當 sync copy」，**不是 workspace pollution**。本次以 canonical 覆蓋同步。

## Phase 4 — Cron Output Retention

```
50  b27de85df4a3
50  94b3875ed533
50  539040a91ad2
 7  89c411611e6d
```

門檻 500，最高 50 檔 → **無需清理**。

## Phase 5 — Hermes Backup

排程存在（job id `89c411611e6d`）。備份於前次 session 已驗證：
22 個 archive、10,161.9 MiB < 10,240 MiB 上限、tar pipe 修補後 rc=0。

---

## 驗證結果

| 檢查 | 結果 |
|------|------|
| Skill_Index actual rows | 759 |
| Summary header | 759 |
| Category Map sum | 759 |
| Section header sum | 759 |
| Per-section (8 個) | 全部 ✓ |
| `skill-index-check.py` | `✓ ALL CLEAN` |
| `sync-check.py` | `RESULT: CLEAN` |
| live code block `ast.parse()` | 20 個通過（僅 1 個 dated session record 為預期的 `/path/to/` 佔位符） |
| 口徑驗證命令實跑 | 759/759/759、8 section 全 ✓ |
