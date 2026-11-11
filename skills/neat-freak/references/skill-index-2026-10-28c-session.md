# neat-freak session — 2026-10-28（15th run，13:40 CST）

**Job:** `539040a91ad2`（Vault 整潔同步 / neat-freak，每 120 分鐘）
**Result:** 五 Phase 全綠。Vault / Agent repo 工作樹皆乾淨且與 origin 同步；memory 雙軌 byte-identical；
`skill-index-check.py` ✓ ALL CLEAN（760 = 760 = 8 sections）；cron output 全 < 500；backup 排程今日已跑。

本次實際變更（皆為機械式可判定項）：

1. **canonical `vault-check` / `vault-GPS` 的 Windows vault 路徑 → Linux**
   `C:\Users\hsi67063\Box\00-home-pigo.hsiao\VBA\Pigo_Obsidian` → `~/Documents/Pigo_Obsidian`
   （含 `.vault-index/query_vault.py` / `notes.db` 子路徑的反斜線 → 正斜線）。
   這兩檔的 Windows 路徑是同類 skill（`vault-deep-clean`、`vault-rag*`、`vault-index`、
   `vault-triage-workflow`）早已遷移完的殘留，canonical 內 12 個 `vault-*` skill 本就混用兩套路徑。
   binary 模式改寫（Pattern SS），改後 YAML frontmatter 仍可解析。

2. **canonical → workspace 單向同步 `vault-check`**
   方向依 2026-10-27b 的新規則（mtime + 內容 superset 實測）判定：canonical mtime 較新
   （12:51 vs 10-22）且為嚴格超集（canon-only 10 行、ws-only 0 行）→ canonical → workspace。
   跨樹比對**以相對路徑為 key**（`vault-check`），非 frontmatter `name`（Pattern 2026-10-28 事故教訓）。

3. **`Skill_Index.md` 27 個 purpose cell 與 frontmatter 敘述不同步 → 依 frontmatter 重寫**
   兩類退化：
   - **陳舊**：index 寫的是舊版 description（如 `executing-plans` 寫「separate session」，
     檔案已是「in the current session」）。
   - **退化為非描述文字**：`llm-wiki` 三個副本的 purpose cell 是 `Path to the active vault root`；
     `web-access` 是 `# web-access Skill`；`Paper-Read` 是 `# Skill Definition: Academic-Omni-Router`
     → 這些是 Pattern OOO-2（frontmatter 缺 fence → body 首行被當 description）的 downstream 症狀。

   **為什麼舊檢查抓不到**：`skill-index-check.py` 只驗「口徑一致性 / dangling / purpose cell 的
   `\` 與 placeholder 型腐蝕」，**不驗 purpose cell 與 frontmatter 敘述的語意一致性**。
   補測方法（用 `/usr/bin/python3`，Hermes venv 沒有 `yaml`）：

   ```python
   rows = re.findall(r'^\|\s*([^|]*?)\s*\|\s*(skills/[^\s|]*SKILL\.md)\s*\|\s*([^|]*?)\s*\|', idx, re.M)
   # 對每列：讀 SKILL.md → yaml.safe_load(frontmatter) → 比 description 前 60 字
   # 排除 d.startswith('#') / 'Path to the active'（退化值），這些需人工補 frontmatter
   ```

   27 個全部改寫後，index 口徑不變（760），8 個 section header 全對，`skill-index-check.py` 仍 ✓ ALL CLEAN。

4. **`Agents_2.md` / `Agents_3.md` 的 OPENSPEC 陳屍（Pattern 22 機械式修復）**
   `openspec/` 目錄經 `find` 確認**從未存在**（不在磁碟、不在 git history）→
   依 Pattern 22 刪除 `Agents_3.md` 的 `<!-- OPENSPEC:START -->…<!-- OPENSPEC:END -->` managed block
   與 `Agents_2.md` 的 `## 1. OpenSpec Instructions` 段落。
   同時把 `C:\Users\hsi67063\.codex\superpowers` → `~/Documents/Agent/skills/agent-workflows/superpowers`
   （實際存在），PowerShell `Test-Path` → `ls`。`Agents_2.md` 章節編號重排為連續 1–15。
   > 註：`Agents_2.md` 的 block 寫著「Do not remove this block」，但它指向的目標檔不存在，
   > 留著只會誤導 agent 讀一個從來不存在的路徑 → 依 Pattern 22「managed block 刪除前確認
   > target 目錄是否存在」的規則處理。

## 觀察（不動作，留待裁決）

- **canonical 84 組同名三軌重疊** → 架構決策，需 Pigo 指定「哪一軌是現行版」。
  本次比對一律以**相對路徑**為 key（`vault-check`），未使用 `name`。
- **workspace 內 10 檔仍含 Windows vault 路徑**（`knowledge-vault/*` 的 8 個 + `browser-web-social/X-note`）：
  這些在 canonical 樹**沒有對應檔案**（canonical 是扁平 `vault-*` 樹，workspace 是 `knowledge-vault/` 分類樹），
  無法用「以 canonical 為準」直接同步。要不要一併遷移屬跨樹政策決策 → 留待裁決。
- **canonical 內 `vault-knowledge` 仍指 `C:\Users\pigow\.codex\.path-config.json`**：
  這是刻意設計（讀 Windows 端的 path-config 來解析路徑，非本機路徑）→ 不改。
- **兩檔 workspace `README.md` 與 canonical `Readme.md` 檔名大小寫不同**
  （`skills/vault-check/README.md` vs canonical `Readme.md`）→ 兩者內容體系不同
  （前者是手寫 skill 說明，後者是 Codex 目錄生成器產物），非 drift，不合併。
- **兩個 neat-freak job（`539040a91ad2`、`b27de85df4a3`）同為 120 分鐘** → 互相踩踏風險仍未解。

## 驗證紀錄

- `sync-check.py` → `RESULT: CLEAN`（canonical vs workspace neat-freak 結構 + 內容逐檔 diff 無差異）
- `skill-index-check.py` → `✓ ALL CLEAN`（760 = 760；8 sections；0 dangling；0 purpose corruption）
- 獨立 Python 三口徑重算 → actual 760 / header 760 / 8 sections 全對
- YAML frontmatter 掃描（canonical 934 + workspace 1578）→ invalid 0、無 fence 0
- ftfy badness 掃描（canonical skills / workspace skills / 雙樹 memory / vault）→ >50 者 0 檔
- Vault `git fsck --full` → 完全無輸出；Agent repo `git fsck --full` → 完全無輸出
