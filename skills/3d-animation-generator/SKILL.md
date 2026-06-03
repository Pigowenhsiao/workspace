---
name: 3d-animation-generator
description: "根據 prompt 生成單一 HTML5 檔案，含動畫場景、字幕、控制條。純 CSS 3D transforms，無 canvas/WebGL/外部函式庫。"
version: 0.1.0
author: Jarvis
metadata:
  hermes:
    tags: [html5, animation, css3d, visual-explainer, presentation]
    category: content-generation
---

# 3D Animation Generator

生成單一 HTML5 檔案，播放動畫敘事的視覺解說。使用純 CSS 3D transforms，無 canvas、WebGL 或外部函式庫。

## 何時使用

- 使用者要你生成一個可自含的 HTML5 動畫
- 要生成視覺化的概念解說（如同 slides 但單頁滾動）
- 要一個可以直接雙擊開啟的演示檔

## 引擎架構

### 核心變數

```javascript
const scenes = [
  { start: 0, end: 3, html: 0 },  // 每幕 { 開始秒數, 結束秒數, 場景編號 }
  { start: 3, end: 6, html: 1 },
  // ...
];
const subs = [
  { s: 0, e: 0.8, t: "字幕文字" },
  { s: 0.8, e: 1.5, t: "另一段字幕" },
  // ...
];
const TOTAL = 15; // 總秒數
```

### 必要元素

1. **Stage**: `#stage` 容器，`perspective:1800px`
2. **Scenes**: `.scene` 每幕絕對定位，用 `cubic-bezier` 轉場
3. **Captions**: `data-at="N"` 控制進場時間
4. **Controls**: 44px 固定底部，含 prev/play/next、字幕、進度條、章節點
5. **Ambient**: 18 個浮動粒子 + 2 個模糊背景形狀
6. **Flash**: `#sceneFlash` 每幕切換時閃爍

### CSS Tokens

```css
:root {
  --bg: #F9F7F7;
  --bg2: #EEF1F7;
  --card: #fff;
  --teal: #3F72AF;
  --teal-soft: rgba(63,114,175,0.08);
  --coral: #E07A5F;
  --coral-soft: rgba(224,122,95,0.08);
  --navy: #112D4E;
  --text: #112D4E;
  --muted: rgba(17,45,78,0.7);
  --border: rgba(17,45,78,0.08);
  --shadow: 0 2px 20px rgba(17,45,78,0.06);
}
```

### Typography

- Heading: `'Chiron GoRound TC', 'Instrument Serif', sans-serif`
- Body: `'Chiron GoRound TC', sans-serif`
- Mono: `'DM Mono', monospace`

### 必備 Classes

- `.subtitle`: mono 風格、teal 色、uppercase、letter-spacing
- `.title`: heading 字型、navy 色、含 `.hl` 強調
- `.note`: body 字型、muted 色、max-width 640px

### 控制項功能

| 按鍵 | 功能 |
|------|------|
| Space | 播放/暫停 |
| ← | 上一幕 |
| → | 下一幕 |
| 觸控左右滑 | 上一幕/下一幕 |
| 進度條點擊 | 跳轉位置 |

### Accessibility

```css
@media (prefers-reduced-motion:reduce) {
  *,*::before,*::after { animation: none !important; transition-duration: 0.01s !important; }
}
```

## 生成 Prompt Template

```
[ATTACH YOUR CONTENT HERE. Provide:
• Topic / one-line pitch
• Total target duration in seconds e.g. 180
• Ordered list of scenes — for each: a heading, the point you want to make, and any specific text/labels/data that must appear on screen
• Caption language(s)
• Optional: any palette/font overrides otherwise keep the reference's]
```

## Output

- 產出單一 `.html` 檔
- 所有 CSS/JS 內嵌
- 只允許 Google Fonts 外部載入
- 可直接雙擊開啟，無需伺服器

## 3D 視覺技巧 Vocabulary

- flip card（翻轉卡片）
- rotating cube（旋轉立方體）
- parallax stacked layers（視差層疊）
- carousel ring（旋轉木馬環）
- floating phone mockup（懸浮手機模型）
- 3D extruded text（3D 突出文字）
- tilted browser mockup（傾斜瀏覽器模型）
- z-axis arc of steps（Z 軸弧形台階）
- 3D conversation bubbles（3D 對話氣泡）
- pop-out spotlight grid（聚光燈格）
- before/after tilted panels（傾斜比對面板）
- orbiting concept network（軌道概念網路）

## 輸出格式

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[標題]</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
...（完整 HTML）
```

## 使用範例

參考輸出：`~/Downloads/3d-animation-demo.html`

內容為「什麼是 AI Agent？」5 幕、15 秒的動畫解說，演示：
- 標題 entrance 動畫
- 4 個場景切換 + flash 效果
- 浮動粒子 ambient 層
- 完整控制條（播放/暫停/上一/下一）
- 鍵盤 + 觸控支援
- 低動態偏好支援