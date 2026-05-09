# OpenCode CLI のインストールガイド

このガイドでは、科学研究で OpenCode CLI を使うための**環境構築手順**を、IT エンジニアリングに不慣れな方でも迷わないよう、ステップバイステップで解説します。

---

## 全体の流れ

OpenCode を使えるようになるまでの大まかな流れは以下の通りです：

```
1. ターミナルの準備（WezTerm を推奨）
2. nix のインストール（パッケージ管理ツール）
3. OpenCode CLI のインストール（nix を使用）
4. 初期設定（API プロバイダの選択）
5. 動作確認
```

---

## Step 1: ターミナルの準備

OpenCode を使うには**ターミナル**（キーボードで命令を打ち込む画面）が必要です。お使いの OS に合わせて準備してください。

### macOS の場合

#### 方法 A: 標準のターミナル.app（簡単）

1. **Spotlight 検索**を開く（画面右上の虫眼鏡アイコン、または `Cmd + Space`）
2. 「ターミナル」と入力
3. 「ターミナル.app」をクリック

#### 方法 B: WezTerm（推奨・高機能）

WezTerm は画像の表示やファイルのドラッグ＆ドロップができる高機能なターミナルです。

1. **nix** をインストールしてから（Step 2 を先に進む）、以下のコマンドを実行：

```bash
nix profile install nixpkgs#wezterm
```

2. または、公式サイト https://wezfurlong.org/wezterm/ からダウンロードしてインストール

### Windows の場合

Windows では **WSL2（Windows Subsystem for Linux）** を使って Linux 環境を用意します。

#### 1.1 WSL2 のインストール

1. スタートメニューを右クリック → **「Windows PowerShell（管理者）」** または **「ターミナル（管理者）」** を選択
2. 以下のコマンドを入力して Enter：

```powershell
wsl --install
```

> このコマンド一つで WSL2 と Ubuntu Linux が自動的にインストールされます。

3. インストールが完了したら PC を再起動
4. 再起動後、自動的に Ubuntu の初期設定画面が開くので、**ユーザー名とパスワード**を設定

#### 1.2 WezTerm のインストール（推奨）

WSL2 上の OpenCode を快適に使うには WezTerm が便利です。

1. 公式サイト https://wezfurlong.org/wezterm/ から Windows 用インストーラをダウンロード
2. インストーラを実行してインストール
3. WezTerm を起動し、画面上部のメニューから **「Ubuntu」** を選択（WSL2 環境に接続）

> **これ以降の操作は WezTerm を使うことをおすすめします。**

---

## Step 2: nix のインストール

**nix** は macOS / Linux / Windows（WSL2）のすべてで使えるパッケージマネージャです。ソフトウェアのインストールやバージョン管理を簡単に行えます。

> nix は Homebrew（Mac 用）のようなものですが、Windows でも使える点が強みです。

### macOS の場合

WezTerm（またはターミナル）で以下のコマンドを実行：

```bash
sh <(curl -L https://nixos.org/nix/install)
```

インストール中にいくつか質問されます：
- `Continue?` → `y`（はい）と入力して Enter
- macOS のパスワードを求められたら、ログインパスワードを入力（画面に文字は表示されませんが、入力はされています）

インストールが完了したら、ターミナルをいったん閉じて、再度開いてください。

### Windows（WSL2）の場合

1. WezTerm を起動し、**Ubuntu** セッションを開く
2. 以下のコマンドを実行：

```bash
sh <(curl -L https://nixos.org/nix/install)
```

3. インストール中に `Continue?` と聞かれたら `y` と入力
4. インストール完了後、以下のコマンドで nix を有効化：

```bash
source ~/.nix-profile/etc/profile.d/nix.sh
```

> 毎回 `source` を実行するのが面倒な場合は、以下のコマンドを一度だけ実行すると次回から自動で有効化されます：
> ```bash
> echo 'source ~/.nix-profile/etc/profile.d/nix.sh' >> ~/.bashrc
> ```

### インストールの確認

以下のコマンドを実行し、バージョンが表示されれば成功です：

```bash
nix --version
```

```
例: nix (Nix) 2.x.x
```

---

## Step 3: OpenCode CLI のインストール

nix を使って OpenCode をインストールします。**この手順は macOS / Windows 共通です。**

### 3.1 nix でインストール

WezTerm（またはターミナル）で以下のコマンドを実行：

```bash
nix profile install nixpkgs#opencode
```

### 3.2 インストールの確認

以下のコマンドを実行し、バージョンが表示されれば成功です：

```bash
opencode --version
```

```
例: opencode/1.x.x
```

### 3.3 `command not found` が出た場合

nix のパスが正しく通っていない可能性があります。以下を試してください：

**macOS の場合：**
```bash
source ~/.zshrc
```

**Windows（WSL2）の場合：**
```bash
source ~/.bashrc
```

---

## Step 4: OpenCode の初期設定

### 4.1 API プロバイダの選択

OpenCode を初めて起動すると、使用する AI モデルのプロバイダを選択するよう促されます。

**おすすめの選択肢：**

| プロバイダ | 特徴 | 料金 |
|---|---|---|
| **OpenCode Zen** | セットアップが最も簡単。初期クレジットあり | 従量課金 |
| **OpenAI（ChatGPT Plus/Pro）** | ChatGPT の契約があれば追加料金なし | 月額 $20+ |
| **GitHub Copilot** | Copilot の契約があれば追加料金なし | 月額 $10+ |
| **Anthropic（Claude）** | Claude の契約があれば追加料金なし | 従量課金または月額 $20+ |

API キーをお持ちでない場合や、まずは無料で試したい場合は、[ローカルモデルの利用方法](./LOCAL_MODEL.md)を参照してください。

### 4.2 API キーの設定

推奨する方法は、OpenCode TUI（ターミナル UI）内で `/connect` コマンドを使うことです。

```bash
opencode
```

起動後に以下のコマンドを入力します：

```
/connect
```

画面の指示に従って、プロバイダを選択し、認証を完了してください。

または、環境変数を使って直接 API キーを設定することもできます：

```bash
# 例: Anthropic の場合
export ANTHROPIC_API_KEY="your-api-key-here"

# 例: OpenAI の場合
export OPENAI_API_KEY="your-api-key-here"
```

これを毎回入力するのが面倒な場合は、設定ファイルに追記します：

**macOS の場合（`~/.zshrc` に追記）：**
```bash
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.zshrc
```

**Windows（WSL2）の場合（`~/.bashrc` に追記）：**
```bash
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
```

> **注意**: API キーは秘密情報です。Git にコミットしたり、他人と共有したりしないでください。

---

## Step 5: 動作確認

### 5.1 研究プロジェクトのフォルダに移動

```bash
cd /path/to/your/research/project
```

> `cd` は「移動する」という意味のコマンドです。ターミナルで `cd` のあとに半角スペースを入れ、移動したいフォルダのパスを入力してください。

### 5.2 OpenCode を起動

```bash
opencode
```

初回起動時は自動的に初期化が行われます。画面下部に `>` の入力欄が表示されれば成功です。

### 5.3 簡単な質問を試す

以下のように入力して、OpenCode が応答するか試してみましょう：

```
このプロジェクトの README.md を読んで、概要を教えてください。
```

応答が返ってくれば、セットアップ完了です！

![OpenCode 起動画面](../images/opencode-launch.png)

---

## トラブルシューティング

### `command not found: opencode`

インストール後、パスが通っていない可能性があります。以下を試してください：

**macOS の場合：**
```bash
source ~/.zshrc
```

**Windows（WSL2）の場合：**
```bash
source ~/.bashrc
```

それでも解決しない場合は、ターミナルを再起動してください。

### nix 関連のエラー

nix のインストールに問題がある場合：

```bash
# nix の状態を確認
nix --version

# 問題がある場合は再インストール
sh <(curl -L https://nixos.org/nix/install) --daemon
```

### その他の問題

[OpenCode 公式トラブルシューティング](https://dev.opencode.ai/docs/troubleshooting/)（英語）も参照してください。

---

## 別のインストール方法

nix 以外にも以下の方法でインストールできます。状況に応じて選んでください。

### インストールスクリプト（簡単）

```bash
curl -fsSL https://opencode.ai/install | bash
```

### Homebrew（macOS）

すでに Homebrew を使っている場合：

```bash
brew install anomalyco/tap/opencode
```

### npm

Node.js がインストールされている環境では：

```bash
npm install -g opencode-ai
```
