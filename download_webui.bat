@echo off
chcp 65001 >nul
title Stable Diffusion WebUI 下载程序

echo.
echo 🎨 Stable Diffusion WebUI 下载程序
echo ====================================
echo 支持断点续传和自动重试功能
echo 下载目录: D:\download
echo 虚拟环境: venv
echo ====================================
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查Git是否可用
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Git，请先安装Git
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM 显示Python和Git版本
echo ✅ 环境检查通过
for /f "tokens=*" %%i in ('python --version') do echo 🐍 %%i
for /f "tokens=*" %%i in ('git --version') do echo 📦 %%i
echo.

REM 创建下载目录
if not exist "D:\download" (
    echo 📁 创建下载目录: D:\download
    mkdir "D:\download" 2>nul
    if %errorlevel% neq 0 (
        echo ⚠️  无法创建D:\download目录，将使用系统临时目录
    )
)

REM 运行下载程序
echo 🚀 开始下载...
echo.
python webui_downloader.py

REM 检查下载结果
if %errorlevel% == 0 (
    echo.
    echo 🎉 下载完成！
    echo.
    echo 📋 接下来的步骤:
    echo 1. 运行 webui-user.bat 启动 WebUI
    echo 2. 首次启动可能需要额外下载模型文件
    echo 3. 在浏览器中访问 http://127.0.0.1:7860
    echo.
) else (
    echo.
    echo ❌ 下载失败！
    echo 请检查错误信息并重试
    echo.
    echo 💡 常见解决方案:
    echo 1. 检查网络连接
    echo 2. 运行 python webui_downloader.py --reset 重置进度
    echo 3. 运行 python webui_downloader.py --status 查看状态
    echo.
)

pause
