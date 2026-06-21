# Project Context

## Terminology

### "ponytail"
When the user says "ponytail", they are referring to the concept described at:
https://abhishek-shankar.com/posts/best-agent-upgrade-wasnt-a-mode

Ponytail is a portable AI agent skill distribution pattern. The core idea: define agent skills/behaviors once in reusable skill files (a `skills/` directory), then deploy them via lightweight platform-specific adapters across multiple AI coding environments (Claude Code, Codex, GitHub Copilot, Cursor, Windsurf, etc.). A single source of truth for agent behavior, no duplication across platforms.

Reference implementation: https://github.com/DietrichGebert/ponytail
