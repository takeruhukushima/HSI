---
name: hsi-pptx
description: Generate PowerPoint presentations from slide titles and Markdown-like text. Use when the user requests a local .pptx presentation.
---

# HSI PowerPoint

Write the presentation specification as JSON and run:

```bash
pnpm --dir .opencode exec tsx skills/hsi-pptx/scripts/create-pptx.ts \
  --input presentation.json \
  --output presentation.pptx
```

Input format:

```json
{
  "title": "Research presentation",
  "slides": [
    {"title": "Background", "content": "Background text"},
    {"title": "Results", "content": "Result text"}
  ]
}
```

Confirm the generated file exists before reporting completion.
