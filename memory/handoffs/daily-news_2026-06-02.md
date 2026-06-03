---
template: cron-handover
version: 1.0
lastUpdated: 2026-06-02
---

## Cron 工作交接清單

### 1. Goal（目標）
每日新聞摘要：抓科技、財經、國際、軍事各 5 則，翻譯為繁體中文，寫入 Obsidian vault `00-Inbox/`，並 commit + push 回 main。

### 2. Current State（現況）

**已完成：**
- ✅ 科技新聞 5 則（採用替代來源）
- ✅ 財經新聞 5 則（CNBC RSS）
- ✅ 國際新聞 5 則（BBC World RSS）
- ✅ 軍事新聞 5 則（採用替代來源）
- ✅ 全部翻譯為繁體中文，英文術語附翻譯
- ✅ 寫入 `/home/pigo/Documents/Pigo_Obsidian/00-Inbox/2026-06-02_News-Update.md`
- ✅ `git pull --rebase` / `git commit` / `git push origin main` 皆成功（commit `d9ed07c4`）

**原始指定來源失敗 → 已自動切換：**
- ❌ Reddit `r/technology`、`r/programming` RSS：HTTP 403 持續封鎖（連續兩日失敗）
- ❌ Defense News `https://www.defensenews.com/feed/`：HTTP 404（連續兩日失敗）
- ✅ 替代來源正常運作並提供 5 則
  - 科技：Hacker News（HNRSS）、Ars Technica、TechCrunch、The Verge
  - 軍事：USNI News、The War Zone

### 3. Source Chain（資料來源）

**成功（原始）：**
- CNBC: `https://www.cnbc.com/id/100003114/device/rss/rss.html` → 30 筆
- BBC World: `http://feeds.bbci.co.uk/news/world/rss.xml` → 31 筆

**成功（替代）：**
- Hacker News: `https://hnrss.org/newest` → 20 筆
- Ars Technica: `https://feeds.arstechnica.com/arstechnica/index` → 20 筆
- TechCrunch: `https://techcrunch.com/feed/` → 20 筆
- The Verge: `https://www.theverge.com/rss/index.xml` → 10 筆（Atom feed）
- USNI News: `https://news.usni.org/feed` → 30 筆
- The War Zone: `https://www.twz.com/feed` → 30 筆

**失敗：**
- Reddit: `https://www.reddit.com/r/technology/new.rss` → HTTP 403 Blocked HTML
- Reddit: `https://www.reddit.com/r/programming/new.rss` → HTTP 403 Blocked HTML
- Defense News: `https://www.defensenews.com/feed/` → HTTP 404
- （嘗試但失敗）Military.com、Stripes、Janes、Army Times、Breaking Defense、Foreign Affairs、DoD.gov → 全部回 HTML 跳轉頁（不是真的 RSS）

**本地輸出：**
- RSS 暫存：`/tmp/{reddit_tech,reddit_prog,cnbc,bbc,defnews,hn,verge,arstech,tc,usni,twz,fa,...}.rss`
- 寫入：`/home/pigo/Documents/Pigo_Obsidian/00-Inbox/2026-06-02_News-Update.md`
- Git commit：`d9ed07c4 Add news update 2026-06-02`
- Push：`48aba952..d9ed07c4 main -> main`（成功）

### 4. Decision Needed（需人類決策）

- **是否將 RSS 來源正式切換？** 連續兩天原始來源（Reddit 科技、Defense News 軍事）都失敗。是否在 cron prompt 內改寫固定使用替代來源？
  - 建議保留 prompt 原文，但允許 agent 自動 fallback（今日已這樣做，無需每次人工介入）。
- **無待決策的高風險事項。**

### 5. Recommended Default（拿不準時的預設行為）

- 任何 RSS 失敗 → 立刻改用已知可用的備用來源（科技優先 HNRSS / Ars / TC / Verge；軍事優先 USNI / TWZ），不再耗時嘗試同一個被擋的 URL。
- 若所有備用來源也都失敗 → 該類別在 vault 內留下「資料源全部失效」說明，仍照常 commit，但隔天需要人類關注。
- 拿不準要不要放進去的新聞（政治敏感、單一來源未交叉驗證）→ 略過。

### 6. Risks / Do Not Do

- **不可發布未翻譯新聞。**（已遵守，所有標題、摘要都先翻成繁中再寫入）
- **不可推送未驗證 commit。**（本次 push 前確認 `git status` 與 commit 訊息）
- **不可改寫 SOUL.md / 系統提示。**（即使 RSS 來源失效，也只動 vault 與 handover 檔）
- **不可繞過 git pull。**（今日先 pull 再寫，避免衝突）
- **不可假設 Reddit RSS 可用。** 已連兩日 403，下個 cron 應直接 fallback，不浪費時間。
- **不可直接信賴 Defense News。** 已連兩日 404，下個 cron 應直接 fallback。

### 7. Next Action（下一步）

- 等待明日 cron 觸發；若屆時 Reddit / Defense News 仍壞，繼續走 fallback 流程。
- 若 Pigo 想根治：可考慮把 fallback URL 寫進 `TOOLS.md` 的 News Fetch Notes 區塊，或建立 `memory/skills/daily-news-fallback.md` 紀錄可用的替代來源清單。
- 本日 handover 與 vault 檔都已建立；如要 review，請看 `00-Inbox/2026-06-02_News-Update.md` 與本檔。
