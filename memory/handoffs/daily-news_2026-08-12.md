# Daily News Handover — 2026-08-12

- **日期**：2026-08-12（Asia/Taipei，台北時間）
- **Cron**：757c1b57-0baa-489e-ba6a-a6f108c54a6d（每日新聞摘要 00:00）
- **執行時間**：2026-08-12 00:04（台北時間）
- **執行 Agent**：Jarvis

## Goal
每日新聞摘要（Asia/Taipei 00:00），依四大類別（科技 / 財經 / 國際 / 軍事）各抓 5 則，全部翻譯為繁體中文（術語保留英文），寫入 Obsidian vault `00-Inbox/2026-08-12_News-Update.md`，完成後 commit + push，並填寫本交接檔。

## Current State

| 類別 | RSS 來源 | HTTP | 取得數 / 目標 | 狀態 |
|---|---|---|---|---|
| 🤖 科技 | The Verge | 200 | 5 / 5 | ✅ |
| 🤖 科技（補強） | Hacker News | 200 | 5 / 5 | ✅（本次未採用，Verge 已足夠） |
| 💰 財經 | CNBC | 200 | 5 / 5 | ✅ |
| 🌍 國際 | BBC World | 200 | 5 / 5 | ✅ |
| ⚔️ 軍事 | The War Zone (The Drive) | 200 | 5 / 5 | ✅ |

- **總計**：20 / 20 全部成功，0 失敗類別。
- **Obsidian 寫入**：`00-Inbox/2026-08-12_News-Update.md`（77 行）
- **Git**：pull rebase（已是最新）→ commit `fc27d606c` → push 成功（`95e5b4b79..fc27d606c`）。

## Source Chain

抓取命令（台北時間 2026-08-12 00:04 執行）：

```
# 科技
curl -L -A "Mozilla/5.0" --max-time 15 "https://www.theverge.com/rss/index.xml"
# → HTTP 200，30K，5 筆採用

# 備援（未採用）
curl -L -A "Mozilla/5.0" --max-time 15 "https://hnrss.org/newest"
# → HTTP 200，19K，5 筆（Verge 已達標故略）

# 財經
curl -L -A "Mozilla/5.0" --max-time 15 "https://www.cnbc.com/id/100003114/device/rss/rss.html"
# → HTTP 200，21K，5 筆採用

# 國際
curl -L -A "Mozilla/5.0" --max-time 15 "http://feeds.bbci.co.uk/news/world/rss.xml"
# → HTTP 200，20K，5 筆採用

# 軍事
curl -L -A "Mozilla/5.0" --max-time 15 "https://www.thedrive.com/the-war-zone/feed"
# → HTTP 200，718K，5 筆採用
```

原始 RSS 快取於 `/tmp/news/2026-08-12/{tech_verge,tech_hn,finance_cnbc,world_bbc,war_thedrive}.xml`。

### 抓取時間（台北時間）
- 開始：2026-08-12 00:04
- RSS 全部抵達：2026-08-12 00:05
- Obsidian push 完成：2026-08-12 00:08 左右

## Decision Needed
無。本批 20 則全部 RSS 直連成功、無需決策介入。

## Recommended Default
若再次出現 RSS 失效，採用以下降級鏈（已驗證穩定）：
- 科技：The Verge → Ars Technica → Hacker News
- 財經：CNBC（無備援建議）
- 國際：BBC World → Reuters
- 軍事：The War Zone → War on the Rocks（必要時跳過）

## Risks / Do Not Do
- ❌ 禁止發布未經翻譯的新聞。
- ❌ 禁止直接推送未驗證的 commit（本批已驗證 push 成功）。
- ❌ 禁止使用 UTC 時間，所有時間戳記一律 Asia/Taipei。
- ❌ 禁止繞過 RSS 直連首頁 DOM 抓取（除非 RSS 全軍覆沒）。
- ❌ 禁止使用 Reddit RSS（已棄用）。

## Next Action
- 等待明日 cron（2026-08-13 00:00 台北時間）自動觸發。
- 若 The Drive / War Zone 隔日失效，啟動降級鏈至 War on the Rocks。
- 觀察 Obsidian `00-Inbox/` 是否被外部流程自動歸檔，必要時調整 `processed: true` 流程。