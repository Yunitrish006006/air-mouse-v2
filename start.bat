@echo off
title Air Mouse Controller
echo ================================
echo     Air Mouse Controller
echo ================================
echo.
echo 正在啟動 Air Mouse...
echo.
echo 使用方式:
echo - GUI模式 (推薦): python app.py
echo - 高效能模式: python app.py --no-preview
echo - 測試模式: python test_ui.py
echo.
echo 按任意鍵啟動GUI模式...
pause >nul

cd /d "%~dp0"
python app.py

echo.
echo 程式已結束，按任意鍵退出...
pause >nul
