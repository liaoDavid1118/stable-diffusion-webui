@echo off
chcp 65001 >nul
title Stable Diffusion WebUI 启动器 (优化版)

echo.
echo ========================================
echo  🚀 Stable Diffusion WebUI 优化启动器
echo ========================================
echo.

:: 检查虚拟环境
if not exist "venv\Scripts\python.exe" (
    echo ❌ 错误: 虚拟环境不存在
    pause
    exit /b 1
)

echo 🎯 选择启动模式:
echo.
echo [1] 标准模式 (推荐)
echo [2] 高性能模式 (启用xformers)
echo [3] 中等显存模式 (4-8GB显存) - 推荐
echo [4] 低显存模式 (少于4GB显存)
echo [5] 调试模式 (显示详细日志)
echo [6] 安静模式 (减少警告信息)
echo [7] 界面修复模式 (解决显示问题)
echo.

set /p choice="请选择模式 (1-6): "

:: 设置基础参数
set COMMANDLINE_ARGS=
set PYTHON=venv\Scripts\python.exe

:: 根据选择设置参数
if "%choice%"=="1" (
    echo 🎯 启动模式: 标准模式
    set COMMANDLINE_ARGS=--autolaunch
)

if "%choice%"=="2" (
    echo 🎯 启动模式: 高性能模式
    set COMMANDLINE_ARGS=--xformers --autolaunch
)

if "%choice%"=="3" (
    echo 🎯 启动模式: 中等显存模式
    set COMMANDLINE_ARGS=--medvram --autolaunch
)

if "%choice%"=="4" (
    echo 🎯 启动模式: 低显存模式
    set COMMANDLINE_ARGS=--lowvram --autolaunch
)

if "%choice%"=="5" (
    echo 🎯 启动模式: 调试模式
    set COMMANDLINE_ARGS=--debug --autolaunch
)

if "%choice%"=="6" (
    echo 🎯 启动模式: 安静模式
    set COMMANDLINE_ARGS=--medvram --autolaunch --skip-version-check --no-hashing
)

echo.
echo 🚀 正在启动 WebUI...
echo 📍 启动参数: %COMMANDLINE_ARGS%
echo 🌐 访问地址: http://127.0.0.1:7860
echo.
echo ⏹️  按 Ctrl+C 可停止服务
echo ========================================
echo.

:: 启动WebUI
venv\Scripts\python.exe webui.py %COMMANDLINE_ARGS%

echo.
echo ========================================
echo 🛑 WebUI 已停止运行
echo ========================================
pause
