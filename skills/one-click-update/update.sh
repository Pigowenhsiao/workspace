#!/usr/bin/env bash
set -euo pipefail

# ========================================
# one-click-update.sh
# 一鍵更新 OpenClaw 知識庫、筆記、索引與技能
# ========================================

ROOT_DIR="${ROOT_DIR:-$HOME/.openclaw/workspace}"
BACKUP_DIR="${ROOT_DIR%/workspace}/.openclaw/backups"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
MEMORY_DIR="$ROOT_DIR/memory"
LEARNING_DIR="$MEMORY_DIR/learning"
SKILLS_DIR="$ROOT_DIR/skills"
INDEX_FILE="$MEMORY_DIR/index.md"
AGENTS_FILE="$ROOT_DIR/AGENTS.md"
MEMORY_FILE="$ROOT_DIR/MEMORY.md"
CHANGELOG="$MEMORY_DIR/CHANGELOG.md"

echo "============================================"
echo "  OpenClaw 一鍵更新 ($TIMESTAMP)"
echo "============================================"
echo "ROOT_DIR: $ROOT_DIR"
echo ""

# ── Step 1: 備份 ──
echo "▶ Step 1/5: 備份現有設定與筆記..."
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/openclaw-backup-${TIMESTAMP}.tar.gz"
tar -czf "$BACKUP_FILE" \
  -C "$ROOT_DIR" \
  AGENTS.md \
  MEMORY.md \
  IDENTITY.md \
  USER.md \
  SOUL.md \
  memory/ \
  skills/ \
  2>/dev/null || true
echo "  備份完成: $BACKUP_FILE"

# ── Step 2: 確保目錄存在 ──
echo "▶ Step 2/5: 確認目錄結構..."
mkdir -p "$LEARNING_DIR"
mkdir -p "$SKILLS_DIR/one-click-update"
echo "  目錄結構 OK"

# ── Step 3: 更新 memory/index.md ──
echo "▶ Step 3/5: 更新索引 (memory/index.md)..."

# 掃描 learning/ 下所有 .md 檔案，自動產生索引
cat > "$INDEX_FILE" << 'HEADER'
---
title: memory index
description: 全域知識筆記快速索引與導航（自動產生）
---
HEADER

for f in "$LEARNING_DIR"/*.md; do
  [ -f "$f" ] || continue
  BASENAME=$(basename "$f")
  # 取第一行當標題
  TITLE=$(head -1 "$f" | sed 's/^#\+ //')
  echo "- memory/learning/$BASENAME" >> "$INDEX_FILE"
  echo "  - title: $TITLE" >> "$INDEX_FILE"
done
echo "  索引已更新: $INDEX_FILE"

# ── Step 4: 更新 CHANGELOG ──
echo "▶ Step 4/5: 寫入 CHANGELOG..."
{
  echo ""
  echo "## $TIMESTAMP"
  echo "- 一鍵更新執行"
  echo "- 備份: $BACKUP_FILE"
  echo "- 索引重建: $INDEX_FILE"
  echo "- 學習筆記數量: $(ls "$LEARNING_DIR"/*.md 2>/dev/null | wc -l)"
  echo "- 技能數量: $(ls -d "$SKILLS_DIR"/*/ 2>/dev/null | wc -l)"
} >> "$CHANGELOG"
echo "  CHANGELOG 已更新: $CHANGELOG"

# ── Step 5: 驗證 ──
echo "▶ Step 5/5: 驗證..."
echo ""
echo "  === 學習筆記 ==="
ls -1 "$LEARNING_DIR"/*.md 2>/dev/null | while read f; do
  echo "    ✓ $(basename "$f")"
done

echo ""
echo "  === 已安裝技能 ==="
ls -d "$SKILLS_DIR"/*/ 2>/dev/null | while read d; do
  SKILL_NAME=$(basename "$d")
  if [ -f "$d/SKILL.md" ]; then
    echo "    ✓ $SKILL_NAME (SKILL.md found)"
  else
    echo "    ⚠ $SKILL_NAME (no SKILL.md)"
  fi
done

echo ""
echo "============================================"
echo "  更新完成！"
echo "============================================"
echo ""
echo "下一步建議："
echo "  1. 重啟 OpenClaw gateway 以載入更新"
echo "  2. 驗證索引: cat $INDEX_FILE"
echo "  3. 檢查備份: ls -la $BACKUP_DIR/"
echo ""
