# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## Agent Repo

- Path: `/home/pigo/Documents/Agent/`
- Skill Index: `docs/Skill_Index.md`（473 skills）
- Git repo，sync with remote

## News Fetch Notes

- CNBC 官方 RSS 可用：
  - `https://www.cnbc.com/id/100003114/device/rss/rss.html`
- 取 CNBC feed 時請帶瀏覽器 User-Agent，否則常見結果是 `HTTP 403`：
  - `curl -L -A "Mozilla/5.0" --max-time 15 https://www.cnbc.com/id/100003114/device/rss/rss.html`
- 新聞抓取優先順序：
  - 先 `curl` 官方 feed / 可讀頁
  - 再用搜尋 skill 或其他搜尋來源
  - 最後才用 browser，且不得假設固定 DOM
