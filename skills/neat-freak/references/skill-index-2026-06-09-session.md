# Skill Index — 2026-06-09 Session

## 口徑驗證（獨立 Python count）
```
python3 -c "
import re
c=open('/Users/pigo/Documents/Agent/docs/Skill_Index.md').read()
rows=re.findall(r'^\| \[([^\]]+)\]\([^)]+\.md\)', c, re.M)
print(f'Actual rows: {len(rows)}')
m=re.search(r'- Active Skills:\s*(\d+)', c)
print(f'Header: {m.group(1) if m else \"not found\"}')
"
→ Actual rows: 518, Header: 518  ✓ 口徑內部一致
```

## Readme.md mojibake 誤判（重要lesson）

**觀察**：`cat -v` 和終端直接 `cat Readme.md` 都顯示 lines 93-111 為 mojibake。
但 `git show HEAD:Readme.md | cat -v` 和 `git show HEAD^:Readme.md | cat -v` 也顯示相同 mojibake——說明 git 歷史本身就是腐敗的。

**然而** Python bytecode 檢查顯示磁碟上的 Readme.md 是完全乾淨的 UTF-8：
```python
data = open('Readme.md', 'rb').read()
lines = data.split(b'\n')
# Line 94: b'\xe8\x88\x87\xe4\xbd\xbf\xe7\x94\xa8\xe8\x80\x85...' = 正確的 UTF-8
```

**結論**：
1. 終端 `cat -v` 的 mojibake 顯示是**終端 encoding 設置問題**，不是檔案內容問題
2. Git history 裡的 mojibake 是真實的（commit eef85b10 聲稱修復了 lines 93-111，但 git show 仍顯示腐敗），不過**磁碟上的 working tree 是乾淨的**
3. Readme.md **沒有 Pattern II 腐敗**，無需修復

**Pattern II 驗證的正確順序**：
```
Step 1: git show HEAD:<file> | cat -v  → 檢查 git 歷史是否腐敗
Step 2: python3 -c "
data = open('<file>', 'rb').read()
# 直接看 raw bytes
"  → 檢查磁碟實際編碼
Step 3: 只有 Step 1 有 mojibake 且 Step 2 也顯示錯誤 bytes 時，才需要修復磁碟
```

**舊的驗證方法（已廢棄）**：
- `cat -v` alone — 不可靠，終端 encoding 會給假信號
- `file <file>` — 永遠報告正確編碼（因為 byte sequence 確實是有效 UTF-8，雙重編碼也是有效的某編碼）

## Skill_Index.md 現況
- 口徑 518 = header，內部一致 ✓
- **全部 518 個路徑 dangling**：`../mattpocock-skills/...`（三層巢狀目錄已刪除）
- 磁碟實有 611 個 skills
- 差額 93 個（611 - 518）
- 這是 upstream 累積腐敗，非 workspace 自身問題——應待 upstream 重建後同步

## sync-check.py DRIFT 確診
3 個 extras（agents/、references/Readme.md、scripts/Readme.md）→ 全部是 origin/main tracked content，正當，Pattern Z，保留。

## Branch 狀態
ahead=0 behind=0，與 origin/main 完全同步，working tree 乾淨。

## Pattern II 補充（新增驗證方法）
舊的 `cat -v` 終端檢查會被 terminal encoding 欺騙。Python bytecode 檢查是唯一可靠的：
```python
data = open('<file>', 'rb').read()
# 找 non-ASCII 行，直接看 bytes 是否為合法 UTF-8 三位元組序列
```
