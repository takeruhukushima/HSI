import asyncio
import os
from pathlib import Path

async def run_shinka_experiment(experiment_name: str, config_dir: str) -> str:
    """
    ShinkaEvolveを使用して、gemma4-E4Bとembeddinggemmaを用いて実験を実行します。
    """
    
    # タスクディレクトリの解決
    task_dir = Path(config_dir) / experiment_name
    if not task_dir.exists():
        return f"Error: Task directory '{task_dir}' was not found."

    # 結果出力ディレクトリの解決
    results_root = Path("./shinka_results")
    results_dir = results_root / experiment_name
    results_dir.mkdir(parents=True, exist_ok=True)

    # ShinkaEvolveのLLM/Embedding設定を上書き
    cmd = [
        "shinka_run",
        "--task-dir", str(task_dir),
        "--results_dir", str(results_dir),
        "--num_generations", "10",
        "--set", 'evo.llm_models=["local/gemma4:e4b@http://localhost:11434/v1"]',
        "--set", "evo.embedding_model=local/embeddinggemma@http://localhost:11434/v1",
        "--set", 'evo.meta_llm_models=["local/gemma4:e4b@http://localhost:11434/v1"]'
    ]

    try:
        # asyncio.create_subprocess_exec を使って非同期でコマンドを実行
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # コマンドの終了を待機し、標準出力とエラー出力を受け取る
        stdout, stderr = await process.communicate()

        # 終了コード (returncode) が 0 なら成功
        if process.returncode == 0:
            return (f"ShinkaEvolve experiment '{experiment_name}' finished successfully.\n\n"
                    f"Results are saved in: {results_dir.absolute()}\n\n"
                    f"Output summary:\n{stdout.decode('utf-8')}")
        else:
            return (f"ShinkaEvolve experiment failed with exit code {process.returncode}.\n\n"
                    f"Error detail:\n{stderr.decode('utf-8')}\n\n"
                    f"Output captured:\n{stdout.decode('utf-8')}")

    except Exception as e:
        return f"Error occurred during ShinkaEvolve execution: {str(e)}"
