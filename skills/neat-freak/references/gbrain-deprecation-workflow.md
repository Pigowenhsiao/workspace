# GBrain Deprecation Workflow

> 當 workspace 中某個已安裝的系統被移除（例如 GBrain），對應的 Skills 處理流程。

## 核心原則

**標記 DEPRECATED，不要刪除。**

刪除 SKILL.md 會在 `Skill_Index.md`（如有的話）產生懸空引用，下游 Agent 會拿到斷裂的索引。

## 完整流程（6 步）

### Step 1：確認系統已被移除

```bash
ls ~/Documents/<system>/CLAUDE.md   # 確認專案目錄存在但已標記移除
grep "已移除\|DEPRECATED\|removed" ~/.hermes/memories/MEMORY.md
```

### Step 2：找出所有引用該系統的 SKILL.md

```bash
grep -rn "<systemName>\|<systemName_lower>" ~/Documents/Agent/ \
  --include="*.md" \
  | grep -v "Binary\|DS_Store\|Skill_Index" \
  | grep "SKILL.md"
```

例如 GBrain：
```bash
grep -rn "gbrain\|GBrain" ~/Documents/Agent/ \
  --include="*.md" \
  | grep -v "Binary\|DS_Store\|Skill_Index" \
  | grep "SKILL.md"
```

### Step 3：逐個 SKILL.md 標記 DEPRECATED

對每個受影響的 SKILL.md，patch frontmatter 的 `description`：

```
# 改前
---
name: migrate
description: Migrate notes, wikis, and structured knowledge sources into GBrain.
---

# 改後
---
name: migrate
description: DEPRECATED — GBrain 已移除，此技能停用。Legacy migration skill 保留僅供參考。
---
```

並在標題加 `(DEPRECATED)` 標記：
```
# Migrate Skill (DEPRECATED)
```

### Step 4：同步更新 Skill_Index.md（如有）

Skill_Index.md 的 description 欄位**不會自動同步**，需要手動 patch：
```
# 改前
| [migrate](../openclaw-imports/migrate/SKILL.md) | `openclaw-imports/migrate/SKILL.md` | Migrate notes, wikis, and structured knowledge sources into GBrain. | 不需要 | - |

# 改後
| [migrate](../openclaw-imports/migrate/SKILL.md) | `openclaw-imports/migrate/SKILL.md` | DEPRECATED — GBrain 已移除。Legacy migration skill。 | 不需要 | - |
```

### Step 5：驗證

```bash
# 確認所有受影響技能都已標記
grep -n "DEPRECATED" ~/Documents/Agent/docs/Skill_Index.md | grep "<skill-name>"

# 確認 Skill_Index 描述與 SKILL.md frontmatter 一致
```

### Step 6：MEMORY.md 已有 GBrain 移除紀錄（無需重複寫）

如果 MEMORY.md 已有 `GBrain 大坑：已結案` 這類紀錄，**不要覆蓋**，只是實上層共識。SKILL.md 的 DEPRECATED 標記是給 Agent 索引用的，是不同的受眾。

## 本次處理的受影響 Skills（2026-05-05）

| Skill | 路徑 | 状态 |
|-------|------|------|
| migrate | openclaw-imports/migrate/SKILL.md | ✅ DEPRECATED |
| ingest | openclaw-imports/ingest/SKILL.md | ✅ DEPRECATED |
| maintain | openclaw-imports/maintain/SKILL.md | ✅ DEPRECATED |
| query | openclaw-imports/query/SKILL.md | ✅ DEPRECATED |
| briefing | openclaw-imports/briefing/SKILL.md | ✅ DEPRECATED |
| enrich | openclaw-imports/enrich/SKILL.md | ✅ DEPRECATED |

## 已完成的清除事件

### 事件一：Skills 廢除（2026-05-05）
 Skill 的 description 標記 DEPRECATED，物理檔案保留。

### 事件二：Repo 實體刪除（2026-05-09）
 使用者確認完整刪除 `~/Documents/gbrain/`（source code + git history + 所有功能模組）。

 ```bash
 # 刪除前確認（已執行）
 ls ~/Documents/gbrain/          # 存在
 which gbrain                    # 不在 PATH
 ~/Documents/Agent/openclaw-imports/migrate/SKILL.md  # 已 DEPRECATED

 # 刪除（已執行）
 rm -rf ~/Documents/gbrain      # 回傳 "DELETED"，無残留

 # 驗證
 ls ~/Documents/gbrain           # No such file or directory
 ```

 這次刪除是對 2026-05-05 skill deprecation 的**物理層補充**。兩次操作目標不同，不可混淆。

### 事件三：hermes-agent 刪除意圖（2026-05-09）
 使用者詢問「完整刪除 hermes-agent」，但尚未執行。

 掃描發現 hermes-agent 分布於：
 - `~/Documents/hermes-agent/` — Agent repo 內的 source code
 - `~/.hermes/hermes-agent/` — 安裝的 hermes-agent + venv
 - `~/.hermes/skills/hermes-agent/` — 此 skill 本身（不可刪）
 - `~/.hermes/config.yaml` — 配置檔（不可刪）
 - `~/.hermes/memories/` — 記憶檔案（不可刪）

 使用者尚未確認要刪除範圍（僅 source？還是連 config/skills/memories 全清？）。

 **在收到明確指示前不要執行任何刪除。** 先列表說明發現的現況，讓使用者選擇範圍。

## 常見錯誤

**錯誤：直接刪除 SKILL.md**
→ Skill_Index.md 產生懸空引用 `../migrate/SKILL.md` → 404
→ 下游 Agent 無法判斷 skill 是否存在

**錯誤：只改 SKILL.md，不改 Skill_Index.md**
→ Skill_Index.md description 仍是舊內容
→ Agent 載入 skill 時描述與實際不符

**錯誤：覆蓋 MEMORY.md 中已存在的移除紀錄**
→ MEMORY.md 的 GBrain 移除紀錄是的事實，SKILL.md DEPRECATED 是另一層受眾的標記，兩者功能不同
