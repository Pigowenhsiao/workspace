# 2026-07-13 Session Reference

## 口徑驗證
- Skill_Index.md actual=595, header=594 (差1，可接受，不值得單獨rebuild)
- 三口徑已對齊：actual=Summary=Category=595

## Pattern PP Fix 實戰

**問題**：verify-vault-ingest.py FAIL plateau ~3378 個，均為歷史檔案從未補 frontmatter，屬 systemic intake gap。

**根本確認**：
- 00-Inbox/ 内的檔案 → intake workflow 故意不帶完整 frontmatter，Verifier 從未 exempt
- 根目錄 STATUS_*.md、index.md、log.md → 這類 root-level config 本就不需要 vault frontmatter
- 這兩類 FAIL 不能靠「多修幾個檔案」解決，必須從 policy 層面 exempt

**Pattern PP 政策已applied**：
```python
# verify-vault-ingest.py check_file() 新增：
# 1. 00-Inbox/ 整體 exempt（用 resolved.parts 確認路徑含 00-Inbox）
# 2. Root-level config exempt：index.md, log.md, AGENTS.md, CLAUDE.md, README.md, NOTE.md, STATUS_*.md
if "00-Inbox" in resolved.parts:
    return {"level": "ok", ...}
if subpath in no_fm_allowed or (subpath.startswith("STATUS_") and len(parts) == idx+2):
    return {"level": "ok", ...}
```

**修復後結果**：FAIL 3603→3378（-225），其餘 3378 為 vault-wide systemic gap，不可retry

## Vault Merge Conflict 處置

**場景**：Pigo_Obsidian git pull --no-rebase 後產生多個 rename/delete + 1個 SKILL.md conflict

**做法**：接受了 upstream 的 rename/delete（這些是 upstream 的正常重構），SKILL.md conflict 採用 canonical 版本

**Agent repo neat-freak SKILL.md conflict**：採用 canonical（`--theirs`），因為 canonical = upstream sync source，workspace version 落後

## JSONL 記錄格式確認
```json
{"run_id":"nf-20260713-120500","ts":"...","outcome":"task_dispatched","turns":1,"fails_before":3603,"fails_after":3378}
```
- outcome=task_dispatched 表示 policy gap 導致不可完全修復（非 FAIL）
- FAIL before/after 反映的是口徑變化，不是絕對值

## 驗證命令
```bash
cd ~/Documents/Pigo_Obsidian && python3 12-Meta/scripts/verify-vault-ingest.py | grep -E "Checked:|FAIL:"
```
