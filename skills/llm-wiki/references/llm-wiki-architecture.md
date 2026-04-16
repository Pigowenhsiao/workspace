# LLM Wiki Architecture for Pigo_Obsidian

這份文件描述 `Pigo_Obsidian` 中 `llm-wiki` 的實際架構，而不是通用的獨立 wiki 模型。

## 核心原則

- `llm-wiki/` 是 runtime package，不是內容主樹
- 正式知識內容寫入既有 vault 結構
- `Learning/` 是 AI 學習內容的 canonical 落點
- `00-Inbox/` 只作為暫存，不作為正式知識目的地

## 實際架構

```text
Pigo_Obsidian/
|- 00-Inbox/                          # 暫存、未完成分類、待後續整理
|- Learning/
|  |- articles/                       # 文章、paper、網頁整理
|  |- youtube/                        # YouTube / video 筆記
|  |- repos/                          # repo、工具、framework、entity-style note
|  |- twitter/                        # X / Twitter 筆記
|  |- notion-knowledge/               # 已有主題知識區
|  `- status/
|     |- LLM-Wiki-Index.md            # llm-wiki 相關索引
|     `- LLM-Wiki-Ingest-Log.md       # llm-wiki ingest 歷史
`- llm-wiki/
   |- SKILL.md                        # runtime 規格
   `- references/                     # 補充參考文件
```

## 與舊模型的差異

這個 vault 不再使用以下舊結構作為正式內容目的地：

- `llm-wiki/index.md`
- `llm-wiki/log.md`
- `llm-wiki/00-Inbox/`
- `llm-wiki/entities/`
- `llm-wiki/concepts/`
- `llm-wiki/comparisons/`
- `llm-wiki/queries/`

如果發現新內容被寫到這些位置，應視為結構錯誤並回收。

## 三層模型

### Layer 1: Capture

來源剛進來、尚未整理完成時，可暫放：

- `00-Inbox/`

適用情境：

- 來源不完整
- 還無法判斷類型
- 使用者明示先暫存不要正式歸檔

### Layer 2: Canonical Knowledge

完成整理後，內容必須進入既有類別：

- article / paper / blog / thread -> `Learning/articles/`
- video / transcript -> `Learning/youtube/`
- repo / tool / framework / project card -> `Learning/repos/`

### Layer 3: Runtime and Rules

`llm-wiki/` 本身只負責：

- skill 規則
- reference templates
- workflow guidance

它不直接承載正式知識內容。

## 導覽入口

每次使用 `llm-wiki` 前，優先讀這些入口：

1. `Learning/index.md`
2. `Learning/status/LLM-Wiki-Index.md`
3. `Learning/status/LLM-Wiki-Ingest-Log.md`

必要時再讀：

- `Learning/articles/index.md`
- `Learning/youtube/index.md`
- `Learning/repos/index.md`
- `Learning/status/index.md`

## 內容更新責任

每次 ingest 或結構調整後，至少要同步：

- 正確的 canonical 筆記檔
- 對應目錄的 index
- `Learning/status/LLM-Wiki-Index.md`
- `Learning/status/LLM-Wiki-Ingest-Log.md`

## 結構錯誤判定

以下情況都應視為錯誤：

- 正式筆記被寫回 `llm-wiki/`
- 筆記仍連到不存在的 `Learning/papers/` 或 `Learning/videos/`
- 有新內容只有主筆記，沒有更新 `LLM-Wiki-Index` 或 `Ingest-Log`
- 大量暫存內容長期滯留在 `00-Inbox/` 沒有回收

## 一句話總結

在 `Pigo_Obsidian` 中，`llm-wiki` 是整理與規則層；正式知識內容必須回收到 `Learning` 與既有 vault 骨架。
