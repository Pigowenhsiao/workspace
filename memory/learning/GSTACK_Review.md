# Garry Tan's gstack review (OpenClaw + gstack integration)

Source: GitHub garrytan/gstack
Date: 2026-03-22
Tags: #GStack #ClaudeCode #AgentSkills #OpenClaw

Summary:
- gstack is a holistic AI engineering factory built around Claude Code, turning it into a team with roles (CEO, Eng Manager, Designer, QA, Release, etc.) and slash commands.
- It emphasizes structured workflow (Think → Plan → Build → Review → Test → Ship → Reflect) and orchestration of multiple agents.
- It provides a library of 18 specialists and 7 power tools, all as commands, designed to streamline multi-agent collaboration.
- The core pattern is to automate end-to-end sprint pipelines, enabling parallel workstreams without chaos.

Key concepts:
- Skills are configured under .agents/skills/ and discovered automatically; SKILL.md defines how an agent performs.
- Hook and safety guards (careful, freeze, guard) can be used for enforcing boundaries.
- MCP (Model Context Protocol) serves as the universal interface to external services (databases, browsers, file systems, etc.).
- The orchestrator (Conductor) can run many Claude Code sessions in parallel, with isolated workspaces.

Core architecture mapping to OpenClaw:
- skills/ directory maps to ~/.openclaw/workspace/skills/
- SKILL.md maps to the agent's behavior spec
- /browse, /office-hours, /plan-ceo-review, /design-review etc. map to various skills and flows
- Hooks integrate with Heartbeat and memory to keep progress and state across sessions

Practical implications for OpenClaw:
- Use gstack to create a structured toolset for agents; it’s not just about having more tools but about disciplined workflows and governance.
- With gstack, you can run multiple parallel sprints, each with its own domain specialists, enabling large-scale automation.
- The combination of Slashes for commands and markdown-based SKILLs provides portability across frameworks.

How to start:
- Install gstack: git clone https://github.com/garrytan/gstack.git ~/.claude/skills/gstack; cd ~/.claude/skills/gstack; ./setup
- Or use the alternative host installation path: 
  - git clone https://github.com/garrytan/gstack.git ~/gstack
  - cd ~/gstack && ./setup --host auto

OpenClaw integration notes:
- Consider adding a dedicated gstack section to CLAUDE.md with recommended browse setup and available commands.
- Ensure SKILL.md files exist for each required capability and that they align with OpenClaw's skill discovery.

Links:
- GitHub: https://github.com/garrytan/gstack
- Documentation: /garrytan/gstack/blob/main/docs/skills.md

Next steps:
- Create a memory/index entry for this review and link to it from AGENTS.md
- Optionally break the content into sub-notes (templates, pitfalls, architecture) under memory/learning/Advanced_OpenClaw_Guides
