---
name: hsi-paperqa
description: Query local scientific papers with PaperQA using the current OpenCode model. Use when the user asks questions about PDFs or papers in a local directory.
---

# HSI PaperQA

Use PaperQA for grounded question answering over a local directory of papers. Its
generation requests are routed through the project-local HSI plugin. The bridge
uses the provider and model selected for the current OpenCode session, including
Ollama, OpenAI, Anthropic, and other configured providers. OpenCode keeps provider
credentials and PaperQA does not need a separate generation API key.

The `openai/hsi-opencode` name inside the Python script selects the OpenAI-compatible
wire protocol between LiteLLM and the local bridge. It does not select OpenAI as
the generation provider.

## Prerequisites

Check that Ollama is running and install the local embedding model if needed:

```bash
ollama list
ollama pull embeddinggemma
```

PaperQA state and indexes are stored under `.pqa/` in the current project.

The OpenCode process injects `HSI_BRIDGE_URL` and `HSI_SESSION_ID` into shell
commands. Do not manually invent these values or expose provider credentials.

## Run

From the repository root:

```bash
uv run .opencode/skills/hsi-paperqa/scripts/query_papers.py \
  --papers "/absolute/path/to/papers" \
  --question "Question to answer"
```

Use `--check` first when diagnosing the bridge. PaperQA's normal ToolSelector
agent is supported through the HSI bridge's OpenAI tool-call translation.

Report the answer with PaperQA's citations. If execution fails, report the exact
missing prerequisite or compatibility error rather than silently answering
without PaperQA.
