# Workspace Snapshot — 2026-05-17

本文為滾動同步的副產物，記錄 workspace 實況，供後續 Agent 初始化時快速定位。

## 主要專案

### hermes-agent
```
~/.hermes/
├── config.yaml
├── skills/                — canonical skills（neat-freak 本體在這）
└── sessions/
```

### Agent（技能倉庫）— OpenClaw workspace
```
~/Documents/Agent/
├── AGENTS.md              — Codex 指令，含 Skill-First Workflow
├── docs/
│   ├── Skill_Index.md     — 568 項技能索引（2026-05-17 實測，全部 5 項檢查通過）
│   ├── Skill_Category.md  — 14 類分類（加總 570，與 Skill_Index Active 口徑一致）
│   ├── STATUS_*.md        — 分散狀態檔（未全部讀過內容前勿刪）
│   └── article-notes/
├── skills/                — workspace sync copy（neat-freak 的 sync 版）
│   └── neat-freak/        — canonical 的正當 sync copy，含完整 references + scripts
└── <category>/            — 技能目錄（ce-compound, gsd-*, etc.）
```

### browser-harness
```
~/Documents/browser-harness/
├── README.md, SKILL.md
├── run.py, helpers.py, admin.py, daemon.py
├── interaction-skills/, domain-skills/
└── docs/setup-remote-debugging.png
```

### graphify
```
~/Documents/graphify/
├── README.md, README.zh-CN.md
├── ARCHITECTURE.md, CHANGELOG.md
├── graphify/              — 原始碼
└── worked/                — 工作目錄
```

## OpenClaw Workspace 記憶
```
~/.openclaw/workspace/
├── MEMORY.md
├── HEARTBEAT.md
├── AGENTS.md
├── SOUL.md
├── TOOLS.md
├── USER.md
├── IDENTITY.md
└── memory/
    ├── index.md           — 記憶索引
    └── 2026-*.md          — 滾動日誌（每 4 小時一筆）
```

## 平台路徑速查

| 平台 | 設定檔 | 技能 |
|------|--------|------|
| Hermes（本 Agent） | `~/.hermes/config.yaml` | `~/.hermes/skills/` |
| Claude Code | `~/.claude/projects/<...>/memory/` | `~/.claude/skills/` |
| Codex | `~/.codex/AGENTS.md` | `~/.codex/skills/` |
| OpenClaw | `~/.openclaw/` | `~/.openclaw/workspace/skills/` |

## 校驗命令

```bash
# Skill_Index.md 五項檢查（首選）
python3 ~/.hermes/skills/neat-freak/scripts/skill-index-check.py

# 版本範例陳屍
grep -rnE 'v[0-9]+\.[0-9]+\.[0-9]+' <project>/docs/

# 相對時間殘留
grep -rE "今天|昨天|這週|上週|最近|recently|today|yesterday|this week|last week" \
  ~/Documents/Agent/ --include="*.md" 2>/dev/null \
  | grep -v "Skill_Index\|optional-skills\|index.md cleanup"

# Skill 口徑 drift（Skill_Index vs Skill_Category 加總）
python3 -c "
import re
with open(os.path.expanduser('~/Documents/Agent/docs/Skill_Index.md')) as f:
    idx = f.read()
active = re.search(r'Active Skills: (\d+)', idx)
with open(os.path.expanduser('~/Documents/Agent/docs/Skill_Category.md')) as f:
    cat = f.read()
cat_counts = re.findall(r'^\| [^|]+\| (\d+) \|', cat, re.MULTILINE)
total_cat = sum(int(c) for c in cat_counts)
active_n = int(active.group(1)) if active else 0
print(f'Skill_Index: {active_n}  Skill_Category sum: {total_cat}  Drift: {active_n - total_cat}')
"
```

## 常見失誤

1. **GBrain 已刪除**（2026-05-09 確認）：`openclaw-imports/migrate/SKILL.md` 已 DEPRECATED，流程見 `references/gbrain-deprecation-workflow.md`
2. **版本範例陳屍**：`grep -E` 相對時間對 blockquote 裡的 `v0.8.0 is available (you're on v0.7.0)` 完全失靈，每次 sync 都要跑版本號 grep
3. **STATUS_*.md 積累**：分散且可能過期，未完整讀過內容前不要刪
4. **雙軌結構混淆**：neat-freak 的 canonical（`~/.hermes/skills/neat-freak/`）和 workspace sync copy（`~/Documents/Agent/skills/neat-freak/`）是正常架構，不是污染。workspace copy 若少於 canonical 就 restore，若多於 canonical 就逐檔問是否 legitimate

## 滾動同步記錄

### 2026-05-17（cron 16:05）

本次發現：
- `Skill_Index.md`：全部 5 項檢查通過（568 項 Active Skills，-2 from 2026-05-16）
- Branch divergence：**ahead 8 / behind 36**，origin/main 落後很多（近期 upstream 有 `Poster-Creater` 集中化等變更）
- `agents/` 在 workspace 多餘但 origin/main 有（Pattern H #21），確認為 legitimate upstream 擴充，不刪
- `docs/Skill_Index.md` 口徑落後（workspace 697 行 / origin 734 行），需 divergence 解決後 pull 拉齊
- Pattern M 新增：Branch divergence 分類處置流程（merge/rebase/squash 依 log 判斷）
- Step 0 順序修正：cron job 無法先 load hermes-agent，canonical self-check 完全獨立，應該先跑

### 2026-05-16（cron 04:05）

本次發現：
- `Skill_Index.md`：全部 5 項檢查通過（570 項 Active Skills，+1 from 2026-05-15）
- `Agent.md`、`Agents_2.md`、`Agents_3.md` 刪除（commit `3a063fc3`）— 確認 origin/main 的刪除 diff 為正當變更，非 workspace pollution
  - ⚠️ **2026-10-28 修正**：三檔已由 Pigo 自己的 commit `918480b5`（2026-09-23「chore: reconcile agent skills and workflows」）重新加入並納入 git 追蹤，
    內容與 `3a063fc3` 刪除前**完全相同**。→ 「永久刪除」的敘述已過期；三檔現為**使用者刻意保留的孤兒**，
    非 workspace pollution，**不得再刪**。其中 `Agents_3.md` 含 `<!-- OPENSPEC:START -->` block 指向不存在的 `openspec/` 目錄
    與 Windows 路徑 `C:\Users\hsi67063\...`（本機為 Linux）。
  - ✅ **2026-10-28 修復**（Pattern 22 機械式修復）：`openspec/` 目錄經 `find` 確認**從未存在**於 workspace
    （不在磁碟、不在 git history）→ 依 Pattern 22 刪除 `Agents_3.md` 的 managed block 與
    `Agents_2.md` 的 `## 1. OpenSpec Instructions` 段落（後者含「Do not remove this block」，
    但其指示的目標檔不存在，留著只會誤導 agent 去讀不存在的檔案）。
    Windows 路徑 `C:\Users\hsi67063\.codex\superpowers` → 改為實際存在的
    `~/Documents/Agent/skills/agent-workflows/superpowers`，並把 PowerShell `Test-Path`
    驗證指令改為 `ls`。`Agents_2.md` 章節編號因移除第 1 節而全數重排為連續 1–15。
- `aihot` 的 `今天/最近` 為功能描述性文字（"適用於詢問今天/最近 AI 圈動態"），非敘事性時間參照，**不需修改**
- `recently` 出現於 `ce-compound`/`ce-compound-refresh` 的 description，為正常關鍵字，非時間殘留
- Branch：`neat-fix` ahead of origin/main 13 commits，需 push；無 branch divergence
- Git 工作樹乾淨，無 workspace pollution

### 2026-05-15（cron 00:04）

本次發現並修復：
- `Skill_Index.md`：全部 5 項檢查通過（569 項 Active Skills）
- `workspace/memory/index.md`：36 記憶檔案完整，timestamp → 2026-05-15 00:04
- `~/Documents/Agent/skills/neat-freak/references/`：restore `agent-paths.md` + `sync-matrix.md`（workspace copy 比 canonical 少），commit `c639b1a8`
- workspace sync copy 的 `skill-index-corruption-patterns.md`、`skill-index-verification.md`、`gbrain-deprecation-workflow.md` 已存在且與 canonical 一致
- scripts：`skill-index-check.py` 兩地一致
- Branch divergence：`neat-fix` 落後錨點 9 commits / 前瞻 origin/main 1 commit，未處理

### 2026-05-14 滾動同步記錄

本次發現並修復：
- `skill-index-check.py`：Python 3.13 `\.+` subpattern bug → 修复為 `[^\\\\]]+` + lookahead `(?=\\))`；全部 5 項檢查通過
- `workspace/memory/index.md`：漏列 `2026-05-12-0404.md` 與 `2026-05-14-0004.md` 已修復
- Skill 口徑：591 → 569（Active Skills os.walk 實測）

### 2026-05-13 滾動同步記錄

本次發現並修復：
- `Skill_Index.md`：口徑 569，全部 5 項乾淨
- `workspace/memory/index.md`：36 記憶檔案完整
- Branch divergence：hermes-agent ahead of origin/main，維持未主動 push

### 2026-05-10 滾動同步記錄

本次發現並修復：
- `Skill_Category.md`：Generated 日期更新至 2026-05-10；口徑 591 與 Skill_Index 對齊
- 口徑 drift 備註已移至歷史記錄（2026-05-14 口徑已重測為 569）
