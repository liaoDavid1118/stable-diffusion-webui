#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试依赖安装器的基本功能
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from install_dependencies import DependencyInstaller

def test_installer():
    """测试安装器的基本功能"""
    print("🧪 测试依赖安装器...")
    
    # 创建安装器实例
    installer = DependencyInstaller()
    
    # 测试GPU检测
    print("\n1. 测试GPU环境检测:")
    gpu_type, gpu_version = installer.detect_gpu_environment()
    print(f"   检测结果: {gpu_type} ({gpu_version})")
    
    # 测试进度文件
    print("\n2. 测试进度文件:")
    print(f"   进度文件路径: {installer.progress_file}")
    print(f"   当前进度: {installer.progress}")
    
    # 测试Python路径设置
    print("\n3. 测试Python路径:")
    installer.setup_python_paths()
    print(f"   Python路径: {installer.python_exe}")
    print(f"   Pip路径: {installer.pip_exe}")
    
    # 测试命令构建（不实际执行）
    print("\n4. 测试PyTorch命令构建:")
    if gpu_type == "cuda":
        if gpu_version == "cu121":
            torch_url = "https://download.pytorch.org/whl/cu121"
            torch_cmd = [
                str(installer.python_exe), "-m", "pip", "install", 
                "torch==2.1.2", "torchvision==0.16.2", 
                "--extra-index-url", torch_url
            ]
        else:
            torch_cmd = ["torch", "torchvision"]
    elif gpu_type == "intel":
        torch_cmd = ["torch==2.0.0a0", "intel-extension-for-pytorch"]
    else:
        torch_cmd = ["torch", "torchvision", "--extra-index-url", "https://download.pytorch.org/whl/cpu"]
    
    print(f"   PyTorch安装命令: {' '.join(torch_cmd[:3])}...")
    
    print("\n✅ 基本功能测试完成")
    return True

def test_requirements_parsing():
    """测试requirements文件解析"""
    print("\n🧪 测试requirements文件解析...")
    
    installer = DependencyInstaller()
    
    # 检查requirements文件
    requirements_file = installer.script_path / "requirements_versions.txt"
    if not requirements_file.exists():
        requirements_file = installer.script_path / "requirements.txt"
    
    if requirements_file.exists():
        print(f"   找到requirements文件: {requirements_file.name}")
        
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            packages = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and line != "torch":
                    packages.append(line)
            
            print(f"   解析到 {len(packages)} 个包")
            print(f"   前5个包: {packages[:5]}")
            
        except Exception as e:
            print(f"   解析失败: {e}")
            return False
    else:
        print("   ❌ 未找到requirements文件")
        return False
    
    print("   ✅ requirements解析测试完成")
    return True

def main():
    """主测试函数"""
    print("🎯 依赖安装器测试套件")
    print("=" * 50)
    
    try:
        # 基本功能测试
        if not test_installer():
            print("❌ 基本功能测试失败")
            return False
        
        # Requirements解析测试
        if not test_requirements_parsing():
            print("❌ Requirements解析测试失败")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 所有测试通过！")
        print("💡 可以运行 python install_dependencies.py 开始实际安装")
        
        return True
        
    except Exception as e:
        print(f"\n💥 测试过程中出现异常: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
