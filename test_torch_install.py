#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PyTorch安装功能
使用新的安全安装方法测试PyTorch安装
"""

import sys
import logging
from pathlib import Path

# 导入我们的下载器
from webui_downloader import WebUIDownloader

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_torch_install():
    """测试PyTorch安装功能"""
    logger.info("🧪 测试PyTorch安装功能...")
    
    downloader = WebUIDownloader()
    
    # 确保虚拟环境存在
    if not downloader.create_virtual_environment():
        logger.error("❌ 无法创建或使用虚拟环境")
        return False
    
    # 测试安装PyTorch
    logger.info("🔥 测试安装 PyTorch...")
    success = downloader.install_torch_safely()
    
    if success:
        logger.info("✅ PyTorch安装测试成功")
        
        # 验证PyTorch是否可以正常导入
        try:
            venv_python = downloader.get_venv_python()
            import subprocess
            result = subprocess.run(
                [venv_python, '-c', 'import torch; print(f"PyTorch版本: {torch.__version__}")'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                logger.info(f"✅ PyTorch导入测试成功: {result.stdout.strip()}")
                return True
            else:
                logger.error(f"❌ PyTorch导入测试失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ PyTorch导入测试异常: {e}")
            return False
    else:
        logger.error("❌ PyTorch安装测试失败")
        return False

def test_package_detection():
    """测试包检测功能"""
    logger.info("🧪 测试包检测功能...")
    
    downloader = WebUIDownloader()
    
    # 测试检测已安装的包
    packages_to_check = ['pip', 'setuptools', 'wheel']
    
    for package in packages_to_check:
        is_installed = downloader.check_package_installed(package)
        logger.info(f"📦 {package}: {'✅ 已安装' if is_installed else '❌ 未安装'}")
    
    return True

def main():
    """主测试函数"""
    logger.info("🚀 开始测试PyTorch安装功能...")
    logger.info("⚠️  注意: PyTorch安装可能需要较长时间，请耐心等待...")
    
    tests = [
        ("包检测功能", test_package_detection),
        ("PyTorch安装", test_torch_install),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 运行测试: {test_name}")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} 通过")
            else:
                logger.error(f"❌ {test_name} 失败")
        except Exception as e:
            logger.error(f"❌ {test_name} 异常: {e}")
    
    logger.info(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        logger.info("🎉 所有测试通过！")
        return True
    else:
        logger.error("❌ 部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
