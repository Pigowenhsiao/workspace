# Memory Sync Protocol

## 同步層級（2026-05-28 確認）

**事實來源**：`~/.hermes/memory/` — 所有記憶檔以 Hermes 為唯一事實來源。
**同步目標**：`~/Documents/Agent/memory/` — Codex 的鏡像副本。

同步方向：Hermes → Agent。永遠不以 Agent 端的內容為準。

## 同步驗證（標準做法）

```bash
diff ~/.hermes/memory/P0-core.md ~/Documents/Agent/memory/P0-core.md && echo "SYNC-OK" || echo "SYNC-DIFF"
diff ~/.hermes/memory/P1-90days.md ~/Documents/Agent/memory/P1-90days.md && echo "SYNC-OK" || echo "SYNC-DIFF"
diff ~/.hermes/memory/P2-30days.md ~/Documents/Agent/memory/P2-30days.md && echo "SYNC-OK" || echo "SYNC-DIFF"
```

**重要**：`diff` 報告「檔案相同」不等於「完全同步」——需確認無 content diff。

## Trailing Newline 陷阱（2026-05-28 發現）

**問題**：`diff` 報告 files identical 但比對失敗：
```
20c20
< *本檔案每 30 天檢視一次，過期項目自動移除或歸檔*
\ 檔案末沒有 newline 字元
---
> *本檔案每 30 天檢視一次，過期項目自動移除或歸檔*
```

**原因**：一個檔案結尾有 `\n`，另一個沒有。`diff` 報告為「相同內容」但 `&&` 判斷失敗。

**修復**：
```bash
# 兩種做法（二選一，保持一致即可）

# 做法 A：strip trailing newline（推薦，若 Hermes 原始檔無 trailing newline）
head -c -1 ~/Documents/Agent/memory/P2-30days.md > /tmp/p2_temp && mv /tmp/p2_temp ~/Documents/Agent/memory/P2-30days.md

# 做法 B：add trailing newline（若 Hermes 原始檔有 trailing newline）
printf '%s\n' "$(cat ~/Documents/Agent/memory/P2-30days.md)" > ~/Documents/Agent/memory/P2-30days.md

# 驗證
diff ~/.hermes/memory/P2-30days.md ~/Documents/Agent/memory/P2-30days.md && echo "SYNC-OK"
```

**預防**：同步完成後立即驗證，發現 trailing newline 差異當場修復。

## 同步後 Commit

記憶同步完成後，Agent repo 需 commit 同步結果：
```bash
cd ~/Documents/Agent && git add memory/ && git commit -m "chore(memory): sync P0/P1/P2 from Hermes source of truth"
```

## 觸發時機

- 任一次 `~/.hermes/memory/` 內檔案被修改之後
- 每次 neat-freak 執行時（標準檢查流程的一環）

## 已知同步項目（2026-05-28）

| 檔案 | 同步內容 |
|------|----------|
| P0-core.md | Vault 路徑（`~/Documents/Pigo_Obsidian/`）、Inbox 路徑 |
| P1-90days.md | himalaya 版本（v1.2.0） |
| P2-30days.md | 2026-05-25 清理區段（Hindsight 模組損壞已移除）、其他過期系統事件 |