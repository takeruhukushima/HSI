# ローカルモデルの利用方法

このガイドでは、OpenCode で **ローカル LLM（大規模言語モデル）** を使う方法を、IT エンジニアリングに不慣れな方でも迷わないよう、ステップバイステップで解説します。

---

## ローカルモデルとは？（研究者向けの簡単な説明）

**ローカルモデル** とは、自分のパソコン上で直接動作する AI モデルのことです。ChatGPT や Claude のようにインターネット上のサーバーを使うのではなく、**あなたの PC の CPU / GPU でモデルが動きます**。

イメージとして：

> 💡 **「自分のパソコンの中に ChatGPT をインストールする」** イメージです。

### ローカルモデルのメリット

| メリット | 説明 |
|---|---|
| **完全無料** | API 使用料が一切かかりません。何度使っても追加料金なし |
| **オフラインで使える** | インターネットがなくても動作します |
| **データが外部に出ない** | 研究データや論文を外部サーバーに送信する必要がありません |
| **プライバシー保護** | 機密性の高い研究データも安心して扱えます |

### ローカルモデルのデメリット

| デメリット | 説明 |
|---|---|
| **性能は PC 次第** | 高性能なモデルほど多くのメモリと GPU が必要です |
| **セットアップが必要** | ソフトウェアのインストールやモデルのダウンロードが必要です |
| **応答がやや遅い** | クラウドの超大規模モデルよりは応答が遅くなることがあります |

---

## 全体の流れ

ローカルモデルを使えるようになるまでの大まかな流れは以下の通りです：

```
1. Ollama をインストール（モデル実行エンジン）
2. 使いたいモデルを Ollama でダウンロード
3. OpenCode にローカルモデルの設定を追加
4. 動作確認
```

OpenCode は **Ollama** と **LM Studio** の 2 つのローカルモデルツールに対応しています。このガイドでは、より簡単な **Ollama** を主に解説します。

---

## Step 1: Ollama をインストールする

**Ollama** は、ローカルで LLM を動かすためのツールです。ターミナルだけでなく、GUI アプリも提供されています。

### 方法 A: 公式サイトからインストール（最も簡単・推奨）

1. **Ollama の公式サイト** をブラウザで開く：  
   [https://ollama.com](https://ollama.com)

2. **「Download」** ボタンをクリック

3. お使いの OS を選択：
   - **macOS**: `macOS` をクリック → `.zip` ファイルがダウンロードされる
   - **Windows**: `Windows` をクリック → インストーラがダウンロードされる

4. ダウンロードしたファイルを開いて、画面の指示に従ってインストール

5. インストールが完了すると、メニューバー（画面右上）に **Ollama のアイコン**（アルパカのマーク）が表示されていれば成功です。

### 方法 B: ターミナルからインストール

ターミナル操作に慣れている場合は、以下のコマンド一発でインストールできます：

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh
```

### インストールの確認

ターミナルで以下のコマンドを実行し、バージョンが表示されれば成功です：

```bash
ollama --version
```

```
例: ollama version 0.x.x
```

---

## Step 2: モデルをダウンロードする

Ollama がインストールできたら、実際に使うモデルをダウンロードします。

### おすすめのモデル

すべて **Gemma 4**（Google DeepMind 製、2026年4月2日リリース、Apache 2.0 ライセンス）です。

| モデル名 | サイズ (Ollama Q4) | 必要メモリ (RAM) | 推奨メモリ | 特徴 |
|---|---|---|---|---|
| **gemma4:e2b** | ~7.2GB | 8GB 以上 | 16GB 以上 | エッジ向け、画像/音声/動画対応、128K コンテキスト、マルチモーダル |
| **gemma4:e4b** | ~9.6GB | 12GB 以上 | 16GB 以上 | 軽量マルチモーダル、画像/音声対応、128K コンテキスト、Arena 1229 |
| **gemma4:26b** | ~18GB | 24GB 以上 | 32GB 以上 | MoE（25.2B中3.8B活性）、コスパ最高、256K コンテキスト、Arena 1441、コーディング高精度 |
| **gemma4:31b** | ~20GB | 24GB 以上 | 32GB 以上 | 最高性能 Dense、256K コンテキスト、Arena テキスト #3、コード ELO 2150 |

> **「どれを選べばいいかわからない」場合**：
> - まずは **gemma4:e4b**（~9.6GB）を試す。軽量マルチモーダルで 128K コンテキスト
> - 余裕があれば **gemma4:26b**（~18GB）にステップアップ。MoE でコスパ最高
> - Mac でメモリが 32GB 以上あるなら **gemma4:31b**（~20GB）もおすすめ

### モデルのダウンロード

ターミナルで以下のコマンドを実行します（例として gemma4:e4b をダウンロード）：

```bash
ollama pull gemma4:e4b
```

ダウンロードの進行状況が表示されます。モデルのサイズによって数分〜数十分かかります。

> **コツ**: `pull` の代わりに `run` を使うと、ダウンロード→起動を一度に行えます：
> ```bash
> ollama run gemma4:e4b
> ```
> 初回だけダウンロードが走り、以降はすぐに起動します。

### ダウンロード済みモデルの確認

```bash
ollama list
```

ダウンロードしたモデルの一覧が表示されます。

---

## Step 3: OpenCode にローカルモデルを設定する

Ollama が動くようになったら、OpenCode から使えるように設定します。

### 3.1 OpenCode を起動して `/model` を使う（推奨・簡単）

```bash
opencode
```

OpenCode が起動したら、以下のコマンドを入力します：

```
/model
```

利用可能なモデル一覧が表示されるので、使いたいモデルを選択してください。これで設定完了です。

### 3.2 opencode.json に直接設定する（手動）

設定ファイルに直接書くこともできます。

プロジェクトのルートフォルダにある `opencode.json` を開き、以下のように追記します：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "gemma4:e4b": {
          "name": "Gemma 4 E4B"
        },
        "gemma4:26b": {
          "name": "Gemma 4 26B"
        }
      }
    }
  }
}
```

> **`baseURL` とは？**: Ollama が API を公開しているアドレスです。Ollama は OpenAI 互換の API を `http://localhost:11434/v1` で提供しています。

> **ツール呼び出しが機能しない場合**: Ollama 側の `num_ctx` が不足している可能性があります。モデルごとに `num_ctx`（コンテキスト長）を増やすと改善します。詳しくは [モデルの設定オプション](#モデルの設定オプション) を参照してください。

### 3.3 デフォルトのモデルを設定する

OpenCode は `provider` に指定された最初のモデルをデフォルトとして使用します。明示的にデフォルトを指定したい場合は `"model"` フィールドを使います：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "ollama/gemma4:e4b",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "gemma4:e4b": {
          "name": "Gemma 4 E4B"
        },
        "gemma4:26b": {
          "name": "Gemma 4 26B"
        }
      }
    }
  }
}
```

`"model": "ollama/gemma4:e4b"` の部分がデフォルトの指定です。  
形式は **`プロバイダID/モデルID`** です。ここでは `ollama` がプロバイダ ID、`gemma4:e4b` がモデル ID になります。

---

## Step 4: 動作確認

### 4.1 Ollama が起動していることを確認

Ollama はバックグラウンドで動作しています。メニューバーにアルパカのアイコンが表示されていれば OK です。

もし動いていない場合は、ターミナルで以下のコマンドを実行して起動します：

```bash
ollama serve
```

### 4.2 OpenCode でモデルを切り替える

OpenCode 起動中に、以下のコマンドを入力するとモデル一覧が表示されます：

```
/models
```

使いたいモデルを選択してください。

### 4.3 テスト

以下のように入力して、応答が返ってくるか確認しましょう：

```
「こんにちは」と日本語で返事をしてください。
```

正常に応答が返ってくれば設定完了です！

> ローカルモデルはクラウドの大規模モデルより応答が遅い場合があります。数秒〜数十秒待つこともありますが、正常な動作です。

---

## Step 5: モデルのバリアント（動作モード）を変える

OpenCode では、同じモデルでも「推論の深さ」を変えることができます。これは **バリアント** と呼ばれます。

### 5.1 組み込みバリアント

ローカルモデルでは、以下のようなバリアントが利用できます（プロバイダにより異なります）：

| プロバイダ | バリアント | 説明 |
|---|---|---|
| Ollama / LM Studio | `low` | 応答が速いが精度はやや低い |
| Ollama / LM Studio | `high` | 時間がかかるが精度が高い |

### 5.2 バリアントの切り替え

OpenCode 起動中に、以下のキーを押すとバリアントを切り替えられます：

- **デフォルトのキーバインド**: 後述のキーバインド設定が必要な場合があります

または、設定ファイルで直接指定することもできます：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "gemma4:e4b": {
          "name": "Gemma 4 E4B",
          "options": {
            "num_ctx": 16384,
            "temperature": 0.7
          }
        }
      }
    }
  }
}
```

よく使われるオプション：

| オプション | 説明 | デフォルト値 |
|---|---|---|
| `num_ctx` | コンテキスト長（一度に処理する文章の長さ） | 2048 |
| `temperature` | 出力のランダム性（0=決定的、1=多様） | 0.8 |
| `top_p` | 出力の多様性を制御 | 0.9 |

> **`temperature` のイメージ**: 0 に近いと毎回同じような回答に、1 に近いと毎回異なる回答になります。研究では 0.3〜0.7 がおすすめです。

---

## 発展編1: LM Studio を使う

**LM Studio** は、Ollama と同じくローカルモデルを動かすツールですが、**完全な GUI（画面操作）** で使える点が特徴です。

### LM Studio のインストール

1. **LM Studio の公式サイト** をブラウザで開く：  
   [https://lmstudio.ai](https://lmstudio.ai)

2. **「Download」** ボタンをクリック

3. お使いの OS に合ったバージョンをダウンロードしてインストール

### LM Studio でモデルをダウンロード

1. LM Studio を起動
2. 画面上部の検索バーでモデル名を検索（例: `gemma-4-e4b`）
3. ダウンロードしたいモデルをクリック
4. **「Download」** ボタンをクリック

### LM Studio のサーバーを起動

1. 左側の **「Local Server」** アイコン（<-> のようなマーク）をクリック
2. ダウンロードしたモデルを選択
3. **「Start Server」** ボタンをクリック
4. サーバーが起動し、`http://localhost:1234` で待ち受け状態になります

### OpenCode の設定

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "lmstudio/gemma-4-e4b",
  "provider": {
    "lmstudio": {
      "baseUrl": "http://localhost:1234",
      "models": {
        "gemma-4-e4b": {
          "type": "chat"
        }
      }
    }
  }
}
```

> **注意**: LM Studio のデフォルトのポート番号は **1234** です（Ollama は 11434）。間違えないようにしましょう。

---

## 発展編2: 複数のモデルを使い分ける

研究用途に応じてモデルを切り替えると便利です。

### 設定例

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "ollama/gemma4:26b",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "gemma4:e4b": {
          "name": "Gemma 4 E4B"
        },
        "gemma4:26b": {
          "name": "Gemma 4 26B"
        },
        "gemma4:31b": {
          "name": "Gemma 4 31B"
        }
      }
    }
  }
}
```

### 使い分けの指針

| タスク | おすすめモデル |
|---|---|
| **簡単な質問・チャット** | gemma4:e4b（軽量・高速、マルチモーダル） |
| **コード作成・データ解析** | gemma4:26b（MoE 高精度、256K コンテキスト） |
| **論文執筆支援** | gemma4:31b（最高品質 Dense） |
| **複雑な推論・計画** | gemma4:31b（Arena テキスト #3、コード ELO 2150） |

OpenCode 起動中に `/models` と入力すれば、いつでもモデルを切り替えられます。

---

## モデルの設定オプション

### グローバル設定 vs モデルごとの設定

`provider.ollama.models.モデルID.options` でモデルごとに細かく設定できます：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "gemma4:e4b": {
          "name": "Gemma 4 E4B",
          "options": {
            "num_ctx": 16384,
            "temperature": 0.5
          }
        },
        "gemma4:26b": {
          "name": "Gemma 4 26B",
          "options": {
            "num_ctx": 32768,
            "temperature": 0.7
          }
        }
      }
    }
  }
}
```

### カスタムバリアントを定義する

同じモデルに異なる設定を複数持たせることもできます：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "gemma4:26b": {
          "name": "Gemma 4 26B",
          "variants": {
            "precise": {
              "temperature": 0.2,
              "num_ctx": 16384
            },
            "creative": {
              "temperature": 0.9,
              "num_ctx": 32768
            }
          }
        }
      }
    }
  }
}
```

---

## トラブルシューティング

### Ollama が見つからない / 接続できない

```
Error: connect ECONNREFUSED http://localhost:11434
```

**原因**: Ollama のサーバーが起動していません。

**解決策**:
```bash
# Ollama サーバーを起動
ollama serve
```

または、メニューバーの Ollama アイコンをクリックして、**「Ollama is running」** と表示されているか確認してください。

### モデルが応答しない / エラーになる

```
Error: model "gemma4:e4b" not found
```

**原因**: 指定したモデルがダウンロードされていません。

**解決策**:
```bash
# ダウンロード済みモデルの一覧を確認
ollama list

# モデルをダウンロード
ollama pull gemma4:e4b
```

### メモリ不足のエラー

```
Error: out of memory
```

**原因**: 使用しているモデルが PC のメモリ容量を超えています。

**解決策**:
1. より小さいモデルを使う（例: gemma4:26b → gemma4:e4b → gemma4:e2b）
2. 他のアプリケーションを終了してメモリを空ける
3. `num_ctx` を減らす（例: 4096 → 2048）

### OpenCode がローカルモデルを認識しない

**原因**: `opencode.json` の設定が正しくない可能性があります。

**解決策**:
```bash
# 設定ファイルの構文チェック
opencode config validate
```

エラーが出た場合は、JSON のカンマや括弧の対応を確認してください。

### 応答が遅すぎる

**原因**: モデルが大きい、または PC の性能が十分でない。

**解決策**:
1. より小さいモデルを使う（推奨: gemma4:e4b）
2. `num_ctx` を減らす（デフォルト 2048 から 1024 に）
3. GPU が使える設定になっているか確認（Ollama は自動的に GPU を使います）
4. PC のメモリ使用量を確認し、余計なアプリを閉じる

---

## 用語集

| 用語 | わかりやすい説明 |
|---|---|
| **LLM** | Large Language Model（大規模言語モデル）。ChatGPT などの脳みそにあたる AI |
| **ローカルモデル** | 自分のパソコン上で動作する AI モデル |
| **Ollama** | ローカルで LLM を手軽に動かすためのツール |
| **LM Studio** | GUI 操作でローカル LLM を動かすツール |
| **プロバイダ** | AI モデルを提供するもの。OpenCode では Ollama や OpenAI などが該当 |
| **モデル ID** | モデルを一意に識別する名前。例: `gemma4:e4b` |
| **温度（temperature）** | 出力の多様性を制御するパラメータ。低いほど決定的な回答に |
| **コンテキスト長（num_ctx）** | モデルが一度に処理できる最大トークン数 |
| **バリアント** | 同じモデルの異なる設定パターン |

---

## 次のステップ

- [MCP の利用方法](./MCP.md) — 外部ツール連携で OpenCode をさらに拡張
- [効果的なプロンプトの書き方](../tips/EFFECTIVE_PROMPTING.md) — より良い結果を得るコツ
- [最初の一歩チュートリアル](../tutorial/FIRST_STEPS.md) — OpenCode の基本的な使い方
