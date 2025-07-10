#!/bin/bash

# cron設定スクリプト
# このスクリプトは管理者権限で実行してください

# スクリプトの実行ディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== fitlog cron設定スクリプト ==="
echo "プロジェクトディレクトリ: $PROJECT_DIR"

# 現在のユーザーを取得
CURRENT_USER=$(whoami)
echo "現在のユーザー: $CURRENT_USER"

# cron設定内容
CRON_COMMAND="0 6 * * * $PROJECT_DIR/scripts/run.sh"

echo ""
echo "設定するcron:"
echo "$CRON_COMMAND"
echo ""

# 既存のcron設定を確認
echo "=== 現在のcron設定 ==="
crontab -l 2>/dev/null || echo "cron設定がありません"

echo ""
read -p "fitlogの自動実行を設定しますか？ (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 既存のcron設定を取得
    TEMP_CRON=$(mktemp)
    crontab -l 2>/dev/null > "$TEMP_CRON"
    
    # fitlogの設定がすでに存在するかチェック
    if grep -q "fitlog" "$TEMP_CRON"; then
        echo "既存のfitlog設定を更新します..."
        grep -v "fitlog" "$TEMP_CRON" > "${TEMP_CRON}.new"
        mv "${TEMP_CRON}.new" "$TEMP_CRON"
    fi
    
    # 新しい設定を追加
    echo "# fitlog: 毎日6時にヘルスデータを取得" >> "$TEMP_CRON"
    echo "$CRON_COMMAND" >> "$TEMP_CRON"
    
    # cron設定を更新
    crontab "$TEMP_CRON"
    
    # 一時ファイルを削除
    rm "$TEMP_CRON"
    
    echo "✅ cron設定を完了しました"
    echo ""
    echo "=== 更新後のcron設定 ==="
    crontab -l
    
else
    echo "cron設定をキャンセルしました"
fi

echo ""
echo "=== 手動でcron設定を行う場合 ==="
echo "以下のコマンドを実行してください:"
echo ""
echo "crontab -e"
echo ""
echo "そして以下の行を追加してください:"
echo "0 6 * * * $PROJECT_DIR/scripts/run.sh"
echo ""
echo "=== ログ確認方法 ==="
echo "tail -f $PROJECT_DIR/logs/fitlog_\$(date +%Y%m%d).log"