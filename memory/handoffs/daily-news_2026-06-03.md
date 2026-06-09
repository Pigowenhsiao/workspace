---
template: cron-handover
version: 1.0
lastUpdated: 2026-06-03
---

## Cron 工作交接清單 — daily-news 2026-06-03

### 1. Goal（目標）
每日 08:00 自動抓 4 大類新聞（科技、財經、國際、軍事）各 5 則，翻譯成繁體中文，寫入 Obsidian vault `/00-Inbox/YYYY-MM-DD_News-Update.md` 並 commit + push。

---

### 2. Current State（現況）

**已完成：**
- ✅ Reddit r/technology 與 r/programming RSS 抓取嘗試（被擋）
- ✅ 科技新聞替代：Ars Technica RSS + The Verge Atom feed（合併取 5 則，4 來自 Ars Technica、1 來自 The Verge）
- ✅ CNBC RSS 抓取與解析（取 5 則）
- ✅ BBC World RSS 抓取與解析（取 5 則）
- ✅ Defense News RSS 抓取（404 失敗，依指示跳過）
- ✅ 全部翻譯為繁體中文，術語附翻譯
- ✅ 寫入 `/home/pigo/Documents/Pigo_Obsidian/00-Inbox/2026-06-03_News-Update.md`
- ✅ git pull --rebase（已為最新）

**卡住/失敗：**
- ❌ Reddit RSS（r/technology、r/programming）回傳 "Blocked" HTML 頁，curl 抓取失敗
- ❌ Defense News RSS（`https://www.defensenews.com/feed/`）回傳 404 頁，feed 已失效
- ⏳ git add / commit / push（待執行）

---

### 3. Source Chain（資料來源）

**主要 RSS 源：**
- `https://www.reddit.com/r/technology/new.rss` — ❌ Blocked HTML
- `https://www.reddit.com/r/programming/new.rss` — ❌ Blocked HTML
- `https://www.cnbc.com/id/100003114/device/rss/rss.html` — ✅ 20,881 bytes
- `http://feeds.bbci.co.uk/news/world/rss.xml` — ✅ 19,269 bytes
- `https://www.defensenews.com/feed/` — ❌ 404 page (51,934 bytes)

**替代 RSS 源（Reddit 被擋時啟用）：**
- `https://feeds.arstechnica.com/arstechnica/index` — ✅ 78,401 bytes
- `https://www.theverge.com/rss/index.xml` — ✅ 33,043 bytes
- `https://hnrss.org/frontpage` — ✅ 15,487 bytes（備援，未採用）

**本地快取：**
- `/tmp/cnbc.xml`、`/tmp/bbc.xml`、`/tmp/arstech.xml`、`/tmp/verge.xml`、`/tmp/hn.xml`
- `/tmp/reddit_tech.xml`、`/tmp/reddit_prog.xml`（失敗快取，HTML 內容）
- `/tmp/defnews.xml`（失敗快取，HTML 內容）

**產出檔案：**
- `/home/pigo/Documents/Pigo_Obsidian/00-Inbox/2026-06-03_News-Update.md`（4,012 bytes）

**解析工具：**
- `/tmp/parse_rss.py`（自製 Python XML/Atom 解析器，支援 CDATA 與 HTML 剝除）

---

### 4. Decision Needed（需人類決策的事）

| 項目 | 決策內容 | 期限 |
|------|----------|------|
| Reddit RSS 長期被擋 | 是否要把 cron 預設改為「Ars Technica + The Verge + Hacker News 輪流」當作科技新聞主源？ | 下一個週一前 |
| Defense News RSS 失效 | 替代軍事新聞源是否要加 War on the Rocks、Military.com、Jane's 或 BBC 中東版？ | 本週內 |
| The Verge Atom 在 RSS 標準上是否算「科技新聞主流源」 | 翻譯任務是否要限制只用 RSS 2.0 規格源？ | 一次性決策 |

---

### 5. Recommended Default（建議路徑）

**若接手者拿不準，建議預設：**
- 科技：繼續用 Ars Technica + The Verge（兩源合併，互補性高、Atom 與 RSS 2.0 都有）
- 軍事：本次先跳過；若 Defense News 連 3 天都 404，下次任務自動改試 War on the Rocks RSS（`https://warontherocks.com/feed/`）
- Reddit：被擋就放棄，不浪費時間換 UA；必要時改用舊版 RSS 端點（`.rss` 改 `&feed=yes` 不可靠，不建議）
- The Verge / BBC / CNBC 任何一個被擋：直接從當日輸出扣掉該類別，並在檔案 frontmatter 與交接清單留下「fail reason」

---

### 6. Risks / Do Not Do（禁止事項）

**禁止事項：**
- ❌ 禁止發布未經翻譯的新聞（必須全部翻成繁中）
- ❌ 禁止直接推送未驗證的 commit（必須先 `git status` 檢查 working tree）
- ❌ 禁止把 Reddit Blocked 頁的標題當作「新聞」產出（曾發生過，會污染 Inbox）
- ❌ 禁止使用 `2>&1` 與 `&&` 等 shell chain 操作 Documents 區域（SOUL.md 規定）
- ❌ 禁止跳過 git pull --rebase 直接 commit（會撞到 remote 變更）
- ❌ 禁止在無 RSS 解析備援時亂猜新聞標題（必須 skip 並回報）

---

### 7. Next Action（下一步）

**下一步：**
1. 完成 `git add -A` + `git commit -m "Add news update 2026-06-03"` + `git push origin main`（每步獨立、workdir=Pigo_Obsidian、security=full）
2. 在 Telegram 頻道回報「✅ 新聞已寫入 Obsidian inbox（科技5則、財經5則、國際5則、軍事0則 — Defense News 404）」
3. 若 Defense News 連 3 天失敗，下次 cron 自動切換備援軍事源（見 §5 預設路徑）
4. 把「Reddit RSS 長期被擋」這個環境事實寫入 MEMORY.md（避免未來反覆嘗試）

---

### 📋 任務元數據

| 欄位 | 內容 |
|------|------|
| Cron Job 名稱 | daily-news |
| Cron Job ID | 757c1b57-0baa-489e-ba6a-a6f108c54a6d |
| 執行時間 | 2026-06-03 16:06 UTC |
| 執行者 | Jarvis |
| 狀態 | 🔄 進行中（檔案已寫入、待 push） |
| 產出檔案 | `00-Inbox/2026-06-03_News-Update.md`、`memory/handoffs/daily-news_2026-06-03.md` |
| 交接時間 | 2026-06-03 16:06 UTC |

---

*此交接清單由 Jarvis 自動產生。*
