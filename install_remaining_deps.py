#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量安装剩余依赖的脚本
解决WebUI启动时的依赖缺失问题
"""

import subprocess
import sys
from pathlib import Path

def run_pip_install(packages):
    """安装Python包"""
    venv_python = Path("venv/Scripts/python.exe")
    
    for package in packages:
        print(f"🔧 安装 {package}...")
        try:
            result = subprocess.run([
                str(venv_python), "-m", "pip", "install", package
            ], capture_output=True, text=True, encoding='utf-8', errors='replace')
            
            if result.returncode == 0:
                print(f"✅ {package} 安装成功")
            else:
                print(f"❌ {package} 安装失败: {result.stderr}")
        except Exception as e:
            print(f"❌ {package} 安装异常: {e}")

def main():
    """主函数"""
    print("🚀 开始批量安装剩余依赖...")
    
    # 需要安装的包列表
    packages = [
        # 核心依赖
        "pytorch_lightning==1.9.5",  # 使用兼容版本
        "lightning==1.9.5",
        
        # 图像处理
        "opencv-python",
        "imageio",
        "imageio-ffmpeg",
        
        # 科学计算
        "scikit-image",
        "matplotlib",
        
        # Web框架
        "fastapi",
        "uvicorn",
        
        # 其他依赖
        "pydantic",
        "httpx",
        "aiofiles",
        "python-multipart",
        
        # 模型相关
        "diffusers",
        "controlnet-aux",
        
        # 工具库
        "rich",
        "typer",
        "click",
        
        # 图像质量评估
        "lpips",
        "clean-fid",
        
        # 其他可能需要的包
        "basicsr",
        "realesrgan",
        "gfpgan",
        "codeformer",
        "facexlib",
        "lark",
        "inflection",
        "jsonmerge",
        "resize-right",
        "tomesd",
        "numba",
        "piexif",
        "psutil",
        "send2trash",
        "torchsde",
        "blendmodes",
    ]
    
    print(f"📋 将安装 {len(packages)} 个包...")
    run_pip_install(packages)
    
    print("\n🎉 依赖安装完成！")
    print("💡 现在可以尝试运行: python webui.py")

if __name__ == "__main__":
    main()
