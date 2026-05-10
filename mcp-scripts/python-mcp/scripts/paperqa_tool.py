import os
import traceback
from pathlib import Path
from paperqa import Settings, ask

# wezterm が設定する AGENT=1 が pydantic-settings に拾われるのを防ぐ
os.environ.pop("AGENT", None)

async def run_paperqa_query(query: str, target_dir: str) -> str:
    """
    Ollama (gemma4-E4B) と Embeddingモデル (embeddinggemma) を使用して
    指定されたディレクトリの論文から回答を生成します。
    Vision機能（画像・図表読み取り）も有効化し、完全にローカルで動作させます。
    """
    
    # Gemma4の設定 (テキスト、Vision、およびエンリッチメント用)
    local_llm_config = {
        "model_list": [
            {
                "model_name": "ollama/gemma4:e4b",
                "litellm_params": {
                    "model": "ollama/gemma4:e4b",
                    "api_base": "http://localhost:11434",
                    "timeout": 600,
                },
            }
        ]
    }
    
    # Embeddingモデルの設定
    local_embedding_config = {
        "model_list": [
            {
                "model_name": "ollama/embeddinggemma:latest",
                "litellm_params": {
                    "model": "ollama/embeddinggemma:latest",
                    "api_base": "http://localhost:11434",
                },
            }
        ]
    }

    # インデックスディレクトリの設定 (論文ディレクトリの親階層に作成)
    index_dir = str(Path(target_dir).parent / "pqa_indexes")
    
    # Ollamaを使用するため、LiteLLMが鍵を要求する場合に備えてダミーを設定
    os.environ["OPENAI_API_KEY"] = "sk-no-key"
    
    # Settingsの構築
    settings = Settings(
        llm="ollama/gemma4:e4b",
        llm_config=local_llm_config,
        summary_llm="ollama/gemma4:e4b",
        summary_llm_config=local_llm_config,
        
        embedding="ollama/embeddinggemma:latest",
        embedding_config=local_embedding_config,

        # 画像読み取り（Vision）の設定
        vision_llm="ollama/gemma4:e4b",
        vision_llm_config=local_llm_config,
        
        # パース設定: マルチモーダルはオフ（画像処理でgemma4がタイムアウトするため）
        parsing={
            "multimodal": False,
            "page_size_limit": 50000,
        },
        
        use_doc_details=False,
        disable_doc_valid_check=True,
        
        # 回答設定: エビデンスチャンク数を絞ってLLM負荷を軽減
        answer={
            "evidence_k": 3,
            "evidence_summary_length": "about 30 words",
            "answer_max_sources": 3,
        },
        
        # エージェントとインデックスの設定
        agent={
            "rebuild_index": True,
            "search_count": 3,
            "agent_llm": "ollama/gemma4:e4b",
            "agent_llm_config": local_llm_config,
            "index": {
                "paper_directory": target_dir,
                "index_directory": index_dir,
            }
        }
    )

    try:
        # 質問の実行 (非同期で待機)
        answer_response = await ask(query, settings=settings)
        # 文脈から最適な回答フィールドを選択
        return getattr(answer_response, "answer", getattr(answer_response, "formatted_answer", str(answer_response)))
    except Exception as e:
        error_details = traceback.format_exc()
        return f"PaperQA Error Detail:\n{error_details}"
