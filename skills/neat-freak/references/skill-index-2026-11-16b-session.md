# neat-freak session — 2026-11-16（04:00 UTC run，OpenClaw cron `31f0439f`）

> 同日已有 Hermes cron 的 00:00 CST run（`skill-index-2026-11-16-session.md`）。本檔為 04:00 UTC 這輪，沿用 `_b` 後綴以免覆蓋。

## 結果摘要：五 Phase 完成；本輪實際修復 = Pattern HHH（同名 skill ambiguity 復發）

| Phase | 結果 |
|---|---|
| 1 Vault git | `origin/main...HEAD = 0/0`；working tree 僅 1 個 untracked QA 報告（其他 session 產物，未動）；`git fsck` = 4 dangling tree + 2 dangling commit，逐一定性後**未刪**（含 917M 保護 bundle／21 refs，仍待裁決） |
| 2 Memory | `~/.hermes/memory/{P0-core,P1-90days,P2-30days}.md` ↔ `~/Documents/Agent/memory/` 逐 byte 相同；`memory/index.md` 19 條連結 missing=0 |
| 3 Skills | **Pattern HHH 修復**：stale `productivity/mail-triage` 移入 `.archive/`；cron-declared 12 個 skill `skill_view()` = 12/12 success；canonical neat-freak 補回 upstream 11-15／11-16 reference 與 Pattern GGGG；五份 SKILL.md md5 全等 `70e781e1e4bc800ff1749065a4eed290`；`skill-index-check.py` = 760 rows／header 760／8 sections ALL CLEAN |
| 4 Cron output | 移除 45 個 >7 天舊輸出檔；複掃 old_remaining=0；`~/.hermes/cron/output` = 4.0M（root 層 44 個 `*_handover.md` 仍不在腳本掃描範圍） |
| 5 Backup | 建立 `~/.hermes/workspace-backups/20261116_042541`（2.0G），prune 最舊一份，維持 14 份；另確認每日 tarball `~/Documents/hermes-backups/hermes-backup-20261116_000028.tar.gz`（2.7M）已產出；磁碟 32G 可用（85%） |

## 本輪主要修復：Pattern HHH — 上游 job 改寫 canonical 副本，讓已修好的 ambiguity 復發

### 症狀

11-13 run（Pattern FFFF）把 `~/.hermes/skills/productivity/mail-triage` 覆寫成 root `mail-triage` 的 byte-identical 副本，量測 12/12 success。
11-16 02:44 的「每日 Gmail Ingest → llm-wiki → Push」job **改寫了 root `~/.hermes/skills/mail-triage/`**：

- `SKILL.md`：索引 wikilink 必須帶 `.md`、legacy 早已是 LF-only（不可硬寫 `\r\n`）、不可用 `git add -A`（HF cron 曾掃走別人的筆記）
- `references/batch-ingest-workflow.md`：log 欄位數檢查（awk NF=8）、前輪遺留郵件清理、只 stage 明確檔案清單

root 變新後兩份再次分歧（SKILL.md 差 12 行、reference 差 28 行），04:15 量測即得到：

```
Skill name collision for 'mail-triage': 2 candidates — /home/pigo/.hermes/skills/mail-triage/SKILL.md; /home/pigo/.hermes/skills/productivity/mail-triage/SKILL.md
```

→ 宣告 `mail-triage` 的 Gmail cron 再次面臨「skill 被 skip 但 job 報綠燈」風險（Pattern FFFF 的 live 復發）。

### 根因

Pattern FFFF 的「覆寫成 byte-identical → loader `provably_same_skill()` 自動解析」只保證**當下**一致，**不保證上游 job 不會再動其中一份**。
任何一方被改寫，identical 前提立即失效 → ambiguity 復發。

### 處置（零覆寫、零刪除）

1. 先備份：`tar -czf ~/.hermes/cache/scratch/mail-triage-collision-20261116_0415.tar.gz -C ~/.hermes/skills productivity/mail-triage`（23K）
2. 將整棵 stale 樹移出 loader 掃描路徑：`mv ~/.hermes/skills/productivity/mail-triage ~/.hermes/skills/.archive/productivity-mail-triage-20261116`
   （`.archive` 在 `EXCLUDED_SKILL_DIRS` 內 → 不再參與 skill discovery）
3. 負向／正向雙向驗證：
   - 修前：12 個 cron-declared skill 中 `mail-triage` unresolvable
   - 修後：`skills=12, unresolvable=[]`，`mail_triage=True`
4. 新 Pattern HHH 已寫入 canonical `SKILL.md`（含復發機制、預防規則、同日 `11-16b` reference 連結）

## canonical neat-freak 補同步（Pattern DDDD 反向形態再現）

比對 canonical 與 Agent `origin/main` 的 `skills/neat-freak/`：

- upstream 獨有：`README.md`、`Readme.md`、`references/skill-index-2026-11-15-session.md`、`references/skill-index-2026-11-16-session.md`
- canonical 獨有：無
- `SKILL.md` 差 27 行（Pattern GGGG + 11-15／11-16 附錄）

處置（方向判定：upstream 為嚴格超集 → upstream → canonical）：
- `cp` upstream `SKILL.md` → canonical（2,666 行，含 Pattern GGGG）
- `cp` upstream 兩份 session reference → canonical
- `sync-to-workspace.sh` 同步至 `~/Documents/Agent/skills/neat-freak/`
- 再手動同步兩份 repo-root 副本：`~/Documents/Agent/neat-freak/SKILL.md`、`~/.openclaw/workspace/neat-freak/SKILL.md`
- 再同步 OpenClaw workspace 副本 `~/.openclaw/workspace/skills/neat-freak/`（含 2 份新 reference）

驗證：`sync-check.py` 對 Agent 與 OpenClaw（帶 `WORKSPACE_DIR` / `WORKSPACE_ROOT`）皆 `RESULT: CLEAN`；
五份 `SKILL.md` md5 全等 `70e781e1e4bc800ff1749065a4eed290`；`verify-skill-frontmatter.sh` = `[OK] name=neat-freak`。

> 註：本輪在 canonical 又新增 Pattern HHH 與 11-16b 附錄後，五份副本的 md5 已由 `70e781e1…` 再變一次（以檔案當下實測為準；下次 run 需重算）。

## Vault 盤點

- `origin/main...HEAD = 0/0`；`git ls-remote` 確認遠端 = `6f91b3926`（含在 origin/main）
- working tree：僅 `?? 99_Output/2026-11-15_x-note-QA-Review.md`（x-agent 其他 session 產物，未動）
- `git fsck --full`：4 dangling tree + 2 dangling commit
  - `47de2ee2b`（autostash，base = 11-13 `63e52ac37`）：相對 HEAD 僅 1 筆 `D`（舊 Inbox 檔名），該筆記已以全形標點剝除的新檔名落位於 `08-Learning/AI-Agent/`（4,397 bytes 完整保留）→ 搬移非遺失
  - `31f037843`：相對 HEAD 僅 `D 11-MOC/index.md` → 已由 11-13 commit `74c919f83` 以大小寫碰撞去重處置，HEAD 現為 `11-MOC/Index.md`
  - `.git/neat-freak-dangling-backup-2026-11-11.bundle`（917M）＋ 21 個保護 refs 仍在 → **本輪未刪**（需 Pigo 裁決）
- `git stash list`：1 筆 `autostash`（`c75aa024e`，base = 11-13 `aab55ff52`，非 HEAD ancestor）
  - 逐檔比對：stash 的 `00-Inbox/index.md` / `LLM-Wiki-Index.md` 新增的 71 個 x-note 索引列，其目標筆記皆已由 11-15 commit `b95a327a5` 搬到 `X-Notes/{author}/`；`LLM-Wiki-Ingest-Log.md` 新增內容已全數存在於 HEAD
  - 判定：stash 內容已被 HEAD 以**不同路徑**涵蓋 → 屬歷史 autostash 殘留，**未 drop**（保持零刪除，待人工裁決）
- `.vault-index/index_vault.py --mode incremental` → scanned 17,654 / changed 542 / created 268 / deleted 79；`notes.db` 更新於 2026-11-16T04:29:16Z
- wikilink 健康：`scripts/check_wikilinks.py` → 17,838 檔、96,915 wikilink、**20,346 個斷鏈目標**（32,162 處引用）
  - 11-11 baseline（tree `163d69608`）= 20,668 → **下降 322**，非本輪引入的新腐敗
  - 本輪未批次改寫 wikilink（既有 legacy/MOC 債，屬人工裁決範圍）
- `vault-supersede-audit.py` → scanned 17,845；auto-superseded **0**；396 筆舊＋時間敏感筆記需人工判讀（多為歷史新聞／人物／教學文件，關鍵字誤命中比例高，未自動改寫）

## Agent repo 狀態

- `origin/main...HEAD = 6/0`（本地落後 6 commits：memory sync 11-15/16、Pattern GGGG、11-15 reference 回補、vault-check purpose 語意同步、SD.cpp status、x-agent artifact 同步）
- 本地另有其他 session 產物未 commit：`skills/x-agent/artifacts/x-agent-state.md`（+40 行，2026-11-15 批次 state）＋ 21 個 untracked artifact JSON
- 其中 8 個 2026-11-15 artifact JSON **不在 upstream**，屬尚未提交的本地成果 → 本輪未混入 neat-freak commit、未 commit、未 push
- `memory/{P0-core,P1-90days,P2-30days}.md` local == canonical == origin/main（byte-identical）
- `docs/Skill_Index.md` upstream 獨立重算：actual rows 760 / header 760 / missing_on_disk 0 → 全綠

## OpenClaw workspace 狀態

- `origin/master...HEAD = 0/3`（ahead：`feba1fa` Pattern FFFF MEMORY 條目、`e250959` Pattern FFFF session、`f493817` research-heartbeat 修復）
- working tree 另有其他 session 成果：6 modified + 58 untracked（DREAMS.md、dreaming journals、codex-helper、google-finance parser、lightpanda、skills/anatomy、skills/model-catalog-prune 等）→ **未動、未混入**
- 本輪同步了 `skills/neat-freak/`（+2 reference）與 repo-root `neat-freak/SKILL.md`

## Cron job 狀態

- 22 個 Hermes cron jobs：21 `last_status=ok`、1 `error`
- 唯一 error：`6688a47a4861`「X 帳號監控 + QA（AM6 TWT）」，2026-11-15 22:01 UTC
  - 根因：**cron prompt 要求 MiniMax，但 `x-agent/SKILL.md` 明確指定 OMP 的 OpenAI Codex OAuth**（禁止回退 MiniMax／OpenRouter）→ agent 無法確認路由而中止
  - 已明確回報：未寫入 Vault、未執行 QA、未 commit/push → **零資料遺失**
  - 與 11-13 交接的 strata tunnel 問題不同（該 tunnel `127.0.0.1:8081/v1/models` 本輪回 401 = 服務活著）
- 本輪 cron-declared skill 量測（loader venv）→ 12/12 success（修 HHH 後）

## RTK 效益

- 累計：17,408 cmds / 172.0M in / 12.9M out / **省 159.1M（92.5%）**；avg 838ms/cmd
- 本週（11-16 當週）516 cmds / 1.0M in / 65.8K out / **省 969.5K（93.7%）**

## 未處理（移交 Pigo 裁決）

1. **917M Vault dangling 保護 bundle + 21 refs**：本輪再次驗證兩個 dangling commit 無資料遺失，32G 可用空間尚不急迫 → 維持保留。
2. **Vault autostash `c75aa024e`**：內容已被 HEAD 以不同路徑涵蓋，但未 drop（零刪除原則）。
3. **Agent repo 落後 6 commits + 21 個未提交 artifact JSON**：是否由 x-agent session 自行收尾並 push。
4. **OpenClaw workspace 3 個 ahead commits + 64 筆其他 session 變更**：是否統一檢查後再推。
5. **X 帳號監控 cron 的模型路由衝突**：cron prompt（MiniMax）vs `x-agent/SKILL.md`（Codex OAuth）二選一。
6. **Vault 架構三題仍待定調**：LLM-Wiki-Index 三副本、`08-Learning/AI-News` vs `10-LLM-Wiki/AI-News` 路由、7,009 distinct tags 白名單。
7. **全庫 wikilink 20,346 斷鏈**：較 11-11 baseline 下降 322，但屬長期 legacy/MOC 債，維持不批次改寫。
