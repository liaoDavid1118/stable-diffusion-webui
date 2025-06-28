@echo off
chcp 65001 >nul
echo 🎨 Stable Diffusion WebUI 依赖安装器
echo 支持断点续传和自动重试功能
echo 下载目录: D:\download
echo ========================================

REM 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

REM 检查Git是否可用
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Git，请先安装Git
    pause
    exit /b 1
)

REM 创建下载目录
if not exist "D:\download" (
    echo 📁 创建下载目录: D:\download
    mkdir "D:\download" 2>nul
    if %errorlevel% neq 0 (
        echo ⚠️  无法创建D:\download目录，将使用系统临时目录
    )
)

echo ✅ 环境检查通过
echo.

REM 运行Python安装脚本
echo 🚀 开始安装依赖...
python install_dependencies.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ 安装完成！
    echo.
    echo 📖 下一步操作：
    echo 1. 运行 webui.bat 启动WebUI
    echo 2. 或者手动激活虚拟环境后运行 python webui.py
    echo.
) else (
    echo.
    echo ❌ 安装失败，请检查错误信息
    echo 💡 提示：可以重新运行此脚本继续安装（支持断点续传）
    echo.
)

pause
