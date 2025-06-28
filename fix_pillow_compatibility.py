#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复Pillow兼容性问题
解决multiline_textsize方法缺失的问题
"""

import subprocess
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_pillow_version():
    """修复Pillow版本兼容性问题"""
    logger.info("🔧 修复Pillow版本兼容性问题...")
    
    venv_python = Path("venv/Scripts/python.exe")
    
    if not venv_python.exists():
        logger.error("❌ 虚拟环境不存在")
        return False
    
    try:
        # 降级Pillow到兼容版本
        cmd = f"{venv_python} -m pip install 'Pillow<10.0.0' --force-reinstall"
        logger.info("📦 安装兼容版本的Pillow...")
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        if result.returncode == 0:
            logger.info("✅ Pillow版本修复成功")
            return True
        else:
            logger.error(f"❌ Pillow修复失败: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 修复过程异常: {e}")
        return False

def check_pillow_version():
    """检查Pillow版本"""
    logger.info("📊 检查Pillow版本...")
    
    venv_python = Path("venv/Scripts/python.exe")
    
    try:
        cmd = f"{venv_python} -c \"import PIL; print('Pillow版本:', PIL.__version__)\""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        if result.returncode == 0:
            logger.info(f"✅ {result.stdout.strip()}")
            return True
        else:
            logger.error(f"❌ 无法获取Pillow版本: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 检查版本异常: {e}")
        return False

def test_multiline_textsize():
    """测试multiline_textsize方法是否可用"""
    logger.info("🧪 测试multiline_textsize方法...")
    
    venv_python = Path("venv/Scripts/python.exe")
    
    test_code = """
try:
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new('RGB', (100, 100), 'white')
    draw = ImageDraw.Draw(img)
    
    # 测试multiline_textsize方法
    if hasattr(draw, 'multiline_textsize'):
        print('✅ multiline_textsize方法可用')
    else:
        print('❌ multiline_textsize方法不可用')
        print('💡 建议使用textbbox方法替代')
        
except Exception as e:
    print(f'❌ 测试失败: {e}')
"""
    
    try:
        cmd = f"{venv_python} -c \"{test_code}\""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        if result.returncode == 0:
            logger.info(f"测试结果: {result.stdout.strip()}")
            return "multiline_textsize方法可用" in result.stdout
        else:
            logger.error(f"❌ 测试失败: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 测试异常: {e}")
        return False

def main():
    """主函数"""
    print("🔧 Pillow兼容性修复工具")
    print("=" * 50)
    
    # 1. 检查当前版本
    check_pillow_version()
    
    # 2. 测试方法可用性
    if not test_multiline_textsize():
        logger.info("🔄 需要修复Pillow版本...")
        
        # 3. 修复版本
        if fix_pillow_version():
            logger.info("🔄 重新测试...")
            test_multiline_textsize()
            check_pillow_version()
        else:
            logger.error("❌ 修复失败")
            return False
    else:
        logger.info("✅ Pillow版本正常，无需修复")
    
    print("\n" + "=" * 50)
    print("🎉 修复完成！")
    print("💡 现在可以重启WebUI测试提示词矩阵功能:")
    print("   venv\\Scripts\\python.exe webui.py")
    
    return True

if __name__ == "__main__":
    main()
