@echo off
chcp 65001 >nul
title GrantDraft - 停止中...

echo.
echo ============================================
echo   GrantDraft を停止します
echo ============================================
echo.

docker compose -f docker-compose.dev.yml down

echo.
echo 停止完了しました。
echo.
pause
