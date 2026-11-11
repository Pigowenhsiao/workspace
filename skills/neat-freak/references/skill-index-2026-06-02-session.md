# Skill_Index Session — 2026-06-02

## 口徑確診

| 指標 | 值 | 備註 |
|------|-----|------|
| Skill_Index.md header | 486 | drift=0（對得上自己的 rows） |
| 磁碟實際 skills | 573 | find 結果（不含 vendor/archive/.system/.agents/shared-skills） |
| 口徑差距 | 87 個 | Pattern EE，仍未修復 |
| script 口徑報告 | 0 | `Actual rows: 0` — 虛假信號，已知 bug |

口徑落後仍在累積（2026-05-31=114，落後到 2026-06-02=87，因為期間刪除了一些壞路徑的 row）。

## sync-check.py DRIFT 確診為正當

sync-check.py 報告三項 EXTRA：
- `EXTRA in workspace: agents/`
- `EXTRA in workspace: references/Readme.md`
- `EXTRA in workspace: scripts/Readme.md`

全部確認為 origin/main 正當 tracked content，非污染：
```bash
git -C ~/Documents/Agent ls-files -- "skills/neat-freak/agents/*"
# → openai.yaml, Readme.md（origin/main 有追蹤）
git -C ~/Documents/Agent ls-files -- "skills/neat-freak/references/Readme.md"
# → 有輸出，origin/main tracked
git -C ~/Documents/Agent ls-files -- "skills/neat-freak/scripts/Readme.md"
# → 有輸出，origin/main tracked
```

Pattern S + Pattern Z 確認：當 EXTRA 恰好是 `agents/` + `references/Readme.md` + `scripts/Readme.md` 這三者組合時，幾乎可以確定是 origin/main 在 canonical 未定義的時間點之後擴充的內容，**不要刪除**。

## Pi-AGENTS.md 路徑遷移（本次核心修改）

### 發現

`docs/Pi-AGENTS.md` 含四處 Windows 特定路徑，使用者已遷移到 macOS 階段，Agent 工作區在 `~/Documents/Agent`。這些路徑已過期。

### 修改內容

| 位置 | 舊值（Windows） | 新值（macOS） |
|------|----------------|--------------|
| 路徑別名（第 294 行） | `E:\python_Code\Agent` | `~/Documents/Agent` |
| 技能探索（第 315 行） | `E:/python_Code/Agent` | `~/Documents/Agent` |
| 外部 Repo Clone 政策（第 468 行） | `E:\AI Training\` | `~/Downloads/` |
| 禁止直接克隆至 | `E:\python_Code\Agent` 等三個 Windows 路徑 | `~/Documents/Agent`、`~/Documents/Pigo_Obsidian`、`~/.codex/skills` |
| Repo 晋升描述 | `E:\AI Training\` | 「下載區」 |

### 驗證

修改後 grep 無殘留 Windows 路徑（僅兩處條件式提示「Windows PowerShell」和「uv install.ps1」保留，屬於技術參考非路徑）：
```bash
grep -n "E:\\\\\|E:/\|C:\\\\" ~/Documents/Agent/docs/Pi-AGENTS.md
# → 328, 413（條件式技術參考，非路徑）
```

已 commit：`f8c2592f fix: sync Windows paths to macOS paths in Pi-AGENTS.md`

## 兩層 AGENTS.md 的獨立性發現

### 觀察

- `~/Documents/Agent/AGENTS.md`（根目錄）：路徑已正確（`~/Documents/Pigo_Obsidian`）
- `~/Documents/Agent/AGENT/AGENTS.md`（subdirectory）：路徑已正確（`~/Documents/Pigo_Obsidian`）
- `~/Documents/Agent/docs/Pi-AGENTS.md`：路徑過期（`E:\...`），需要遷移

### 原則

`docs/Pi-AGENTS.md` 是 Pi 的全域指令文件，與根目錄 `AGENTS.md` 是**獨立的兩層**。兩者：
- 各自有不同受眾（Pi-AGENTS 是給 Pi 的全域疊加，AGENTS.md 是給 Agent 架構的本地參照）
- 各自維護自己的路徑事實
- **不能假設修改了一層另一層也會跟著改**

每次 neat-freak 對路徑進行 cross-document 檢查時，必須對每層 AGENTS.md 獨立驗證，不能只讀根目錄版本就以為 subdirectory 也正確。

## AGENT/AGENTS.md 無需修改

`AGENT/AGENTS.md` 的路徑別名章節（第 100-104 行）已正確：
- Vault root path: `~/Documents/Pigo_Obsidian` ✓
- 00-Inbox path: `~/Documents/Pigo_Obsidian/00-Inbox/` ✓

無需同步。

## 未處理

1. **Skill_Index.md 口徑落後 87 個**（486 vs 573）：Path format 漂移導致所有路徑 dangling。需從磁碟重建而非逐筆修補。Pattern EE 仍活躍，下次專門安排。
2. **Pi-AGENTS.md 的 openspec/ 專案參照**（章節 11）：條件式觸發（"當工作在含 `openspec/` 目錄的專案內"），非陳屍，保留不刪。
3. **openspec/ 目錄不存在**於 workspace：`ls ~/Documents/Agent/openspec/` → No such file or directory，但 Pi-AGENTS.md 引用它是條件式，不算錯誤。

## Pattern HH（2026-06-02 新增）：Pi-AGENTS.md 與根 AGENTS.md 的 path drift

**觀察**：`docs/Pi-AGENTS.md`（Pi 全域指令）含過期 Windows 路徑，而根目錄 `AGENTS.md` 已為正確 macOS 路徑。兩層來自同一 repo 但各自維護，之間沒有自動同步。

**為什麼舊檢查抓不到**：
- Step 1 的 `find -name "*.md"` 只列舉檔案，不交叉比對同類文件（如所有 AGENTS.md）之間的路徑事實一致性
- 過去的路徑檢查主要針對記憶和單一文件，未擴展到同層 multiple copies

**修復**：在 Step 1 末段新增 AGENTS.md 規範一致性交叉檢查（已見 Pattern FF），但需注意：
- `docs/Pi-AGENTS.md` 是 Pi 的全域疊加，**不是**根 AGENTS.md 的 copy
- 兩者受眾不同，各自維護各自的路徑事實
- 發現 drift 時，檢查磁碟實際路徑，以正確的為準，各自更新

**預防**：每次平台遷移後（Windows→macOS、換 vault 路徑），對所有 AGENTS.md 層級檔案做路徑 cross-check，不要只檢查根目錄。