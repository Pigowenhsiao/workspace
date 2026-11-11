# Skill Index — 2026-07-03 Session

## 口徑狀態
- Header Summary: **606** ✓（drift=1，Header 舊值 605）
- All 8 section headers: 606 actual rows total ✓
- Category Map: row 6 (Engineering) 92→91，與 section header actual 同步 ✓

## Drift 發現過程
1. `skill-index-check.py` 報告 `Actual rows: 0`（已知虛假信號，script regex 無效）
2. 獨立 Python count：606 actual data rows
3. Header 顯示 605 → drift=1
4. Section headers 全部對齊 actual
5. Category Map row 6（Engineering）= 92，但 section actual = 91 → 修復

## Sync Check DRIFT
- `MISSING in workspace`: `references/skill-index-2026-07-03-session.md` → 從 canonical restore
- `EXTRA in workspace` (4): `agents/`、`references/Readme.md`、`references/frontmatter-corruption-bug.md`、`scripts/Readme.md`
  → 全部 `git ls-files` 確認 origin/main tracked → **正當，保留（Pattern S/Z）**

## Pattern LL 初發現：Concurrent cron race
兩個 cron neat-freak 同時對同一 drift 修正：
- `7e96b27e`：本地修正口徑（Summary 605→606, Category Map row 6: 92→91）
- `795e3e97`：另一 job 同樣修正（競爭 commit）
- push rejection → `git commit --amend` 產生新 commit object（不是覆寫）
- `pull --no-rebase` → merge commit → push 成功

**正確處置徑**：push rejection → `git pull --no-rebase` → merge → push。**不要 `commit --amend`**，在已有 remote commit 的 branch 上 amend 產生新 commit object 而非覆寫。

**Guard（已加入 SKILL.md Step 0）**：
```bash
LATEST=$(git ls-remote --refs origin main | awk '{print $1}' | head -1)
PREV=$(git rev-parse HEAD)
if [ "$LATEST" != "$PREV" ]; then
  git log --oneline origin/main..HEAD | grep -qi "drift\|fix.*Skill_Index" && \
    echo "WARNING: Remote may have competing fix. Pull before continuing."
fi
```

## 39 Unlisted Paths（磁碟有但 index 未列）
- `nuwa-skill/examples/*/` 視角系列（12個）、`yao-geo-*` 系列（19個）、`yao-geoflow*`（5個）、`handoff`（1個）
- `guizang-social-card-skill`：npm bundle，非 canonical skill，不應列入
- `handoff/SKILL.md`：磁碟存在但 index 未列，下次 rebuild 應納入

## Commit
```
f971e74d feat: add guizang-social-card-skill
```
口徑修正 commit `5898a433` 已被 merge commit 吸收，workspace 乾淨，branch 與 origin 同步。
