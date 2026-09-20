---
name: news-aggregator
version: 2.0.0
description: 科技、軍事、財經、國際新聞彙總。全部翻譯為繁體中文。每個類別抓取10筆新聞。
license: MIT
---

# News Aggregator

聚合科技、軍事、財經、國際新聞，翻譯為繁體中文輸出。每個類別抓取 10 筆新聞。

## 新聞源與備用源

### 🤖 科技新聞（主要：Reddit）
- 主要：Reddit r/technology、r/programming、r/artificial
- RSS：`https://www.reddit.com/r/{subreddit}/new.rss`
- 備用 1：TechCrunch (https://techcrunch.com)
- 備用 2：The Verge (https://www.theverge.com)
  - RSS：`https://www.theverge.com/rss/index.xml`（Atom feed）
  - ⚠️ 週末有時不更新（最近一次 06-15 凌晨見證），fallback 條件：最近 6h 內 0 筆新文 → 自動向下取 feed 內最新
- 備用 3：Ars Technica (https://arstechnica.com)
  - RSS：`https://feeds.arstechnica.com/arstechnica/index`（FeedBurner，每小時更新，最後一次驗證 2026-08-15 06:53 UTC HTTP 200）
  - 觸發：The Verge 6h 內 0 筆 或 RSS 抓取失敗 → 第一順位切換
- 備用 4：Hacker News (https://news.ycombinator.com)
  - RSS：`https://news.ycombinator.com/rss`

**科技 fallback 順序建議**：Reddit → TechCrunch → The Verge → **Ars Technica** → HN
（Ars Technica 提升為 3rd 順位，補強 The Verge 週末斷料空窗；HN 留為最後一道）

### ⚔️ 軍事新聞（主要：NBC News）
- 主要：NBC News Military (https://www.nbcnews.com/military)
- 備用 1：Defense News (https://www.defensenews.com)
- 備用 2：Military Times (https://www.militarytimes.com)
- 備用 3：Jane's Defence (https://www.janes.com)
- 備用 4：路透社軍事 (https://www.reuters.com/topics/arms)

### 💰 財經新聞（主要：CNBC）
- 主要：CNBC Top News (https://www.cnbc.com)
- RSS：`https://www.cnbc.com/id/100003114/device/rss/rss.html`
- 備用 1：Yahoo Finance (https://finance.yahoo.com)
- 備用 2：Bloomberg (https://www.bloomberg.com)
- 備用 3：MarketWatch (https://www.marketwatch.com)
- 備用 4：CNN Business (https://money.cnn.com)

### 🌍 國際新聞（主要：CNN）
- 主要：CNN World News (https://www.cnn.com/world)
- 備用 1：BBC News (https://www.bbc.com/news)
- 備用 2：路透社 (https://www.reuters.com)
- 備用 3：AP News (https://www.apnews.com)
- 備用 4：Al Jazeera (https://www.aljazeera.com)

## 工作流

1. **優先抓主要 RSS** - 用 curl 帶 User-Agent 抓 RSS（最快）
2. **RSS 失敗時換備用** - 依序嘗試備用 RSS，最後用 Tavily 搜尋
3. **翻譯** - 所有內容翻譯為繁體中文
4. **整理** - 每類 10 條新聞，標題 + 來源 + 摘要
5. **輸出** - 寫入 Obsidian vault

## RSS 抓取方式

```bash
# Reddit RSS
curl -L -A "Mozilla/5.0" --max-time 15 "https://www.reddit.com/r/technology/new.rss"

# The Verge RSS
curl -L -A "Mozilla/5.0" --max-time 15 "https://www.theverge.com/rss/index.xml"

# Ars Technica RSS（FeedBurner，必帶 User-Agent）
curl -L -A "Mozilla/5.0" --max-time 15 "https://feeds.arstechnica.com/arstechnica/index"

# Hacker News RSS
curl -L -A "Mozilla/5.0" --max-time 15 "https://news.ycombinator.com/rss"

# CNBC RSS
curl -L -A "Mozilla/5.0" --max-time 15 "https://www.cnbc.com/id/100003114/device/rss/rss.html"
```

### 科技 fallback 自動切換 SOP

```
1. 抓 Reddit RSS（主要）
2. 成功且 ≥ 10 筆 → 用 Reddit
3. 失敗 / 不足 → 抓 TechCrunch RSS
4. 失敗 / 不足 → 抓 The Verge RSS（Atom）
   └─ 條件：最近 6h 內 0 筆新文 → 視為「週末斷料」，跳過 The Verge
5. 抓 Ars Technica RSS（FeedBurner） ← 加入 2026-08-15
6. 抓 Hacker News RSS
7. 全部失敗 → Tavily 搜尋
```

## 可信度規則

**優先：**
- 官方媒体报道
- 權威機構發布

**謹慎：**
- 論壇帖文
- 匿名消息

## 輸出格式

```markdown
## 🤖 科技新聞（10則）

1. [標題](連結)
   來源：xxx | 時間：xxx
   摘要：xxx（繁體中文）

## ⚔️ 軍事新聞（10則）

1. [標題](連結)
   來源：NBC News | 時間：xxx
   摘要：xxx（繁體中文）

## 💰 財經新聞（10則）

1. [標題](連結)
   來源：CNBC | 時間：xxx
   摘要：xxx（繁體中文）

## 🌍 國際新聞（10則）

1. [標題](連結)
   來源：CNN | 時間：xxx
   摘要：xxx（繁體中文）
```

## 翻譯原則

- 全部翻譯為繁體中文
- 術語保留原文並附上翻譯（如：AI（人工智慧）、LLM（大語言模型））
- 保持原文語氣和風格
- 標注新聞來源與發布時間
