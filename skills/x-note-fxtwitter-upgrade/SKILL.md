---
name: "x-note-fxtwitter-upgrade"
description: "x-note Flow B Step 2: replace GraphQL upgrade with api.fxtwitter.com. No auth, fewer CDP dependencies."
---

# x-note fxtwitter Upgrade Proposal

> Status: **PROPOSAL** · Author: Jarvis · Date: 2026-06-20

## Goal

Replace `xnote_fetch_full.py` (GraphQL + cookies) with `fetch_fxtwitter.py`
(api.fxtwitter.com) for **Flow B Step 2** of x-note 7.7.0 — upgrading
400-char preview candidates to full text + media + engagement.

**Decisions locked in (2026-06-20)**:
- Flow A (single URL baoyu-fetch + CDP) → **unchanged**
- Flow B Step 1 (`fetch_fresh.py` scan timeline) → **unchanged**
- Flow B Step 2 (this proposal) → **swap to fxtwitter**
- Failure behavior → **Option X (tolerant)**: keep original `text`, add `fxtwitter_error`

## Why

- FxTwitter = no auth, no cookies, no CDP
- Note tweets (Pigo's primary "long-form") get full text via fxtwitter
- Existing `xnote_fetch_full.py` is dead code (writes `xnote_full_texts.json` nobody reads)
- Public `api.fxtwitter.com` is maintained by dangeredwolf (FxEmbed upstream)

## Hard Rules (write into SKILL.md)

1. Per-tweet sleep: **1.0s**
2. Per-run cap: **100 tweets** (hard stop, fail-loud)
3. Failure → keep original `text`, set `fxtwitter_error` (do not abort batch)
4. Twitter Article (article with cover/chapters) → **not supported** by fxtwitter consumer;
   heuristic warning via `fxtwitter_warning: ["possible_twitter_article_truncated"]`
   when `is_note_tweet=False` and `text_len >= 270`
5. User-Agent header required (returns 401 otherwise)

## Files Touched

| File | Change |
|---|---|
| `scripts/fetch_fxtwitter.py` | NEW (120 lines, written 2026-06-20) |
| `SKILL.md` | UPDATE: Tool Priority table, Flow B Step 3, Hard Rules |
| `scripts/xnote_fetch_full.py` | MARK LEGACY (do not delete, add deprecation header) |
| `score_candidates.py` / `score_and_note.py` | UNCHANGED (they read `text`, fxtwitter upgrades it in place) |

## Output Contract

`fetch_fxtwitter.py` reads `~/Downloads/xnote_fetch_YYYY-MM-DD_fresh.json`,
upgrades each `handles[].target_candidates[]` in place:

- `text` ← upgraded to full text (was 400-char preview)
- New fields added:
  - `full_text_upgraded: true`
  - `full_text_source: "fxtwitter"`
  - `is_note_tweet: bool`
  - `lang`, `source`, `author{...}`, `engagement_complete{...}`,
    `media_urls[{type,url,...}]`, `created_at`, `created_timestamp`,
    `replying_to`, `replying_to_status`, `reposted_by`, `fxtwitter_url`,
    `fxtwitter_warning` (or absent)
- On failure: `fxtwitter_error: "code=N msg=..."`, original fields preserved

Plus `fxtwitter_upgrade_at` + `fxtwitter_upgrade_meta{...}` at root.
Debug copy: `~/Downloads/xnote_fetch_YYYY-MM-DD_fxtwitter.json`.

## Verification

### Done (2026-06-20)
- ✅ `fetch_fxtwitter.py` importable without side effects (path resolution deferred to `main()`)
- ✅ 200 OK on `2067769761371676875` (Bindu Reddy note tweet, 323 chars, is_note_tweet=True)
- ✅ engagement_complete fully populated (likes=2158, retweets=166, replies=66, views=1524869)
- ✅ 404 path returns `fxtwitter_error`, leaves original `text` and `likes` untouched
- ✅ Downstream `score_candidates.py` line 56 reads `c.get('text','')[:400]` — only depends on `text` field, no migration needed

### TODO (1-week soak)
- [ ] Run on real Pigo's 2026-06-20 batch (`xnote_fetch_2026-06-20_*_fresh.json`)
- [ ] Measure transient failure rate (target: <5%)
- [ ] Confirm score_and_note.py produces ≥20 retained notes (same as CDP baseline)
- [ ] Confirm `xnote2 inbox stub` format still satisfied (frontmatter fields auto-extracted from upgraded fields)

## Rollback Plan

If failure rate >10% or output regression:
1. Stop running `fetch_fxtwitter.py` (just skip Step 2)
2. `xnote_fetch_full.py` (GraphQL) still on disk as legacy
3. score_candidates falls back to 400-char `text` — Flow B still completes with lower fidelity

## Risk

- **Public API dependency**: `api.fxtwitter.com` is community infra. Pigo has no SLA.
  Mitigation: small batch cap (100/run), tolerant fallback.
- **Twitter Article unsupported**: rare for Pigo's handles (none observed in 2026-06-19 vault sample).
  Mitigation: heuristic warning flag.
