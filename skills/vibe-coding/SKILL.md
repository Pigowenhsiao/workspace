---
name: vibe-coding
description: Build a practical, end-to-end coding vibe app workflow. Provide guided, real-world coding performances that you can run, share, and deploy. Use when you want a hands-on, product-ready coding assistant that helps design, implement, and ship code with clear trade-offs and decisions.
---

# Vibe Coding

## 當前觸發時機
- 使用者需要一個「技術聯合創始人」角色，幫忙從想法到落地的全流程實作。
- 需要對話式指引，但又要落地成可部署的檔案與腳本。
- 想要可重用的技能模塊（config-migration、release-check、incident-triage 等等）來組裝新產品。

## 快速開始（Quick Start）

1) 啟動 Plan Mode
- 問題描述清晰，並以 Plan Mode 開始：探索需求、產出執行計畫、風險評估
- 產出 Plan Document，包含明確的版本範圍與里程碑

2) 產出可落地的實作內容
- 對應的腳本與模板（config-migration、release-check、incident-triage 等）放在 scripts/、references/、assets/
- 提供初步的 CLAUDE.md 風格契約（此技能會引用到全域 CLAUDE.md 的原則）

3) 驗證與回滾
- 每個變更有對應的 verifiers，確定成功/失敗
- 若失敗，提供清晰的回滾方案與修正路徑

4) 打包與分發
- 使用 packaging 流程，輸出 .skill 檔供分發

## 適用原則（Principles）

- Progressive Disclosure：先提供核心流程與關鍵步驟，細點放在 references/ 與 assets/ 之中，必要時才加載
- 最小可用單位：先建立最小穩定版本，逐步擴充
- 具體而清晰的輸入/輸出：每個步驟都要有輸入與輸出定義
- 安全與可控：避免自動化觸發不可控的外部行為，必要時使用 Hooks

## 內容結構（Files）

- SKILL.md（本檔）
- references/
  - architecture.md
  - workflows.md
  - patterns.md
- scripts/
  - init_skill.py（初始化模板，可選）
  - sample-run.sh（示例執行腳本）
- assets/
  - templates/
  - sample-project/

## Core Workflow（核心工作流）

1) Discovery & Plan
- 從用戶需求出發，提出針對 vibe-coding 的具體版本目標
- 明確需要何種資源與風險
- 產出 Plan Document：版本 1 的範圍、核心能力、里程碑

2) Design & Preparation
- 設計最小可行的模組：例如 config-migration、release-check、incident-triage 的基本骨架
- 準備必要的 assets 與 references（如 API 規範、資料結構、錯誤碼表）

3) Build & Test
- 自動化腳本與模板：建立 rotate_pdf 等常見工具的替代版本，若需要
- 測試計畫：單元測試、整合測試、視覺對比等

4) Verify & Validate
- Verifier：執行狀態與結果比對
- 回滾條件與回滾步驟的定義

5) Handoff & Deploy
- HANDOFF.md 結合 CLAUDE.md 的執行結果
- 打包並上線（若需要）

6) Iterate & Improve
- 依據使用反饋持續改進 SKILL.md 與 references 的內容

## Progressive Disclosure Patterns 例子

Pattern 1: High-level guide with references
- PDF Processing
- Quick start → Advanced features
- 參考文件放 references/

Pattern 2: Domain-specific organization
- bigquery-skill/
  - SKILL.md
  - references/
    - finance.md
    - sales.md
    - product.md
Pattern 3: Conditional details
- DOCX Processing
  - Creating documents
  - Editing documents
  - For tracked changes: REDLINING.md

## Skill Creation Process

Skill creation involves these steps:

1. Understand the skill with concrete examples
2. Plan reusable skill contents (scripts, references, assets)
3. Initialize the skill (init_skill.py)
4. Edit the skill (SKILL.md)
5. Package the skill (package_skill.py)
6. Iterate based on usage

### Skill Naming

- Use lowercase letters, digits, and hyphens only; normalize user-provided titles to hyphen-case (e.g., "Plan Mode" -> `plan-mode`).
- When generating names, generate a name under 64 characters (letters, digits, hyphens).
- Prefer short, verb-led phrases that describe the action.
- Namespace by tool when it improves clarity or triggering (e.g., `gh-address-comments`, `linear-address-issue`).
- Name the skill folder exactly after the skill name.

### Step 1: Understanding the Skill with Concrete Examples

Skip this step only when the skill's usage patterns are already clearly understood. It remains valuable even when working with an existing skill.

To create an effective skill, clearly understand concrete examples of how the skill will be used. This understanding can come from either direct user examples or generated examples that are validated with user feedback.

...
