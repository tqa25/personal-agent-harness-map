# Python Agent Harness

This repo contains a small Python agent harness scaffold based on Microsoft's
"Meet your agent harness and claw" article.

It builds a general-purpose harness agent with:

- Microsoft Foundry chat client configuration from environment variables.
- A custom tool exposed to the model.
- Planning mode, todos, memory, and hosted web search enabled by default.
- A streaming console entrypoint.

## Requirements

- Python 3.11+
- `uv`
- Azure CLI login for the default credential path
- A Microsoft Foundry project endpoint that supports Responses and hosted web search

## Configure

```bash
export FOUNDRY_PROJECT_ENDPOINT="https://..."
export FOUNDRY_MODEL="gpt-5.4"
```

`FOUNDRY_MODEL` is optional. If omitted, the app uses the article's default
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
