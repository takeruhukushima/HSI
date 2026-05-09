# OpenCode Desktop のインストールガイド

OpenCode Desktop は、ターミナルを使わずに**GUI アプリケーション**として OpenCode を利用できるベータ版です。
ターミナル操作に不慣れな方は、こちらから始めるのもよいでしょう。

> **注意**: Desktop 版はベータ版です。本格的な研究利用には CLI 版をおすすめします。

---

## Step 1: ダウンロード

以下の公式ダウンロードページから、お使いの OS に合ったインストーラをダウンロードしてください。

[公式ダウンロードページ](https://opencode.ai/download)

### macOS の場合

| Mac の種類 | ダウンロードするもの |
|---|---|
| Apple Silicon（M1 / M2 / M3 / M4） | macOS (Apple Silicon) |
| Intel 製 CPU | macOS (Intel) |

> **Mac の種類の確認方法**: 画面左上のマーク → 「この Mac について」→「チップ」に表示されます

### Windows の場合

| ダウンロードするもの |
|---|
| Windows (x64) |

### Linux の場合

| お使いの環境 | ダウンロードするもの |
|---|---|
| Debian / Ubuntu | Linux (.deb) |
| Fedora / RHEL | Linux (.rpm) |

---

## Step 2: インストール

### macOS の場合

1. ダウンロードした `.dmg` ファイルをダブルクリックして開く
2. 表示されたウインドウで **OpenCode** アイコンを **Applications** フォルダにドラッグ＆ドロップ
3. **「アプリケーション」** フォルダから OpenCode を起動

> 初回起動時に「インターネットからダウンロードされたアプリケーションです」という警告が出た場合は、「開く」をクリックしてください。

### Windows の場合

1. ダウンロードした `.exe` ファイルをダブルクリック
2. 「はい」をクリックしてインストーラを実行
3. インストーラの指示に従ってインストール
4. スタートメニューから OpenCode を起動

### Linux の場合

```bash
# Debian / Ubuntu の場合
sudo dpkg -i opencode-desktop-x.x.x-linux-x64.deb

# Fedora / RHEL の場合
sudo rpm -i opencode-desktop-x.x.x-linux-x64.rpm
```

または、nix パッケージマネージャを使っている場合：

```bash
nix profile install nixpkgs#opencode-desktop
```

---


## Step 3: 動作確認

アプリが起動し、メッセージ入力欄に以下のように入力して応答が返ってくれば成功です：

```
Hello! これから研究でお世話になります。よろしくお願いします。
```

---

## CLI 版との違い

| 機能 | Desktop | CLI（ターミナル） |
|---|---|---|
| GUI 操作 | ✅ マウス操作可能 | ❌ キーボード操作中心 |
| Plan / Build モード | ✅ | ✅ |
| 画像ドラッグ＆ドロップ | ✅ | ✅（対応ターミナルのみ） |
| MCP サーバー連携 | ✅ | ✅ |
| 自動アップデート | ✅ | ✅（設定による） |
| 複数セッション管理 | ✅ | ✅ |
| SSH / VPS での利用 | ❌ | ✅ |

研究で本格的に使う場合は CLI 版の方がカスタマイズ性が高いですが、Desktop 版でも十分な機能が使えます。

---

## 次のステップ

- [最初の一歩チュートリアル](../tutorial/FIRST_STEPS.md) — 実際に研究で使ってみる
- [CLI 版のインストール](../cli/INSTALL.md) — より高度な機能が必要な場合
