# Python Agent Harness

This repo contains a small Python agent harness scaffold based on Microsoft's
"Meet your agent harness and claw" article.

It builds a general-purpose harness agent with:

- OpenRouter chat client configuration through the OpenAI-compatible API.
- A custom tool exposed to the model.
- Planning mode, todos, memory, and hosted web search enabled by default.
- A streaming console entrypoint.

## Requirements

- Python 3.11+
- `uv`
- An OpenRouter API key
- Optional `SEARCH_PROVIDER_API_KEY` if you later add a non-default external search backend

## Configure

```bash
export OPENROUTER_API_KEY="sk-or-..."
export OPENROUTER_MODEL="~openai/gpt-latest"
```

Optional variables:

```bash
export OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
```

`OPENROUTER_MODEL` is optional. If omitted, the app defaults to
`~openai/gpt-latest`.

This repo uses the OpenAI-compatible SDK path against OpenRouter. OpenRouter's
official docs describe that setup as:

- `base_url` / `baseURL`: `https://openrouter.ai/api/v1`
- `api_key` / `apiKey`: your `OPENROUTER_API_KEY`

## Install and Run

```bash
uv sync --extra dev
uv run agent-harness
```

Console commands:

- `/todos` shows the current todo list.
- `/mode` shows or changes the current agent mode.
- `/session-export <file>` saves the current session.
- `/session-import <file>` restores a saved session.
- `/exit` exits.

## Test

```bash
uv run pytest
```
