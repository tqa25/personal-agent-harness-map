# Python Agent Harness

This repo contains a small Python agent harness scaffold based on Microsoft's
"Meet your agent harness and claw" article.

It builds a general-purpose harness agent with:

- OpenAI chat client configuration from environment variables.
- A custom tool exposed to the model.
- Planning mode, todos, memory, and hosted web search enabled by default.
- A streaming console entrypoint.

## Requirements

- Python 3.11+
- `uv`
- An OpenAI API key
- Optional `OPENAI_BASE_URL` if you are using a compatible non-default endpoint

## Configure

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-5.4"
```

Optional variables:

```bash
export OPENAI_BASE_URL="https://api.openai.com/v1"
export OPENAI_ORG_ID="org_..."
```

`OPENAI_MODEL` is optional. If omitted, the app uses the article's default
model name.

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
