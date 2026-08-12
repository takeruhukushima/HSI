---
name: hsi-shinka
description: Run ShinkaEvolve experiments using the current OpenCode model and local Ollama embeddings. Use when evolving or optimizing code with a Shinka task directory.
---

# HSI ShinkaEvolve

Run ShinkaEvolve with generation routed through the project-local HSI OpenCode
bridge. The bridge uses the provider and model selected for the current OpenCode
session; it is not tied to OpenAI. OpenCode retains provider credentials. Code
similarity embeddings use Ollama locally.

## Prerequisites

```bash
ollama list
ollama pull embeddinggemma
```

The task directory must contain `initial.py` and `evaluate.py`.

## Run

```bash
uv run .opencode/skills/hsi-shinka/scripts/shinka.py \
  --task-dir "/absolute/path/to/task" \
  --generations 10
```

For an initial smoke test, use `--generations 1 --max-proposal-jobs 1`.
Do not pass OpenCode provider API keys to ShinkaEvolve.
