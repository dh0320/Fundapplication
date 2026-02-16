@echo off
chcp 65001 >nul
title GrantDraft - 起動中...

echo.
echo ============================================
echo   GrantDraft セットアップ
echo ============================================
echo.

:: Docker Desktop が起動しているか確認
docker info >nul 2>&1
if errorlevel 1 (
    echo [エラー] Docker Desktop が起動していません。
    echo.
    echo Docker Desktop をインストール・起動してから再実行してください。
    echo ダウンロード: https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

echo [1/4] Docker Desktop を検出しました ✓
echo.

:: .env がなければ作成
if not exist .env (
    echo [2/4] 環境設定ファイルを作成中...
    copy .env.example .env >nul
) else (
    echo [2/4] 環境設定ファイルは既にあります ✓
)
echo.

:: Docker Compose でビルド＆起動
echo [3/4] アプリケーションを起動中...（初回は数分かかります）
echo.
docker compose -f docker-compose.dev.yml up -d --build

if errorlevel 1 (
    echo.
    echo [エラー] 起動に失敗しました。
    echo Docker Desktop が正常に動作しているか確認してください。
    pause
    exit /b 1
)

echo.
echo [4/4] データベースを準備中...
timeout /t 10 /nobreak >nul

docker compose -f docker-compose.dev.yml exec -T api alembic -c /alembic.ini upgrade head

echo.
echo ============================================
echo   起動完了！
echo ============================================
echo.
echo   ダッシュボード:  http://localhost:3000
echo   API:            http://localhost:8000
echo   API ドキュメント: http://localhost:8000/docs
echo.
echo   ※ 初回はデータが空です。
echo   ※ ダッシュボードの「データ同期」ボタンを押すと
echo     補助金データが取得されます。
echo.
echo   終了するには stop.bat を実行してください。
echo ============================================
echo.

:: ブラウザを自動で開く
start http://localhost:3000

pause
