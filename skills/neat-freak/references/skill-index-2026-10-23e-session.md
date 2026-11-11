# neat-freak session — 2026-10-23 (第五 run)

**Job:** Vault 整潔同步（neat-freak）· 5-Phase · cron `539040a91ad2`
**Result:** 修復 `check_wikilinks.py` basename 比對 bug（假斷鏈 22,418 → 17,288）+
移除 24 檔 x-note 假 wikilink；兩 repo commit + push 完成；Phase 1/2/4/5 全綠

## 各 Phase 結果

| Phase | 項目 | 結果 |
|---|---|---|
| 1 | Vault `git status` | 工作區乾淨，與 origin/main 同步 ✅ |
| 1 | dangling objects | `git fsck` 僅 1 個 dangling tree（無害）✅ |
| 1 | **x-note 假 wikilink** | **24 檔 `[[待補充]]` / `[[待補充：…]]` → 純文字佔位** |
| 1 | Vault commit + push | `ff38c46e4` → merge `53e4a2bbf` → `8bc0d0a5b` → push ✅ |
| 2 | memory 鏡像 | `diff -rq` 一致（merge 後修正 1 檔）✅ |
| 3 | `sync-check.py` | RESULT: CLEAN ✅ |
| 3 | canonical ↔ workspace | `diff -r` → IDENTICAL ✅ |
| 3 | `skill-index-check.py` | ✓ ALL CLEAN（759 = header = 8 sections，0 dangling）✅ |
| 3 | **check_wikilinks.py bug** | **修 3 個缺陷；repo 根重複實作改為轉呼叫 canonical** |
| 3 | Agent repo commit + push | `eb5f5ba7` → merge `fcd4e395` → push ✅ |
| 4 | cron output | 50 / 50 / 7 檔，全 < 500 門檻，**無需清理** ✅ |
| 5 | Hermes Backup | job `89c411611e6d`（每日 03:00）正常，40 份備份，最新 463M ✅ |
| — | mojibake (Pattern II) | Vault active 0（僅歷史 audit 報告）／Agent repo active 0（僅 skill-backups）✅ |

## 新 Pattern SS：批次改寫用文字模式會吃掉 CRLF 行尾

### 症狀

對 Vault 10 檔 x-note 做 regex 批次改寫（`[[待補充]]` → `待補充`）後，
`git diff --stat` 顯示 **每檔 142–224 行全變**，而非預期的 1 行。

### 根因

Python `open(p, encoding='utf-8').read()` 走 **universal newlines**：
讀入時把 `\r\n` 正規化成 `\n`；`open(p, 'w').write()` 寫出時用 `\n`。
→ **CRLF 檔案的行尾被無聲改成 LF**，整檔在 git 眼中全變。

Vault 內 x-note 多為 CRLF（Windows 來源），因此每次批次改寫都會踩到。

### 修復

改用 **binary 模式**做 regex 替換，完全不經過 newline 正規化：

```python
import re, subprocess
out = subprocess.run(['git','grep','-z','-l','-E',r'\[\[待補充','--','*.md'],
                     capture_output=True)
files = [f for f in out.stdout.decode('utf-8').split('\0') if f]
pat = re.compile(r'\[\[(待補充(?::[^\]]*)?)\]\]'.encode('utf-8'))
for f in files:
    b = open(f, 'rb').read()
    nb = pat.sub(lambda m: m.group(1), b)   # bytes pattern
    if nb != b:
        open(f, 'wb').write(nb)
```

### 驗證

- 修復前：`git diff --stat` = 10 files, **890 insertions / 890 deletions**
- 修復後：`git diff --stat` = 10 files, **10 insertions / 10 deletions** ✅

### 預防

1. **Vault 內批次改寫一律用 binary 模式**（`rb`/`wb`），不要用文字模式
2. 改寫後**立刻看 `git diff --stat` 的行數**——若遠超預期，就是行尾被吃掉了
3. `git checkout -- .` 可回退，但會一併丟掉同一批次其他變更
4. 若已誤改且無其他變更 → `git checkout -- .` 後用 binary 模式重做

> ⚠️ 與 Pattern RR（掉首字元）同屬「批次改寫靜默破壞」家族，但成因不同：
> RR 是 regex 本身吃掉字元，本 Pattern 是 I/O 層的 newline 正規化。

## Pattern TT：check_wikilinks.py 的 basename 比對 bug（假斷鏈 22,418）

### 症狀

`check_wikilinks.py --repo ~/Documents/Pigo_Obsidian` 回報 **22,418 個斷鏈目標**，
包含 `[[AI agents]]`、`[[Claude Code]]`、`[[OpenAI]]` 等**確實存在**的筆記。

### 根因（三個缺陷疊加）

1. **basename 集合比對失敗**（主因）
   ```python
   base_lower = {p.rsplit("/", 1)[-1].lower() for p in paths}
   # → {"ai agents.md", "claude code.md", ...}   ← 帶副檔名
   ...
   base = target.rsplit("/", 1)[-1]
   if base.endswith(".md"): base = base[:-3]        # → "ai agents"  ← 已剝副檔名
   ok = base.lower() in base_lower                  # → 永遠 False
   ```
   集合存「帶副檔名」形式，比對時卻用「去副檔名」形式 → **所有短名 wikilink 全被誤判**。
   修法：集合同時收 stem 與含副檔名兩種形式。

2. **範本佔位符被當成真連結**
   `note-name`（x-note 改寫範本的格式說明，LLM 照抄進正文）、
   `...`、`topic:*`（x-note 內部標籤）、`待補充` / `TODO` / `TBD`。
   修法：新增 `is_placeholder()` 排除。

3. **目錄型連結未解析**
   `[[00-Inbox/]]`（Obsidian 允許連資料夾）與 `[[00-Inbox]]`（解析到該目錄 `index.md`）。
   修法：加入目錄前綴比對 + `<dir>/index.md` 比對。

### 修復

- canonical：`skills/x-agent/scripts/check_wikilinks.py`（三處修正）
- repo 根 `scripts/check_wikilinks.py` 是 2026-09-08 的**舊版重複實作**，
  只做相對路徑比對、不支援 basename → 把數萬條正常 wikilink 全判成斷鏈。
  **改為轉呼叫 canonical**（`sys.path.insert` + `import check_wikilinks`），
  消除雙軌漂移。

### 效果

| 階段 | 斷鏈目標數 |
|---|---|
| 修復前 | 22,418 |
| basename 修正後 | 17,302 |
| + placeholder 排除 + 目錄連結 | **17,288**（含 24 處 `[[待補充]]` 已修 → 最終 17,264） |

剩餘 17,264 是**真實斷鏈**（多為 archive 內的舊連結），屬既有積壓，
非本次引入，需獨立議題處理。

## 新 Pattern UU：repo 根 scripts/ 與 skill 內 scripts/ 的重複實作

**發現**：`~/Documents/Agent/scripts/check_wikilinks.py` 與
`~/Documents/Agent/skills/x-agent/scripts/check_wikilinks.py` 是同名不同實作，
前者舊、後者新，但**兩者都被 git 追蹤**，且 `grep -rn check_wikilinks` 找不到
任何文件引用它們——只能靠人肉記憶知道該跑哪個。

**處置**：repo 根版本改為薄 wrapper，轉呼叫 canonical。

**預防**：
- 新增工具腳本時，**canonical 放在 `skills/<name>/scripts/`**，repo 根 `scripts/`
  只放 wrapper 或不放
- 定期 `grep -rn "<script-name>"` 確認有文件指向 canonical

## Merge conflict：upstream force-push 的 sanitized 版本

**情境**：Agent repo 上游（`2b96a374`）force-push 了**去除本機絕對路徑**的
sanitized 版本（公開 GitHub 用）。本地 12 commits 與之 divergence。

**4 處 conflict 全部是「詳細本機路徑 vs 通用描述」**：
- `D:/anaconda3/python.exe` vs `python`
- `~/.pi/agent/.path-config.json` vs 「Agent path configuration」
- `~/.xnote_cache/` vs 「本機 cache directory」
- `/home/x/.hermes/cache/scratch/repair_fm_keys.py` vs 「本機暫存檔，已省略」

**判斷依據**：這是**上游刻意的隱私處理**，不是錯誤的 merge。
採 theirs（sanitized）可避免把本機路徑重新帶回公開 repo。

**教訓**：
- 上游 sanitization 與本地詳細版衝突時，**幾乎永遠採 theirs**
- 判斷方法：`git show <upstream-commit> --stat` 看 commit 訊息是否為
  「publish sanitized」「chore: sanitize」之類
- 剩餘的 `D:/anaconda3` / `/home/x/.hermes` 命中是 upstream **既有**內容
  （用 `git show origin/main:<file> | grep -c` 確認），非本次回歸

## 未處理（需人工裁決 / 獨立議題）

1. **Vault 剩餘 17,264 條真實斷鏈**：多集中於 `04-Archive` 與 `08-Learning`
   的舊 x-note（`[[AI]]` ×193、`[[AI Agent]]` ×124、`[[Jev]]` ×82…）。
   大部分是「概念名」而非真實檔名（LLM 生成的推測性連結）。
   全面清理需決策：**刪連結 vs 補建 concept-hub 筆記**。
2. **Vault 1,024 檔 YAML frontmatter 無法解析**（前次 run 記錄，與本次無關）
3. **818 檔不在 Skill_Index**：`_dead-skills/` 368 + `*_revived/` 414 +
   `gstack.v1.1.0.bak/` 36 — revived 晉升需政策裁決
4. **canonical ↔ Agent repo 技能名分歧**：canonical 269 top-level /
   repo 471 top-level（+ 1,214 巢狀）。canonical-only 54 個
   （gstack-* 30+、comfyui-* 4、vault-rag-* 5、pi-intercom 等）為
   **runtime-only skills**，前次 run 已裁決「維持不動」。
5. **Vault `12-Meta/reports/2026-08-08-audit-wikilinks.md`**（badness 351）
   — 歷史 audit 報告，刻意保留

## 環境事實

- `ftfy` 只在 `/usr/bin/python3`（3.12）
- `check_wikilinks.py` canonical：`~/Documents/Agent/skills/x-agent/scripts/check_wikilinks.py`
  （repo 根 `scripts/check_wikilinks.py` 為 wrapper）
- Vault x-note 多為 **CRLF 行尾** → 批次改寫必須用 binary 模式
- 記憶鏡像：`~/.hermes/memory/` ↔ `~/Documents/Agent/memory/`（本次已重同步一致）
