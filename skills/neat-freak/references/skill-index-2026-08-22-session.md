# neat-freak session — 2026-08-22

## 口徑狀態
- Skill_Index.md: **已刪除**（upstream `d3dfa00a5` 重構）
- upstream 口徑: N/A（無集中索引）
- 磁碟 SKILL.md: 5 個（`skills/` 根目錄），其餘在子目錄

## Branch 衝突處置
- local commit `bc3fbe018`（P0-core.md sync）被放棄
- 原因：upstream 完成了 440 revived skills 的大規模重構，local 落後 origin/main 2 commits
- Workspace reset 到 `origin/main`（`760a7aaa1`）

## 架構變更摘要（upstream）
- `docs/Skill_Index.md` 已刪除
- `skills/` 目錄全面重組：`skills/*_revived/` 系列（新命名）
- `skills/AGENTS.md` 為 skills CLI 框架文件（非 Agent 工作區設定）
- 新增：`.github/workflows/`、`.husky/`、`.prettierrc` 等標準 project files

## 記憶同步
- `~/.hermes/memory/P0-core.md`：更新「工作流程」第 2 步，從 `docs/Skill_Index.md` 改為 `skills/ 目錄（已重構，無集中索引）`
- `~/Documents/Agent/memory/`：目錄不存在，無需同步

## 未處理
- `tmp_arxiv_papers/` 未追蹤（含 PDF，應加進 .gitignore 或移除）
- 多個未追蹤目錄（`Horizon/`、`book-reader/`、`finance-reports/`、`ClawTeam-OpenClaw/` 等）— 需確認是否應進 git
- `.system/skill-creator/scripts/__pycache__/` — 應清理
- `skills/x-note/__pycache__/` — 應清理
