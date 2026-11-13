# neat-freak session reference — 2026-11-13（16:00 UTC run，OpenClaw cron `31f0439f`）

> 本檔為同日第二份 reference（第一份：`skill-index-2026-11-13-session.md`，凌晨 04:00 run）。
> 命名沿用 repo 既有的 `-session` / `-b-session` / `-c-session` 機制，零刪除。

## 本輪主軸：修掉兩個「cron 悄悄跳過 skill」的 live 故障

### 發現

`~/.hermes/logs/agent.log*` 內出現 `cron.scheduler: Cron job '每日 Gmail Ingest → llm-wiki → Push': Ambiguous skill name mail-triage: use one of productivity/mail-triage — skipping`。
這不是歷史噪音：**2026-11-13 02:00 的當日排程**（agent.log 第 1994 行）就是這樣被跳過的。

量測（用 hermes-agent 自己的 venv 跑 `skill_view`，這是 loader 的真實路徑，不是模擬）：

```bash
cd ~/.hermes/hermes-agent && ./.venv/bin/python -c "
import sys,json; sys.path.insert(0,'/home/pigo/.hermes/hermes-agent')
from tools.skills_tool import skill_view
d=json.load(open('/home/pigo/.hermes/cron/jobs.json'))
jobs = d if isinstance(d,list) else d.get('jobs',d)
if isinstance(jobs,dict): jobs=list(jobs.values())
names=set()
for j in jobs:
    for s in (j.get('skills') or []): names.add(s)
for n in sorted(names):
    print(n, json.loads(skill_view(name=n)).get('success'))
"
```

修前結果：`llm-wiki` = False、`mail-triage` = False（其餘 10 個 True）。
修後結果：**12/12 全部 True，TOTAL_UNRESOLVABLE = 0**。

### 根因

Hermes 的 skill loader（`tools/skills_tool.locate_skill`）在同一 tier 遇到**同名但內容不同**的 skill 時不猜，直接回 `Ambiguous skill name`；cron scheduler（`cron/scheduler_prompt._load_cron_skill_parts`）收到後就 `_skip(...)`，**整個 skill 從 prompt 裡消失，job 仍然 `last_status=ok`**。

即：**兩個 cron job 正在「成功」地跑，但沒有帶著它們宣告的 skill 跑**。這與 Pattern EEEE（watchdog 報綠燈但實際紅）同源——量測層報綠、被量測對象是壞的。

### 修了什麼（全部零刪除、全部先備份）

備份：`~/.hermes/cache/scratch/skill-collision-backup-20261113_1640.tar.gz`（582,753 bytes，涵蓋 10 個目錄）。

| skill | 衝突來源 | 處置 |
|---|---|---|
| `neat-freak` | `~/.hermes/skills/productivity/neat-freak/`（舊副本，1051 行 vs canonical 1941 行） | **canonical → productivity 單向覆寫**（`cp -a neat-freak/. productivity/neat-freak/`）。先驗證 productivity 副本是 canonical 的嚴格子集（獨有檔案 = 0）才覆寫，覆寫後 `diff -r` exit 0 |
| `mail-triage` | `~/.hermes/skills/productivity/mail-triage/`（406 行 vs canonical 395 行） | 同上。覆寫前逐行比對確認 productivity 缺的 18 行在 canonical 皆有（reddit `.rss` → `web_extract?utm_source=share`、frontmatter 欄位清單、ingest log 格式…） |
| `llm-wiki` | root `~/.hermes/skills/llm-wiki/`（v3.1.0-darwin，348 行）vs `research/llm-wiki/`（v2.4.1，602 行） | **兩者內容不同 → 單向覆寫會吃掉一邊的獨有內容**，所以走「先保全再移出掃描路徑」：<br>1. `research/llm-wiki/scripts/` ← root 的 4 個腳本（build.sh / bootstrap.sh / build_lumentum_weekly_relation_index.py / Readme.md）<br>2. `research/llm-wiki/references/` ← root 獨有的 4 個 reference（article-template / heartbeat-integration / wiki-playbook / youtube-obsidian-notion-ingest-SKILL）<br>3. root 整棵搬到 `~/.hermes/skills/.archive/llm-wiki-root-v3-20261113/llm-wiki/`（`.archive` 在 `EXCLUDED_SKILL_DIRS`，不參與掃描）<br>4. 驗證 `skill_view(name='research/llm-wiki')` → success=True |
| `Article-writer` / `daily-news-briefing-runner` | `productivity/` 與 `creative/` 副本 | **未動**：兩者都不是 cron job 宣告的 skill（cron 只用 `article-to-obsidian-knowledge`、`follow-builders` 等），且內容雙向分歧（top-only 125 行 / prod-only 88 行），屬架構決策，見 Decision Needed |

修前 `neat-freak` / `mail-triage` 是「同名不同內容」→ ambiguous；**同步成 byte-identical 後 loader 的 `provably_same_skill()` 就會判定為同一份 skill**，bare name 直接可解析——這是 Pattern BBB 記載的正解，本次實測再次驗證。

### 其他量測結果（本輪）

- **Vault**：`~/Documents/Pigo_Obsidian` working tree **0 筆**、HEAD `c5072d363`、`origin/main...HEAD = 0/0`。本次 fetch 後由 `603aca4a5` fast-forward 到 `c5072d363`（215 A + 50 M + **0 D**）。`git fsck --full` → 3 dangling tree + 1 dangling commit `31f037843`（`git diff --diff-filter=D 31f037843 HEAD` = 1 筆 `D 11-MOC/index.md`，該檔已由凌晨 run 的 `74c919f83` 明確去重處置 → 無資料遺失）。
- **Vault index**：`python3 .vault-index/index_vault.py --mode incremental` 跑完 → scanned 17,465 / changed 3,173 / created 916 / deleted 578，`notes.db` 由 301MB → 332MB。索引是 11-12 02:56 的舊版，本輪補上。
- **Vault wikilink**：`scripts/check_wikilinks.py` → 掃 17,650 檔、96,697 條 wikilink、**20,669 個斷鏈目標**（涉及 32,495 處引用）。用 `--tree 163d69608`（11-11 的 commit）比對 → 20,668 斷鏈 → **與 11-11 幾乎持平（+1），不是本輪引入的新腐敗**，屬既有積壓。前 200 個目標只涵蓋 8.9% 的引用量，長尾分散在 archive/舊 entity 頁。
- **Agent repo**：`~/Documents/Agent` working tree **0 筆**、HEAD `d893decf47`、`origin/main...HEAD = 0/0`（fetch 後由 `cf51456210` fast-forward）。
- **Skill_Index**：`skill-index-check.py` → `OVERALL: ✓ ALL CLEAN`（760 rows / header 760 / 8 sections / 32+193+535）。**口徑從 761 → 760 是上游 11-13 commit `47bdcedadd` 归档重複的 `vault-check` 所致**，本次僅確認一致性，未自行改寫。
- **Skill_Index 磁碟↔index 雙向比對**（`skill-index-check.py` 不做，見 Pattern QQQ-2）：index 760 rows、磁碟 1,203 個非 `_dead-skills`/`*_revived` 的 SKILL.md，**443 個未列**——其中 420 個是 `*_revived/`、`gstack.v1.1.0.bak/`、`nuwa-skill/examples/` 等非 active 樹，**不是 drift**。index 列出的 760 筆全部在磁碟上存在（missing = 0）。
- **Memory 三軌**：`~/.hermes/memory/{P0-core,P1-90days,P2-30days}.md` ↔ `~/Documents/Agent/memory/` 對應檔 `cmp` 皆 exit 0。
- **OpenClaw workspace**：HEAD `f493817`（ahead origin/master 1），working tree 60 筆（6 M + 54 ??）為其他 session 成果，本輪未動。
- **Cron output retention**：`cron-output-cleanup.py` 移除 4 檔（>7 天），總量 4.6M。腳本只掃 `<job_id>/*.md`，**root 層 34 個 `*_handover.md` 不在清理範圍**——這是已知口徑，非本輪新增。
- **Hermes backup**：`20261113_161010`（2.0G），prune `20261019_161122`，維持 14 份。
- **Cron job 狀態**：22 個 job 中 19 個 `ok`。3 個仍 `error`（`fbb0a9e5147b` / `ba23c28aec2c` / `ed7968b363f1`，皆 `RuntimeError: Connection error.`）——這是 11-12 交接已查清的 strata SSH tunnel（`127.0.0.1:8081` → v100）11-08 離線所致，**11-13 自然重跑仍是 error**，v100 端仍未恢復（`curl 127.0.0.1:8081/v1/models` 本輪未復測）。

## 新 Pattern：FFFF

**cron 宣告的 skill 若解析失敗，job 仍會 `last_status=ok`** ——「job 成功」不代表「skill 有載入」。

**量測方法（必須用 loader 自己的 venv，不是系統 python3）**：

```bash
cd ~/.hermes/hermes-agent && ./.venv/bin/python -c "
import sys,json; sys.path.insert(0,'/home/pigo/.hermes/hermes-agent')
from tools.skills_tool import skill_view
d=json.load(open('/home/pigo/.hermes/cron/jobs.json'))
jobs = d if isinstance(d,list) else d.get('jobs',d)
if isinstance(jobs,dict): jobs=list(jobs.values())
names=set()
for j in jobs:
    for s in (j.get('skills') or []): names.add(s)
bad=[n for n in sorted(names) if not json.loads(skill_view(name=n)).get('success')]
print('UNRESOLVABLE =', bad)
"
```

**教訓**：
1. `.venv/bin/python` 是唯一能 import `ruamel.yaml` 的直譯器；用系統 `python3` 會在 `hermes_yaml` import 階段就 `ModuleNotFoundError`，看起來像「skill 載入失敗」，實際是量測方法錯了。
2. **每個 cron job 的 `skills` 都要逐一量**，不能只驗 neat-freak 自己的名字。
3. `~/.hermes/logs/agent.log*` 的 `Ambiguous skill name ... — skipping` 是唯一的告警來源；registry 的 `last_status` 不會反映。
4. 修法分兩種，**要按內容關係選**：
   - 同名副本是嚴格子集 → 單向覆寫成 byte-identical（loader 的 `provably_same_skill()` 會判定為同一份）
   - 兩邊各有獨有內容 → 先把獨有檔案搬進要保留的那棵樹，再把另一棵移出掃描路徑（`.archive/` 或改名）——**不要覆寫**
5. 搬走任何 skill 樹之前，先 `diff <(cd A && find . -type f|sort) <(cd B && find . -type f|sort)` 列出獨有檔案，並把獨有 reference / scripts 搬過去。

## 附：2026-11-13 run 新增參考

- **[references/skill-index-2026-11-13b-session.md](references/skill-index-2026-11-13b-session.md)** — Pattern FFFF 新增（cron 宣告的 skill 若 ambiguous 被 skip，job 仍報 `last_status=ok`；用 `~/.hermes/hermes-agent/.venv/bin/python` + `skill_view()` 逐一量 12 個 job 的 skills，修前 2 個 False、修後 12/12 True）；修掉 `neat-freak` / `mail-triage` 的 `productivity/` 同名副本（canonical 單向覆寫，覆寫前驗證嚴格子集）與 `llm-wiki` root/research 雙樹（先搬 4 scripts + 4 references 再把 root 移進 `.archive/`）；Vault index 補建（17,465 檔）；wikilink 20,669 斷鏈與 11-11 持平（+1）非本輪引入
