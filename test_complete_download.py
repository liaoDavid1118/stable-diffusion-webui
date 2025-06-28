#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整的下载程序
包括PyTorch、其他Python包和Git仓库
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

def test_complete_download():
    """测试完整的下载流程"""
    logger.info("🧪 测试完整的下载流程...")
    
    downloader = WebUIDownloader(
        download_dir="D:/download",
        retry_count=3,
        retry_interval=5
    )
    
    # 显示当前状态
    logger.info("📊 下载前状态:")
    downloader.show_status()
    
    # 执行完整下载
    logger.info("\n🚀 开始完整下载...")
    success = downloader.download_all()
    
    if success:
        logger.info("✅ 完整下载成功")
        
        # 显示下载后状态
        logger.info("\n📊 下载后状态:")
        downloader.show_status()
        
        # 验证PyTorch
        logger.info("\n🔥 验证PyTorch安装:")
        try:
            venv_python = downloader.get_venv_python()
            import subprocess
            
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
        # 测试GPU张量操作
        x = torch.randn(3, 3).cuda()
        print(f"GPU张量测试: {x.device}")
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
                logger.info("✅ PyTorch验证成功:")
                for line in result.stdout.strip().split('\n'):
                    logger.info(f"   {line}")
            else:
                logger.error(f"❌ PyTorch验证失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ PyTorch验证异常: {e}")
        
        return True
    else:
        logger.error("❌ 完整下载失败")
        return False

def main():
    """主测试函数"""
    logger.info("🚀 开始测试完整下载程序...")
    logger.info("🎯 目标: 下载所有WebUI依赖")
    logger.info("📁 临时文件目录: D:/download")
    logger.info("📁 虚拟环境: venv")
    logger.info("=" * 60)
    
    try:
        success = test_complete_download()
        
        if success:
            logger.info("\n🎉 完整下载测试成功！")
            logger.info("💡 现在可以运行 webui-user.bat 启动WebUI")
            return True
        else:
            logger.error("\n❌ 完整下载测试失败")
            return False
            
    except KeyboardInterrupt:
        logger.info("\n⚠️ 用户中断测试")
        return False
    except Exception as e:
        logger.error(f"\n❌ 测试异常: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
