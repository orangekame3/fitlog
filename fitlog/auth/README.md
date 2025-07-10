# 認証ファイル配置ディレクトリ

このディレクトリには、Google Fit APIの認証に必要なファイルを配置します。

## 必要なファイル

### 1. client_secret.json
- Google Cloud Platform コンソールからダウンロードした認証情報ファイル
- OAuth 2.0 クライアント ID の認証情報が含まれます
- **重要**: このファイルは機密情報のため、gitignoreに追加済みです

### 2. token.json
- 初回認証時に自動生成されるトークンファイル
- 有効期限内であれば、再認証を求められません
- **重要**: このファイルも機密情報のため、gitignoreに追加済みです

## セットアップ手順

1. Google Cloud Platform コンソールで新しいプロジェクトを作成
2. Google Fit API を有効化
3. OAuth 2.0 クライアント ID を作成（アプリケーションタイプ: デスクトップアプリケーション）
4. 認証情報をダウンロードして、このディレクトリに `client_secret.json` として配置
5. 初回実行時に自動的に `token.json` が生成されます

## 必要なOAuth スコープ

```python
SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/fitness.sleep.read',
    'https://www.googleapis.com/auth/fitness.heart_rate.read'
]
```

## セキュリティ注意事項

- 認証ファイルは絶対に公開リポジトリにコミットしないでください
- 必要に応じて、定期的にトークンを更新してください
- 不要になった認証情報は適切に削除してください