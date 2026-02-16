# GrantDraft

補助金情報ダッシュボード — JグランツAPIとe-Rad公募一覧からデータを収集し、一覧表示・検索・フィルタリングを提供するWebアプリケーション。

## 構成

- **apps/web** — Next.js 14 (App Router) + TypeScript フロントエンド
- **apps/api** — Python 3.12 + FastAPI バックエンドAPI
- **workers/scraper** — データ収集ワーカー（JGrants API連携 / e-Radスクレイパー）
- **alembic** — DBマイグレーション

## セットアップ

```bash
# 環境変数ファイルをコピー
cp .env.example .env

# Docker起動
make up

# マイグレーション実行
make migrate

# データ収集
make scrape-all
```

## 主要コマンド

| コマンド | 説明 |
|---|---|
| `make up` | 全サービス起動 |
| `make down` | 全サービス停止 |
| `make migrate` | DBマイグレーション実行 |
| `make scrape-jgrants` | JグランツAPIからデータ取得 |
| `make scrape-erad` | e-Radからデータ取得 |
| `make scrape-all` | 全ソースからデータ取得 |
| `make test-api` | バックエンドテスト実行 |

## アクセス

- フロントエンド: http://localhost:3000
- API: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs
