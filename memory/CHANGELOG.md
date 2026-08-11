# CHANGELOG

2026-03-19: OpenClaw 更新與筆記整理。新增與整理如下：

- 整理並納入三層記憶模型的筆記與索引，方便跨裝置共享與檢索。
- 新增/補充「5 種 Agent Skill 設計模式」的骨架與摘要，方便落地實作。
- 加強安全審查與 approvals 機制的參考內容，並規劃自動化審核腳本的雛形。
- 推出骨架檔案模板，方便快速建立新技能（Tool Wrapper、Generator、Pipeline 等模式的骨架與範例）。
- 建立索引頁 memory/index.md 的骨架，方便快速導航現有筆記。
## 20260327-075531
- 一鍵更新執行
- 備份: /home/pigo/.openclaw/.openclaw/backups/openclaw-backup-20260327-075531.tar.gz
- 索引重建: /home/pigo/.openclaw/workspace/memory/index.md
- 學習筆記數量: 9
- 技能數量: 8

## 20260404-102542
- 一鍵更新執行
- 備份: /home/pigo/.openclaw/.openclaw/backups/openclaw-backup-20260404-102542.tar.gz
- 索引重建: /home/pigo/.openclaw/workspace/memory/index.md
- 學習筆記數量: 17
- 技能數量: 20

## 2026-08-02

### HF Daily Papers cron — 重複批次處理模式確立
- **現象**：週日（2026-08-02）觸發的 cron 從 arXiv cs.AI 取得的 10 筆論文與前一天（2026-08-01）完全相同（2607.28575 ~ 2607.28628，全部 published 2026-07-30）
- **根因**：arXiv 週末（週六/週日）無新提交，cron 仍按 schedule 觸發，arXiv API 返回「最新 10 篇」即為前一週最後的批次
- **決策**：跳過新 markdown 寫入，僅更新索引/日誌說明原因
- **理由**：避免 vault 重複污染（昨日筆記已涵蓋完整內容），保持 vault 整潔
- **下次預期**：2026-08-03（週一）01:02 UTC 應有新批次
- **長期建議**：可考慮將 cron schedule 改為週一至週六觸發，或在週日偵測到「與上次相同批次」時自動跳過
- 相關檔案：
  - `/home/pigo/.openclaw/workspace/memory/handoffs/hf-daily-papers_2026-08-02.md`
  - `/home/pigo/Documents/Pigo_Obsidian/00-Inbox/log.md`（已追加 2026-08-02 段落）
  - Git commit `8063d8ca`
