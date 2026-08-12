# /// script
# requires-python = ">=3.10"
# dependencies = ["shinka-evolve>=0.0.7"]
# ///

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ShinkaEvolve through the HSI OpenCode bridge")
    parser.add_argument("--task-dir", required=True, type=Path)
    parser.add_argument("--results-dir", type=Path)
    parser.add_argument("--generations", type=int, default=10)
    parser.add_argument("--max-evaluation-jobs", type=int, default=1)
    parser.add_argument("--max-proposal-jobs", type=int, default=1)
    args = parser.parse_args()

    bridge_url = os.environ.get("HSI_BRIDGE_URL")
    session_id = os.environ.get("HSI_SESSION_ID")
    if not bridge_url or not session_id:
        raise RuntimeError("Run this script from an OpenCode shell so HSI_BRIDGE_URL and HSI_SESSION_ID are available")

    task_dir = args.task_dir.expanduser().resolve()
    for filename in ("initial.py", "evaluate.py"):
        if not (task_dir / filename).is_file():
            raise FileNotFoundError(f"Required Shinka task file not found: {task_dir / filename}")

    results_dir = (args.results_dir or Path("shinka_results") / task_dir.name).expanduser().resolve()
    results_dir.mkdir(parents=True, exist_ok=True)
    model_url = f"local/hsi-opencode@{bridge_url}"
    command = [
        "shinka_run",
        "--task-dir", str(task_dir),
        "--results_dir", str(results_dir),
        "--num_generations", str(args.generations),
        "--max-evaluation-jobs", str(args.max_evaluation_jobs),
        "--max-proposal-jobs", str(args.max_proposal_jobs),
        "--set", f'evo.llm_models=["{model_url}"]',
        "--set", f'evo.meta_llm_models=["{model_url}"]',
        "--set", "evo.embedding_model=local/embeddinggemma@http://localhost:11434/v1",
    ]
    env = os.environ.copy()
    env["LOCAL_OPENAI_API_KEY"] = session_id
    completed = subprocess.run(command, env=env, check=False)
    if completed.returncode:
        raise SystemExit(completed.returncode)
    print(f"ShinkaEvolve results: {results_dir}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"HSI ShinkaEvolve error: {error}", file=sys.stderr)
        sys.exit(1)
