# fitlog

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

Google Fit APIからヘルスデータを取得し、InfluxDBに保存、Grafanaで可視化する個人用ヘルストラッキングシステムです。ローカルマシン（Raspberry Piなど）での動作を想定し、Cloudflare Tunnelを介した安全な外部アクセスが可能です。

## 特徴

- **データ収集**: Google Fit APIから自動的にヘルスデータを取得
  - 歩数と日次活動量
  - 体重の推移
  - 睡眠時間とパターン
  - 心拍数モニタリング
  - カロリー消費量
- **ストレージ**: InfluxDBによる時系列データ保存
- **可視化**: Grafanaによるインタラクティブダッシュボード
- **セキュリティ**: OAuth 2.0認証と安全な認証情報管理
- **自動化**: cronジョブによるスケジュール実行
- **外部アクセス**: Cloudflare Tunnelによる安全なリモートアクセス
- **デモモード**: テストやデモンストレーション用のモックデータ生成

## システム構成

### 本番モード
```
Google Fit API → Python取得スクリプト → InfluxDB (Docker) → Grafana (Docker) → Cloudflare Tunnel
```

### デモモード
```
モックデータジェネレーター → InfluxDB (Docker) → Grafana (Docker)
```

## クイックスタート

### 🎬 デモモード（認証不要）
```bash
# リポジトリをクローン
git clone <repository-url>
cd fitlog

# 自動モックデータ生成付きデモ
task demo

# 即座モックデータ付きクイックデモ
task demo-quick

# http://localhost:3000 でGrafanaにアクセス
# ログイン: admin / fitlogdemo2024
```

### オプション1: Dockerのみ（推奨）
```bash
# リポジトリをクローン
git clone <repository-url>
cd fitlog

# Dockerクイックセットアップ
task quickstart-docker

# コンテナでデータ取得実行
task docker-run-fetch-dry
```

### オプション2: ローカル開発
```bash
# リポジトリをクローン
git clone <repository-url>
cd fitlog

# ローカルクイックセットアップ（依存関係インストールとサービス起動）
task quickstart

# 利用可能なタスクを表示
task --list

# ヘルプを表示
task help
```

## 前提条件

- Docker & Docker Compose
- Python 3.8+
- [uv](https://github.com/astral-sh/uv) (Pythonパッケージマネージャー)
- [Task](https://taskfile.dev/) (タスクランナー)
- Google Cloud Platformアカウント

## インストール

1. **プロジェクトセットアップ**
   ```bash
   task setup
   ```

2. **環境設定**
   ```bash
   # 環境ファイルを作成
   cp .env.example .env
   # .envを編集して設定を調整
   ```

3. **Google Cloudセットアップ**
   - Google Cloud Consoleで新しいプロジェクトを作成
   - Google Fit APIを有効化
   - OAuth 2.0認証情報を作成（デスクトップアプリケーション）
   - 認証情報を`fitlog/auth/client_secret.json`としてダウンロード

4. **サービス開始**
   ```bash
   task docker-up
   ```

5. **初回認証**
   ```bash
   task run-dry
   ```

## 使用方法

### データ収集

#### Docker実行（推奨）
```bash
# データ取得（デフォルト: 過去24時間）
task docker-run-fetch

# 指定日数分のデータ取得
task docker-run-fetch-days DAYS=7

# ドライラン（データベースへの書き込みなし）
task docker-run-fetch-dry
```

#### モックデータ（テスト・デモ用）
```bash
# モックヘルスデータを生成
task mock

# 指定日数分のモックデータを生成
task mock DAYS=14

# データベースに書き込まずにモックデータを表示
task mock-dry

# Dockerでモックデータを生成
task docker-mock
```

#### ローカル実行
```bash
# データ取得（デフォルト: 過去24時間）
task run

# 指定日数分のデータ取得
task run-days DAYS=7

# ドライラン（データベースへの書き込みなし）
task run-dry

# InfluxDB接続テスト
task influx-test
```

### 開発

```bash
# コードフォーマット
task fmt

# リンターを実行
task lint

# テスト実行
task test

# カバレッジ付きテスト
task test-cov
```

### Docker管理

#### デモ環境
```bash
# デモサービス開始（自動モックデータ）
task demo-up

# デモサービス停止
task demo-down

# デモログ表示
task demo-logs

# デモ状態確認
task demo-status
```

#### 本番環境
```bash
# 本番サービス開始
task docker-up

# 本番サービス停止
task docker-down

# fitlogイメージビルド
task docker-build

# 本番ログ表示
task docker-logs

# 本番状態確認
task docker-status

# 本番コンテナでコマンド実行
task docker-exec CMD="python --version"
```

### モニタリング

```bash
# アプリケーションログを表示
task logs

# すべてのログを表示
task logs-all

# 認証リセット
task auth-reset
```

## 設定

### 環境変数

`.env`の主要変数：

```bash
# InfluxDB設定
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=your_secure_password
INFLUXDB_ORG=fitlog
INFLUXDB_BUCKET=health_data
INFLUXDB_ADMIN_TOKEN=your_admin_token

# Grafana設定
GRAFANA_ADMIN_PASSWORD=your_grafana_password

# データ収集設定
FETCH_DAYS_BACK=1
TIMEZONE=Asia/Tokyo
```

### OAuthスコープ

必要なGoogle Fit APIスコープ：

- `https://www.googleapis.com/auth/fitness.activity.read`
- `https://www.googleapis.com/auth/fitness.body.read`
- `https://www.googleapis.com/auth/fitness.sleep.read`
- `https://www.googleapis.com/auth/fitness.heart_rate.read`

## Grafanaダッシュボード

`http://localhost:3000`でGrafanaにアクセス：

1. 管理者認証情報でログイン
2. データソースとしてInfluxDBを追加：
   - URL: `http://influxdb:8086`
   - Organization: `fitlog`
   - Token: 管理者トークン
   - デフォルトバケット: `health_data`
3. 以下のダッシュボードを作成：
   - 日次歩数
   - 体重推移
   - 睡眠パターン
   - 心拍数モニタリング

## 自動化

自動データ収集の設定：

```bash
# cronジョブを設定
./scripts/setup_cron.sh

# または手動でcrontabに追加：
# 0 6 * * * /path/to/fitlog/scripts/run.sh
```

## 外部アクセス（オプション）

リモートアクセス用のCloudflare Tunnel設定：

1. Cloudflare Tunnelをインストール
2. `cloudflared/config.yml`を設定
3. トンネル実行: `cloudflared tunnel run fitlog`

## 開発ツール

このプロジェクトでは最新のPython開発ツールを使用：

- **[uv](https://github.com/astral-sh/uv)**: 高速Pythonパッケージマネージャー
- **[Ruff](https://github.com/astral-sh/ruff)**: 高速Pythonリンター・フォーマッター
- **[Ty](https://github.com/astral-sh/ty)**: 高速型チェッカー
- **[Task](https://taskfile.dev/)**: 開発ワークフロー用タスクランナー

## コントリビューション

1. リポジトリをフォーク
2. 機能ブランチを作成
3. 変更を実装
4. テスト実行: `task test`
5. リンター実行: `task lint`
6. コードフォーマット: `task fmt`
7. プルリクエストを送信

## セキュリティ

- 認証ファイル（`client_secret.json`、`token.json`）は絶対にコミットしない
- データベースアクセスには強固なパスワードを使用
- 環境変数を安全に管理
- APIトークンを定期的に更新

## トラブルシューティング

### よくある問題

1. **認証エラー**
   ```bash
   task auth-reset
   task run-dry
   ```

2. **データベース接続エラー**
   ```bash
   task docker-status
   task docker-logs
   ```

3. **データが取得できない**
   - Google Fitアプリでデータが記録されているか確認
   - OAuthスコープが正しいか確認
   - APIレート制限を確認

### ログ

```bash
# アプリケーションログを表示
task logs

# Dockerログを表示
task docker-logs

# 全履歴ログを表示
task logs-all
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

## サポート

問題や質問がある場合：

1. [トラブルシューティングセクション](#トラブルシューティング)を確認
2. アプリケーションログを確認
3. GitHubでIssueを作成

## 謝辞

- Google Fit API - ヘルスデータアクセス
- InfluxDB - 時系列データストレージ
- Grafana - データ可視化
- Cloudflare - セキュアトンネリング

---

📖 **詳細な日本語セットアップガイド**: [SETUP_ja.md](SETUP_ja.md)をご覧ください。

🌐 **English Documentation**: See [README.md](README.md) for English documentation.