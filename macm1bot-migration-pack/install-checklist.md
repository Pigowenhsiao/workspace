# install-checklist.md - MACM1BOT 安裝與驗證清單

## A. 套用文件

- [ ] 備份 MACM1BOT 原本的 `AGENTS.md`
- [ ] 備份原本的 `SOUL.md`
- [ ] 備份原本的 `IDENTITY.md`
- [ ] 備份原本的 `TOOLS.md`
- [ ] 備份原本的 `MEMORY.md`
- [ ] 複製這份移植包中的對應檔案到 MACM1BOT workspace

## B. 安裝 skills

建議流程：

1. `openclaw skills search <query>`
2. `openclaw skills info <slug>` 或 `openclaw skills list`
3. `openclaw skills install <slug>`

安裝後驗證：
- [ ] 確認 skill 真的出現在 `workspace/skills/`
- [ ] 不要只因為命令跑過就當作成功

## C. 建議優先安裝清單

- [ ] multi-search-engine
- [ ] openclaw-tavily-search
- [ ] agent-browser
- [ ] summarize-pro
- [ ] skill-vetter

## D. 功能驗證

### 搜尋
- [ ] 能正常查網頁
- [ ] 單一來源失敗時能切換策略

### 摘要
- [ ] 能摘要長文並產出重點

### 瀏覽
- [ ] 遇到動態頁時能使用 browser 類技能

### 風格
- [ ] 回覆為繁體中文
- [ ] 語氣直接
- [ ] 不再滿嘴塑膠客服話術

## E. 實戰測試題

1. 叫它整理今天的重要科技新聞
2. 叫它總結一篇長文
3. 叫它比較兩個方案並給建議
4. 叫它先讀 workspace 規則後再回答

如果這四關過了，基本上 MACM1BOT 就不是裝飾品了。
