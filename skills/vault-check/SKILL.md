---
name: vault-check
description: Use when the user wants a low-frequency full-vault health check for duplicates, broken links, orphan notes, frontmatter drift, or classification inconsistency before deeper cleanup or restructuring.
---

# Vault Check

## Description

`vault-check` æ˜¯ Pigo vault çš„ä½Žé »å…¨å±€æª¢æŸ¥æ¨¡å¼ã€‚  
å®ƒçš„å·¥ä½œä¸æ˜¯å¤§é‡æ”¹æª”ï¼Œè€Œæ˜¯å…ˆç”¨ `.vault-index` åšå€™é¸ç›¤é»žï¼Œå†è¼¸å‡ºä¸€ä»½å¯åŸ·è¡Œçš„å¥åº·æª¢æŸ¥çµæžœã€é¢¨éšªåˆ†ç´šèˆ‡å¾ŒçºŒå»ºè­°ã€‚

## When to Use

ä½¿ç”¨æ™‚æ©Ÿï¼š

- ä½ è¦åšæ•´å€‹ vault çš„å¥åº·æª¢æŸ¥
- ä½ æ‡·ç–‘æœ‰é‡è¤‡ç­†è¨˜ã€å­¤å…’ç­†è¨˜ã€åˆ†é¡žæ¼‚ç§»æˆ– index éºæ¼
- å¤§é‡æ¬ç§»ã€åˆä½µæˆ–é‡åˆ†é¡žä¹‹å‰ï¼Œè¦å…ˆç›¤é»žé¢¨éšª
- `vault-reshape` æˆ– `vault-deep-clean` åŸ·è¡Œå‰å¾Œï¼Œéœ€è¦ä¸€ä»½åŸºæº–å ±å‘Š

ä¸è¦ç”¨åœ¨ï¼š

- å–®ç¯‡ç­†è¨˜æ­£å¼åŒ–ï¼šæ”¹ç”¨ `note-update`
- `00-Inbox` å°æ‰¹æ¬¡æ•´ç†ï¼šæ”¹ç”¨ `inbox-triage`
- å¤§è¦æ¨¡çµæ§‹é‡æ•´ï¼šæ”¹ç”¨ `vault-reshape`
- æ·±åº¦ä¿®å¾©èˆ‡æ‰¹æ¬¡æ¸…ç†ï¼šæ”¹ç”¨ `vault-deep-clean`

## Vault Index Usage

æŠŠ vault index è¦–ç‚º primary lookupï¼Œä¸è¦ä¸€é–‹å§‹å°±æš´åŠ›æŽƒæ•´å€‹ vaultã€‚

- Vault rootï¼š
  `C:\Users\hsi67063\Box\00-home-pigo.hsiao\VBA\Pigo_Obsidian`
- Query toolï¼š
  `C:\Users\hsi67063\Box\00-home-pigo.hsiao\VBA\Pigo_Obsidian\.vault-index\query_vault.py`
- Databaseï¼š
  `C:\Users\hsi67063\Box\00-home-pigo.hsiao\VBA\Pigo_Obsidian\.vault-index\notes.db`

å„ªå…ˆæŸ¥é€™äº›ï¼š

- `duplicate-candidates`
- `fts`
- `by-classification`
- `links-to`
- `links-from`

åŽŸå‰‡ï¼š

1. å…ˆç”¨ index æ‰¾å€™é¸é›†åˆ
2. å†å°é«˜é¢¨éšªæˆ–é«˜åƒ¹å€¼å€™é¸åšé€æª”æª¢æŸ¥
3. åªæœ‰åœ¨ index ä¸å¯ç”¨ã€æˆ–è¦é©—è­‰ç´°ç¯€æ™‚æ‰ fallback åˆ° `rg`

## Risk-Tier Contract

- `Low-risk`
  å¯ç›´æŽ¥ç”¢å‡ºå ±å‘Šã€çµ±è¨ˆã€å€™é¸åå–®èˆ‡æ˜Žç¢ºå¯é€†çš„å°åž‹ hygiene å»ºè­°ã€‚
- `Medium-risk`
  ä¸ç›´æŽ¥åŸ·è¡Œã€‚æ•´ç†æˆ `Pending Approval Plan`ï¼Œåˆ—å‡ºç²¾ç¢ºè·¯å¾‘ã€å»ºè­°å‹•ä½œã€å›žæ»¾æ–¹å¼ã€‚
- `High-risk`
  ä¸åœ¨ `vault-check` å…§åŸ·è¡Œã€‚æ‡‰è½‰çµ¦ `vault-reshape` æˆ– `vault-deep-clean`ã€‚

## Audit Workflow

### 1. Coverage Scan

ç›¤é»žæ•´é«”è¦æ¨¡èˆ‡ä¸»è¦å€å¡Šï¼š

- note æ•¸é‡
- ä¸»åˆ†é¡žè¦†è“‹
- æœ€è¿‘æ›´æ–°ç†±å€
- `youtube/twitter` é€™é¡žä¾†æºåž‹æ®˜ç•™å€å¡Š

### 2. Duplicate Review

æª¢æŸ¥ï¼š

- åŒæ¨™é¡Œç«¶çˆ­é 
- åŒ `source_url` ç«¶çˆ­é 
- é«˜åº¦ç›¸è¿‘çš„æ­£å¼ç­†è¨˜

è¼¸å‡ºï¼š

- å¯ç›´æŽ¥æŽ’é™¤çš„å‡é™½æ€§
- éœ€è¦äººå·¥åˆ¤æ–·çš„ merge candidates

### 3. Link Health

æª¢æŸ¥ï¼š

- broken wikilinks
- orphan notes
- åªå‡ºç¾åœ¨å–®ä¸€å­¤ç«‹å€å¡Šçš„ç­†è¨˜
- æ‡‰è¢« `index.md` æˆ–ä¸»é¡Œé æ”¶éŒ„ä½†å°šæœªæ”¶éŒ„çš„å…§å®¹

### 4. Metadata Health

æª¢æŸ¥ï¼š

- frontmatter ç¼ºæ¬„
- `classification_path` èˆ‡å¯¦éš›è·¯å¾‘ä¸ä¸€è‡´
- `processed` / `status` ä¸åˆç†
- `Source` èˆ‡ `source_url` ç´€éŒ„ä¸ä¸€è‡´

### 5. Navigation Health

æª¢æŸ¥ï¼š

- `index.md` æ˜¯å¦ç¼ºå…¥å£
- æ˜¯å¦å­˜åœ¨å€¼å¾—ç¨ç«‹æˆä¸»é¡Œé çš„ cluster
- æ˜¯å¦æœ‰ä¾†æºåž‹åˆ†é¡žæ®˜ç•™ï¼Œæ‡‰æ”¶æ–‚æˆä¸»é¡Œåž‹åˆ†é¡ž

## Expected Output

è¼¸å‡ºæ‡‰è‡³å°‘åŒ…å«ï¼š

- `æ ¸å¿ƒçµè«–`
- `ä¸»è¦é¢¨éšª`
- `å¯ç›´æŽ¥è™•ç†çš„ low-risk é …ç›®`
- `Pending Approval Plan`
- `å»ºè­°ä¸‹ä¸€æ­¥`

è‹¥æœ‰å¯¦éš›ç”¢å‡ºæª”æ¡ˆï¼Œå„ªå…ˆæ”¾åœ¨ï¼š

- `C:\Users\hsi67063\Box\00-home-pigo.hsiao\VBA\Pigo_Obsidian\.vault-index\`
  æˆ–
- ç•¶å‰å°ˆæ¡ˆæ–‡ä»¶å€

## Common Mistakes

- æŠŠ `vault-check` ç•¶æˆå…¨é¢æ”¹æª”å·¥å…·
- ä¸ç¶“éŽ index å°±ç›´æŽ¥å…¨ vault æŽƒæ
- æŠŠçµæ§‹é‡æ•´æ··é€² audit
- åªåˆ—å•é¡Œï¼Œä¸åˆ—ç²¾ç¢ºè·¯å¾‘èˆ‡å»ºè­°å‹•ä½œ
- æŠŠå–®ç¯‡ä¿®è£œå·¥ä½œå¡žé€²å…¨å±€ audit

## Handoff

`vault-check` å®Œæˆå¾Œï¼Œä¸‹ä¸€æ­¥é€šå¸¸æ˜¯ï¼š

- `vault-reshape`
- `vault-deep-clean`
- `tag-check`
- æˆ–å›žåˆ° `note-update` / `inbox-triage` åšå®šé»žä¿®è£œ

