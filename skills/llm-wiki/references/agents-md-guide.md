# AGENTS.md Guide for LLM Wiki Runtime

這份文件說明 `AGENTS.md` 在 `Pigo_Obsidian` 中扮演的角色。

## 定位

`AGENTS.md` 是整個 vault 的中央 dispatcher 與操作規則層。

它負責：

- 定義技能與 agent 的路由順序
- 指定哪些 workflow 要優先走 local skill
- 指定 vault 的固定路徑與操作習慣
- 約束哪些內容可以寫、哪些位置不能再用

它不是用來承載知識內容本身，而是用來約束知識如何被處理。

## 在 llm-wiki 流程中的作用

當 `llm-wiki` 被觸發時，`AGENTS.md` 會決定：

- 是否真的該走 `llm-wiki`
- 還是其實應該走：
  - `note-update`
  - `inbox-check`
  - `vault-check`
  - 其他更合適的 local skill

因此 `AGENTS.md` 是 routing layer，`llm-wiki` 是 execution workflow。

## 與舊 Schema 模型的關係

舊的通用 LLM Wiki 常會使用：

- `SCHEMA.md`
- `index.md`
- `log.md`

作為知識庫約束層。

在 `Pigo_Obsidian` 中，這個角色已由以下組合取代：

- `AGENTS.md`：全域 routing 與操作規則
- `Meta/vault-structure.md`：結構說明
- `Learning/.../index.md`：內容入口
- `Learning/status/LLM-Wiki-Index.md`：llm-wiki 專用索引
- `Learning/status/LLM-Wiki-Ingest-Log.md`：llm-wiki 專用歷史

也就是說，這個 vault 不再依賴單一 `SCHEMA.md` 作為規則中心。

## 建議在 AGENTS.md 內維持的 llm-wiki 規則

### 1. 路由優先順序

- skills first
- agents second
- 同類需求優先走已存在的 local crew workflow

### 2. llm-wiki 的邊界

應明確規定：

- `llm-wiki` 用於外部來源 ingest、結構化知識沉澱、索引與 cross-link 維護
- 單篇既有筆記升級應優先考慮 `note-update`
- 批次整理 Inbox 應優先考慮 `inbox-check`

### 3. 內容落點

應明確規定：

- `llm-wiki/` 只保留 runtime/reference
- 正式內容落到 `Learning/` 與其他既有內容域

### 4. 驗證義務

每次 llm-wiki 相關修改後，應檢查：

- 是否放對目錄
- 是否更新索引
- 是否有壞連結
- 是否誤把內容寫回 `llm-wiki/`

## 實際使用原則

如果之後有人要調整 `llm-wiki`，應先看：

1. `AGENTS.md`
2. `Meta/vault-structure.md`
3. `llm-wiki/SKILL.md`
4. `llm-wiki/references/`

不要只改單一 skill 而忽略 dispatcher 規則，不然很容易造成：

- 路由與落點不一致
- 舊目錄被重新啟用
- skill 邊界再次漂移

## 一句話總結

在這個 vault 中，`AGENTS.md` 是 llm-wiki 的上位規則層；它不是知識內容模板，而是整個 runtime 的操作憲法。
