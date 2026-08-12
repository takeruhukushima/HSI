# /// script
# requires-python = ">=3.11"
# dependencies = ["paper-qa==2026.3.18", "fhlmi==0.45.2"]
# ///

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path


MODEL_NAME = "hsi-opencode"


def bridge_config(bridge_url: str, session_id: str) -> dict:
    return {
        "model_list": [
            {
                "model_name": MODEL_NAME,
                "litellm_params": {
                    "model": f"openai/{MODEL_NAME}",
                    "api_base": bridge_url,
                    "api_key": "local",
                    "extra_headers": {"x-hsi-session-id": session_id},
                },
            }
        ]
    }


async def check_bridge(config: dict) -> None:
    from litellm import Router

    router = Router(model_list=config["model_list"])
    response = await router.acompletion(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": "Return exactly HSI_BRIDGE_OK"}],
    )
    content = response.choices[0].message.content
    if not content or "HSI_BRIDGE_OK" not in content:
        raise RuntimeError(f"Unexpected bridge response: {content!r}")
    print("HSI bridge and LiteLLM Router are ready.")


async def query_papers(question: str, papers: Path, config: dict) -> None:
    project_dir = Path.cwd().resolve()
    pqa_home = project_dir / ".pqa"
    index_dir = pqa_home / "indexes"
    pqa_home.mkdir(parents=True, exist_ok=True)
    os.environ["PQA_HOME"] = str(pqa_home)

    from paperqa import Settings, ask
    settings = Settings(
        llm=MODEL_NAME,
        llm_config=config,
        summary_llm=MODEL_NAME,
        summary_llm_config=config,
        embedding="ollama/embeddinggemma",
        embedding_config={"api_base": "http://localhost:11434"},
        parsing={
            "multimodal": False,
            "page_size_limit": 50_000,
            "use_doc_details": False,
            "disable_doc_valid_check": True,
        },
        answer={
            "evidence_k": 3,
            "evidence_summary_length": "about 30 words",
            "answer_max_sources": 3,
            "max_concurrent_requests": 1,
        },
        agent={
            "agent_type": "ToolSelector",
            "rebuild_index": True,
            "search_count": 3,
            "agent_llm": MODEL_NAME,
            "agent_llm_config": config,
            "index": {
                "paper_directory": str(papers),
                "index_directory": str(index_dir),
            },
        },
    )
    response = await ask(question, settings=settings)
    print(response.session.answer)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Query local papers through the HSI OpenCode bridge")
    parser.add_argument("--papers", type=Path, help="Directory containing papers")
    parser.add_argument("--question", help="Question to ask")
    parser.add_argument("--check", action="store_true", help="Only verify LiteLLM bridge connectivity")
    args = parser.parse_args()

    bridge_url = os.environ.get("HSI_BRIDGE_URL")
    session_id = os.environ.get("HSI_SESSION_ID")
    if not bridge_url or not session_id:
        raise RuntimeError("Run this script from an OpenCode shell so HSI_BRIDGE_URL and HSI_SESSION_ID are available")

    config = bridge_config(bridge_url, session_id)
    if args.check:
        await check_bridge(config)
        return
    if not args.papers or not args.question:
        parser.error("--papers and --question are required unless --check is used")

    papers = args.papers.expanduser().resolve()
    if not papers.is_dir():
        raise FileNotFoundError(f"Paper directory not found: {papers}")
    await query_papers(args.question, papers, config)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as error:
        print(f"HSI PaperQA error: {error}", file=sys.stderr)
        if os.environ.get("HSI_DEBUG") == "1":
            raise
        sys.exit(1)
