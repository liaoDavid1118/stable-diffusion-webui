@echo off
chcp 65001 >nul
title Stable Diffusion WebUI 启动器

echo.
echo ========================================
echo    🎨 Stable Diffusion WebUI 启动器
echo ========================================
echo.

:: 检查虚拟环境
if not exist "venv\Scripts\python.exe" (
    echo ❌ 错误: 虚拟环境不存在
    echo 💡 请先运行安装程序
    pause
    exit /b 1
)

:: 检查主模型
if not exist "models\Stable-diffusion\*.safetensors" (
    if not exist "models\Stable-diffusion\*.ckpt" (
        echo ⚠️  警告: 未找到Stable Diffusion模型
        echo 💡 WebUI将尝试自动下载模型
        echo.
    )
)

echo 🚀 正在启动 Stable Diffusion WebUI...
echo 📍 项目目录: %CD%
echo 🐍 Python环境: venv\Scripts\python.exe
echo.

:: 设置环境变量
set COMMANDLINE_ARGS=
set PYTHON=venv\Scripts\python.exe
set GIT=git
set VENV_DIR=venv

:: 启动WebUI
echo 🌟 启动中，请稍候...
echo 💡 启动完成后将自动打开浏览器
echo 🌐 访问地址: http://127.0.0.1:7860
echo.
echo ⏹️  按 Ctrl+C 可停止服务
echo ========================================
echo.

venv\Scripts\python.exe webui.py

echo.
echo ========================================
echo 🛑 WebUI 已停止运行
echo 💡 如需重新启动，请再次运行此脚本
echo ========================================
pause
