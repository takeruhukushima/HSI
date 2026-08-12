---
name: hsi-proteomics
description: Analyze proteomics spreadsheets with volcano plots, functional clustermaps, and ESM-2 protein ontology analysis. Use for differential protein abundance and protein corona workflows.
---

# HSI Proteomics

The scripts in `scripts/` are importable analysis modules. Run them with `uv`
and pass real file paths and group definitions from the user's dataset.

## Volcano analysis

```bash
uv run .opencode/skills/hsi-proteomics/scripts/volcano_plot.py \
  --input data.xlsx \
  --groups '{"control":["C1","C2"],"target":["T1","T2"]}' \
  --comparisons '[["target","control"]]'
```

## Clustermap

```bash
uv run .opencode/skills/hsi-proteomics/scripts/clustermap.py \
  --input data.xlsx --stats stats_target_vs_control.xlsx
```

## PO analysis

```bash
uv run .opencode/skills/hsi-proteomics/scripts/po_analysis.py \
  --stats stats_target_vs_control.xlsx --anchors '["CLUS_MOUSE"]'
```

This requires network access to UniProt. The large ESM-2 dependencies are
installed and loaded only when requested.

Validate input columns before running and report the absolute output directory.
