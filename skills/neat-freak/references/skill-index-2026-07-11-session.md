# 2026-07-11 session — verify-vault-ingest.py FAIL count interpretation

## Pattern QQ（2026-07-11 初發現）：verify-vault-ingest.py 總結行 FAIL count 解讀陷阱

**觀察**：2026-07-11 cron job 的 `verify-vault-ingest.py` 輸出：
```
Checked: 4507  OK: 29  WARN: 935  FAIL: 3543
```

乍看 3543 個 FAIL，但實際非豁免 FAIL = **0**。全部 3543 個 FAIL 都來自 `00-Inbox/`（verifier 會對 inbox 報告 FAIL，但同時將其標記為 exempt，因此不應計入 action threshold）。

**為什麼舊檢查找不到**：
- verifier 對 `00-Inbox/` 的 intake stub 報 FAIL，這是預期行為（intentional triage workflow）
- 但 summary 行 `FAIL: 3543` 沒有區分 exempt / non-exempt
- 沒有先做 `grep -v "00-Inbox/"` 就直接解讀 FAIL count 會嚴重高估實際工作量

**正確的 pre-check 判斷徑**：
```bash
# Step 1：取 summary 行（第一行）
python3 12-Meta/scripts/verify-vault-ingest.py 2>&1 | head -1
# 輸出：Checked: 4507  OK: 29  WARN: 935  FAIL: 3543

# Step 2：計算非豁免 FAIL（排除 00-Inbox/）
python3 12-Meta/scripts/verify-vault-ingest.py 2>&1 | grep "^\[FAIL\]" | grep -v "00-Inbox/" | wc -l
# 輸出：0 → vault 實際乾淨，neat-freak 跳過

# Step 3：若 > 0，繼續執行 neat-freak 目標導向工作流程
```

**與 Pattern PP 的關係**：
- Pattern PP（2026-07-09）確定了 00-Inbox intake stub exemption gap 的**政策根因**
- Pattern QQ 解決的是：**在執行 workflow 前，如何正確解讀 FAIL count**，避免把 exempt FAIL 當成需要修復的工作量
- Pattern PP 的 plateau signal（FAIL count 在多個 turn 不下降）是因為不斷對同一類 exempt 檔案 retry；Pattern QQ 確認後，plateau 不再是「fix 不夠」，而是「政策 gap 已知」

**口徑記錄**：
- 2026-07-11 FAIL count: 3543（全部 00-Inbox/ exempt）
- 2026-07-10 FAIL count: 3524（已知 plateau，3 systemic categories）
- 非豁免 FAIL: 0（00-Inbox/ 外無 FAIL）
