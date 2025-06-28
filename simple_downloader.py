#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版下载程序
只下载基本的依赖，避免大包安装问题
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

def download_basic_dependencies():
    """下载基本依赖（不包括PyTorch）"""
    logger.info("🚀 开始下载基本依赖...")
    
    downloader = WebUIDownloader()
    
    # 检查系统要求
    if not downloader.check_python_version():
        return False
    
    if not downloader.check_git_available():
        return False
    
    # 创建虚拟环境
    if not downloader.create_virtual_environment():
        return False
    
    # 升级 pip
    if not downloader.upgrade_pip():
        return False
    
    # 安装基本的Python包（跳过PyTorch）
    basic_packages = {
        'requests': 'requests',
        'tqdm': 'tqdm',
        'pillow': 'Pillow',
        'numpy': 'numpy'
    }
    
    logger.info("📦 开始安装基本Python包...")
    for package_name, package_spec in basic_packages.items():
        if not downloader.install_python_package(package_name, package_spec):
            logger.error(f"❌ {package_name} 安装失败")
            return False
    
    # 克隆一个小的Git仓库进行测试
    test_repo = {
        'url': 'https://github.com/AUTOMATIC1111/stable-diffusion-webui-assets.git',
        'commit': '6f7db241d2f8ba7457bac5ca9753331f0c266917',
        'dir': 'repositories/stable-diffusion-webui-assets'
    }
    
    logger.info("📥 开始克隆测试仓库...")
    if not downloader.clone_git_repository('stable-diffusion-webui-assets', test_repo):
        logger.error("❌ 测试仓库克隆失败")
        return False
    
    logger.info("🎉 基本依赖下载完成！")
    return True

def main():
    """主函数"""
    logger.info("🎨 简化版 Stable Diffusion WebUI 下载程序")
    logger.info("=" * 50)
    logger.info("📋 本程序将下载基本依赖（不包括PyTorch）")
    logger.info("📋 适用于测试下载功能是否正常")
    logger.info("=" * 50)
    
    try:
        success = download_basic_dependencies()
        
        if success:
            logger.info("🎉 基本依赖下载完成！")
            logger.info("💡 接下来可以:")
            logger.info("   1. 运行 python test_torch_install.py 测试PyTorch安装")
            logger.info("   2. 运行 python webui_downloader.py 下载完整依赖")
            sys.exit(0)
        else:
            logger.error("❌ 基本依赖下载失败！")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n⚠️ 用户中断下载")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 程序执行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
