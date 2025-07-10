#!/bin/bash

# fitlog データ取得スクリプト
# cron での実行を想定

# スクリプトの実行ディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# ログディレクトリを作成
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

# ログファイルのパス
LOG_FILE="$LOG_DIR/fitlog_$(date +%Y%m%d).log"

# 実行時刻をログに記録
echo "$(date '+%Y-%m-%d %H:%M:%S') - fitlog データ取得開始" >> "$LOG_FILE"

# プロジェクトディレクトリに移動
cd "$PROJECT_DIR"

# 環境変数の読み込み
if [ -f ".env" ]; then
    source .env
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - エラー: .env ファイルが見つかりません" >> "$LOG_FILE"
    exit 1
fi

# uvがインストールされているか確認
if ! command -v uv &> /dev/null; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - エラー: uvがインストールされていません" >> "$LOG_FILE"
    exit 1
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') - uvを使用してPythonスクリプトを実行" >> "$LOG_FILE"

# Docker コンテナの状態を確認
if ! docker compose ps | grep -q "fitlog-influxdb.*Up"; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - エラー: InfluxDBコンテナが起動していません" >> "$LOG_FILE"
    exit 1
fi

# データ取得実行
echo "$(date '+%Y-%m-%d %H:%M:%S') - データ取得を開始" >> "$LOG_FILE"

# Pythonスクリプトを実行
if uv run fitlog-fetch --days 1 >> "$LOG_FILE" 2>&1; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - データ取得完了" >> "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - エラー: データ取得に失敗しました" >> "$LOG_FILE"
    exit 1
fi

# 古いログファイルを削除（30日より古い）
find "$LOG_DIR" -name "fitlog_*.log" -type f -mtime +30 -delete

echo "$(date '+%Y-%m-%d %H:%M:%S') - fitlog データ取得完了" >> "$LOG_FILE"