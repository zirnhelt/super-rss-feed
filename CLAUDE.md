# Project Context

## Terminology

### "ponytail"
When the user says "ponytail", they are referring to the concept described at:
https://abhishek-shankar.com/posts/best-agent-upgrade-wasnt-a-mode

Ponytail is a portable AI agent skill distribution pattern. The core idea: define agent skills/behaviors once in reusable skill files (a `skills/` directory), then deploy them via lightweight platform-specific adapters across multiple AI coding environments (Claude Code, Codex, GitHub Copilot, Cursor, Windsurf, etc.). A single source of truth for agent behavior, no duplication across platforms.

Reference implementation: https://github.com/DietrichGebert/ponytail

## API Cost Management

Keep API costs as low as possible at all times. This is a hard constraint.

- **Prefer small models** (e.g. `claude-haiku-4-5-20251001`) for simple tasks like classification, extraction, summarization, and short-form generation. Only use larger models when the task genuinely requires it.
- **Use prompt caching** wherever possible. Structure prompts so that long, stable context (system prompts, documents, tool definitions) comes first and can be cached.
- **Minimize tokens**: write concise system prompts, strip unnecessary whitespace, avoid redundant instructions.
- **Batch requests** rather than issuing one call per item when the API supports it.
- **Short-circuit early**: if a cheap check (keyword filter, regex, small model) can rule out most cases, do it before calling a larger/more expensive model.
- **Never call the API speculatively** or "just in case" — every call must serve a clear purpose.
- When in doubt, ask: "Can I do this with fewer tokens or a cheaper model?"
