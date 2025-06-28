#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试下载程序的简化版本
只下载一个小的Git仓库来验证功能
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

def test_git_clone():
    """测试Git仓库克隆功能"""
    logger.info("🧪 测试Git仓库克隆功能...")
    
    downloader = WebUIDownloader()
    
    # 测试克隆一个小的仓库
    test_repo = {
        'url': 'https://github.com/AUTOMATIC1111/stable-diffusion-webui-assets.git',
        'commit': '6f7db241d2f8ba7457bac5ca9753331f0c266917',
        'dir': 'repositories/test-assets'
    }
    
    success = downloader.clone_git_repository('test-assets', test_repo)
    
    if success:
        logger.info("✅ Git仓库克隆测试成功")
        return True
    else:
        logger.error("❌ Git仓库克隆测试失败")
        return False

def test_venv_detection():
    """测试虚拟环境检测"""
    logger.info("🧪 测试虚拟环境检测...")
    
    downloader = WebUIDownloader()
    
    success = downloader.create_virtual_environment()
    
    if success:
        logger.info("✅ 虚拟环境检测/创建测试成功")
        return True
    else:
        logger.error("❌ 虚拟环境检测/创建测试失败")
        return False

def main():
    """主测试函数"""
    logger.info("🚀 开始测试下载程序...")
    
    tests = [
        ("虚拟环境检测", test_venv_detection),
        ("Git仓库克隆", test_git_clone),
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
