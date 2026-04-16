---
name: paper-read
description: |
  學術論文路由 Skill。當需要處理學術論文、研究文獻，或需要路由到特定研究雷達模組時觸發。
  適用場景：
  - 分析研究論文
  - 路由查詢到專門研究雷達模組
  - 學術文獻評估
  - 論文結構分析
  
  觸發詞：paper read, 論文分析, 學術, research, radar
  
  基於：Gemini-Prime Academic-Omni-Router 框架
---

# Paper Read / Academic Omni Router

## 什麼時候用

- 使用者說「分析這篇論文」
- 使用者說「這篇研究值不值得看」
- 使用者說「論文路由」
- 需要將學術查詢路由到正確的專門模組

## 工作流程

### Step 1: 確認論文來源

```
必要：
- 論文 URL / PDF 檔案 / arXiv ID
- 或純文字內容

可選：
- 特定分析類型（摘要、評估、路由）
- 是否需要翻譯
```

### Step 2: 路由判斷

```markdown
## 路由決策

### 如果是...
- arXiv 論文 → 使用 arXiv 專門處理
- PDF 檔案 → 提取文字再分析
- 純文字 → 直接分析
- 需要翻譯 → 先翻譯再分析

### 否則...
使用通用學術分析流程
```

### Step 3: 分析類型

根據需求選擇分析深度：

```markdown
## 分析層級

### 輕量級（摘要）
- 一句話總結
- 核心貢獻
- 適用讀者

### 中量級（評估）
- 論文結構
- 方法論評估
- 創新點分析
- 局限性

### 重量級（深度分析）
- 完整論文解析
- 與相關工作對比
- 實驗設計評估
- 實際應用建議
```

### Step 4: 路由到專門模組

```markdown
## 路由到雷達模組

根據學科領域路由：
- AI/ML 研究 → AI Research Radar
- 生物/醫學 → Bio-Med Radar
- 物理 → Physics Radar
- 化學 → Chemistry Radar
- 其他 → General Academic Radar

或者路由到參考目錄中的特定模組。
```

## 雷達模組架構

```
reference/
├── ai-radar.md           # AI/ML 研究雷達
├── biomed-radar.md        # 生物/醫學雷達
├── physics-radar.md       # 物理學雷達
├── chemistry-radar.md      # 化學雷達
└── general-radar.md       # 通用雷達
```

## 邊界條件

| 情況 | 處理方式 |
|------|----------|
| 論文格式不支持 | 嘗試 PDF 提取或 OCR |
| 無法訪問付費論文 | 告知需要合法途徑取得 |
| 領域無法判斷 | 使用通用學術雷達 |
| 需要翻譯 | 先翻譯再路由 |

## 示例

### 典型使用場景

**輸入：**
> 分析這篇 arXiv 論文 https://arxiv.org/abs/2301.00001

**處理流程：**
1. 提取論文摘要
2. 識別領域（AI/ML）
3. 路由到 AI Research Radar
4. 生成分析報告

**輸出：**
```markdown
# 論文分析

## 基本資訊
- 標題：[論文標題]
- 作者：[作者]
- 領域：AI/ML

## 核心貢獻
[貢獻描述]

## 路由到的雷達模組
AI Research Radar

## 分析結果
[雷達模組生成的詳細分析]
```
