#!/bin/bash
set -e

echo ""
echo "============================================"
echo "  GrantDraft セットアップ"
echo "============================================"
echo ""

# Docker が起動しているか確認
if ! docker info > /dev/null 2>&1; then
    echo "[エラー] Docker が起動していません。"
    echo ""
    echo "Docker Desktop をインストール・起動してから再実行してください。"
    echo "ダウンロード: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

echo "[1/4] Docker を検出しました ✓"
echo ""

# .env がなければ作成
if [ ! -f .env ]; then
    echo "[2/4] 環境設定ファイルを作成中..."
    cp .env.example .env
else
    echo "[2/4] 環境設定ファイルは既にあります ✓"
fi
echo ""

# Docker Compose でビルド＆起動
echo "[3/4] アプリケーションを起動中...（初回は数分かかります）"
echo ""
docker compose -f docker-compose.dev.yml up -d --build

echo ""
echo "[4/4] データベースを準備中..."
sleep 10

docker compose -f docker-compose.dev.yml exec -T api alembic -c /alembic.ini upgrade head

echo ""
echo "============================================"
echo "  起動完了！"
echo "============================================"
echo ""
echo "  ダッシュボード:  http://localhost:3000"
echo "  API:            http://localhost:8000"
echo "  API ドキュメント: http://localhost:8000/docs"
echo ""
echo "  ※ 初回はデータが空です。"
echo "  ※ ダッシュボードの「データ同期」ボタンを押すと"
echo "    補助金データが取得されます。"
echo ""
echo "  終了するには ./stop.sh を実行してください。"
echo "============================================"
echo ""

# ブラウザを自動で開く
if command -v open > /dev/null 2>&1; then
    open http://localhost:3000
elif command -v xdg-open > /dev/null 2>&1; then
    xdg-open http://localhost:3000
fi
