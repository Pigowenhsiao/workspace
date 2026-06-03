# 變更影響矩陣

遇到不確定「這次改動要同步哪些檔案」時查這張表。

## 程式碼層變更 → 文件層變更

| 本次對話發生的事 | 要改的檔案（按受眾） |
|---|---|
| 新增 API / 路由 | 專案根 markdown 路由清單 · `docs/integration-guide.md` API 速查表 · `docs/architecture.md` Routes 小節 |
| 新增 / 改名 環境變數 | 專案根 markdown 環境變數表 · `docs/operator-runbook.md` 環境變數章節 · `docs/integration-guide.md`（如果下游要配） |
| 新增資料庫表 / 欄 | 專案根 markdown 資料庫表 · `docs/architecture.md` Data Model |
| 新增 / 改動 使用者流程 | 專案根 markdown 使用者流程 · README 相關命令列範例 · `docs/handoff.md` What Exists Today |
| 新增大特性（能跨多檔案） | 以上全部 + `docs/architecture.md` 新增章節 + `docs/handoff.md` 已完成清單 |
| 新增術語 / 改命名 | `docs/integration-guide.md` 術語表（如果有）+ 全域搜尋舊術語替換 |
| 部署參數 / 基礎設施變化 | `docs/operator-runbook.md` · 專案根 markdown 部署章節 |
| 下游專案接入方式變化 | 下游專案的 `docs/<integration>.md` · 上游專案的 `integration-guide.md` |

## 記憶層變更

| 情況 | 處理方式 |
|---|---|
| 過期事實 | 改記憶檔案，同時更新索引（如 MEMORY.md）的 description |
| 相對時間（「今天」、「最近」） | 全部轉成絕對日期（`2026-04-29` 而非「今天」） |
| 重複記錄（多條說同一件事） | 合併為一條，改索引 |
| 已完成的待辦 | 刪除——知識庫不是歷史檔案 |
| 推翻的決策 | 刪除舊條目，留新決策 |
| 跨會話只用一次的臨時上下文 | 刪除 |

## 跨專案影響檢查

最容易漏改的場景：

- **上游 API 變了 → 下游 SDK 文件**：協定變化必須兩邊對齊
- **共享子網域 / 路由 / 環境變數改了 → 所有 consumer 專案的 setup 文件**
- **認證中台變更 → 所有接入應用的 integration guide**
- **公共元件 / 基礎設施 升級 → 各專案的 operator-runbook 提及版本號的地方**

判斷方法：這次改的東西有沒有 SDK、子網域、共享設定、跨程序協定？有就要在所有依賴專案裡搜一遍提到這件事的文件。

## 文件結構通用約定

新增一個能力（API、flow、特性）的標準動作是**四處都補**：

1. **integration-guide / 外部視角文件**：怎麼用（curl / SDK 範例 / 錯誤碼）
2. **architecture**：怎麼運作（資料流、狀態機、設計取捨）
3. **runbook**：怎麼運維（冒煙命令、故障排除、環境變數）
4. **handoff / CHANGELOG**：已完成

API 速查表、環境變數表、術語表是高頻查詢的結構化資訊，**必須保持「所見即最新」**。