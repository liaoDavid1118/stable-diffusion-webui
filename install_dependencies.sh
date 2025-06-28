#!/bin/bash

echo "🎨 Stable Diffusion WebUI 依赖安装器"
echo "支持断点续传和自动重试功能"
echo "========================================"

# 检查Python是否可用
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ 未找到Python，请先安装Python 3.8或更高版本"
    exit 1
fi

# 优先使用python3
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# 检查Python版本
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python版本过低，需要3.8或更高版本，当前版本: $PYTHON_VERSION"
    exit 1
fi

# 检查Git是否可用
if ! command -v git &> /dev/null; then
    echo "❌ 未找到Git，请先安装Git"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 运行Python安装脚本
echo "🚀 开始安装依赖..."
$PYTHON_CMD install_dependencies.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 安装完成！"
    echo ""
    echo "📖 下一步操作："
    echo "1. 运行 ./webui.sh 启动WebUI"
    echo "2. 或者手动激活虚拟环境："
    echo "   source .venv/bin/activate"
    echo "   python webui.py"
    echo ""
else
    echo ""
    echo "❌ 安装失败，请检查错误信息"
    echo "💡 提示：可以重新运行此脚本继续安装（支持断点续传）"
    echo ""
fi
