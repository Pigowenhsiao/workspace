# neat-freak session — 2026-11-16（00:00 CST run，Hermes cron）

## 結果摘要：五 Phase 全綠；主要產出是 00-Inbox/index.md 斷鏈清零（16→0）

| Phase | 結果 |
|---|---|
| 1 Vault git | 兩 repo `git status` 乾淨、與 origin/main 同步；兩 repo `git fsck` 完全無輸出（無需 Pattern EEE/KKK） |
| 2 Memory | P0-core / P1-90days / P2-30days 三檔 sha256 byte-identical（~/.hermes/memory ↔ Agent/memory） |
| 3 Skills | sync-check CLEAN（結構+內容+repo-root）；skill-index-check 7 項全綠（760 三口徑一致）；RRR 語意補測（frontmatter mtime > 11-15 的 10 檔）：neat-freak jac=0.37 OK、vault-check/x-agent 已於 11-15 修過、其餘 9 檔不存在於 Skill_Index——確認為 **Hermes 專屬 skills**（`~/.hermes/skills/{hermes,media,devops,browser-automation}/`），Agent 樹無對應目錄、不在 index 管轄，非漂移；ftfy 掃描 0 命中 |
| 4 Cron output | 9 個 job 目錄，最大 50 檔（<500），無需清理 |
| 5 Backup | `~/Documents/Backup/hermes/hermes_2026-11-15_030039.tar.gz`（487MB）昨日 03:00 已產出；本機 cron 00:00 距下一次 03:00 backup 尚早 |

## 本次實際修復：00-Inbox/index.md 斷鏈 16 → 0

11-15 run 聲稱「16 broken = gitignored transcript scratch」，實測**只有 5 條是 transcript**，其餘定性錯誤。逐條 NFC-normalize candidate 配對後處置（commit `61d660bd9`）：

1. **7 條 11-13 arXiv 行**（醫療影像分割／對比式發現／代理評測／ReTrace／Re-Search／BEHAVIOR／兩個社群）：
   - 連結用「帶全形冒號」的舊 inbox 檔名，檔案 11-15 已落位 `08-Learning/05_Papers/arxiv/` 且**落位時被剝掉全形標點**（：、，）。
   - `08-Learning/05_Papers/index.md` 用的是正確 filed 路徑，只有 `00-Inbox/index.md` 這批沒 remap——上次 triage 的漏網。
   - 全部改指 filed 路徑。
2. **1 條 yibie 105458**：`./` 舊鏈 → 改指 `08-Learning/AI-News/` filed 版（1603 行已有同目標連結，去重 1563 行完全重複列）。
3. **2 條幽靈 x-note**（wallstengine 497734、xiaoxiaodong 864924）：`git log --all --name-only` 全歷史查無 → **從未進過 git**，僅 99_Output poster summary 有原文 URL 佐證。列為純文字「（筆記缺失）」標記，保留日期/作者/評分 metadata，不刪行。
4. **5 條 transcript scratch**（6pYhK6xRuHE / MrmO_XMJLhE ×2 重複列 / MzklWMQ87Yw ×2 / article2media yaml）：檔案 gitignored 且已清除（09-Article-Notes 無對應檔）。改純文字「（scratch 已清除）」。
5. **1 條 wikilink**：`08-Learning/02_Knowledge-Systems/2026-11-13_every_ai…` 筆記的相關筆記區引用 `[[00-Inbox/2026-11-13_arXiv_ReTrace：…]]` → 改 filed 路徑。

## 教訓（沉澱為 Pattern GGGG）：「transcript scratch」標籤不能被當成斷鏈免死金牌

- 11-15 commit message 寫 "16 broken, rest are gitignored transcript scratch"，實際僅 5/16 為 transcript；7 條是**可 remap 的落位漏網**、2 條是幽靈檔案。
- 判定規則：每條斷鏈都要跑 `git log --all --name-only | grep` （幽靈與否）+ NFC normalize basename 配對（remap 與否），不能依上次 run 的籠統標籤跳過。
- 另注意：**落位腳本會剝掉檔名中的全形標點（：，）**，index 連結若用原始標題檔名就會斷；triage remap 時要用 `git show` 後的實際檔名，不是來源標題。

## 其他盤點（未處置，理由如下）

- **00-Inbox**：只剩 index.md / log.md / STATUS_ALL.md，維持 11-15 結論（Pigo 政策：Inbox 是 active intake zone，留空是常態不是問題）。
- **tags 一致性**：全庫 15,621 檔有 tags、7,009 個 distinct 值（主要變體源：作者 handle 大小寫如 `voxyz_ai`/`Voxyz_ai`、`AIllm-wiki x-post` 這類含空格多字標籤）。白名單定稿仍是 Pigo 人工裁決範圍（VAULT-OVERVIEW.md 明示「不得自行新增/批次改寫標籤」），維持 11-13 結論不動。
- **兩棵重複筆記**：`08-Learning/AI-News` vs `10-LLM-Wiki/AI-News` 15 個同名檔（14 內容有差異、1 全同），另有 `01_AI-Agent` vs `X-Notes/yibie` 兩對、Gary-Chen MzklWMQ87Yw 兩份——`12-Meta/vault-structure.md` 明載 AI-News 存 `10-LLM-Wiki/AI-News/`，`08-Learning/AI-News/`（352 檔）疑似 mac-side 舊路由產物。去重涉及刪除，屬 Pigo 裁決範圍，列 unresolved。
- **根目錄 STATUS_x-agent.md / STATUS_2026-10-26_Vault-Overview-Draft.md**：內容已 COMPLETED、與 00-Inbox/STATUS_ALL.md 无重疊；12-Meta/vault-deep-clean-report-2026-11-10 的 Pending Approval Plan 明確「保留兩版並標記 review」等 Pigo 裁決——不動（Pattern DD 根目錄檔案處理規則）。
- **根目錄 LLM-Wiki-Index.md（538KB）vs 08-Learning/99_Maintenance/status/LLM-Wiki-Index.md（482KB）**：雙軌並存、mtime 不同（11-15 00:09 vs 12:21），兩者都被 cron 寫入。屬 llm-wiki skill 路由問題，非本次 neat-freak 範圍，列 unresolved 給 Pigo。
- **Agent repo 根目錄 ~40 支 2026-09 一次性 xlsx 處理腳本**（create/verify/inspect/repair_*.py）+ 5 個 2.1MB xnote JSON：全數 git tracked、xnote JSON 被 x-agent scripts 引用。移入 archive 屬大動作且 Pigo 未授權，維持 11-15 不處置結論。
- **18-Wealth overlong-path warnings**：每日要聞目錄名超長，`git status` 仍可運作僅警告；既有 11-13 run 已記錄 fixup 過一輪，不重複處理。

## 未處理（移交 Pigo 裁決）

1. `08-Learning/AI-News/`（352 檔）與 `10-LLM-Wiki/AI-News/`（917 檔）路由去重（vault-structure.md 只認後者）。
2. 全庫 wikilink 斷鏈 32.5k legacy/MOC 債（維持 11-13/11-15 結論）。
3. 標籤白名單定稿（7,009 distinct 值）。
4. 根目錄 LLM-Wiki-Index.md 雙軌問題。
