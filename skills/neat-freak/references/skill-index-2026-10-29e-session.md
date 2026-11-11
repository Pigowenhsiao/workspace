# neat-freak 2026-10-29 第二十三 run session

## 本次唯一新增發現：canonical reference 的 `fos.` typo — Pattern NNN 家族新變體

### 觀察

canonical `references/openclaw-exec-allowlist-fix.md` 第 77–78 行是**無效 Python**：

```python
fos.path.expanduser('~/.nvm/versions/node/v22.22.3/bin/{runtime}'),
```

兩個錯疊加：
1. `fos` 是未定義名稱（typo，應為 `os`）→ 照抄執行必 `NameError`
2. 字串少了 `f` prefix → `{runtime}` 不會展開，`expanduser` 拿到字面 `{runtime}`

### 來源判定（mtime 證據）

- workspace copy（10-24 版）：`f'/home/pigo/.nvm/...'` — 正確但 macOS/舊主機絕對路徑（Pattern HHH 待修狀態）
- canonical（10-29 13:17 改）：`fos.path.expanduser('~/...')` — 某個 10-29 run 做 Pattern HHH 修復時**批次取代注入的 typo**

即：修 Pattern HHH（絕對路徑 → expanduser）的批次動作本身產生了新腐敗。
這是 Pattern NNN 的變體——「批次取代產生語法錯誤的無效 Python」，
但這次連 `ast.parse()` 都不需要跑就抓得到（`fos.` 是明顯 typo）。

### 修復

canonical 改為 `os.path.expanduser(f'~/.nvm/.../bin/{runtime}')`，
並用 `ast.parse()` 驗證文件內**全部 2 個 python block 通過**（NNN 預防手段，本次首次對 reference 文件執行）。

### 同步動作

- canonical → workspace 2 檔（`hermes-cron-jobs.md`：`/home/pigo/` → `$HOME`；`openclaw-exec-allowlist-fix.md`：`/home/pigo/` → `~` + 修 typo）
- Agent repo commit `098485c2` + push（ahead 立即 push，Pattern U）

## Phase 結果

| Phase | 結果 |
|---|---|
| 1 Vault git | clean；dangling 清零（reflog expire + gc --prune=now，count: 0，fsck 無輸出；有 2 條「檔名太長」warning 為 emoji 長檔名，既有狀況非錯誤） |
| 2 Memory | P0/P1/P2 三檔 byte-identical |
| 3 Skills | sync-check CLEAN（修 2 檔後）；skill-index-check ALL CLEAN（760）；磁碟↔index 雙向比對 760=760；canonical↔workspace 33 檔真分歧 = 2026-10-28e 的 29 檔清單（Readme 用途不同 + x-note 平台遷移），狀態未變，持續待裁決 |
| 4 Cron output | 最大目錄 50 檔 << 500，免清理 |
| 5 Backup | 排程 `0 3 * * *` 今天 03:41 已跑，last_status=ok，tarball 486MB |

## 預防（納入腐蝕圖譜）

1. **批次修路徑後，對被改文件的所有 python code block 跑 `ast.parse()`**——`fos.` 這種 typo 只有 parser 抓得到，grep 抓不到
2. reference 文件裡的 Python 片段也是「會被照抄的代碼」，品質標準與 script 相同
