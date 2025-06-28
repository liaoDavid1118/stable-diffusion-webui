#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stable Diffusion WebUI 依赖安装脚本
支持断点续传和多次重试功能
"""

import os
import sys
import json
import time
import subprocess
import platform
import shutil
import urllib.request
import tempfile
import signal
import requests
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from tqdm import tqdm

# 尝试导入psutil，如果没有则安装
try:
    import psutil
except ImportError:
    print("📦 安装psutil...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    import psutil

# 尝试导入requests和tqdm，如果没有则安装
try:
    import requests
    from tqdm import tqdm
except ImportError:
    print("📦 安装requests和tqdm...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "tqdm"])
    import requests
    from tqdm import tqdm

# 配置参数
RETRY_COUNT = 10  # 重试次数
RETRY_INTERVAL = 3  # 重试间隔（秒）
VENV_DIR = ".venv"  # 虚拟环境目录
PROGRESS_FILE = "install_progress.json"  # 进度记录文件
DOWNLOAD_DIR = "D:/download"  # 下载临时文件目录

class AdvancedDownloader:
    """高级下载器，支持断点续传和重试"""

    def __init__(self, download_dir: Path, max_retries: int = 10, retry_interval: int = 3):
        self.download_dir = download_dir
        self.max_retries = max_retries
        self.retry_interval = retry_interval

    def download_with_resume(self, url: str, local_path: Path) -> bool:
        """支持断点续传的下载"""
        local_path.parent.mkdir(parents=True, exist_ok=True)

        for attempt in range(self.max_retries):
            try:
                # 检查本地文件是否已存在
                resume_byte_pos = 0
                if local_path.exists():
                    resume_byte_pos = local_path.stat().st_size
                    print(f"📂 发现已存在文件，从字节位置 {resume_byte_pos} 开始续传")

                # 设置请求头支持断点续传
                headers = {}
                if resume_byte_pos > 0:
                    headers['Range'] = f'bytes={resume_byte_pos}-'

                # 发起请求
                response = requests.get(url, headers=headers, stream=True, timeout=30)

                # 检查响应状态
                if response.status_code == 416:  # Range Not Satisfiable
                    print("✅ 文件已完整下载")
                    return True
                elif response.status_code not in [200, 206]:
                    response.raise_for_status()

                # 获取文件总大小
                if 'content-length' in response.headers:
                    total_size = int(response.headers['content-length'])
                    if resume_byte_pos > 0:
                        total_size += resume_byte_pos
                else:
                    total_size = None

                # 下载文件
                mode = 'ab' if resume_byte_pos > 0 else 'wb'
                with open(local_path, mode) as f:
                    with tqdm(
                        total=total_size,
                        initial=resume_byte_pos,
                        unit='B',
                        unit_scale=True,
                        desc=f"下载 {local_path.name}"
                    ) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))

                print(f"✅ 文件下载成功: {local_path}")
                return True

            except Exception as e:
                print(f"❌ 下载尝试 {attempt + 1}/{self.max_retries} 失败: {str(e)}")
                if attempt < self.max_retries - 1:
                    print(f"⏳ 等待 {self.retry_interval} 秒后重试...")
                    time.sleep(self.retry_interval)
                else:
                    print("💥 所有下载尝试均失败")
                    return False

        return False

class DependencyInstaller:
    def __init__(self):
        self.script_path = Path(__file__).parent.absolute()
        self.venv_path = self.script_path / VENV_DIR
        self.progress_file = self.script_path / PROGRESS_FILE
        self.download_dir = Path(DOWNLOAD_DIR)
        self.progress = self.load_progress()
        self.python_exe = None
        self.pip_exe = None

        # 创建下载目录
        self.setup_download_directory()

        # 创建高级下载器
        self.downloader = AdvancedDownloader(
            self.download_dir,
            max_retries=RETRY_COUNT,
            retry_interval=RETRY_INTERVAL
        )

    def setup_download_directory(self):
        """设置下载目录"""
        try:
            self.download_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 下载目录: {self.download_dir}")

            # 测试写入权限
            test_file = self.download_dir / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()

        except Exception as e:
            print(f"⚠️  无法创建下载目录 {self.download_dir}: {e}")
            print("🔄 使用默认临时目录")
            self.download_dir = Path(tempfile.gettempdir()) / "sd_webui_download"
            self.download_dir.mkdir(parents=True, exist_ok=True)

    def load_progress(self) -> Dict:
        """加载安装进度"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"警告：无法加载进度文件: {e}")
        return {
            "venv_created": False,
            "torch_installed": False,
            "requirements_installed": False,
            "repos_cloned": False,
            "installed_packages": [],
            "cloned_repos": []
        }
    
    def save_progress(self):
        """保存安装进度"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"警告：无法保存进度文件: {e}")
    
    def detect_gpu_environment(self) -> Tuple[str, str]:
        """检测GPU环境"""
        print("🔍 检测GPU环境...")
        
        # 检测NVIDIA GPU
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ 检测到NVIDIA GPU")
                # 检测CUDA版本
                try:
                    import torch
                    if torch.cuda.is_available():
                        cuda_version = torch.version.cuda
                        print(f"✅ CUDA版本: {cuda_version}")
                        if cuda_version.startswith("12.1"):
                            return "cuda", "cu121"
                        elif cuda_version.startswith("11.8"):
                            return "cuda", "cu118"
                        else:
                            return "cuda", "cu121"  # 默认使用12.1
                except ImportError:
                    pass
                return "cuda", "cu121"  # 默认CUDA 12.1
        except FileNotFoundError:
            pass
        
        # 检测Intel GPU
        try:
            result = subprocess.run(['intel-gpu-top', '--help'], capture_output=True)
            if result.returncode == 0:
                print("✅ 检测到Intel GPU")
                return "intel", "xpu"
        except FileNotFoundError:
            pass
        
        print("⚠️  未检测到GPU，将使用CPU版本")
        return "cpu", "cpu"
    
    def run_command_with_retry(self, command: List[str], description: str,
                             check_success=None, use_custom_temp=True) -> bool:
        """带重试的命令执行"""
        for attempt in range(RETRY_COUNT):
            try:
                print(f"📦 {description} (尝试 {attempt + 1}/{RETRY_COUNT})")

                # 设置环境变量使用自定义临时目录
                env = os.environ.copy()
                if use_custom_temp and self.download_dir:
                    env['TMPDIR'] = str(self.download_dir)
                    env['TMP'] = str(self.download_dir)
                    env['TEMP'] = str(self.download_dir)
                    env['PIP_CACHE_DIR'] = str(self.download_dir / "pip_cache")

                result = subprocess.run(
                    command,
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=self.script_path,
                    env=env
                )

                # 自定义成功检查
                if check_success and not check_success():
                    raise subprocess.CalledProcessError(1, command, "自定义检查失败")

                print(f"✅ {description} 成功")
                return True

            except subprocess.CalledProcessError as e:
                print(f"❌ {description} 失败 (尝试 {attempt + 1}/{RETRY_COUNT})")
                print(f"错误: {e.stderr if e.stderr else e.stdout}")

                # 在重试前清理可能的文件锁定
                if attempt < RETRY_COUNT - 1:
                    if "另一个程序正在使用此文件" in str(e.stderr) or "WinError 32" in str(e.stderr):
                        print("🔧 检测到文件锁定，尝试清理...")
                        self.prepare_for_installation()

                    print(f"⏳ {RETRY_INTERVAL}秒后重试...")
                    time.sleep(RETRY_INTERVAL)
                else:
                    print(f"💥 {description} 最终失败，已达到最大重试次数")
                    return False
            except Exception as e:
                print(f"❌ {description} 出现异常: {e}")
                if attempt < RETRY_COUNT - 1:
                    time.sleep(RETRY_INTERVAL)
                else:
                    return False

        return False
    
    def create_virtual_environment(self) -> bool:
        """创建虚拟环境"""
        if self.progress["venv_created"] and self.venv_path.exists():
            print("✅ 虚拟环境已存在，跳过创建")
            self.setup_python_paths()
            return True
        
        print("🏗️  创建虚拟环境...")
        
        # 删除已存在的虚拟环境
        if self.venv_path.exists():
            shutil.rmtree(self.venv_path)
        
        success = self.run_command_with_retry(
            [sys.executable, "-m", "venv", str(self.venv_path)],
            "创建虚拟环境"
        )
        
        if success:
            self.progress["venv_created"] = True
            self.save_progress()
            self.setup_python_paths()
            
            # 升级pip
            self.run_command_with_retry(
                [str(self.python_exe), "-m", "pip", "install", "--upgrade", "pip"],
                "升级pip"
            )
        
        return success
    
    def setup_python_paths(self):
        """设置Python和pip路径"""
        if platform.system() == "Windows":
            self.python_exe = self.venv_path / "Scripts" / "python.exe"
            self.pip_exe = self.venv_path / "Scripts" / "pip.exe"
        else:
            self.python_exe = self.venv_path / "bin" / "python"
            self.pip_exe = self.venv_path / "bin" / "pip"

    def kill_python_processes(self):
        """终止可能占用文件的Python进程"""
        try:
            current_pid = os.getpid()
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        if proc.info['pid'] != current_pid:  # 不终止当前进程
                            cmdline = proc.info['cmdline'] or []
                            # 检查是否是pip相关进程
                            if any('pip' in arg for arg in cmdline):
                                print(f"🔄 终止pip进程: PID {proc.info['pid']}")
                                proc.terminate()
                                proc.wait(timeout=5)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    pass
        except Exception as e:
            print(f"⚠️  清理进程时出现问题: {e}")

    def clear_pip_cache(self):
        """清理pip缓存和临时文件"""
        try:
            print("🧹 清理pip缓存和临时文件...")

            # 清理系统pip缓存
            cache_dirs = [
                Path.home() / "AppData" / "Local" / "pip" / "Cache",  # Windows
                Path.home() / ".cache" / "pip",  # Linux/Mac
            ]

            for cache_dir in cache_dirs:
                if cache_dir.exists():
                    try:
                        shutil.rmtree(cache_dir, ignore_errors=True)
                        print(f"✅ 清理系统缓存: {cache_dir}")
                    except Exception as e:
                        print(f"⚠️  无法清理 {cache_dir}: {e}")

            # 清理系统临时文件夹中的pip相关文件
            temp_dir = Path(tempfile.gettempdir())
            for item in temp_dir.glob("pip-*"):
                try:
                    if item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)
                    else:
                        item.unlink(missing_ok=True)
                except Exception:
                    pass

            # 清理我们的自定义下载目录
            if self.download_dir.exists():
                try:
                    for item in self.download_dir.iterdir():
                        if item.is_dir():
                            shutil.rmtree(item, ignore_errors=True)
                        else:
                            item.unlink(missing_ok=True)
                    print(f"✅ 清理下载目录: {self.download_dir}")
                except Exception as e:
                    print(f"⚠️  无法清理下载目录: {e}")

        except Exception as e:
            print(f"⚠️  清理缓存时出现问题: {e}")

    def force_cleanup_download_dir(self):
        """强制清理下载目录"""
        try:
            print("🧹 强制清理下载目录...")

            # 多次尝试清理
            for attempt in range(3):
                try:
                    if self.download_dir.exists():
                        # 使用Windows的rmdir命令强制删除
                        if platform.system() == "Windows":
                            subprocess.run(
                                ["cmd", "/c", "rmdir", "/s", "/q", str(self.download_dir)],
                                capture_output=True
                            )
                        else:
                            shutil.rmtree(self.download_dir, ignore_errors=True)

                        # 重新创建目录
                        time.sleep(1)
                        self.download_dir.mkdir(parents=True, exist_ok=True)
                        print(f"✅ 强制清理完成 (尝试 {attempt + 1})")
                        break

                except Exception as e:
                    if attempt < 2:
                        print(f"⚠️  清理失败，重试... ({e})")
                        time.sleep(2)
                    else:
                        print(f"⚠️  无法完全清理: {e}")

        except Exception as e:
            print(f"⚠️  强制清理异常: {e}")

    def prepare_for_installation(self):
        """为安装做准备"""
        print("🔧 准备安装环境...")

        # 终止可能冲突的进程
        self.kill_python_processes()

        # 强制清理下载目录
        self.force_cleanup_download_dir()

        # 清理缓存
        self.clear_pip_cache()

        # 等待一下让系统释放文件句柄
        time.sleep(3)

    def install_package_with_predownload(self, package_name: str, package_url: str = None) -> bool:
        """使用预下载策略安装包"""
        try:
            print(f"🔄 使用预下载策略安装 {package_name}")

            # 如果没有提供URL，尝试从PyPI获取
            if not package_url:
                # 先尝试直接安装
                cmd = [str(self.python_exe), "-m", "pip", "install", package_name, "--no-cache-dir"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    print(f"✅ {package_name} 直接安装成功")
                    return True
                else:
                    print(f"⚠️  直接安装失败，尝试其他方法: {result.stderr}")

            # 如果有URL，尝试预下载
            if package_url:
                # 解析文件名
                filename = package_url.split('/')[-1]
                if not filename.endswith(('.whl', '.tar.gz')):
                    filename += '.whl'

                local_file = self.download_dir / filename

                # 下载文件
                if self.downloader.download_with_resume(package_url, local_file):
                    # 从本地文件安装
                    cmd = [str(self.python_exe), "-m", "pip", "install", str(local_file), "--no-deps"]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    if result.returncode == 0:
                        print(f"✅ {package_name} 从本地文件安装成功")
                        return True
                    else:
                        print(f"❌ 从本地文件安装失败: {result.stderr}")

            return False

        except Exception as e:
            print(f"❌ 预下载安装失败: {e}")
            return False
    
    def install_torch(self, gpu_type: str, gpu_version: str) -> bool:
        """安装PyTorch"""
        if self.progress["torch_installed"]:
            print("✅ PyTorch已安装，跳过")
            return True

        print("🔥 安装PyTorch...")

        # 准备安装环境
        self.prepare_for_installation()

        # 使用新的安装策略
        success = False

        if gpu_type == "cuda":
            if gpu_version == "cu121":
                print("📦 安装CUDA 12.1版本的PyTorch...")
                # 尝试多种安装方法
                methods = [
                    # 方法1: 直接从PyTorch官方源安装
                    [str(self.python_exe), "-m", "pip", "install",
                     "torch==2.1.2", "torchvision==0.16.2",
                     "--index-url", "https://download.pytorch.org/whl/cu121",
                     "--no-cache-dir"],

                    # 方法2: 使用extra-index-url
                    [str(self.python_exe), "-m", "pip", "install",
                     "torch==2.1.2", "torchvision==0.16.2",
                     "--extra-index-url", "https://download.pytorch.org/whl/cu121",
                     "--no-cache-dir"],

                    # 方法3: 分别安装
                    [str(self.python_exe), "-m", "pip", "install",
                     "torch==2.1.2",
                     "--index-url", "https://download.pytorch.org/whl/cu121",
                     "--no-cache-dir"]
                ]
            elif gpu_version == "cu118":
                print("📦 安装CUDA 11.8版本的PyTorch...")
                methods = [
                    [str(self.python_exe), "-m", "pip", "install",
                     "torch==2.1.2", "torchvision==0.16.2",
                     "--index-url", "https://download.pytorch.org/whl/cu118",
                     "--no-cache-dir"]
                ]
            else:
                print("📦 安装默认CUDA版本的PyTorch...")
                methods = [
                    [str(self.python_exe), "-m", "pip", "install",
                     "torch", "torchvision", "--no-cache-dir"]
                ]
        elif gpu_type == "intel":
            print("📦 安装Intel XPU版本的PyTorch...")
            methods = [
                [str(self.python_exe), "-m", "pip", "install",
                 "torch==2.0.0a0", "intel-extension-for-pytorch==2.0.110+gitba7f6c1",
                 "--extra-index-url", "https://pytorch-extension.intel.com/release-whl/stable/xpu/us/",
                 "--no-cache-dir"]
            ]
        else:
            print("📦 安装CPU版本的PyTorch...")
            methods = [
                [str(self.python_exe), "-m", "pip", "install",
                 "torch", "torchvision",
                 "--index-url", "https://download.pytorch.org/whl/cpu",
                 "--no-cache-dir"]
            ]

        # 尝试不同的安装方法
        for i, method in enumerate(methods):
            print(f"🔄 尝试安装方法 {i+1}/{len(methods)}")
            success = self.run_command_with_retry(
                method,
                f"PyTorch安装方法{i+1}",
                use_custom_temp=True
            )
            if success:
                break

        # 验证安装
        if success:
            def check_torch():
                try:
                    result = subprocess.run([
                        str(self.python_exe), "-c",
                        "import torch; print(f'PyTorch {torch.__version__} 安装成功'); "
                        "print(f'CUDA可用: {torch.cuda.is_available()}') if hasattr(torch.cuda, 'is_available') else None"
                    ], capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        print("✅ PyTorch验证成功:")
                        print(result.stdout.strip())
                        return True
                except Exception as e:
                    print(f"⚠️  PyTorch验证失败: {e}")
                return False

            if check_torch():
                self.progress["torch_installed"] = True
                self.save_progress()
                return True
            else:
                print("❌ PyTorch安装验证失败")
                return False

        return success

    def install_requirements(self) -> bool:
        """安装requirements.txt中的依赖"""
        if self.progress["requirements_installed"]:
            print("✅ Requirements已安装，跳过")
            return True

        print("📋 安装requirements依赖...")

        # 检查requirements文件
        requirements_file = self.script_path / "requirements_versions.txt"
        if not requirements_file.exists():
            requirements_file = self.script_path / "requirements.txt"

        if not requirements_file.exists():
            print("❌ 未找到requirements文件")
            return False

        # 读取requirements并逐个安装
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            packages = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and line != "torch":  # 跳过torch，已单独安装
                    packages.append(line)

            print(f"📦 需要安装 {len(packages)} 个包")

            # 逐个安装包以支持断点续传
            failed_packages = []
            for i, package in enumerate(packages):
                if package in self.progress["installed_packages"]:
                    print(f"✅ {package} 已安装，跳过 ({i+1}/{len(packages)})")
                    continue

                print(f"📦 安装 {package} ({i+1}/{len(packages)})")
                success = self.run_command_with_retry(
                    [str(self.python_exe), "-m", "pip", "install", package,
                     "--prefer-binary",
                     "--cache-dir", str(self.download_dir / "pip_cache"),
                     "--no-warn-script-location"],
                    f"安装 {package}"
                )

                if success:
                    self.progress["installed_packages"].append(package)
                    self.save_progress()
                else:
                    failed_packages.append(package)

            if failed_packages:
                print(f"⚠️  以下包安装失败: {failed_packages}")
                return False

            self.progress["requirements_installed"] = True
            self.save_progress()
            return True

        except Exception as e:
            print(f"❌ 读取requirements文件失败: {e}")
            return False

    def clone_repositories(self) -> bool:
        """克隆必要的Git仓库"""
        if self.progress["repos_cloned"]:
            print("✅ Git仓库已克隆，跳过")
            return True

        print("📂 克隆Git仓库...")

        # 定义需要克隆的仓库
        repos = [
            {
                "url": "https://github.com/AUTOMATIC1111/stable-diffusion-webui-assets.git",
                "dir": "repositories/stable-diffusion-webui-assets",
                "name": "WebUI Assets"
            },
            {
                "url": "https://github.com/Stability-AI/stablediffusion.git",
                "dir": "repositories/stable-diffusion-stability-ai",
                "name": "Stable Diffusion"
            },
            {
                "url": "https://github.com/Stability-AI/generative-models.git",
                "dir": "repositories/generative-models",
                "name": "Stable Diffusion XL"
            },
            {
                "url": "https://github.com/crowsonkb/k-diffusion.git",
                "dir": "repositories/k-diffusion",
                "name": "K-diffusion"
            },
            {
                "url": "https://github.com/salesforce/BLIP.git",
                "dir": "repositories/BLIP",
                "name": "BLIP"
            }
        ]

        # 创建repositories目录
        repos_dir = self.script_path / "repositories"
        repos_dir.mkdir(exist_ok=True)

        failed_repos = []
        for repo in repos:
            repo_path = self.script_path / repo["dir"]

            if repo["name"] in self.progress["cloned_repos"]:
                print(f"✅ {repo['name']} 已克隆，跳过")
                continue

            # 如果目录已存在，先删除
            if repo_path.exists():
                shutil.rmtree(repo_path)

            success = self.run_command_with_retry(
                ["git", "clone", repo["url"], str(repo_path)],
                f"克隆 {repo['name']}"
            )

            if success:
                self.progress["cloned_repos"].append(repo["name"])
                self.save_progress()
            else:
                failed_repos.append(repo["name"])

        if failed_repos:
            print(f"⚠️  以下仓库克隆失败: {failed_repos}")
            return False

        self.progress["repos_cloned"] = True
        self.save_progress()
        return True

    def install_additional_packages(self) -> bool:
        """安装额外的包"""
        print("🔧 安装额外包...")

        additional_packages = [
            ("clip", "https://github.com/openai/CLIP/archive/d50d76daa670286dd6cacf3bcd80b5e4823fc8e1.zip"),
            ("open_clip", "https://github.com/mlfoundations/open_clip/archive/bb6e834e9c70d9c27d0dc3ecedeebeaeb1ffad6b.zip")
        ]

        for package_name, package_url in additional_packages:
            if f"additional_{package_name}" in self.progress["installed_packages"]:
                print(f"✅ {package_name} 已安装，跳过")
                continue

            success = self.run_command_with_retry(
                [str(self.python_exe), "-m", "pip", "install", package_url,
                 "--cache-dir", str(self.download_dir / "pip_cache"),
                 "--no-warn-script-location"],
                f"安装 {package_name}"
            )

            if success:
                self.progress["installed_packages"].append(f"additional_{package_name}")
                self.save_progress()

        return True

    def verify_installation(self) -> bool:
        """验证安装"""
        print("🔍 验证安装...")

        # 验证PyTorch
        try:
            result = subprocess.run([
                str(self.python_exe), "-c",
                "import torch; print(f'PyTorch: {torch.__version__}'); "
                "print(f'CUDA可用: {torch.cuda.is_available()}') if torch.cuda.is_available() else print('CPU模式')"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ PyTorch验证成功:")
                print(result.stdout.strip())
            else:
                print("❌ PyTorch验证失败")
                return False
        except Exception as e:
            print(f"❌ PyTorch验证异常: {e}")
            return False

        # 验证关键包
        key_packages = ["gradio", "transformers", "accelerate", "safetensors"]
        for package in key_packages:
            try:
                result = subprocess.run([
                    str(self.python_exe), "-c", f"import {package}; print(f'{package}: OK')"
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    print(f"✅ {package}: OK")
                else:
                    print(f"❌ {package}: 导入失败")
            except Exception as e:
                print(f"❌ {package}: 验证异常 {e}")

        return True

    def run_installation(self) -> bool:
        """运行完整的安装流程"""
        print("🚀 开始安装 Stable Diffusion WebUI 依赖")
        print("=" * 60)

        # 检测GPU环境
        gpu_type, gpu_version = self.detect_gpu_environment()
        print(f"🎯 目标环境: {gpu_type} ({gpu_version})")
        print("=" * 60)

        # 步骤1: 创建虚拟环境
        if not self.create_virtual_environment():
            print("💥 虚拟环境创建失败")
            return False

        # 步骤2: 安装PyTorch
        if not self.install_torch(gpu_type, gpu_version):
            print("💥 PyTorch安装失败")
            return False

        # 步骤3: 安装requirements依赖
        if not self.install_requirements():
            print("💥 Requirements安装失败")
            return False

        # 步骤4: 安装额外包
        if not self.install_additional_packages():
            print("💥 额外包安装失败")
            return False

        # 步骤5: 克隆Git仓库
        if not self.clone_repositories():
            print("💥 Git仓库克隆失败")
            return False

        # 步骤6: 验证安装
        if not self.verify_installation():
            print("💥 安装验证失败")
            return False

        print("=" * 60)
        print("🎉 所有依赖安装完成！")
        print("=" * 60)

        # 显示使用说明
        self.show_usage_instructions()

        return True

    def show_usage_instructions(self):
        """显示使用说明"""
        print("\n📖 使用说明:")
        print("-" * 40)
        print("1. 激活虚拟环境:")
        if platform.system() == "Windows":
            print(f"   {self.venv_path}\\Scripts\\activate.bat")
        else:
            print(f"   source {self.venv_path}/bin/activate")

        print("\n2. 启动WebUI:")
        print("   python webui.py")
        print("   或者运行: webui.bat (Windows) / webui.sh (Linux/Mac)")

        print("\n3. 如需重新安装某个组件，删除对应的进度记录:")
        print(f"   编辑 {self.progress_file} 文件")

        print("\n4. 完全重新安装:")
        print(f"   删除 {self.progress_file} 和 {self.venv_path} 目录")

        print("\n🔧 故障排除:")
        print("- 如果遇到网络问题，脚本会自动重试")
        print("- 如果某个包安装失败，可以手动安装后重新运行脚本")
        print("- 查看详细错误信息请检查命令行输出")


def main():
    """主函数"""
    print("🎨 Stable Diffusion WebUI 依赖安装器")
    print("支持断点续传和自动重试功能")
    print("重试次数: 10次，间隔: 3秒")
    print("=" * 60)

    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        sys.exit(1)

    # 检查Git是否可用
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 未找到Git，请先安装Git")
        sys.exit(1)

    # 创建安装器实例
    installer = DependencyInstaller()

    try:
        # 运行安装
        success = installer.run_installation()

        if success:
            print("\n✅ 安装成功完成！")
            sys.exit(0)
        else:
            print("\n❌ 安装失败，请检查错误信息")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️  用户中断安装")
        installer.save_progress()
        print("💾 进度已保存，可以稍后继续安装")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 安装过程中出现异常: {e}")
        installer.save_progress()
        sys.exit(1)


if __name__ == "__main__":
    main()
