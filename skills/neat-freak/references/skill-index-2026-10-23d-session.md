# neat-freak session — 2026-10-23（第四 run：Vault frontmatter key 首字元遺失）

## 觸發

cron job「Vault 整潔同步（neat-freak）」5-Phase 同步。Phase 1 發現 Vault working tree
有 **2,672 檔未 commit 的修改**（前幾個 session 遗留），內容是 tag 小寫化 + quote 正規化
+ wikilink 路徑更新（`04_AI-Engineering-Tools` → `08-Learning` 重構的後續）。

**但其中 655 檔的 YAML frontmatter key 被掉了第一個字元**。

## Pattern RR（2026-10-23 初發現）：Bulk rewrite 掉 frontmatter key 首字元

### 症狀

frontmatter key 首位字元消失：

| HEAD（正確） | Working tree（損壞） |
|---|---|
| `sources:` | `ources:` |
| `type:` | `ype:` |
| `status:` | `tatus:` |
| `score:` | `core:` |
| `date:` | `ate:` |
| `rating:` | `ating:` |
| `created:` | `reated:` |
| `source:` | `ource:` |
| `category:` | `ategory:` |
| `categories:` | `ategories:` |
| `classification_path:` | `lassification_path:` |
| `related_to:` | `elated_to:` |

**受影響檔案：655 / 2,672**（前 12 類 key 合計 ~651 次）

### 為什麼舊檢查抓不到

1. `git diff` 會把 `-sources:` / `+ources:` 顯示為**看似合理的兩行**，肉眼看是「key 名不同」，
   不會意識到是「掉字元」
2. YAML 解析**不會報錯**——`ources:` 是合法的 YAML key，只是 key 名錯了
3. `file` / grep / 相對時間檢查全部無效
4. 檔案「讀起來正常」，只有比對 HEAD 才知道 key 被改過

### 偵測法（可靠）

比對 HEAD 與 working tree 的 **frontmatter key 序列**：

```python
import subprocess, re
KEYRE = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*):')

def keys(fm_text):
    return [KEYRE.match(l).group(1) for l in fm_text.split('\n') if KEYRE.match(l)]

for f in modified_files:
    old_fm = frontmatter(subprocess.run(['git','show','HEAD:'+f], capture_output=True).stdout.decode())
    new_fm = frontmatter(open(f, encoding='utf-8').read())
    ko, kn = keys(old_fm), keys(new_fm)
    if len(ko) == len(kn):
        for a, b in zip(ko, kn):
            if a != b and b == a[1:]:
                print('DROPPED FIRST CHAR:', f, a, '->', b)
```

**關鍵前提**：key 序列的**長度必須相同**。本次 2,672 檔全部長度一致（0 mismatch），
所以位置對齊（zip）是安全的。若長度不同 → 該檔有其他結構變更，必須人工檢視。

### 修復法

對每個 key 位置，若 `kn[i] == ko[i][1:]` → 把首字元補回。
**只補 key 名，不動 value**（value 的變化如 tag 小寫化是預期變更，必須保留）。

### 驗證（本次實測）

| 檢查 | 修復前 | 修復後 |
|---|---|---|
| frontmatter key mismatch 數 | 655 檔 | **0** |
| 殘留 mangled key（`ources:` 等 12 類） | 655 | **0** |
| YAML 解析失敗檔案數 | 1,024 | 1,024（**與修復前完全相同 → 皆為既有問題，非本次引入**） |
| 改寫後 wikilink target 可解析 | — | 836 / 836 |

**驗證技巧**：修復後必須**同時比對修復前後的 YAML invalid 數**。
兩者相等 → 證明本次修復沒有引入新的解析錯誤。
只比對「修復後是否 0 invalid」會誤判（既有 1,024 檔本來就 invalid）。

## 本次修復清單

| 項目 | 結果 |
|---|---|
| Vault frontmatter key 首字元遺失 | **655 檔已修復**（0 殘留） |
| Vault commit | `9571475ba`（2672 檔） |
| Vault merge origin/main | `0374e373e`（1 conflict，見下） |
| Vault push | `82cd45b00..0374e373e` ✅ |
| Memory 鏡像 | `diff -rq` 完全一致，無需同步 |
| neat-freak canonical ↔ workspace | `diff` 全一致，CLEAN |
| Skill_Index | 759 = header = 8 sections，0 dangling，0 purpose corruption |
| cron output | 50 / 50 / 7 檔，全 < 500 門檻，無需清理 |
| Hermes Backup | 03:00 正常完成，`hermes_2026-10-23_030034.tar.gz` |

## Merge conflict 處理：LLM-Wiki-Index.md 路徑形式分歧

- **HEAD 側**：`[[10-LLM-Wiki/...]]`（root-relative）
- **origin 側**：`[[../../../10-LLM-Wiki/...]]`（file-relative）
- **判斷依據**：該檔既有 519 筆 root-relative、1 筆 relative → **root-relative 是主流慣例**
- **處置**：採 root-relative + 保留 origin 新增的條目 + 刪除重複的 relative 條目
- **驗證**：解決後 relative 筆數 = 0

## 既有問題（非本次引入，記錄待處理）

1. **Vault 1,024 檔 YAML frontmatter 無法解析**
   - 分布：08-Learning 720 / 09-Article-Notes 92 / 04-Archive 80 / 03-Resources 54 / 其他
   - 主因：`mapping values are not allowed here`（453）、`while parsing a block mapping`（305）、
     `while scanning for the next token`（222）——多為 value 內含未引號的 `:` 或特殊字元
   - 修復前 = 修復後，與本次變更無關；全面修復需批次處理 1,024 檔，屬獨立議題

2. **`_dead-skills/` 與 `*_revived/` 共 818 檔不在 Skill_Index**
   - `_dead-skills/` 368 檔 = 已歸檔（2026-07-13 commit「archive: move 379 dead Codex skills」）
   - `*_revived/` 414 檔 = 從 dead 復原但未納入 index 的候選
   - `gstack.v1.1.0.bak/` 36 檔 = 備份目錄
   - **不自動納入**：818 檔的分類政策需裁決（哪些 revived 該晉升為 active）

3. **canonical ↔ Agent repo 技能名分歧**
   - canonical 854 個 skill 名 / Agent repo 1,081 個
   - canonical-only 326 個（含 41 個 archived/backup 命名）、agent-only 553 個
   - 兩邊是不同層級的 skill 存放處（canonical = Hermes runtime，repo = Agent workspace），
     非一對一鏡像關係；2026-10-23c session 已記錄為「架構決策，未動」

## 預防

- 任何對 vault 做批次 YAML 重寫的腳本，**必須在寫回後驗證 key 名逐檔比對 HEAD**
- 批次改寫 frontmatter 優先用「解析 → 修改 value → 重新序列化」而非 regex 取代整行，
  regex 取代整行容易吃掉 key 首字元
- 批次改寫後立刻跑 YAML 解析 + 與 HEAD 的 key 序列比對，兩者缺一不可
- **修復前後都要量一次 YAML invalid 數**，才能區分「既有問題」與「本次引入」
