---
name: one-click-update
description: 一鍵更新 OpenClaw 知識庫與技能庫的打包與部署流程骨架
metadata:
  pattern: generator
  output-format: markdown
---

你是一個方便的一鍵更新 Skill。此 Skill 負責自動化產生並部署以下內容到工作區的更新：
- 新增/更新筆記與骨架
- 更新 memory/index.md、AGENTS.md 的導航連結
- 產出自動化測試與重新載入指令

輸出簽名與結構：
- 輸入：{ action, payload }
- 輸出：{ ok, data?, error? }

常見動作
- initUpdatePack: 準備更新包，寫入 Skeleton 與草案檔案
- applyUpdate: 將更新套用到 workspaces（寫入檔案、更新索引）
- testUpdate: 產出測試指令與結果

範例觸發詞（觸發器可自訂）
- update all
- update workspace

注意事項
- 請確保版本可回滾機制存在，並有備份
- 更新前後要有日誌與審核點
