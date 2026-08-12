# HSI Skills と Plugin の利用方法

HSIはプロジェクトローカルなAgent SkillsとOpenCode Pluginで、PaperQA、
ShinkaEvolve、プロテオミクス解析、PowerPoint生成を提供します。MCP
サーバーの設定や常駐プロセスは不要です。

## 構成

```text
.opencode/
├── plugins/hsi.ts
└── skills/
    ├── hsi-paperqa/
    ├── hsi-shinka/
    ├── hsi-proteomics/
    └── hsi-pptx/
```

`SKILL.md`が利用条件と手順をOpenCodeへ教え、各` scripts/`のCLIが実処理を
行います。`hsi.ts`はPaperQAとShinkaEvolveの生成リクエストをOpenCodeの
子セッションへ中継します。APIキーを外部プロセスへ渡すことはありません。

## 準備

```bash
nix profile install nixpkgs#uv nixpkgs#nodejs_22 nixpkgs#pnpm
ollama pull embeddinggemma
pnpm install --dir .opencode
```

OpenCodeをこのリポジトリで再起動するとPluginとSkillsが自動検出されます。

## PaperQA

OpenCodeへ次のように依頼します。

```text
refディレクトリの論文をPaperQAで調べて、PaperQA2とは何か引用付きで答えて。
```

生成LLMはOpenCodeで現在選択中の任意のProviderとモデルを使用し、Embeddingは
Ollamaの`embeddinggemma`を使用します。両者は同じ会話を再入実行するのでは
なく、OpenCodeが認証済みの独立した子セッションです。

PaperQA設定内の`openai/hsi-opencode`は、LiteLLMからローカルBridgeまでの
通信形式を表す名前です。実際の生成ProviderをOpenAIへ固定する設定では
ありません。OpenCodeでOllama、Anthropic、OpenAIなどへモデルを切り替えると、
次のHSI実行からその`providerID/modelID`が子セッションへ引き継がれます。

PaperQAの通常のToolSelector Agentを使用します。PaperQAのindex、回答履歴、
その他の状態はプロジェクトルートの`.pqa/`へ保存されます。

## ShinkaEvolve

```text
/path/to/taskをShinkaEvolveで1世代だけ試して。
```

タスクには`initial.py`と`evaluate.py`が必要です。生成はHSI Bridge、コード
類似度EmbeddingはOllamaを使用します。

## プロテオミクスとPowerPoint

各Skillの`SKILL.md`にCLI例があります。重いPython依存関係は`uv run`で
オンデマンドに解決され、PPTX依存関係は`.opencode/package.json`で管理します。

## 確認

```bash
opencode debug config
opencode debug skill
ollama list
```

設定変更後はOpenCodeを終了して再起動してください。

---

## 次のステップ

- [最初の一歩チュートリアル](../tutorial/FIRST_STEPS.md) — OpenCode の基本的な使い方
- [ローカルモデルの利用方法](./LOCAL_MODEL.md) — Ollama でローカルLLMを動かす
