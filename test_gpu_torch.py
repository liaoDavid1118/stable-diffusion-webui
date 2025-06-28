#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试GPU版PyTorch安装
使用d:\download作为临时下载目录
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

def test_gpu_torch_install():
    """测试GPU版PyTorch安装"""
    logger.info("🧪 测试GPU版PyTorch安装...")
    logger.info(f"📁 临时下载目录: D:/download")
    
    downloader = WebUIDownloader(
        download_dir="D:/download",
        retry_count=3,  # 减少重试次数以便快速测试
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
    
    # 测试安装GPU版PyTorch
    logger.info("🔥 开始安装GPU版PyTorch...")
    logger.info("⚠️  这可能需要10-20分钟，请耐心等待...")
    
    success = downloader.install_torch_safely()
    
    if success:
        logger.info("✅ GPU版PyTorch安装成功")
        
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
    print(f"当前GPU: {torch.cuda.get_device_name(0)}")
else:
    print("未检测到CUDA支持")
                '''],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("✅ PyTorch导入和CUDA检测成功:")
                for line in result.stdout.strip().split('\n'):
                    logger.info(f"   {line}")
                return True
            else:
                logger.error(f"❌ PyTorch导入测试失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ PyTorch验证异常: {e}")
            return False
    else:
        logger.error("❌ GPU版PyTorch安装失败")
        return False

def check_download_dir():
    """检查下载目录"""
    download_dir = Path("D:/download")
    logger.info(f"📁 检查下载目录: {download_dir}")
    
    try:
        download_dir.mkdir(parents=True, exist_ok=True)
        
        # 测试写入权限
        test_file = download_dir / "test_write.txt"
        test_file.write_text("test", encoding='utf-8')
        test_file.unlink()
        
        logger.info("✅ 下载目录可用且有写入权限")
        return True
    except Exception as e:
        logger.error(f"❌ 下载目录检查失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("🚀 开始测试GPU版PyTorch安装...")
    logger.info("🎯 目标: 安装支持CUDA 12.1的PyTorch")
    logger.info("📁 临时文件目录: D:/download")
    logger.info("=" * 60)
    
    tests = [
        ("下载目录检查", check_download_dir),
        ("GPU版PyTorch安装", test_gpu_torch_install),
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
        logger.info("🎉 所有测试通过！GPU版PyTorch安装成功！")
        return True
    else:
        logger.error("❌ 测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
