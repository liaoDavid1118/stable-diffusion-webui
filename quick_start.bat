@echo off
chcp 65001 >nul
title Stable Diffusion WebUI 快速启动

echo.
echo 🎨 Stable Diffusion WebUI 快速启动
echo ====================================
echo 📋 检查安装状态并启动WebUI
echo ====================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\python.exe" (
    echo ❌ 虚拟环境不存在，请先运行下载程序
    pause
    exit /b 1
)

echo ✅ 虚拟环境已就绪

REM 检查PyTorch
echo 🔍 检查PyTorch安装...
venv\Scripts\python.exe -c "import torch; print(f'PyTorch版本: {torch.__version__}'); print(f'CUDA可用: {torch.cuda.is_available()}')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ PyTorch未正确安装
    echo 💡 请运行: python webui_downloader.py
    pause
    exit /b 1
)

echo ✅ PyTorch已安装

REM 检查主要仓库
if not exist "repositories\stable-diffusion-webui-assets" (
    echo ❌ 缺少必要的代码仓库
    echo 💡 请运行: python webui_downloader.py
    pause
    exit /b 1
)

echo ✅ 代码仓库已就绪

echo.
echo 🚀 启动 Stable Diffusion WebUI...
echo ⚠️  首次启动可能需要下载额外的依赖，请耐心等待
echo.

REM 激活虚拟环境并启动WebUI
call venv\Scripts\activate.bat
python webui.py %*

if %errorlevel% neq 0 (
    echo.
    echo ❌ WebUI启动失败
    echo.
    echo 💡 可能的解决方案:
    echo 1. 运行 python webui_downloader.py 完成依赖安装
    echo 2. 手动安装缺失的依赖包
    echo 3. 检查错误日志
    echo.
) else (
    echo.
    echo 🎉 WebUI已成功启动！
    echo 📱 请在浏览器中访问显示的地址（通常是 http://127.0.0.1:7860）
    echo.
)

pause
