# Vault Frontmatter Repair — 2026-10-28 (16th run)

## 背景

Vault 有 **91 檔** frontmatter 無效（YAML 解析失敗）。前幾次嘗試都用 regex 批次改寫，
結果踩到三個坑。本 session 重寫成 byte-level 修補器後，一次修好 26 檔。

## 新工具

`/home/x/.hermes/cache/scratch/fix_yaml.py`（v4）

核心設計：**byte-level、只替換單行**。
- `split_fm(raw)` 只用 byte offset 切出 frontmatter 區段，**不回頭重建整個檔案**
- 逐行 `raw.split(b'\n')` → 只把「需要修的那一行」換掉 → `b'\n'.join()` 回去
- 寫出用 `raw[:4] + newfm + rest`（`raw[:4]` = 開頭 fence + 可能的 `\r`）

## 三個坑（都是本 session 實際踩到）

### 坑 1：切 frontmatter 時把收尾 fence 弄掉

第一版 `split_fm` 是：
```python
idx = raw.find(b'\n---', 3)
end = raw.find(b'\n', idx + 1)     # ← 錯
return raw[4:idx], raw[end:]      # rest 從 fence「後面」開始 → fence 被吃掉
```
症狀：每個被修的檔案都少一行 `---`，且 diff 顯示 `----` / 無對應 `+`。
**修法**：`rest` 要從 `idx` 開始（`raw[idx:]`），這樣 `\n---` 本身留在 rest 裡。

### 坑 2：CRLF 檔案的 fence 會少掉 `\r`

`raw[:4]` 假設是 `b'---\n'`。CRLF 檔案（Vault 內 x-note / arxiv 大量存在）
實際是 `b'---\r\n'`，`raw[:4]` = `b'---\r'` → 開頭 fence 變成 `---\r`（沒有 `\n`），
下一行直接黏上去。
**修法**：不要寫死 `b'---\n'`，一律用 `raw[:4]`（原封不動帶走原本的換行）。

### 坑 3：R6「引號值 + 後綴散文」規則會吃掉散文（資料遺失）

原規則：
```python
m = re.match(r'^("[^"]*")\s+\((.+)\)$', val)
return m.group(1)          # ← 只留引號內的值，後面的 (prose) 被丟掉
```
症狀：diff 顯示 `-  - "[[Claude-Code-15-Tips-...]]" (Claude-Code-15-Tips tip 5 — "Cowork Dispatch…", prior mention)`
變成 `+  - "[[Claude-Code-15-Tips-...]]"`，**整段 prose 消失**。

**修法**：整個字串用單引號包起來，散文保留：
```python
if re.match(r'^"[^"]*"\s+\(.+\)$', val):
    return "'" + val.replace("'", "''") + "'"
```

## 驗證方法（每步都要跑，不能跳）

1. **body 未動**：逐檔比對 `old[idx+4:] == new[idx+4:]`（frontmatter fence 之後的位元組必須完全相同）
2. **CRLF 存活**：`git diff | cat -A` 看有沒有 `^M$`
3. **值守恆**：逐行比對「去掉引號/反斜線/空白後」的字串必須相同
   ```python
   def sq(s): return re.sub(r"[\s'\"\[\]]", '', s.replace('\\',''))
   ```
4. **key 序列不變**：`yaml.safe_load` 後比較 top-level key 集合
5. **行數不變**：`len(ofm) == len(nfm)`（坑 1 會在這裡現形）

⚠️ 驗證腳本本身有個陷阱：從 `git show HEAD:file` 讀出來的是 **LF** 版本，
磁碟上是 **CRLF**，直接 `split('\n')` 會差一行。
**解法**：比對前先 `.replace('\r\n','\n')` 正規化兩邊。

## 本次結果

- 修好 **26 檔**（91 - 65 unresolved）
- 30 insertions / 30 deletions，26 檔全部 ≤2 行變更
- 全部通過上述 5 項驗證
- 已 commit + push：`cf809e276 fix(vault): repair 26 files with invalid YAML frontmatter`

## 未處理（65 檔，plateau）

剩下的 65 檔不是 scalar 層級可解的問題，主要型態：
- `title: > dude built...`（把 block-scalar indicator 當普通文字用）
- `title: Our great national tragedy:  "Today,..."`（值裡的 colon 沒引號）
- `date: "2025-06-17" (I'll need to estimate...)`（引號值 + 散文，且散文含 `:`）
- list item 本身是壞的 quoted scalar（`-"[[...]]" (...)`）
- `created: {{date}}`（YAML 認不出 `{{ }}` 當 key）

這些需要**結構性**處理（例如把 `title:` 的值改成 block scalar `>-`，或把 list item 重新序列化），
已超出「value-preserving scalar 修補」的安全邊界，留待人工裁決。
**不要對同一類反覆 try fix**——plateau 訊號代表 policy gap，不是次數不夠。

## 預防

1. 批次改寫 frontmatter **一律 byte-level**，逐行替換，不要「切出→修→拼回」重建
2. `raw[:4]` 帶走原始 fence 與換行，不要寫死 `b'---\n'`
3. 任何「丟棄尾隨內容」的規則都是資料遺失——修補必須**保留全部語意**
4. 修完立刻看 `git diff --numstat`：任何單檔 >2 行變更 = 有東西不對
