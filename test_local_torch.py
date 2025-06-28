#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试从本地安装PyTorch
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

def check_local_torch_files():
    """检查本地PyTorch文件"""
    logger.info("🔍 检查本地PyTorch文件...")
    
    script_path = Path(__file__).parent.absolute()
    torch_wheels = list(script_path.glob("torch-*.whl"))
    
    if torch_wheels:
        for wheel in torch_wheels:
            logger.info(f"📦 找到PyTorch文件: {wheel.name}")
            logger.info(f"   文件大小: {wheel.stat().st_size / 1024 / 1024:.1f} MB")
        return True
    else:
        logger.error("❌ 未找到本地PyTorch wheel文件")
        return False

def test_local_torch_install():
    """测试从本地安装PyTorch"""
    logger.info("🧪 测试从本地安装PyTorch...")
    
    downloader = WebUIDownloader(
        download_dir="D:/download",
        retry_count=3,
        retry_interval=5
    )
    
    # 确保虚拟环境存在
    if not downloader.create_virtual_environment():
        logger.error("❌ 无法创建或使用虚拟环境")
        return False
    
    # 升级pip
    if not downloader.upgrade_pip():
        logger.error("❌ pip升级失败")
        return False
    
    # 安装PyTorch（优先本地，不兼容则在线下载）
    logger.info("🔥 开始安装PyTorch...")

    success = downloader.install_torch_from_local_or_online()
    
    if success:
        logger.info("✅ 本地PyTorch安装成功")
        
        # 验证PyTorch是否可以正常导入和检测CUDA
        try:
            venv_python = downloader.get_venv_python()
            import subprocess
            
            # 测试导入
            result = subprocess.run(
                [venv_python, '-c', '''
import torch
print(f"PyTorch版本: {torch.__version__}")
print(f"CUDA可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA版本: {torch.version.cuda}")
    print(f"GPU数量: {torch.cuda.device_count()}")
    if torch.cuda.device_count() > 0:
        print(f"当前GPU: {torch.cuda.get_device_name(0)}")
else:
    print("未检测到CUDA支持")
    
# 测试基本张量操作
x = torch.randn(3, 3)
print(f"测试张量: {x.shape}")
if torch.cuda.is_available():
    x_gpu = x.cuda()
    print(f"GPU张量: {x_gpu.device}")
                '''],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("✅ PyTorch功能验证成功:")
                for line in result.stdout.strip().split('\n'):
                    logger.info(f"   {line}")
                return True
            else:
                logger.error(f"❌ PyTorch功能验证失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ PyTorch验证异常: {e}")
            return False
    else:
        logger.error("❌ 本地PyTorch安装失败")
        return False

def main():
    """主测试函数"""
    logger.info("🚀 开始测试本地PyTorch安装...")
    logger.info("🎯 目标: 从本地wheel文件安装PyTorch")
    logger.info("=" * 60)
    
    tests = [
        ("检查本地PyTorch文件", check_local_torch_files),
        ("本地PyTorch安装", test_local_torch_install),
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
                break  # 如果前面的测试失败，停止后续测试
        except Exception as e:
            logger.error(f"❌ {test_name} 异常: {e}")
            break
    
    logger.info(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        logger.info("🎉 所有测试通过！本地PyTorch安装成功！")
        return True
    else:
        logger.error("❌ 测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
