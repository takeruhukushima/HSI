# MCP（Model Context Protocol）の利用方法

このガイドでは、OpenCode に **MCP（Model Context Protocol）** を追加して、プロテオミクス解析・PaperQA・ShinkaEvolve・PowerPoint生成を利用する方法を解説します。

---

## MCP とは？

MCP は OpenCode に**外部ツールを追加する拡張スロット**です。
本リポジトリでは以下の2つの MCP サーバーを設定しています：

| MCP サーバー | 言語 / 実行 | 提供ツール |
|---|---|---|
| **python-mcp** | Python + uv | PaperQA（RAG質問応答）、ShinkaEvolve（進化アルゴリズム）、プロテオミクス解析（Volcano Plot / Clustermap / PO解析） |
| **tsx-mcp** | TypeScript + pnpm + tsx | PowerPoint生成（pptxgenjs） |

---

## 事前準備

### uv のインストール（Python用パッケージマネージャ）

```bash
# nix を使う場合（推奨）
nix profile install nixpkgs#uv

# 確認
uv --version
```

nix 以外の方法：`curl -LsSf https://astral.sh/uv/install.sh | sh`

### pnpm のインストール（Node.js用パッケージマネージャ）

```bash
# nix を使う場合（推奨）
nix profile install nixpkgs#nodejs_22 nixpkgs#pnpm

# 確認
pnpm --version
```

---

## Step 1: 依存関係をインストールする

### python-mcp の依存関係

```bash
cd mcp-scripts/python-mcp

# コア機能のみ（プロテオミクス / ShinkaEvolve）
uv sync

# PaperQAも使う場合
uv sync --group paperqa

# 全機能（PaperQA + プロテオミクスPO解析）
uv sync --group all
```

### tsx-mcp の依存関係

```bash
cd mcp-scripts/tsx-mcp
pnpm install
```

---

## Step 2: 設定を確認する

プロジェクトルートの `opencode.json` に以下の設定が書かれています：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "python-mcp": {
      "type": "local",
      "command": ["uv", "run", "--directory", "mcp-scripts/python-mcp", "server.py"],
      "enabled": true
    },
    "tsx-mcp": {
      "type": "local",
      "command": ["pnpm", "--prefix", "mcp-scripts/tsx-mcp", "exec", "tsx", "index.ts"],
      "enabled": true
    }
  }
}
```

### 設定の説明

| 項目 | 説明 |
|---|---|
| `python-mcp` / `tsx-mcp` | MCP サーバーの名前。プロンプトでこの名前を使って呼び出します |
| `type: "local"` | 自分のPC上で動作するサーバーであることを示します |
| `command` | スクリプトの実行方法。**配列（`[]`）** で指定します |
| `enabled: true` | 起動時に自動的に有効にします |

> **注意**: `command` は必ず配列で書いてください。`"uv run ..."` のような文字列指定はできません。

### このリポジトリだけで使う場合（プロジェクトローカル）

上記の `opencode.json` をプロジェクトルートに置けば、**このリポジトリでのみ** MCP が有効になります。

### 全リポジトリで使う場合（グローバル設定）

全てのプロジェクトで同じ MCP を使いたい場合は、プロジェクトの `opencode.json` ではなく、**OpenCode のグローバル設定ファイル** に記述します。

グローバル設定ファイルの場所：

| OS | パス |
|---|---|
| **macOS / Linux** | `~/.config/opencode/opencode.json` |
| **Windows** | `%USERPROFILE%\.config\opencode\opencode.json` |

ただし、グローバル設定に書く場合は `command` のパスが **絶対パス** か、**ホームからの相対パス** である必要があります。

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "python-mcp": {
      "type": "local",
      "command": ["uv", "run", "--directory", "/Users/yourname/HSI/mcp-scripts/python-mcp", "server.py"],
      "enabled": true
    },
    "tsx-mcp": {
      "type": "local",
      "command": ["pnpm", "--prefix", "/Users/yourname/HSI/mcp-scripts/tsx-mcp", "exec", "tsx", "index.ts"],
      "enabled": true
    }
  }
}
```

> `yourname` は自分のユーザー名に置き換えてください。

OpenCode は **プロジェクトローカル → グローバル** の順で設定をマージします。同じ名前の MCP サーバーが両方にある場合はプロジェクトローカルが優先されます。

---

## Step 3: 使ってみる

OpenCode を起動して、以下のように指示します：

### PaperQA（論文RAG質問応答）

```
python-mcp の paperqa_query ツールを使って、
「gemma4のE4Bモデルの性能は？」
という質問を mcp-scripts/python-mcp/scripts/paperqa_tool.py
に対して実行してください。
target_dir は /path/to/papers です。
```

### ShinkaEvolve（進化アルゴリズム）

```
python-mcp の shinka_experiment ツールを実行してください。
experiment_name は test_run、config_dir は ./shinka_configs です。
```

### プロテオミクス解析（Volcano Plot）

```
python-mcp の volcano_plot を実行。
file_path は raw_data/sample.xlsx、
groups は {"groupA": ["A1","A2","A3"], "groupB": ["B1","B2","B3"]}、
comparisons は [["groupA","groupB"]] です。
```

### PowerPoint生成

```
tsx-mcp の create_pptx でスライドを作って。
タイトルは「研究発表」、スライドは2枚。
1枚目は「背景」、内容は「本研究の背景を説明します」
2枚目は「結果」、内容は「実験結果を示します」
output は presentation.pptx で保存して。
```

---

## トラブルシューティング

### `uv: command not found`

uv がインストールされていません。事前準備の手順でインストールしてください。

### `pnpm: command not found`

pnpm がインストールされていません。`nix profile install nixpkgs#pnpm` を実行してください。

### ModuleNotFoundError / ImportError

依存関係が不足しています。以下のコマンドでインストールしてください：

```bash
cd mcp-scripts/python-mcp && uv sync --group all
```

### MCP サーバーが応答しない

`opencode.json` の構文を確認：

```bash
python3 -c "import json; json.load(open('opencode.json'))"
```

エラーが出なければ設定は正しいです。

---

## 用語集

| 用語 | 説明 |
|---|---|
| **MCP** | Model Context Protocol。OpenCode が外部ツールと連携するための規格 |
| **uv** | Python の高速なパッケージマネージャ |
| **pnpm** | Node.js の高速なパッケージマネージャ |
| **tsx** | TypeScript ファイルを直接実行するツール |
| **PaperQA** | ローカルLLMを使ったRAGシステム。論文フォルダに対して質問応答ができる |
| **ShinkaEvolve** | 進化アルゴリズムを用いた自動アルゴリズム改善ツール |
| **PO解析** | Protein Ontology解析。ESM-2でタンパク質埋め込みを生成し、アンカータンパク質との類似度を計算 |

---

## 次のステップ

- [最初の一歩チュートリアル](../tutorial/FIRST_STEPS.md) — OpenCode の基本的な使い方
- [ローカルモデルの利用方法](./LOCAL_MODEL.md) — Ollama でローカルLLMを動かす
