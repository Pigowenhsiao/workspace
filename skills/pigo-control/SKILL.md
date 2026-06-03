---
name: pigo-control
description: |
  Linux browser control workflow for Pigo. Use when Pigo asks to control the currently open webpage/browser/tab, 
  attach to an existing Chrome/Chromium session, use agent-browser on an active tab, inspect or operate a web app,
  or fall back to a fixed Chrome profile with saved login state. Provides safe detection, launch/check commands,
  CDP conventions, and confirmation rules before submitting forms, sending messages, or taking account actions.
---

# Pigo Control（Linux 版）

Use this skill to control Pigo's currently open webpage or browser tab on Linux.

Priority order：

1. **Current agent-browser tab**：if agent-browser already sees the target tab, use it directly.
2. **Existing CDP browser**：if an already-open Chrome/Chromium exposes a reachable DevTools endpoint, attach/use that session.
3. **Fixed profile fallback**：if no current browser is controllable, launch Pigo's dedicated Chrome profile.

The fixed profile is a fallback for stable login state, not the only path.

## Current Browser First

When Pigo says "目前已經開啟的瀏覽器", "目前這個網頁", "current browser", "current page", "this tab", "這個 browser", or asks to continue work on an already open website:

1. First use `agent-browser snapshot` to list tabs or snapshot the current page.
2. If the desired tab is visible, operate that tab directly.
3. If agent-browser only sees `about:blank` or the wrong browser, discover existing CDP endpoints with the bash discovery script.
4. If no endpoint is reachable, explain that an ordinary Chrome window cannot be attached after launch unless it was started with remote debugging.
5. Only then offer to launch the fixed profile fallback.

## Fixed Browser Fallback

Default profile path on Linux：

```bash
/home/pigo/.codex/chrome-login-profile
```

Default fallback CDP endpoint：

```text
http://127.0.0.1:9222
```

Pigo 常用 CDP 端點：
- `http://127.0.0.1:19825` — X.com 搜索專用 Chrome
- `http://127.0.0.1:9233` — Pigo 個人 Chrome（已登入）

Default fallback start URL：

```text
about:blank
```

This profile is for agent-controlled browser work only. Do not use it for banking, primary email, password managers, admin consoles, or other high-sensitivity accounts.

## Discover, Check, Or Start Browser

### Discover existing CDP browsers

```bash
~/.openclaw/workspace/skills/pigo-control/scripts/find-pigo-browser.sh
```

### Check a known endpoint

```bash
~/.openclaw/workspace/skills/pigo-control/scripts/check-pigo-browser.sh
```

### Check specific host/port

```bash
~/.openclaw/workspace/skills/pigo-control/scripts/check-pigo-browser.sh --host 127.0.0.1 --port 9222
```

### Start the fixed fallback browser

```bash
~/.openclaw/workspace/skills/pigo-control/scripts/start-pigo-browser.sh
```

### Open a specific site directly

```bash
~/.openclaw/workspace/skills/pigo-control/scripts/start-pigo-browser.sh --url "https://example.com"
```

## Operating Workflow

1. Try the current agent-browser tab first.
2. If the target is not visible, run `find-pigo-browser.sh` to discover existing CDP browsers.
3. If a reachable existing browser is found, use that endpoint/session where the current toolchain supports attaching.
4. If no existing controllable browser is found, run `start-pigo-browser.sh` as fallback.
5. If the site requires login, ask Pigo to complete login manually.
6. Navigate or search only as needed for the explicit task.
7. Before sending, deleting, forwarding, joining, leaving, blocking, pinning, or changing account/chat settings, show the exact action and get Pigo's confirmation.
8. After action, verify via browser snapshot or visible state.

## Site Operation Rules

- Treat the currently visible webpage as the target unless Pigo names another site or tab.
- Prefer concise Traditional Chinese communication with Pigo.
- Do not read unrelated tabs, chats, accounts, inboxes, documents, or private content unless Pigo explicitly asks.
- Do not summarize private content unless Pigo asks for that specific page/chat/document.
- Do not submit forms, send messages, delete content, purchase, publish, forward, join, leave, block, pin, change settings, or perform account-changing actions without explicit approval in the current turn.
- If Pigo directly provides a specific message/form content and says to send/submit it, that counts as approval for that specific action only.
- Telegram/Jarvis is just one supported example, not the default binding.

## Recovery

If agent-browser only sees `about:blank` or a different browser:

1. Run `find-pigo-browser.sh`.
2. If an endpoint shows the requested site/page, try to use that session.
3. If the automation runtime cannot attach to that Chrome instance, tell Pigo the limitation.
4. Start the fixed profile only if Pigo wants the fallback.

If port `9222` is already in use：

```bash
~/.openclaw/workspace/skills/pigo-control/scripts/check-pigo-browser.sh --port 9222
```

Only terminate processes after confirming they are using the dedicated profile path, not Pigo's normal Chrome profile.

## Attachment Limitation

An already-open normal Chrome window is not attachable unless it was launched with `--remote-debugging-port` or is already controlled by the current browser automation runtime. This skill can discover reachable CDP endpoints and operate tool-visible tabs, but it cannot retroactively turn a normal Chrome window into a controllable browser without relaunching it.

## Security Boundary

Remote debugging exposes browser control to local processes. Keep the endpoint bound to `127.0.0.1`, use the dedicated profile, and close the browser when finished with sensitive sessions.
