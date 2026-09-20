# Cron Handover: daily-news-noon

## Goal
執行 2026-08-04 午間新聞摘要任務：抓取科技、財經、國際、軍事 4 類 RSS，每類 5 則，整理為繁體中文後寫入 Obsidian vault（`/home/pigo/Documents/Pigo_Obsidian/00-Inbox/2026-08-04_News-Update-Noon.md`），commit + push。

## Current State
- ✅ Verge RSS（Atom 格式）抓取成功，112432 bytes，10 則項目
- ✅ Hacker News RSS 抓取成功，16419 bytes，20 則項目
- ✅ CNBC RSS 抓取成功，20779 bytes，30 則項目
- ✅ BBC World RSS 抓取成功，20379 bytes，26 則項目
- ✅ The War Zone RSS 抓取成功，690193 bytes，31 則項目
- ✅ Ars Technica 備援未觸發（Verge 主來源 OK）
- ✅ 寫入 `/home/pigo/Documents/Pigo_Obsidian/00-Inbox/2026-08-04_News-Update-Noon.md`
- ✅ 填寫本交接檔

## Source Chain
執行時間：2026-08-04 12:06 台北時間（CST / UTC+8）

curl 命令（台北時間 12:06:33 執行）：
- `curl -L -A "Mozilla/5.0" --max-time 15 "https://www.theverge.com/rss/index.xml"` → 112432 bytes
- `curl -L -A "Mozilla/5.0" --max-time 15 "https://hnrss.org/newest"` → 16419 bytes
- `curl -L -A "Mozilla/5.0" --max-time 15 "https://www.cnbc.com/id/100003114/device/rss/rss.html"` → 20779 bytes
- `curl -L -A "Mozilla/5.0" --max-time 15 "http://feeds.bbci.co.uk/news/world/rss.xml"` → 20379 bytes
- `curl -L -A "Mozilla/5.0" --max-time 15 "https://www.thedrive.com/the-war-zone/feed"` → 690193 bytes

選擇邏輯：6 小時窗口 = UTC 22:06 (08-03) ~ 04:06 (08-04)，優先取窗口內項目，不足 5 則補上當日最新。

時間轉換範例：
- CNBC "Tue, 04 Aug 2026 03:03:18 GMT" → 2026-08-04 11:03 CST
- War Zone "Mon, 03 Aug 2026 18:55:22 -0400" → 2026-08-04 06:55 CST
- Verge (Atom ISO) "2026-08-03T20:00:00-04:00" → 2026-08-04 08:00 CST

## Decision Needed
無（任務已按既定流程完成）

## Recommended Default
拿不準的來源 → 跳過該類別；這次 5 個來源全部成功，無需跳過。

## Risks / Do Not Do
- 🚫 勿覆蓋 00:00 的 `2026-08-04_News-Update.md`
- 🚫 勿發布未經翻譯的新聞原文
- 🚫 勿在 commit 失敗時直接 force push
- 🚫 勿使用 UTC 時間戳記（hander 與新聞內文一律台北時間）
- 🚫 勿擅自改用未經驗證的備援 RSS 而不留下日誌

## Next Action
- 需 git pull / add / commit / push（見 cron 訊息規格）
- 寫入檔名：`2026-08-04_News-Update-Noon.md`（已建立）
- commit 訊息：`Add news update noon 2026-08-04`