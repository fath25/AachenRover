# Portable agent harness

The harness is instructions, task skills, repeatable commands, and observable
acceptance tests. It does not require an OpenAI SDK, model API, or a specific
provider. The same files can be read by a host using Claude, Qwen, Meta/Llama,
OpenAI, Gemini, or another model. Native file discovery varies by host; a model
name is not a guarantee of tool access or instruction support.

| Host | Entry point |
| --- | --- |
| Codex / AGENTS.md-aware hosts | `AGENTS.md`, `.agents/skills` link |
| Claude Code | `CLAUDE.md` imports `AGENTS.md`, `.claude/skills` link |
| Qwen hosts | `QWEN.md`, or explicit project context |
| Gemini hosts | `GEMINI.md`, or explicit project context |
| GitHub Copilot | `.github/copilot-instructions.md` points to shared instructions |
| Other hosts / local Llama or Qwen | Supply `./scripts/rover context` output |

Canonical skills live in `skills/`; links prevent provider copies diverging.
Each skill has a concise name and description for discovery, then task-specific
instructions loaded on demand. This follows OpenAI's
[AGENTS.md guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
and [skills guidance](https://learn.chatgpt.com/docs/build-skills), without
assuming that every provider implements their discovery conventions.

A host needs repository read/write, a shell with bounded execution, diff review,
and permission handling. Read context, state acceptance criteria, implement,
run relevant checks, inspect the diff, and report results with limitations.
`./scripts/rover context` emits ordinary text for hosts with no native discovery;
redirect it to a temporary file or supply it through that host's context UI.
It does not invoke a model or execute model-generated commands.

Useful task prompt:

> Read AGENTS.md and the rover-simulation skill. Add one lidar-visible obstacle
> to the test yard without changing the ROS interface. Build and run relevant
> checks, and report exactly what was tested.

For Claude assistance, use the installed CLI with normal permissions, scoped
read-only review tools when reviewing, and a bounded task. Never share secrets
in prompts or disable permissions to make a task succeed. Provider adapters
have not all been exercised; see `validation.md` for actual evidence.
