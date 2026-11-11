# neat-freak session — 2026-10-28 (第十六 run)

## 主題：canonical skill 樹的「同名 skill」造成的 `skill_view` ambiguity

## 現象

`skill-index-check.py`、`sync-check.py`、frontmatter 掃描全部綠，但：

```python
from tools.skills_tool import skill_view
skill_view(name='weather')
# → {"success": false, "error": "Ambiguous skill name 'weather': 3 candidates — ..."}
```

canonical 樹 `~/.hermes/skills/` 有 **151 個 name 對應多個目錄**。
loader 對這類 name **無法用 bare name 解析**（`skill_view` 直接失敗），
只有 `/skill <name>` 路徑或完整路徑能用。

## 為什麼舊檢查抓不到

- `sync-check.py` 只比 canonical ↔ workspace 的 **neat-freak 單一 skill**，不掃整棵樹
- `skill-index-check.py` 只驗 `docs/Skill_Index.md`（Agent repo 側），完全不碰 canonical 樹
- frontmatter 掃描只驗 YAML 可解析與 `name` 存在 — 重複 name 是**合法**的 YAML
- `scan_skill_commands()` 回報 `dups: 0` — 因為它用 **slash command 名**當 key，
  而 slash command 由「目錄 basename + 命名空間」推導，與 frontmatter `name` 不同

## 關鍵方法論修正（本次最重要的一條）

**比對「重複」時必須比對「全部檔案」，不能只比 SKILL.md。**

第一次篩選只比 `SKILL.md` 的 sha256 → 得到 82 個「可刪」候選。
實際逐檔比對後，**45 個候選的其他檔案有內容差異**
（例：`openclaw-imports/baoyu-cover-image` 的 `references/style-presets.md` 等 17 個
reference 檔案與 top-level 版本不同）。

→ 若照第一次的清單刪除，會**靜默丟失 17 個 reference 檔案的差異版本**。

正確做法（三層比對）：

```python
def tree(p):   # 全檔案 sha256 map（排除 __pycache__）
    ...
winner = min(candidates, key=lambda p: (p.count('/'), len(p)))   # 最淺路徑勝出
# 對每個 loser c、winner w：
#   1. c 的每個檔案 f 必須在 w 存在（無 only-in-loser）
#   2. 且 hash 完全相同（無 content-diff）
# 三條件全過才可刪
```

## 刪除前後的量化

| 項目 | 刪除前 | 刪除後 |
|---|---|---|
| canonical skill 目錄數 | 929 | 851 |
| 重複 name 數 | 151 | 93 |
| `skill_view` 可解析 name | 94 | 151 |
| frontmatter YAML invalid | 0 | 0 |
| frontmatter 缺 fence | 0 | 0 |

- 刪除 **78 個完全 byte-identical 的重複目錄**（一次到位，零風險）
- 另 **6 個**用「union 合併」處理：SKILL.md 相同、差異只在
  `Readme.md` / `*.bak` 等非功能檔 → 把唯一檔案併入勝出者後刪 loser
- 剩餘 **88 個**是「多版本並存」型（上游 bundle vs 本地 fork，內容實質不同）
  → **留待人工裁決，不自動刪**

## 執行時的兩個陷阱

### 陷阱 1：union 合併時漏搬唯一檔案

合併 `openclaw-imports/pptx-posters` → `openclaw-imports/latex-posters` 時，
手動列出要搬的檔案清單漏了 `assets/poster_html_template.html`
（因為該檔只存在於 loser 的 `assets/`，而 `assets/` 被 SKIP 規則排除在
tree 比對之外 → 沒被偵測到）。

**後果**：刪掉 loser 後該檔永久消失。

**還原**：從 `~/Documents/Backup/hermes/hermes_<TS>.tar.gz` 取出
`./skills/openclaw-imports/pptx-posters/assets/poster_html_template.html`。

**預防**：
- union 合併時，**不要手列檔案清單** → 用程式枚舉 loser 的所有檔案，
  對每個「在 winner 不存在」的檔案自動搬過去
- `assets/` / `references/` / `scripts/` 這些子目錄名**不在** SKIP 集合裡時
  才會被 tree 比對涵蓋；SKIP 集合要按「哪些目錄是 skill 的支援內容」而非
  「哪些目錄是 skill 本體」來劃分

### 陷阱 2：刪除前必須確認備份涵蓋

canonical 樹 **沒有 git**（`~/.hermes/skills/` 不是 repo）→ 刪除不可逆。
唯一的還原路徑是 `~/Documents/Backup/hermes/` 的 tarball。

刪除前先做一份專屬備份：

```bash
cd ~/.hermes/skills
tar -czf /home/x/.hermes/cache/scratch/canon-dup-backup-<TS>/removable-dirs.tar.gz \
    -T <relative-paths-list>
```

注意 `tar -cf`（不壓縮）與 `-czf` 的差別，以及 `-T` 要用**相對路徑**。

## 「哪一份勝出」的判定

loader 的 rank 規則是**路徑越淺越優先**（`skill_candidate_rank`）。
canonical 樹常見的三層結構：

```
~/.hermes/skills/<name>/SKILL.md              ← 最淺，通常勝出
~/.hermes/skills/<category>/<name>/SKILL.md   ← 次之
~/.hermes/skills/openclaw-imports/<name>/     ← 上游 bundle，最深
```

**但勝出者不一定是最新的**：實測 93 個殘餘重複中，**59 個的勝出者
mtime 比某個 sibling 還舊**。這代表「淺路徑優先」與「內容最新」是兩回事 ——
判斷哪份該保留，不能只看路徑深度。

## 剩餘 88 個的分類（待裁決）

| 類型 | 特徵 | 例子 |
|---|---|---|
| gstack 三軌 | `gstack-<x>` / `gstack/commands/gstack-<x>` / `gstack-new/<x>` / `gstack-new/.hermes/skills/gstack-<x>` 四份 | `autoplan`, `benchmark`, `browse` |
| 上游 bundle vs 本地 fork | `openclaw-imports/<x>` vs top-level，body 實質不同 | `baoyu-danger-gemini-web`, `baoyu-creative` |
| category 副本 | `creative/<x>` vs top-level | `Article-writer`, `baoyu-creative` |
| 備份目錄 | `openclaw-imports/_backup_remotion_2026-04-03_0016` | `Remotion` |
| 同 skill 不同世代 | `gstack/` vs `gstack-new/`（body 不同） | 多數 gstack |

這批**不能機械式刪** —— 刪錯會丟失實質不同的功能。列為「未處理」。

## 檢查清單更新

Phase 3 應加入：

```bash
# canonical 樹重複 name 掃描（不看 SKILL.md 就會漏掉 body 差異）
python3 -c "
import os, re, collections, hashlib
root=os.path.expanduser('~/.hermes/skills')
def tree(p):
    d={}
    for dp,dirs,fs in os.walk(p):
        dirs[:]=[x for x in dirs if x!='__pycache__']
        for f in fs:
            fp=os.path.join(dp,f)
            d[os.path.relpath(fp,p)]=hashlib.sha256(open(fp,'rb').read()).hexdigest()
    return d
byname=collections.defaultdict(list)
for dp,dirs,fs in os.walk(root):
    dirs[:]=[d for d in dirs if d not in ('references','examples','scripts','agents','assets','templates','.archive','__pycache__','.git')]
    if 'SKILL.md' in fs:
        raw=open(os.path.join(dp,'SKILL.md'),'rb').read()
        ps=raw.split(b'---',2)
        n=os.path.basename(dp)
        if len(ps)>=3:
            m=re.search(rb'^name:\s*(.+)$',ps[1],re.M)
            if m: n=m.group(1).decode('utf-8','replace').strip().strip('\"\'')
        byname[n].append(dp)
dups={k:v for k,v in byname.items() if len(v)>1}
print('dup names:',len(dups))
"
```

## 與其他 Phase 的交叉

- **Phase 3 是唯一會動 canonical 樹的 Phase** → 其餘 Phase（Vault / memory /
  cron output / backup）全部不碰 canonical
- canonical 樹無 git → **刪除前必須先備份**（本次用 tarball）
- Agent repo 側不受影響：`~/Documents/Agent/skills/` 的目錄與 canonical 樹
  是**獨立的兩份內容**，canonical 刪重複不會讓 Agent repo 的 index 產生 dangling
  （實測：`index rows pointing to nonexistent path: 0`）
