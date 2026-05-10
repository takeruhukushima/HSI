import importlib.util
import sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP

app = FastMCP("python-mcp")
SCRIPTS_DIR = Path(__file__).parent / "scripts"

def _try_import(module_name, file_path, *extra_pkgs):
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = mod
            spec.loader.exec_module(mod)
            return mod
    except ImportError as e:
        missing = extra_pkgs or [e.name]
        return f"Error: missing dependency `{missing[0]}`. Run: uv sync --group <group>"
    except Exception:
        return None
    return None

@app.tool()
def search_pubmed(query: str, max_results: int = 5) -> str:
    """Search PubMed articles by keyword"""
    import json, urllib.request, urllib.parse
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    params = {"db": "pubmed", "term": query, "retmax": max_results, "retmode": "json"}
    with urllib.request.urlopen(base_url + "esearch.fcgi?" + urllib.parse.urlencode(params)) as r:
        ids = json.loads(r.read().decode()).get("esearchresult", {}).get("idlist", [])
    if not ids:
        return json.dumps({"papers": []}, ensure_ascii=False)
    params = {"db": "pubmed", "id": ",".join(ids), "retmode": "json"}
    with urllib.request.urlopen(base_url + "esummary.fcgi?" + urllib.parse.urlencode(params)) as r:
        summary = json.loads(r.read().decode())
    papers = []
    for uid in ids:
        p = summary.get("result", {}).get(uid, {})
        papers.append({
            "title": p.get("title", "N/A"),
            "authors": ", ".join(a.get("name", "") for a in p.get("authors", [])) if p.get("authors") else "N/A",
            "journal": p.get("source", "N/A"),
            "year": str(p.get("pubdate", "N/A"))[:4],
            "pmid": uid,
        })
    return json.dumps({"papers": papers}, ensure_ascii=False)

@app.tool()
def text_stats(text: str) -> str:
    """Calculate text statistics (word count, character count, sentence count, reading time)"""
    import re, json
    sents = [s for s in re.split(r'[.!?]+', text) if s.strip()]
    return json.dumps({
        "word_count": len(text.split()),
        "character_count": len(text),
        "sentence_count": len(sents),
        "estimated_reading_time_min": round(len(text.split()) / 200, 1),
    }, ensure_ascii=False)

@app.tool()
async def paperqa_query(query: str, target_dir: str) -> str:
    """Ask a question to papers in a directory using PaperQA (RAG). Requires: uv sync --group paperqa"""
    import json
    mod = _try_import("paperqa_tool", SCRIPTS_DIR / "paperqa_tool.py", "paper-qa")
    if isinstance(mod, str):
        return mod
    if mod is None:
        return "Error: paperqa_tool.py not found"
    return await mod.run_paperqa_query(query, target_dir)

@app.tool()
async def shinka_experiment(experiment_name: str, config_dir: str) -> str:
    """Run a ShinkaEvolve experiment"""
    mod = _try_import("shinka_tool", SCRIPTS_DIR / "shinka_tool.py")
    if isinstance(mod, str):
        return mod
    if mod is None:
        return "Error: shinka_tool.py not found"
    return await mod.run_shinka_experiment(experiment_name, config_dir)

@app.tool()
def volcano_plot(file_path: str, groups: str, comparisons: str,
                 p_cutoff: float = 0.05, min_log2: float = -1.0, max_log2: float = 1.0,
                 output_dir: str = "") -> str:
    """Generate volcano plot from proteomics data. groups and comparisons are JSON strings"""
    import json
    mod = _try_import("volcano_plot", SCRIPTS_DIR / "proteomics" / "volcano_plot.py", "seaborn")
    if isinstance(mod, str):
        return mod
    if mod is None:
        return "Error: volcano_plot.py not found"
    result = mod.run_volcano_analysis(
        file_path, json.loads(groups), json.loads(comparisons),
        p_cutoff=p_cutoff, min_log2=min_log2, max_log2=max_log2,
        output_base_dir=output_dir or None,
    )
    return json.dumps({"output_dir": result}, ensure_ascii=False)

@app.tool()
def clustermap_analysis(input_file: str, stats_file: str,
                        output_dir: str = "") -> str:
    """Generate clustermap/heatmap from volcano analysis results"""
    import json
    mod = _try_import("clustermap_from_volcano",
                      SCRIPTS_DIR / "proteomics" / "clustermap_from_volcano.py", "seaborn")
    if isinstance(mod, str):
        return mod
    if mod is None:
        return "Error: clustermap_from_volcano.py not found"
    result = mod.run_clustermap_analysis(
        input_file, stats_file, output_base_dir=output_dir or None,
    )
    return json.dumps({"output_dir": result}, ensure_ascii=False)

@app.tool()
def po_analysis(stats_file: str, anchors: str = '["CLUS_MOUSE"]',
                output_dir: str = "") -> str:
    """Run Protein Ontology (PO) analysis with ESM-2 embeddings. Requires: uv sync --group proteomics"""
    import json
    mod = _try_import("po_analysis",
                      SCRIPTS_DIR / "proteomics" / "PO_analysis_from_volcano.py",
                      "fair-esm")
    if isinstance(mod, str):
        return mod
    if mod is None:
        return "Error: PO_analysis_from_volcano.py not found"
    result = mod.run_po_analysis(
        stats_file, anchors=json.loads(anchors),
        output_base_dir=output_dir or None,
    )
    return json.dumps({"output_dir": result}, ensure_ascii=False)

if __name__ == "__main__":
    app.run()
