# 路由模型

## URL 判斷決策樹

```
收到 URL
  │
  ├─ github.com → GitHub 處理流程
  ├─ youtube.com / youtu.be → YouTube 處理流程
  ├─ mp.weixin.qq.com → 微信文章流程
  ├─ bilibili.com → Bilibili 流程（未來擴展）
  ├─ x.com / twitter.com → Twitter/X 流程（未來擴展）
  └─ 其他 → 普通文章流程
```

## 已定義的處理器

| URL 類型 | 目標位置 | 輸出形式 |
|----------|---------|---------|
| 普通文章 | `Learning/clips.md` | 表格行 |
| GitHub | `Learning/github-research/{owner}-{repo}.md` | 獨立調研報告 |
| YouTube | `Learning/youtube/{video-id-or-title}.md` | 獨立視頻總結報告 |
| 微信文章 | 按普通文章處理（寫入 clips） | 表格行 |

## URL 規範化

```
- 移除 utm_* 參數
- 移除 YouTube si= 參數
- 歸一化為 canonical URL
```

## 重複檢查

處理 URL 前，先檢查是否已存在於 clips.md 或對應目錄中。已存在則跳過。

## 未來擴展方向

- arXiv 論文下載 + 總結
- Twitter/X 推文線程歸檔
- 小紅書筆記歸檔
- 微博文章歸檔
- 抖音影片字幕下載
- Notion 頁面同步
