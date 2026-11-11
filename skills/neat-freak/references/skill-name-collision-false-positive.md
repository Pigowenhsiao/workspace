# 技能名稱碰撞造成的「假 drift」——2026-10-28 第 14 run 實測

## 事件

2026-10-28 執行 Phase 3（Skills Consistency）時，我用 **frontmatter `name` 作為比對 key**
去比對 canonical（`~/.hermes/skills/`）與 workspace（`~/Documents/Agent/skills/`），
得出「3 個 canonical→workspace、7 個 workspace→canonical」的同步清單，並實際執行了覆寫。

覆寫後才發現：**canonical 有同一個 skill name 的多條平行路徑**，
`name`-based 比對把不同目錄樹的同名 skill 配成了一對，導致：

- `~/.hermes/skills/weather/SKILL.md` 被寫入 `~/.hermes/skills/productivity/weather/` 的內容
- `~/.hermes/skills/openclaw-imports/remotion/SKILL.md` 被寫入 workspace `skills/...` 另一棵樹的內容
- `gstack-new/.hermes/skills/gstack-{careful,freeze,unfreeze}/` 三檔同樣被錯配覆寫

共 7 個 canonical 檔案被污染（Agent repo 側的 3 個已用 `git checkout --` 還原）。

## 修復

從 2026-10-28 03:00 的備份 tarball（`~/Documents/Backup/hermes/hermes_2026-10-28_030026.tar.gz`）
解出這 7 檔原檔覆回 canonical，逐一 `diff -q` 確認 OK，並與 09:17 備份交叉比對一致。

## 根因

canonical 技能樹是**多軌並存**的結構（歷史匯入造成）：

| name | 平行路徑（canonical 內） |
|---|---|
| `weather` | `weather/`、`weather/weather/`、`productivity/weather/` |
| `aihot` | `aihot/`、`productivity/aihot/`、`research/aihot/` |
| `agent-create` | `agent-create/`、`autonomy/agent-create/`、`autonomous-ai-agents/agent-create/` |
| `careful`/`freeze`/`unfreeze` | `gstack/`、`gstack-new/`、`gstack-new/.hermes/skills/`、`gstack-new/.hermes/commands/` |
| `Remotion`/`latex-posters`/`generate-image`/`obsidian-markdown` | top-level、`openclaw-imports/`、`productivity/`、`_backup_*` |

2026-10-27 run 的 handoff 已記錄「84 個同名但內容不同的 skill」，但**沒有記錄
「因此不能拿 name 當比對 key」這個後果**。本次就是踩在這個缺口上。

## 正規做法

### ✅ 唯一安全的比對方式：**相對路徑**（relative path）

```python
# canonical 與 workspace 都以「相對於 skill 根目錄的路徑」為 key
rel = os.path.relpath(os.path.join(dp, 'SKILL.md'), root)
```

實測結果（2026-10-28）：canonical 933 路徑 / workspace 1208 路徑 /
**同路徑 56 組，內容差異 0 組**。這是乾淨的。

兩棵樹的**路徑集合本身就不對齊**（workspace 有 `_dead-skills/`、`01-Knowledge-System/`、
`browser-web-social/` 等 canonical 沒有的分組；canonical 有 `productivity/`、
`openclaw-imports/`、`gstack-new/` 等 workspace 沒有的分組），
這是**結構性差異，不是 drift**，不該靠「把 A 的檔案寫到 B」來「修正」。

### ❌ 不要做的事

1. **不要用 frontmatter `name` 當比對 key** → 必然跨樹誤配
2. **不要用「嚴格超集 + mtime 較新」這種啟發式決定同步方向** →
   它只能證明「內容包含關係」，證明不了「這兩棵樹是同一個 skill 的兩份副本」
3. **不要因為 name 相同就假設路徑相對應** → 3 軌結構下同一 name 對應 3 個不同路徑

### 想要收斂三軌重疊？

那是**架構決策**，需要人工裁決「哪些是歷史版、哪些是現行版」，
不能由機械式比對自動決定。Pigo 未明確指示前，不動 canonical 結構。

## 預防

1. **任何跨樹比對，key 必須是相對路徑，不是 frontmatter name**
2. 覆寫任何 canonical 檔案前，先確認它是否為「多軌路徑中的一條」——
   檢查 `find ~/.hermes/skills -name SKILL.md -path "*<name>*"` 是否回傳多筆
3. **canonical 樹沒有 git**（`~/.hermes/skills/.git` 不存在）→ 覆寫後無法 `git checkout` 還原。
   唯一還原途徑是 `~/Documents/Backup/hermes/` 的 tarball。
   **因此：覆寫 canonical 前，先確認備份存在且涵蓋該檔案**
4. 定期跑 `git fsck` / 磁碟比對時，用「同相對路徑」的交集做基準

## 相關

- `references/skill-index-2026-10-28-session.md` — 本次完整 session 記錄
- `references/workspace-snapshot.md` — workspace 拓撲快照
- Pattern BBB（2026-10-24）— 同名 skill 被 loader 判定 ambiguous 而 skip
