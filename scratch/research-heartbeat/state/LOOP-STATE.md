# LOOP-STATE.md — 每日美股+台股投研 Loop 狀態檔

> **用途**：研究心跳 Loop 的記憶核心。每次 loop 跑完會更新這份檔案，讓下一次 loop 知道上次重點、市場線索、下次繼續追蹤主題。
>
> **格式版本**：v1.1（2026-07-08 加入 Completion Criteria 段）
>
> **更新時機**：每日 fetch + reviewer + writer 跑完後自動 append；手動可加註解

---

## Loop Completion Criteria（每次跑完必須全達成）

> 對齊 Anthropic 「Getting Started with Loops」（2026-06-24）：在跑 loop 之前談判「什麼叫完成」。
> 任一項 FAIL → 不能 commit loop-report，必須先解釋失敗原因並修正。

- [ ] **覆蓋率**：31/31 ticker 都有結果（status=ok 或 SUSPECT/ERROR 有明確說明）
- [ ] **帶寬合規**：所有 ticker 通過 `KNOWN_TICKER_BANDS` 檢查（reviewer Check 3b，0 SUSPECT）
- [ ] **Baseline 可比**：LITE / 2330 / NVDA / TSM / PLTR / ORCL / 2454 七大關注股都在 LOOP-STATE.md 的「上次報告摘要」段有 baseline
- [ ] **產出檔案**：`~/Downloads/Sotck/loop-report-YYYYMMDD-HHMMSS.md` + `google-finance-YYYYMMDD-HHMMSS.json` 都寫入
- [ ] **異常告警**：任何 SUSPECT/ERROR 都同步寫進 vault 的 `00-Inbox/YYYY-MM-DD_alert-*.md`
- [ ] **狀態更新**：本檔案的「當前市場線索」段被 append 3-5 條新觀察
- [ ] **Baseline 完備**：首次 fetch 的 ticker（無 baseline）需在「上次報告摘要」段加入 baseline
- [ ] **錯誤率上限**：單次 loop ERROR ≤ 2（transient timeout 屬 ERROR，超過即視為 fetch 環境問題）

**SOP**：跑 loop 之前 reviewer 必須先讀這段；不達標不 commit。詳見 vault `00-Inbox/2026-07-08_finance-parser-reviewer-fix.md` + `00-Inbox/2026-07-09_Anthropic-Getting-Started-With-Loops.md`。

---

## 用戶偏好（User Preferences）

- **時區**：Asia/Taipei (UTC+8)
- **報告語言**：繁體中文（技術術語保留英文，如 HBM、CoWoS、RSI）
- **投資風格**：偏多 AI / 半導體 / Lumentum 本業（光通訊雷射元件）
- **報告長度**：簡潔，總結 < 500 字；完整報價表可保留
- **觀察市場**：美股（NASDAQ / NYSE）+ 台股 TPE
- **關注個股**：LITE（自家公司）、TSM/NVDA/ORCL/PLTR（半導體+AI 鏈）、台積電 2330 + 聯發科 2454 + 聯電 2303 + 台達電 2308
- **訊息偏好**：Telegram announce，含 LITE / 2330 / SOX 重點

---

## 觀察中的重點板塊（Watched Sectors）

- **LITE** (Lumentum Holdings) — 自家產業，光通訊雷射 / 3D sensing / 資料中心
- **NVDA / TSM / ORCL / PLTR** — AI + 半導體鏈
- **TSM / 2330** — 全球晶圓代工龍頭
- **半導體指數 SOX** — 美國上市半導體指數（手動觀察，目前未自動抓）
- **HBM / CoWoS / 2nm 製程** — 結構性題材
- **AI 資料中心資本支出** — 大型 capex 驅動供應鏈
- **台股 AI 概念股**：台積電、聯發科、台達電、鴻海

---

## 可靠來源（Reliable Sources）

### 即時報價（active）
- ✅ **Google Finance via Playwright** — 已驗證 31 ticker 全綠（2026-07-07 05:12 UTC）
  - 路徑：`https://www.google.com/finance/quote/{ticker}:{exchange}`
  - 工具：`google-finance skill`（`~/.openclaw/workspace/skills/google-finance/`）
  - 不 rate-limit，polite delay 2s

### 已停用（deprecated）
- ❌ **Yahoo Finance API** — `query1.finance.yahoo.com` 自 2026-07-07 02:14 起被 pigoserver2 IP 整段 ban (HTTP 429)，預計 ban 解除時間未知
- ❌ **Yahoo Finance 網頁版** — 改用 Google Finance 取代

### 規劃中
- ⏳ **X / Twitter 監控** — 用 `x-note` skill（已安裝）+ fxtwitter API
- ⏳ **AI 新聞** — Agent repo `aihot` skill
- ⏳ **宏觀指標** — VIX / 美元指數 / 10Y yield（WS4c）

---

## 資料源注意事項（Data Source Notes）

- **Playwright profile**：`/home/pigo/.config/google-chrome/Profile 1`（GAIA = Hsiao Hsiao Pigo）
- **Google session 已登入**：無需 OAuth，每次直接 fetch
- **headless = True**：無 X server 環境使用 `--headless --no-sandbox --disable-gpu`
- **TPE vs TPEX**：台股上市公司用 `TPE`，上櫃用 `TPEX`（但 Google Finance 對 TPEX 支援差，會 unavailable）
- **HKG 港股**：用 4-5 位數字 ticker（如 `0700`, `9988`）
- **價格單位**：USD 美股、NTD/NT$ 台股、HKD 港股、Google Finance 用 `$` 符號標 NT dollars（需從 exchange 推斷）

---

## 上次報告摘要（Last Report Summary）

**2026-07-28 07:00 UTC（台北 15:00）**

- **總計**：31 ticker 全部 `status=ok`，0 ERROR；reviewer verdict FAIL (100, 7/8 PASS, C6 LOOP-STATE update 須人工補完)
- **七大關注股 baseline**：
- LITE：**$711.96 USD**（-14.60%，從 $833.64 高位回落 14.6%，跌破 $750/$700 雙關卡）
- TSM：**$399.09 USD**（-3.97%）
- 2330：**NT$2,280**（-2.98%）
- 2454：**NT$3,315**（-11.60%，從 NT$3,750 一週內回吐）
- NVDA：**$196.51 USD**（-5.87%，跌破 $200）
- PLTR：**$97.15 USD**（-4.47%，跌破 $100）
- ORCL：**$119.90 USD**（-0.12%，七股中唯一近平持平）
- **市場觀察**：七大關注股 6 檔收黑、AI/光通訊鏈全面退潮；ORCL 逆勢持平待觀察；高度警戒 LITE 個股走勢

**2026-07-24 07:00 UTC（台北 15:00）**

- **總計**：31 ticker 全部 `status=ok`，0 ERROR
- **七大關注股 baseline**：
- LITE：**$833.64 USD**（+0.47%，從 $765.55 續漲 8.9%）
- TSM：**$415.58 USD**（-1.34%）
- 2330：**NT$2,350**（-2.29%）
- 2454：**NT$3,750**（-3.23%，從 NT$3,340 反彈後回測）
- NVDA：**$208.76 USD**（-1.56%，從 $203.28 短線創高）
- PLTR：**$101.70 USD**（-2.67%，跌破 $102）
- ORCL：**$120.04 USD**（-4.61%）
- **市場觀察**：TSLA -4.34% 最弱；台股 AI 鏈普遍修正

**2026-07-21 07:00 UTC（台北 15:00）**

- LITE：**$765.55 USD**（+4.47%，突破前次 $722 高位 +6.0%）
- TSM：**$402.30 USD**
- 2330：**NT$2,410**
- 2454：**NT$3,340**
- NVDA：**$203.28 USD**
- PLTR：**$102.50 USD**
- ORCL：**$121.38 USD**

**2026-07-07 05:12 UTC（台北 13:12，初版基準）**

- **總計**：31 ticker 全部 `status=ok`，美股 19（新增 ORCL/PLTR/TSM/LITE）+ 台股 12（TPE）
- LITE（公司股）：**$722.05 USD**（高位，待驗證持續性）
- TSM（台積電 ADR）：**$451.79 USD**
- 2330 台積電：**NT$2,450**
- 2454 聯發科：**NT$3,970**
- NVDA：**$195.55**
- PLTR：**$106.20**
- ORCL：**$143.76**

---

## 當前市場線索（Market Context）

> 每日 loop 跑完會在這裡 append 3-5 條觀察；writer 生成報告時會引用這段

- **[2026-07-28 07:00]** **全面下修訊號**：七大關注股 6 檔收黑、僅 ORCL 持平——LITE -14.60% 最劇、2454 -11.60%、NVDA -5.87%、PLTR -4.47%、TSM -3.97%、2330 -2.98%；LITE 從 07-24 高位 $833.64 一週內回吐 14.6%，需釐清是否為個股因素（Lumentum 自身事件？）或整體 AI/光通訊鏈修正
- **[2026-07-28 07:00]** **LITE $711.96 跌破 $750 與 $700 雙重整數關卡**，從 07-21 $765.55 → 07-24 $833.64 → 今日 $711.96，區間高點 $833 → 區間低點 $712 振幅 17%，波動率急遽放大——高度警戒自家公司股價
- **[2026-07-28 07:00]** **2454 聯發科 NT$3,315（-11.60%）** 從 07-24 NT$3,750 一週內回吐 -11.6%，與 07-21 NT$3,340 已逼近；HBM/CoWoS 題材是否退燒待驗證
- **[2026-07-28 07:00]** **2330 NT$2,280 / TSM ADR $399.09 同步走弱**（-2.98% / -3.97%），ADR/現股裂口需追蹤；NVDA $196.51 已跌破 $200 心理關卡，AI 鏈全面退潮
- **[2026-07-28 07:00]** **PLTR $97.15 跌破 $100 整數關卡**，從 07-24 $101.70 → 今日 $97.15（-4.47%），與 NVDA / TSM 同向；ORCL $119.90 近乎持平為七大關注股唯一紅盤，逆勢特性待觀察

- **[2026-07-24 07:00]** **LITE 突破 $833.64（+0.47%）**，延續 07-21 $765.55 強勢再漲 8.9%，距 $850 僅 2.0%——追蹤 $800 整數關卡站穩
- **[2026-07-24 07:00]** **2330 台積電 NT$2,350（-2.29%）**，從 07-21 NT$2,410 微回檔 -2.5%；TSM ADR $415.58（-1.34%）同步走弱
- **[2026-07-24 07:00]** **NVDA $208.76（-1.56%）** 從 07-21 $203.28 短線回檔後續創高，AI 鏈仍有韌性
- **[2026-07-24 07:00]** **PLTR $101.70（-2.67%）跌破 $102** 關卡，與 2454 -3.23% / 2308 -5.05% / 2303 -7.58%／1303 -9.9% 同向，台股 AI 鏈普遍修正
- **[2026-07-24 07:00]** **TSLA $319.69（-14.52，-4.34%）** 為今日美股最弱勢；2454 NT$3,750 從 07-21 NT$3,340 反彈 +12.3% 後再回測

- **[2026-07-21 07:00]** **LITE 突破 $765.55（+4.47%）**，創觀察期新高，距 $800 整數關卡約 +4.5%——密切追蹤是否站穩或回測 $750
- **[2026-07-21 07:00]** **ORCL 大幅回檔 -3.98% 至 $121.38**，從 07-07 $143.76 高位累計修正 -15.6%，與 MSFT +2.15% 走勢分歧——需追蹤是否為單日雜訊或趨勢反轉
- **[2026-07-21 07:00]** **2454 聯發科單日 +9.88% 至 NT$3,340**，AI/HBM 題材發酵？與 2330 +3.88% 同向但強度更高
- **[2026-07-21 07:00]** **TSM ADR $402.30 vs 2330 NT$2,410**，ADR/現股同步反彈但 ADR 仍低於 07-07 $451.79，需驗證折溢價關係
- **[2026-07-21 07:00]** **NVDA $203.28（+0.23%）** 從 07-07 $195.55 反彈 +4.0%，盤整轉強訊號待確認
- **[2026-07-21 07:00]** **PLTR $102.50（+4.20%）** 從 07-07 $106.20 修正後反彈，$100 整數關卡守住

- **[2026-07-07 05:12]** LITE 報價 $722.05，創近期高位，需觀察是否突破或回落
- **[2026-07-07 05:12]** 2330 台積電 NT$2,450（微跌 0.20%），TSM ADR $451.79（同向）
- **[2026-07-07 05:12]** NVDA $195.55（前次 v1 demo 也是 $195.55，可能已反彈後盤整）
- **[2026-07-07 05:12]** PLTR $106.20（首次觀察價位，未建立基準）
- **[2026-07-07 05:12]** ORCL $143.76（首次觀察價位，未建立基準）

---
- **[2026-07-07 07:07 UTC]** Loop run OK, fetch=31/31, verdict=PASS(100)
- **[2026-07-08 02:52 UTC]** Loop run OK, fetch=31/31, verdict=PASS(100)
- **[2026-07-08 07:07 UTC]** Loop run OK, fetch=31/31, verdict=PASS(100)

## 下次繼續追蹤的主題（Next Watch Items）

> 每次 loop 結束時，reviewer 會建議下次要看什麼，writer 寫進下一份報告

- [ ] **LITE**：$722 是否持續？或突破 $730？或回測 $700？
- [ ] **NVDA**：$195 是盤整還是反彈起點？
- [ ] **SOX 半導體指數**：目前沒在 watchlist，要不要加入？
- [ ] **PLTR**：$106 是底部還是短暫反彈？
- [ ] **ORCL**：$143 是高位還是中段？
- [ ] **台股聯電 2303**：NT$23.1 低檔，觀察是否突破 NT$25 上沿，或跌破 NT$22 下緣
- [ ] **TSM vs 2330**：ADR 折溢價是否正常？

---

## 變更日誌（Changelog）

- **2026-07-28 07:08 UTC** — Loop 收尾修補（自動駕駛補完）：reviewer C6 FAIL 因今日「當前市場線索」段未含今天日期；補上 07-28 baseline 段（7 大關注股）+ 5 條當前線索（全面下修、LITE 波動急遽、2454 回吐、2330/TSM/NVDA 同步走弱、PLTR 破整數）；verdict FAIL(100) 經手動補完後重跑 review gate
- **2026-07-21 08:46 UTC** — Loop 收尾修補（Pigo 指示）：補上 07-21 07:00 baseline 段（7 大關注股）+ 當前市場線索 6 條新觀察；研究心跳 cron 07:04 抓完資料但未跑收尾，本手動補完讓 loop_write_allowed 重新評估
- **2026-07-07 05:12 UTC** — 初版建立（WS1 完成），從 google-finance skill v2 demo 報告初始化
- **2026-07-08 23:45 UTC** — v1.1：加入「Loop Completion Criteria」段（8 條 checkbox），對齊 Anthropic 「Getting Started with Loops」（2026-06-24）的「談判完成條件」精神。詳見 vault `00-Inbox/2026-07-09_Anthropic-Getting-Started-With-Loops.md`。下一步（Step 4）：把 criteria 從文件變成 fetch_batch.py / review_report.py 的程式化 gate