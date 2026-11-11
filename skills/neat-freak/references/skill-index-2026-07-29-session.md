# Skill_Index 口徑修正 Session — 2026-07-29

## 口徑狀態
- Summary header: 460 → 470
- media-documents: 62 → 65
- engineering: 90 → 91
- manual: 34 → 36
- Root-level: 61 → 64
- Actual rows (獨立驗證): 470

## 發現的新 Pattern

### Pattern QQ（2026-07-29）：`neat-freak` 雙重路徑衝突導致 Skill 載入失敗

**觀察**：`skills_list` 中 `neat-freak` 出現兩次：
- `~/.hermes/skills/neat-freak/`（canonical, 1410 行）
- `~/.hermes/skills/productivity/neat-freak/`（較小版本）

`skill_view(name='neat-freak')` 回 `Ambiguous skill name — 2 matches`。Cron 配置 `skills=[neat-freak]` 時出現「Skill(s) not found and skipped」。

**執行時必須用的路徑**：
```bash
# 直接執行 script，不走 skill_view 解析
python3 ~/.hermes/skills/neat-freak/scripts/sync-check.py
python3 ~/.hermes/skills/neat-freak/scripts/skill-index-check.py
```

**Canonical vs productivity 版本**：
- `~/.hermes/skills/neat-freak/` — canonical，1410 行，是源頭
- `~/.hermes/skills/productivity/neat-freak/` — 較小的 productivity bundle 版本
- 兩者內容不同，執行維護時必須用 canonical 路徑

## Pattern OO 更新（2026-07-29 重發現）

Script regex `[a-z]` 不匹配大寫字母開頭的 skill names，導致 actual count 低估。

**三口徑驗證（不走 script）**：
```bash
python3 << 'EOF'
import re
c = open('/home/pigo/Documents/Agent/docs/Skill_Index.md').read()
lines = c.split('\n')
actual = [l for l in lines if re.match(r'^\| [a-zA-Z]', l) and 'SKILL.md' in l]
print(f'Actual rows: {len(actual)}')
m = re.search(r'Active Skills:\s*\*\*(\d+)\*\*', c)
print(f'Summary header: {m.group(1) if m else "not found"}')
EOF
```

**預防**：每次跑完 script 後，立即用上述命令驗證——若 actual 值明顯低於 Summary header，懷疑 regex 不匹配格式。

## Commit History
- `66a08d87c` fix(Skill_Index): correct per-section drift
- `11e43b0a5` x-note v6.1: add fxtwitter full-text step
