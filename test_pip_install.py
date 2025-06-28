#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试pip安装功能
先安装一个小的包来验证pip安装是否正常工作
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

def test_pip_install():
    """测试pip安装功能"""
    logger.info("🧪 测试pip安装功能...")
    
    downloader = WebUIDownloader()
    
    # 确保虚拟环境存在
    if not downloader.create_virtual_environment():
        logger.error("❌ 无法创建或使用虚拟环境")
        return False
    
    # 测试安装一个小的包
    logger.info("📦 测试安装 requests 包...")
    success = downloader.install_python_package('requests', 'requests')
    
    if success:
        logger.info("✅ pip安装测试成功")
        return True
    else:
        logger.error("❌ pip安装测试失败")
        return False

def test_pip_upgrade():
    """测试pip升级"""
    logger.info("🧪 测试pip升级...")
    
    downloader = WebUIDownloader()
    
    success = downloader.upgrade_pip()
    
    if success:
        logger.info("✅ pip升级测试成功")
        return True
    else:
        logger.error("❌ pip升级测试失败")
        return False

def main():
    """主测试函数"""
    logger.info("🚀 开始测试pip安装功能...")
    
    tests = [
        ("pip升级", test_pip_upgrade),
        ("pip安装", test_pip_install),
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
