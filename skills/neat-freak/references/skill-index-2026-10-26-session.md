# neat-freak session — 2026-10-26

## Pattern OOO（本次初發現）：YAML frontmatter 內混入 Markdown 指令 → Hermes loader 整個跳過該 skill

**觀察**：canonical `~/.hermes/skills/` 有 13 個 `SKILL.md` 的 YAML frontmatter 無效，
但 skill-index-check.py（只檢查 workspace `docs/Skill_Index.md`）完全看不到。

**注入內容**（13 檔全部同一行）：

```
**重要：所有輸出內容必須使用繁體中文。**
```

它被塞在 `---` fence **之間**（不是 fence 之外），讓 YAML parser 看到
`key: **重要...**` → 語法錯誤 → `parse_frontmatter` 失敗 → loader 記
`Skipping invalid skill` → 該 skill 從未進入 command catalog。

**為什麼舊檢查抓不到**：
- `skill-index-check.py` 只掃 `~/Documents/Agent/docs/Skill_Index.md`，不碰 canonical skill 檔
- `sync-check.py` 只比 canonical vs workspace 的**目錄結構**，不比 frontmatter
- `hermes skills list` 輸出格式不明顯，不會直觀顯示「少了 13 個」
- 檔案在磁碟上存在、內容完整、只是 YAML 解析失敗 → 沒有任何「檔案遺失」訊號

**修復（binary 模式，見 Pattern SS）**：
1. 以 bytes 讀入 → 找 frontmatter fence 邊界
2. 把注入的 Markdown 指令**移到 fence 之外的 Markdown body**（不可刪除：會改變 skill 行為）
3. 順帶修掉同批的 trailing comma、巢狀 key 縮排錯誤
4. 備份原件到 scratch 再改

**驗證（必做，通用 YAML 解析不足夠）**：
```python
import sys; sys.path.insert(0, '/home/x/.local/share/uv/tools/hermes-agent/lib/python3.12/site-packages')
from agent.skill_utils import parse_frontmatter
from agent.skill_commands import scan_skill_commands
```
- `parse_frontmatter(path)` 對 13 檔全部回傳合法 metadata
- `scan_skill_commands()` 能發現 12 個 active skill（`.archive/` 底下的正確被排除）

**Prevention**：
1. **frontmatter 掃描必須覆蓋 canonical skill 樹**（`~/.hermes/skills/**/SKILL.md`），
   不能只掃 index
2. 通用 YAML 解析通過 **≠** Hermes 能載入 → 必須用 Hermes 自己的
   `parse_frontmatter` / `scan_skill_commands` 驗證
3. 任何「在 frontmatter 裡加一句話」的動作都要用 binary 模式，
   且加完立刻跑 `parse_frontmatter`
4. `.archive/` 底下的 skill 也要修 YAML（只是不進 active command catalog）

---

## Pattern PPP（本次初發現）：workspace copy 與 canonical 各有各的 frontmatter 損壞 — 兩邊都要掃

**觀察**：本次在 canonical 修完 13 檔後，掃 workspace `~/Documents/Agent/skills/`
（1,209 檔）又發現 **5 檔**獨有的無效 frontmatter，canonical 沒這問題：

| 檔案 | 損壞型別 |
|---|---|
| `learning-recap-to-x/SKILL.md` | 巢狀 key 縮排 3 空格（應 4） |
| `learning-recap-to-x_revived/SKILL.md` | 同上 |
| `hv-analysis/SKILL.md` | list 項缺 `- ` marker → 變成獨立 key |
| `xiaocui-skill/SKILL.md` | `source_channel: "x" 尾隨散文` → YAML 視為 nested mapping |
| `guizang-material-illustration_revived/SKILL.md` | 未加引號的 description 內含 `: ` |

**為什麼重要**：canonical 與 workspace 是**兩份獨立內容**，修一邊不等於修好另一邊。
「同步」是流程，不是保證。

**掃描口徑（兩邊都要跑）**：
```python
import os, yaml
for root in ('/home/x/.hermes/skills', '/home/x/Documents/Agent/skills'):
    for dp, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP]   # 排除 references/examples/scripts/agents/assets/templates
        if 'SKILL.md' in files:
            raw = open(os.path.join(dp,'SKILL.md'),'rb').read()
            yaml.safe_load(raw.split(b'---',2)[1].decode('utf-8','replace'))
```

**陷阱 — 重寫 frontmatter 會吃掉 fence 後的空白行**：
用 `raw[start:idx] + b'\n---' + body` 重建時，若 body 開頭原本是 `\n`，
會變成 `---\n# Title`（少一個空行）→ diff 顯示每檔多一處雜訊。
**修復方式：不要重建**。改用**精確 bytes 取代**（`raw.replace(old, new, 1)`），
其他位元組完全不動，diff 最小、最安全。

**教訓**：
> 第一次嘗試用「切出 frontmatter → 修 → 拼回」的方式改檔，結果 4 個檔案的
> fence 後空行全部消失。改用 `bytes.replace()` 逐一取代後，diff 乾淨到只剩
> 真正的語意修正行。**批次改寫 frontmatter 一律用 replace，不要用重建。**

---

## Pattern QQQ（本次實測確認）：`Skill_Index.md` 的 759 與磁碟 1,209 差額有可解釋結構 — 不是 drift

本次獨立掃描（排除 `references/ examples/ scripts/ agents/ assets/ templates/` 等
非 skill 目錄）：

| 項目 | 數量 |
|---|---|
| 磁碟上 active `SKILL.md` | 1,209 |
| `docs/Skill_Index.md` 列出的 | 759 |
| 差額：`*_revived/` 樹 | 414 |
| 差額：`gstack.v1.1.0.bak/` + `test/fixtures/` | 36 |

**判斷**：
- `*_revived` = 從上游 sync 復原的**舊版** skill（canonical `~/.hermes/skills/` 完全沒有
  `_revived` 目錄），內容與新版有實質差異（`knowledge-vault` vs `knowledge-vault_revived`
  差 11 檔），是「保留歷史」而非「現行 skill」
- `*.bak/` 與 `test/fixtures/` = 明確的備份 / 測試資料

→ **index 的 759 是正確口徑**，不是落後。`skill-index-check.py` 報 `✓ ALL CLEAN`
（759 = header = 8 sections 合計、dangling 0）是可信的。

**教訓**：
> 「磁碟比 index 多」不自動等於 drift。先把差額按**目錄性質**分類
> （現行 / 歷史復原 / 備份 / 測試 fixture），分類完再判斷。
> 這次若直接「重建 index 把 1,209 全部列進去」，會把 414 個歷史版 skill
> 誤標為 active。

---

## 本次其他事實校正（memory 已同步）

- **Port 分家已變**：8081 = Strata IQ3_S（`strata-v100-iq3_s.service`，2026-10-26 起唯一常駐）；
  8080 = Q2_0（inactive）；8082 = UD-IQ4_XS（inactive）；8188 = ComfyUI（非常駐）
  舊記憶寫「8080 = Q2_0 唯一 owner、8081 = llama.cpp」→ 已過期
- **ComfyUI 已升 v0.37.1**（舊記憶寫 v0.33.0 + 固定 PID 1858553）→ PID 這種
  一次性數字不該寫進記憶，改寫啟動方式
- **`.dreams/` 被 gitignore**（`memory/.dreams/` 在 `.gitignore:69`）→
  `~/.hermes/memory/` 與 `~/Documents/Agent/memory/` 的差異只有 2 個 corpus 檔，
  那是設計如此，不是 drift

## Vault mojibake 掃描的假陽性判準（重要）

`ftfy` 的 `badness` 對**中英混排的標點**也會給非零分數。
`12-Meta/reports/2026-08-08-audit-wikilinks.md` file-level badness = 169，
逐行看有 19 行 badness > 0 —— 但那 19 行全是 `target=\`...中文標題...\`` 這種
報告列，內容完全正常。

**判準**：確認是否真 mojibake 必須用 **`fix_encoding()`**（不是 `fix_text()`）：
```python
from ftfy import fix_encoding
fix_encoding(content) == content   # True → 沒有真 mojibake
```
本次結果：19 行 `fix_text` 會改（它在做全形標點轉換，那是**不需要的副作用**），
但 `fix_encoding` **0 行改動** → 全部假陽性。

**教訓**：
> `badness > 0` ≠ mojibake。`fix_text()` 會動全形標點（記憶已記：修復用
> `fix_encoding()` 非 `fix_text()`）。本次驗證再度確認：**判斷用 `fix_encoding`，
> 不要用 `fix_text`**。
