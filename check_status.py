#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速状态检查脚本
检查Stable Diffusion WebUI的安装状态
"""

import sys
import subprocess
from pathlib import Path

def print_header(title):
    """打印标题"""
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print(f"{'='*50}")

def check_venv():
    """检查虚拟环境"""
    print_header("虚拟环境检查")
    
    venv_path = Path("venv")
    python_exe = venv_path / "Scripts" / "python.exe"
    
    if venv_path.exists() and python_exe.exists():
        print("✅ 虚拟环境存在")
        
        # 检查Python版本
        try:
            result = subprocess.run([str(python_exe), "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Python版本: {result.stdout.strip()}")
            else:
                print("❌ 无法获取Python版本")
        except Exception as e:
            print(f"❌ Python版本检查失败: {e}")
    else:
        print("❌ 虚拟环境不存在")
        return False
    
    return True

def check_pytorch():
    """检查PyTorch"""
    print_header("PyTorch检查")
    
    python_exe = Path("venv/Scripts/python.exe")
    if not python_exe.exists():
        print("❌ 虚拟环境不存在")
        return False
    
    try:
        # 检查PyTorch安装
        result = subprocess.run([
            str(python_exe), "-c", 
            "import torch; print(f'PyTorch版本: {torch.__version__}'); print(f'CUDA可用: {torch.cuda.is_available()}'); print(f'CUDA版本: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                print(f"✅ {line}")
            return True
        else:
            print(f"❌ PyTorch检查失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ PyTorch检查超时")
        return False
    except Exception as e:
        print(f"❌ PyTorch检查异常: {e}")
        return False

def check_repositories():
    """检查Git仓库"""
    print_header("Git仓库检查")
    
    repos = [
        "repositories/stable-diffusion-webui-assets",
        "repositories/stable-diffusion-stability-ai", 
        "repositories/generative-models",
        "repositories/k-diffusion",
        "repositories/BLIP"
    ]
    
    all_exist = True
    for repo in repos:
        repo_path = Path(repo)
        if repo_path.exists():
            print(f"✅ {repo}")
        else:
            print(f"❌ {repo}")
            all_exist = False
    
    return all_exist

def check_main_files():
    """检查主要文件"""
    print_header("主要文件检查")
    
    files = [
        ("webui.py", "WebUI主程序"),
        ("launch.py", "启动脚本"),
        ("requirements_versions.txt", "依赖列表"),
        ("webui_downloader.py", "下载程序")
    ]
    
    all_exist = True
    for file_path, description in files:
        if Path(file_path).exists():
            print(f"✅ {description}: {file_path}")
        else:
            print(f"❌ {description}: {file_path}")
            all_exist = False
    
    return all_exist

def check_key_packages():
    """检查关键Python包"""
    print_header("关键包检查")
    
    python_exe = Path("venv/Scripts/python.exe")
    if not python_exe.exists():
        print("❌ 虚拟环境不存在")
        return False
    
    packages = ["torch", "clip", "open_clip_torch", "xformers"]
    
    all_installed = True
    for package in packages:
        try:
            result = subprocess.run([
                str(python_exe), "-c", f"import {package}; print('已安装')"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ {package}: 已安装")
            else:
                print(f"❌ {package}: 未安装")
                all_installed = False
                
        except subprocess.TimeoutExpired:
            print(f"❌ {package}: 检查超时")
            all_installed = False
        except Exception as e:
            print(f"❌ {package}: 检查失败 ({e})")
            all_installed = False
    
    return all_installed

def get_readiness_score():
    """计算就绪度评分"""
    print_header("就绪度评估")
    
    checks = [
        ("虚拟环境", check_venv),
        ("PyTorch", check_pytorch),
        ("Git仓库", check_repositories),
        ("主要文件", check_main_files),
        ("关键包", check_key_packages)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"❌ {name}检查异常: {e}")
    
    score = (passed / total) * 100
    
    print(f"\n📊 就绪度评分: {passed}/{total} ({score:.1f}%)")
    
    if score >= 90:
        print("🎉 WebUI已准备就绪，可以启动！")
        print("💡 建议运行: quick_start.bat 或 python webui.py")
    elif score >= 70:
        print("⚠️ WebUI基本就绪，可能需要安装少量依赖")
        print("💡 建议运行: python webui.py 并根据提示安装缺失依赖")
    else:
        print("❌ WebUI未就绪，需要完成安装")
        print("💡 建议运行: python webui_downloader.py")
    
    return score

def main():
    """主函数"""
    print("🎨 Stable Diffusion WebUI 状态检查")
    print("=" * 50)
    print("📍 当前目录:", Path.cwd())
    
    try:
        score = get_readiness_score()
        
        print(f"\n{'='*50}")
        print("📋 快速操作指南:")
        print("  python webui_downloader.py --status  # 查看下载状态")
        print("  python webui_downloader.py          # 完成下载安装")
        print("  quick_start.bat                     # 快速启动WebUI")
        print("  python webui.py                     # 直接启动WebUI")
        print(f"{'='*50}")
        
        return score >= 70
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断检查")
        return False
    except Exception as e:
        print(f"\n❌ 检查过程出错: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
