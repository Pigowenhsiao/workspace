# 2026-05-03 OpenClaw Memory Restore

Updated: 2026-05-03T05:34:27Z
Purpose: Restore OpenClaw's working context after memory repair and recent Vault / Agent changes.

## Restore Status

- OpenClaw gateway is reachable.
- Telegram default channel is enabled, configured, running, connected, and using polling mode.
- Active agent is `main`.
- Session store: `/home/pigo/.openclaw/agents/main/sessions/sessions.json`.
- Memory backend: builtin.
- Memory source: `/home/pigo/.openclaw/workspace/memory`.
- Memory index: `/home/pigo/.openclaw/memory/main.sqlite`.
- Indexed memory state: 32 files, 176 chunks, `dirty: false`.
- FTS search is available.
- Vector / semantic search is intentionally disabled.

## Core Identity And Preferences

- Identity: Jarvis, an efficient assistant for Pigo.
- Always communicate with Pigo in Traditional Chinese unless explicitly told otherwise.
- Do not proactively send external messages without confirmation.
- Telegram groups use mention-only behavior: `requireMention: true`; only respond in groups when mentioned.
- New tasks should follow skill-first routing:
  1. Check installed skills.
  2. Check `/home/pigo/Documents/Agent/docs/Skill_Index.md`.
  3. Use own judgment only if no matching skill exists.

## Paths To Remember

- Vault: `/home/pigo/Documents/Pigo_Obsidian`.
- Agent repo: `/home/pigo/Documents/Agent`.
- New external clones default to `/home/pigo/Downloads` unless Pigo specifies another path.
- OpenClaw workspace: `/home/pigo/.openclaw/workspace`.
- OpenClaw memory: `/home/pigo/.openclaw/workspace/memory`.
- OpenClaw memory index DB: `/home/pigo/.openclaw/memory/main.sqlite`.

## Memory Repair Context

- 2026-05-03 memory repair restored a stable FTS-only setup.
- `openclaw config validate --json` succeeded after config changes.
- `openclaw memory status --index --json` succeeded.
- `openclaw memory search` returned matching memory results.
- `openclaw gateway probe` succeeded after gateway restart.
- Keep current FTS-only setup for stability.

## Known Memory Limits

- Semantic/vector memory remains disabled because no supported embedding provider is configured.
- Missing or unavailable embedding providers include Copilot, OpenAI, Google, Mistral, DeepInfra, Bedrock, and related auth profiles.
- Ollama embedding was tested with local models but ran on CPU, not GPU.
- Ollama-based embedding caused memory search/index hangs or timeouts, so provider/model settings were removed.
- Do not re-enable vector search or Ollama embedding until GPU/provider health is fixed and verified.

## Important Historical Context

- `memory-lancedb-pro` previously had embedding configuration problems; treat it as historical risk, not current stable memory.
- GBrain was removed from OpenClaw config and local state on 2026-04-26, then re-cloned to `/home/pigo/Documents/gbrain` for code work.
- GBrain default engine path was changed back to Postgres-first.
- GBrain had local commits noted in memory: `6ee481f` and `9393af1`; verify current git state before assuming they are pushed.
- Notion token checks previously returned invalid-token errors; do not assume Notion integration is healthy without re-verification.
- ClawTeam-OpenClaw is installed, but it is a coding-agent coordination framework and not a good fit for autonomous research. Spawned agents require TTY input.

## Vault And Wiki Context

- `llm-wiki` new notes must default to `00-Inbox/`.
- Formal Learning notes should later be organized into the current `08-Learning` topic-first architecture.
- `note-update` has already learned the topic-first architecture.
- Recent rule update: `llm-wiki` should preserve `00-Inbox/` as the new-note landing zone while treating old top-level source folders as retired canonical destinations.

## Recovery Evidence Read

- `/home/pigo/.openclaw/workspace/MEMORY.md`
- `/home/pigo/.openclaw/workspace/AGENTS.md`
- `/home/pigo/.openclaw/workspace/memory/index.md`
- `/home/pigo/.openclaw/workspace/memory/USER_PREFERENCES.md`
- `/home/pigo/Documents/STATUS_OPENCLAW.md`
- `/home/pigo/.openclaw/workspace/memory/.dreams/short-term-recall.json`
- `/home/pigo/.openclaw/workspace/memory/CHANGELOG.md`
- `/home/pigo/.openclaw/workspace/memory/2026-04-10.md`
- `/home/pigo/.openclaw/workspace/memory/2026-04-13-group-bot-debugging.md`
- `/home/pigo/.openclaw/workspace/memory/2026-04-26.md`
- `/home/pigo/Documents/Agent/memory/P0-core.md`
- `/home/pigo/Documents/Agent/memory/P1-90days.md`
- `/home/pigo/Documents/Agent/memory/P2-30days.md`

## Next Operational Rule

When OpenClaw seems to have lost context again, first read this restore note, then search memory with:

```bash
openclaw memory search --query "OpenClaw memory restore Pigo FTS-only Vault Agent" --max-results 5
```

Then inspect the cited source files before asking Pigo to repeat context.
