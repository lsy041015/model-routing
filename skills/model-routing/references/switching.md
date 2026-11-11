# Switching and mixing models

## Switching the main session

- The prompt cache belongs to the model that wrote it. The first turn on a new
  model pays the cache-write price on the whole conversation.
- Switch at a natural break: run `/compact` first, or start a fresh session with
  a short written plan.
- Thinking blocks are kept only when the new model can read them. A model never
  reads the thinking of a model above it, so moving down loses earlier
  reasoning. Moving off Fable 5.2 to any other model drops its reasoning.
  Readable: Opus 5.5 reads Sonnet 5.5 and Haiku 5.5; Sonnet 5.5 reads Haiku 5.5;
  Fable 5.2 reads Opus 5.5, Sonnet 5.5 and Haiku 5.5.

## Subagents on smaller models

- Set `model:` in the agent file; `CLAUDE_CODE_SUBAGENT_MODEL` sets the default
  for agents without one (built-in general-purpose and Plan).
- The built-in Explore runs on the session's model; override it with a user
  agent named `Explore` (`model: haiku`). See the plugin's `extras/Explore.md`.
- `haiku` resolves to Haiku 5.5 on the Anthropic API with Claude Code v2.1.293+;
  on Bedrock, Vertex, Foundry and Claude Platform on AWS it may still be Haiku
  4.5. Pin it with `ANTHROPIC_DEFAULT_HAIKU_MODEL`.
- `opusplan` (plan on Opus, edit on Sonnet) puts code edits on the smaller
  model, the opposite of this routing. Measure before adopting.

## Advisor tool (beta)

A cheap executor asks a stronger advisor mid-task. Pays off only when most turns
are routine and the executor actually consults it. Published pairings did not
clearly beat the executor alone (Opus high + Fable 5.1 advisor: +1.7 points for
2.1x cost, within noise). Measure the consult rate first.

## Moving an API request between models

- **Thinking**: Opus 5.5 and Fable 5.2 always think; disabling it errors. Read
  content blocks by type; a response can start with a thinking block.
- **Fable 5.2 preserved thinking**: changing anything before a Fable thinking
  block (system prompt, tools, earlier messages) returns 400 unless you opt in
  to dropping it. Keep history append-only.
- **Forced tool use**: `tool_choice` `any`/`tool` returns 400 on Sonnet 5.5,
  Opus 5.5 and Fable 5.2. Send `auto`, mark the tool `strict: true`, say in the
  prompt when to use it.
- **Computer use**: only through `computer_toolset_20260801`.
- **Haiku 4.5 → 5.5**: replace `budget_tokens` with an effort level; drop
  non-default `temperature`/`top_p`/`top_k`; end with a user turn.
- **Safety fallbacks**: flagged cybersecurity requests may re-run on Opus 4.8,
  flagged biology on Opus 5; Claude Code shows a notice.
- One system, several models: build every request for the strictest one
  (append-only history, `tool_choice: auto` with strict tools, blocks read by
  type, precise prompts). Let code pick the model when the rule is simple.
