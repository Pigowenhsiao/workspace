---
name: transcribe
description: |
  音頻轉錄 Skill。當使用者需要將音頻檔案（mp3、m4a、wav 等）轉換為文字稿，或處理 YouTube/影片的字幕檔案時觸發。
  適用場景：
  - 會議錄音需要轉成文字
  - 錄音檔案需要變成可編輯文字
  - YouTube/影片需要字幕檔
  - 音頻內容需要進一步分析或整理
  
  觸發詞：轉錄、transcribe、語音轉文字、音頻轉文字、影片字幕、youtube字幕
  
  依賴：需要 Whisper（已安裝：/opt/homebrew/bin/whisper）或 yt-dlp
---

# Transcribe Skill

## 什麼時候用

- 使用者說「幫我把這段錄音轉成文字」
- 使用者說「把 YouTube 影片的字幕下載下來」
- 使用者說「這個音頻檔案幫我轉寫」
- 使用者說「幫我產生字幕」

## 工作流程

### Step 1: 確認輸入來源

向使用者確認：

```
必要：
- 音頻檔案路徑（本地檔案）
- 或 YouTube/影片 URL

可選：
- 語言（預設自動偵測）
- 輸出格式（txt / srt / vtt）
```

### Step 2: 選擇轉換方式

根據輸入來源選擇：

#### 方式 A：本地音頻檔案（使用 Whisper）

```bash
# 基本轉換
whisper "/path/to/audio.m4a" --model medium --language Chinese --output_format txt --output_dir /tmp/

# 若要翻譯為英文
whisper "/path/to/audio.m4a" --task translate --model medium --output_format srt --output_dir /tmp/
```

#### 方式 B：YouTube 影片

```bash
# 先下載音頻
yt-dlp -x --audio-format m4a "YouTube_URL" -o /tmp/audio.%(ext)s

# 再用 Whisper 轉換
whisper /tmp/audio.m4a --model medium --language Chinese --output_format txt --output_dir /tmp/
```

#### 方式 C：已有字幕檔

```bash
# 使用 yt-dlp 下載字幕
yt-dlp --write-subs --sub-lang zh-Hant,zh-Hans,en "YouTube_URL" -o /tmp/subs.%(ext)s
```

### Step 3: 後處理

根據需求處理轉換結果：

```
後處理選項：
1. 直接交付文字稿
2. 進一步整理成摘要（結合 note-update）
3. 翻譯（結合 translate skill）
4. 存入 vault 特定位置
```

### Step 4: 交付與整理

```markdown
# 轉換結果

## 基本資訊
- 來源：[檔案路徑或 URL]
- 語言：[偵測到的語言]
- 時長：[總時長]
- 模型：[使用的模型]

## 輸出位置
- 文字稿：/tmp/[檔案名].txt
- 字幕：/tmp/[檔案名].srt

## 下一步
- [ ] 審閱文字稿
- [ ] 整理重點（使用 note-update）
- [ ] 存入 vault
```

## 支援格式

| 輸入格式 | 支援 | 說明 |
|---------|------|------|
| mp3 | ✅ | 標準音頻格式 |
| m4a | ✅ | Apple 常用格式 |
| wav | ✅ | 無損格式 |
| ogg | ✅ | 開放格式 |
| YouTube | ✅ | 需先下載音頻 |
| 其他影片 | ⚠️ | 需先提取音頻 |

## 輸出格式

| 格式 | 說明 | 適用場景 |
|------|------|----------|
| txt | 純文字 | 進一步編輯、分析 |
| srt | 字幕格式 | 影片字幕、 時間戳記 |
| vtt | 網頁字幕 | 網頁嵌入 |
| json | 結構化 | 程式處理 |

## Whisper 模型選擇

| 模型 | 速度 | 準確率 | 記憶體需求 | 適用場景 |
|------|------|--------|-----------|----------|
| tiny | 最快 | 較低 | 最低 | 快速預覽 |
| base | 快 | 中等 | 低 | 一般用途 |
| small | 中等 | 良好 | 中等 | 標準用途 |
| medium | 慢 | 優秀 | 高 | 需要高準確率 |
| large | 最慢 | 最佳 | 最高 | 專業用途 |

**預設使用 medium（中文表現良好）**

## 邊界條件

| 情況 | 處理方式 |
|------|----------|
| 檔案格式不支援 | 嘗試用 ffmpeg 轉換，或告知使用者需先轉換格式 |
| YouTube 無字幕 | 自動使用 Whisper 產生字幕 |
| 音頻品質極差 | 告知可能影響轉換準確率，建議改善錄音品質 |
| 檔案過大（>2小時） | 分段處理或使用较小模型 |
| 網路問題無法下載 YouTube | 告知使用者需要網路連線 |

## 示例

### 典型使用場景 1

**輸入：**
> 幫我把這個錄音轉成文字 /Users/Pigo/recordings/meeting.m4a

**執行：**
```bash
whisper "/Users/Pigo/recordings/meeting.m4a" --model medium --language Chinese --output_format txt --output_dir /tmp/
```

**輸出：**
```
轉換完成！
- 來源：meeting.m4a
- 時長：45分鐘
- 模型：medium
- 輸出：/tmp/meeting.txt
```

### 典型使用場景 2

**輸入：**
> 把這個 YouTube 的字幕抓下來 https://youtu.be/xxx

**執行：**
```bash
yt-dlp --write-subs --sub-lang zh-Hant,zh-Hans,en "https://youtu.be/xxx" -o /tmp/subs.%(ext)s
```

**輸出：**
```
字幕下載完成！
- 格式：vtt + srt
- 位置：/tmp/subs.zh-Hant.vtt
```

## 依賴說明

| 工具 | 路徑 | 安裝方式 |
|------|------|----------|
| Whisper | /opt/homebrew/bin/whisper | `brew install openai-whisper` |
| yt-dlp | (系統已有或需安裝) | `brew install yt-dlp` |
| ffmpeg | (系統已有) | `brew install ffmpeg` |

## 限制說明

- Whisper 對中文口語辨識效果較好，文言文或專有名詞可能需後處理
- 即時錄音轉換需要其他工具（如 macOS 语音備忘錄）
- 音頻品質直接影響轉換準確率
