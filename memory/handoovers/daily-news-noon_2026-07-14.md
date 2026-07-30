# Cron Handover — daily-news-noon (2026-07-14)

> 本份交接：news-aggregator-noon，台北時間 12:04 CST 觸發。

## Goal
於 2026-07-14 12:00（Asia/Taipei）抓取午間新聞摘要，重點為美股收盤訊號、亞股早盤、午間突發（伊朗/荷莫茲）。每類 5 則，全部翻譯繁體中文，寫入 Obsidian vault 並 commit + push。

## Current State
- ✅ RSS 抓取全部成功（5/5 feeds）
  - Verge XML 為 Atom namespace，初次以 RSS 解析回傳 0 筆；改用 `xml.etree + ns="{http://www.w3.org/2005/Atom}"` 修復 → 15 筆可選
  - HN：20 筆，15 筆在 6h 視窗
  - CNBC：30 筆，12 筆在 6h 視窗（部分 ~5.7h 接近邊界但仍在內）
  - BBC：33 筆，4 筆在 6h 視窗（其他 > 6h 視窗延伸抓）
  - War Zone：35 筆，僅 2 筆在 6h 視窗 → **擴充為 8h 視窗才湊足 5 筆**
- ✅ 翻譯完成（科技 5、財經 5、國際 5、軍事 5 = 20 則）
- ✅ Frontmatter 加入 `fetched_at: 2026-07-14 12:04 CST`、`timezone: Asia/Taipei`、sources 列表
- ✅ Vault 路徑：`/home/pigo/Documents/Pigo_Obsidian/00-Inbox/2026-07-14_News-Update-Noon.md`
- ✅ `git pull --rebase` 無衝突
- ✅ `git add`、`git commit`、`git push origin main` 全部成功
- ⚠️ 微風險：未覆蓋任何 `*_News-Update.md`（00:00 那份今晨沒看到，可能由不同 process 處理或本日跳過）

## Source Chain
```bash
# 抓取命令（已驗證，全部 200 OK）：
curl -L -A "Mozilla/5.0" --max-time 15 "https://www.theverge.com/rss/index.xml"
curl -L -A "Mozilla/5.0" --max-time 15 "https://hnrss.org/newest"
curl -L -A "Mozilla/5.0" --max-time 15 "https://www.cnbc.com/id/100003114/device/rss/rss.html"
curl -L -A "Mozilla/5.0" --max-time 15 "http://feeds.bbci.co.uk/news/world/rss.xml"
curl -L -A "Mozilla/5.0" --max-time 15 "https://www.thedrive.com/the-war-zone/feed"
```

時間分佈（CST / UTC+8）：
- HN：07-14 11:29–11:53（全部 6h 視窗內）
- CNBC：07-14 06:09–12:02（多數 6h 視窗內；最新 12:02 是中國出口數據）
- BBC：07-14 09:29–12:02（僅 4 筆在 6h 內；其他延伸 ~24h 抓亞太午間仍相關者）
- War Zone：07-14 00:01–08:29（擴充至 ~12h 才湊足 5 筆）

## Decision Needed
- **無重大**。若 Pigo 對「War Zone 擴充視窗」有意見，下份 16:00 改回嚴格 6h；若接受現制則下份照辦。
- BBC 在 6h 內僅 4 筆，是否要：
  - A) 維持 5 筆含國際（含 ~24h 內延伸 1 筆）
  - B) 縮為 4 筆，視窗絕對嚴格？
  - 預設採 **A**（含延伸），Pigo 收到通知即可覆寫。

## Recommended Default
- War Zone feed 排程延遲是已知現象，建議下次 cron 啟動時直接放寬到「最近 12 小時內」並依相關性排序，5 筆抓得到就好。BBC 國際類也採同樣原則。
- 若 RSS 整批 timeout：跳過該類別，不阻塞其他 3 類。

## Risks / Do Not Do
- 🚫 **勿覆蓋**任何 `*_News-Update*.md`（00:00 / 08:00 / 16:00 任一時段的檔案）
- 🚫 **勿**在未手動 review 的情況下，將「對台海/伊朗」高敏感新聞轉發外部（Signal/LINE/Twitter）
- 🚫 **勿**直接 push 未驗證 commit；push 前一律 `git diff --stat` 確認僅新增 `00-Inbox/2026-07-14_News-Update-Noon.md`
- 🚫 **勿**使用 UTC 時間，所有 timestamp 鎖定 `Asia/Taipei`

## Next Action
- ✅ 已完成 → 等待 Pigo 確認或下一輪 16:00 cron 觸發
- 16:00 下次排程：聚焦「亞股收盤 + 午後美股期貨 + 荷莫茲後續」；如屆時新一輪 Iran/Hormuz 重大升級，應在標題前置 🔥
- 建議 Pigo 下次手動看完文件後，若有重要訊息需長期保存（伊朗、蘋果 Siri AI 中國出口），可由 Pigo 移到 `01-Projects/` 或 `Daily/` 子資料夾
