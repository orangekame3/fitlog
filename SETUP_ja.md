# fitlog セットアップガイド

Google Fit APIからヘルスデータを取得し、InfluxDBとGrafanaで可視化するシステムの完全セットアップ手順です。

### クイックスタート

```bash
# 全自動セットアップ
task quickstart

# 利用可能なタスクを確認
task --list

# ヘルプを表示
task help
```

## 前提条件

- Docker & Docker Compose
- Python 3.8+
- uv (Pythonパッケージマネージャー)
- Task (タスクランナー)
- Google Cloud Platformアカウント

## 1. プロジェクトのセットアップ

```bash
# リポジトリをクローン
git clone <repository-url>
cd fitlog

# プロジェクトセットアップ（推奨）
task setup

# または手動でuvを使用
uv sync --dev
```

## 2. Google Cloud Platform設定

### 2.1 プロジェクトの作成とAPI有効化

1. [Google Cloud Console](https://console.cloud.google.com/)にログイン
2. 新しいプロジェクトを作成
3. 以下のAPIを有効化：
   - Google Fit API
   - Google People API（オプション）

### 2.2 OAuth 2.0認証情報の作成

1. 「APIとサービス」→「認証情報」→「認証情報を作成」→「OAuth クライアント ID」に移動
2. アプリケーションタイプ: **デスクトップアプリケーション**
3. 名前: `fitlog-client`（任意の名前）
4. 作成後、JSONファイルをダウンロード
5. `fitlog/auth/client_secret.json`として保存

## 3. 環境設定

```bash
# 環境設定ファイルを作成
cp .env.example .env

# 環境設定ファイルを編集
nano .env
```

必要な環境変数を設定：

```env
# InfluxDB設定
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=your_secure_password_here
INFLUXDB_ORG=fitlog
INFLUXDB_BUCKET=health_data
INFLUXDB_ADMIN_TOKEN=your_admin_token_here
INFLUXDB_URL=http://localhost:8086

# Grafana設定
GRAFANA_ADMIN_PASSWORD=your_grafana_password_here

# データ取得設定
FETCH_DAYS_BACK=1
TIMEZONE=Asia/Tokyo
```

## 4. Dockerサービスの起動

```bash
# InfluxDBとGrafanaを起動
task docker-up

# サービス状態を確認
task docker-status

# ログを確認
task docker-logs
```

## 5. 初回認証

```bash
# 初回実行（OAuth認証フローが開始される）
task run-dry

# ブラウザでGoogle認証画面が開きます
# 認証後、token.jsonが自動生成されます
```

## 6. データ取得テスト

```bash
# テストデータ取得
task run-days DAYS=7

# 通常実行
task run

# InfluxDB接続テスト
task influx-test

# ドライラン（データベースに書き込まない）
task run-dry
```

## 7. 自動実行の設定

```bash
# cron設定スクリプトを実行
./scripts/setup_cron.sh

# または手動でcronを設定
crontab -e
# 以下の行を追加:
# 0 6 * * * /path/to/fitlog/scripts/run.sh
```

## 8. Grafanaダッシュボードの設定

1. ブラウザで `http://localhost:3000` にアクセス
2. 管理者認証情報でログイン（admin / .envで設定したパスワード）
3. データソースとしてInfluxDBを追加：
   - URL: `http://influxdb:8086`
   - Organization: `fitlog`
   - Token: .envで設定した管理者トークン
   - Bucket: `health_data`

## 9. Cloudflare Tunnelの設定（オプション）

外部アクセス用：

```bash
# Cloudflare Tunnelをインストール
# https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/

# トンネルを作成
cloudflared tunnel create fitlog

# cloudflared/config.ymlを設定
# トンネルを起動
cloudflared tunnel run fitlog
```

## トラブルシューティング

### よくある問題

1. **認証エラー**
   - `client_secret.json`が正しい場所にあるか確認
   - Google Cloud ConsoleでAPIが有効化されているか確認

2. **InfluxDB接続エラー**
   - Dockerコンテナが起動しているか確認
   - .env設定が正しいか確認

3. **データが取得できない**
   - Google Fitアプリでデータが記録されているか確認
   - OAuthスコープが正しいか確認

### ログの確認

```bash
# アプリケーションログを確認
task logs

# すべてのログを表示
task logs-all

# Dockerログを確認
task docker-logs
```

## セキュリティ注意事項

- 認証ファイル（`client_secret.json`、`token.json`）は絶対にコミットしない
- .envファイルは機密情報を含むため適切に管理する
- 本番環境では強力なパスワードとトークンを使用する

## サポート

問題が発生した場合：

1. ログを確認
2. Dockerコンテナの状態を確認
3. Google Cloud Consoleの設定を確認
4. 環境変数の設定を確認

## 開発者向けコマンド

```bash
# コードフォーマット
task fmt

# コードチェック
task lint

# テスト実行
task test

# テスト（カバレッジ付き）
task test-cov

# 認証リセット
task auth-reset

# 一時ファイル削除
task clean
```

## 主要なタスク一覧

| タスク | 説明 |
|--------|------|
| `task setup` | 初期セットアップ |
| `task quickstart` | クイックスタート |
| `task run` | データ取得実行 |
| `task run-dry` | ドライラン実行 |
| `task docker-up` | Docker起動 |
| `task docker-down` | Docker停止 |
| `task logs` | ログ確認 |
| `task fmt` | コードフォーマット |
| `task lint` | コードチェック |
| `task test` | テスト実行 |
| `task clean` | 一時ファイル削除 |

詳細は `task --list` で確認できます。