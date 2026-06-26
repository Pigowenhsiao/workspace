# Cron Handover Template (v2 — 2026-06-26)

> **變更說明**：v1 凍結於 2026-06-18，沿用 8 天。v2 採表格化、加入沿用異常區塊、RTK 效益欄位。
> **MEMORY 引用原則**：MEMORY.md = 永久事實（source of truth）；handover = 本週期 delta。
> **本範本不重複 MEMORY 已記的事實**——只列本週期有動的、新增的、待裁決的。

---

## Goal
[任務目標描述]

## Current State

| 類別 | 來源 | 狀態 | 數量 |
|------|------|------|------|
| 科技 | [RSS URL] | ✅/❌ | N |
| 財經 | [RSS URL] | ✅/❌ | N |
| 國際 | [RSS URL] | ✅/❌ | N |
| 軍事 | [RSS URL] | ✅/❌ | N |

## Source Chain

### 科技
```
curl [RSS URL]
→ [結果：成功/失敗/被封鎖]
```

### 財經
```
curl [RSS URL]
→ [結果]
```

### 國際
```
curl [RSS URL]
→ [結果]
```

### 軍事
```
curl [RSS URL]
→ [結果]
```

## 沿用異常（從 MEMORY 沿用，本週期無新進度）

> 完整清單見 `~/.openclaw/workspace/MEMORY.md`「沿用異常」索引。
> 本表只列**本週期觸碰過、或即將到期的**。

| ID | 問題 | 現況（YYYY-MM-DD 驗證） | 風險 | 處置 | Owner | 截止 |
|----|------|------------------------|------|------|-------|------|
| OBS-NNN | [問題] | [現況] | [風險] | [處置] | [Owner] | [截止] |

## Decision 待裁決（本週期新增）

| ID | Decision | 選項 | 建議 | 來源 |
|----|----------|------|------|------|
| DEC-NNN | [主題] | (a) ... / (b) ... / (c) ... | (x) | OBS-NNN |

## 本週期已關閉
- [關閉的決策、完成的異常，附 commit / 動作連結]

## Recommended Default
[拿不準時的預設行為]

## Risks / Do Not Do
- ❌ 禁止發布未經翻譯的新聞
- ❌ 禁止直接推送未驗證的 commit
- ❌ 不得對外發送未確認的消息來源
- ❌ 不得假設 OpenClaw session 與 Hermes session 互通

## RTK 效益（若 neat-freak / 整理任務才填）
- cmds：N
- tokens in / out：N / N
- saved：N (X%)
- 平均 cmd 時間：N s

## Runtime 標記（必填）
- [ ] 此 handover 從 **OpenClaw cron** 觸發
- [ ] 此 handover 從 **Hermes session** 觸發
- [ ] 此 handover 從 **手動對話** 觸發

> 06-22 已記：OpenClaw session 跟 Hermes session 是兩個獨立 runtime，**不會互相看到訊息**。
> 寫出來給未來的自己看，避免下次又誤判。

## Next Action
[下一步要做什麼]
