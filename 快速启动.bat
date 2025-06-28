@echo off
chcp 65001 >nul
title Stable Diffusion WebUI - 快速启动

echo.
echo ========================================
echo    🚀 Stable Diffusion WebUI 快速启动
echo ========================================
echo.

:: 检查虚拟环境
if not exist "venv\Scripts\python.exe" (
    echo ❌ 错误: 虚拟环境不存在
    pause
    exit /b 1
)

echo 🎯 使用推荐设置启动...
echo 📍 启动参数: --medvram --autolaunch
echo 🌐 访问地址: http://127.0.0.1:7860
echo 💡 浏览器将自动打开
echo.
echo ⏹️  按 Ctrl+C 可停止服务
echo ========================================
echo.

:: 启动WebUI (使用中等显存模式，自动打开浏览器)
venv\Scripts\python.exe webui.py --medvram --autolaunch

echo.
echo ========================================
echo 🛑 WebUI 已停止运行
echo 💡 如需重新启动，请再次运行此脚本
echo ========================================
pause
