---
name: librarian
description: 根據 URL 類型和內容類型，將外部連結路由到正確的 Obsidian 處理流程。適用於文章、普通網頁、GitHub 項目、YouTube 影片、微信文章等外部連結的整理、總結、調研和歸檔。目標是把不同類型的連結自動送入 Obsidian PARA 倉庫中的正確位置，並支持未來擴充更多 URL 類型處理規則。
---

# Librarian

當用戶分享外部 URL，並希望將其整理進 Obsidian 倉庫時，使用此 skill。

## Obsidian 倉庫位置

- **Vault 路徑**：`~/Documents/Pigo/`

倉庫結構：
- Personal/
- Work/
- Learning/
- Projects/
- Inbox/

---

## URL 路由規則

### 域名啟發式判斷

| URL 關鍵字 | 類型 |
|------------|------|
| github.com | GitHub |
| youtube.com / youtu.be | YouTube |
| mp.weixin.qq.com | 微信文章 |
| bilibili.com | Bilibili |
| x.com / twitter.com | Twitter/X（未來擴展）|
| 微博 | 微博（未來擴展）|
| 小紅書 | 小紅書（未來擴展）|
| 抖音 | 抖音（未來擴展）|
| arxiv.org | 論文（未來擴展）|
| 其他預設 | 普通文章 |

### 1. 普通文章 / 觀點評論 / 一般網頁
- **目標位置**：`~/Documents/Pigo/Learning/clips.md`
- **輸出形式**：表格中的一行
- 表頭結構：`| 日期 | 標題 | 連結 | 分類標籤 | 摘要 |`
- 標籤要克制，只使用 Obsidian 友好大類標籤

### 2. GitHub 項目連結
- **目標位置**：`~/Documents/Pigo/Learning/github-research/{owner}-{repo}.md`
- **輸出形式**：獨立調研報告
- 報告內容：
  - 功能特性
  - 優缺點
  - 與現有系統/skills 的重疊
  - 是否值得替換現有部分 skill
  - 結合可能性
- **不寫入 clips**

### 3. YouTube 連結
- **目標位置**：`~/Documents/Pigo/Learning/youtube/{video-id-or-title}.md`
- **輸出形式**：獨立視頻總結報告
- **報告內容**：
  - 影片標題、頻道、時長
  - **可點選的 YouTube 連結**（獨立一行，方便點擊）
  - 核心內容總結
  - 核心觀點
  - 章節時間軸（若有）
  - 使用的工具/項目
  - 結論
  - 引用的論文、影片連結
  - 引用的工具/項目/服務/產品
- **不寫入 clips**

### 4. 微信公眾號文章
- 優先嘗試文章提取（camoufox 或其他方式）
- 被攔截時回退到瀏覽器態方法
- 如果拿到正文，按普通文章處理（寫入 clips）

---

## URL 規範化規則

在寫入任何記錄/報告前：
- 移除 `utm_*` 參數
- 移除 YouTube 的 `si=` 參數
- 盡量歸一化為 canonical URL

## 重複處理規則

如果同一個規範化後的 URL 已經處理過：
- **跳過**
- 不重複追加 clip
- 不重複創建 GitHub/YouTube 報告

---

## 當前推薦工具路線

- 網頁正文抓取/提取 → Lightpanda 或 bb-browser
- 瀏覽器自動化/登入態操作 → bb-browser
- 搜尋/發現資訊源 → agent-reach（edison-agent-reach）
- GitHub 操作 → gh CLI

---

## 未來可擴展的 URL 類型

- arXiv / 論文
- Twitter/X 推文線程
- Bilibili 影片
- Notion 頁面
- 產品頁 / SaaS 官網
