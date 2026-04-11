# skills-plan.md - MACM1BOT 建議技能組合

## 核心必備

### 1. multi-search-engine
用途：
- 全網搜尋
- 多來源交叉查證
- 找新聞、找網站、找資料

為什麼要裝：
- 單一搜尋引擎常被擋
- 這個能降低卡死機率

### 2. openclaw-tavily-search
用途：
- 快速網路搜尋
- 當主要搜尋路徑的備援

為什麼要裝：
- 有時比其他搜尋更快更乾淨

### 3. agent-browser
用途：
- 需要點擊、展開、模擬瀏覽時使用
- 當 RSS / 可讀頁 / 搜尋都不夠時再上

為什麼要裝：
- 處理動態頁面有用
- 但應該當最後手段，不是第一反應

### 4. summarize-pro
用途：
- 摘要文章、長文、會議、報告
- 產出 TL;DR、重點、行動項目

為什麼要裝：
- 幾乎天天用得到
- 能把資訊壓縮成可執行內容

### 5. skill-vetter
用途：
- 安裝第三方 skill 前先掃一遍

為什麼要裝：
- 不然亂裝就是把門拆掉請鬼進來

## 視需求加裝

### llm-wiki
適合：
- 要長期維護知識庫
- 想把外部內容整理進 Obsidian / Wiki

### notion-vault-sync
適合：
- 同步 Obsidian 與 Notion
- 要固定格式沉澱資料

### obsidian-official-cli
適合：
- 常直接操作 Obsidian vault
- 建立、移動、搜尋筆記

### agent-reach / edison-agent-reach
適合：
- 常讀特定平台內容
- 需要跨平台研究

## 不要亂裝的原則

- 功能重疊太高的先不要一起裝
- 沒明確用途的不要裝
- 裝完一定要驗證是否真的出現在 workspace/skills

## 建議的最小實戰組合

如果你只想先讓 MACM1BOT 變能打，先裝這 5 個：

1. `multi-search-engine`
2. `openclaw-tavily-search`
3. `agent-browser`
4. `summarize-pro`
5. `skill-vetter`

這套已經夠它做大部分查找、整理、摘要、瀏覽、風險檢查工作了。
