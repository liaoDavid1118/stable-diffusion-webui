#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stable Diffusion WebUI 下载程序
参考 main.py 中的下载方法，下载 webui-user.bat 中涉及到的所有文件
支持断点续传和重试功能，下载临时文件到 D:/download 路径
"""

import os
import sys
import time
import json
import shutil
import logging
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 尝试导入必要的库，如果没有则安装
try:
    import requests
    from tqdm import tqdm
except ImportError:
    print("📦 安装基础依赖 requests 和 tqdm...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "tqdm"])
    import requests
    from tqdm import tqdm

# 配置参数
RETRY_COUNT = 10  # 重试次数
RETRY_INTERVAL = 3  # 重试间隔（秒）
VENV_DIR = "venv"  # 虚拟环境目录
DOWNLOAD_DIR = "D:/download"  # 下载临时文件目录
PROGRESS_FILE = "webui_download_progress.json"  # 进度记录文件

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webui_downloader.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WebUIDownloader:
    """WebUI 下载器类"""

    def __init__(self, venv_dir=VENV_DIR, download_dir=DOWNLOAD_DIR,
                 retry_count=RETRY_COUNT, retry_interval=RETRY_INTERVAL):
        self.script_path = Path(__file__).parent.absolute()
        self.venv_path = self.script_path / venv_dir
        self.download_dir = Path(download_dir)
        self.progress_file = self.script_path / PROGRESS_FILE
        self.retry_count = retry_count
        self.retry_interval = retry_interval
        self.progress = self.load_progress()

        # 创建必要的目录
        self.setup_directories()

        # 定义需要下载的资源
        self.define_resources()
    
    def setup_directories(self):
        """创建必要的目录"""
        try:
            self.download_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 下载目录已准备: {self.download_dir}")
        except Exception as e:
            logger.error(f"❌ 无法创建下载目录 {self.download_dir}: {e}")
            # 使用系统临时目录作为备选
            import tempfile
            self.download_dir = Path(tempfile.gettempdir()) / "webui_download"
            self.download_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 使用备选下载目录: {self.download_dir}")
    
    def define_resources(self):
        """定义需要下载的资源"""
        # Git 仓库列表
        self.git_repos = {
            'stable-diffusion-webui-assets': {
                'url': 'https://github.com/AUTOMATIC1111/stable-diffusion-webui-assets.git',
                'commit': '6f7db241d2f8ba7457bac5ca9753331f0c266917',
                'dir': 'repositories/stable-diffusion-webui-assets'
            },
            'stable-diffusion-stability-ai': {
                'url': 'https://github.com/Stability-AI/stablediffusion.git',
                'commit': 'cf1d67a6fd5ea1aa600c4df58e5b47da45f6bdbf',
                'dir': 'repositories/stable-diffusion-stability-ai'
            },
            'generative-models': {
                'url': 'https://github.com/Stability-AI/generative-models.git',
                'commit': '45c443b316737a4ab6e40413d7794a7f5657c19f',
                'dir': 'repositories/generative-models'
            },
            'k-diffusion': {
                'url': 'https://github.com/crowsonkb/k-diffusion.git',
                'commit': 'ab527a9a6d347f364e3d185ba6d714e22d80cb3c',
                'dir': 'repositories/k-diffusion'
            },
            'BLIP': {
                'url': 'https://github.com/salesforce/BLIP.git',
                'commit': '48211a1594f1321b00f14c9f7a5b4813144b2fb9',
                'dir': 'repositories/BLIP'
            }
        }
        
        # Python 包列表（不包括torch，将从本地安装）
        self.python_packages = {
            'clip': 'https://github.com/openai/CLIP/archive/d50d76daa670286dd6cacf3bcd80b5e4823fc8e1.zip',
            'open_clip': 'https://github.com/mlfoundations/open_clip/archive/bb6e834e9c70d9c27d0dc3ecedeebeaeb1ffad6b.zip',
            'xformers': 'xformers==0.0.23.post1'
        }
    
    def load_progress(self) -> Dict:
        """加载下载进度"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ 无法加载进度文件: {e}")
        return {
            'git_repos': {},
            'python_packages': {},
            'requirements': False,
            'venv_created': False
        }
    
    def save_progress(self):
        """保存下载进度"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ 无法保存进度文件: {e}")
    
    def download_with_resume_and_retry(self, url: str, local_path: Path,
                                     max_retries: int = None,
                                     retry_interval: int = None) -> bool:
        """
        支持断点续传和重试的下载函数（参考 main.py）

        Args:
            url: 下载链接
            local_path: 本地保存路径
            max_retries: 最大重试次数
            retry_interval: 重试间隔（秒）
        """
        if max_retries is None:
            max_retries = self.retry_count
        if retry_interval is None:
            retry_interval = self.retry_interval

        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        for attempt in range(max_retries):
            try:
                # 检查本地文件是否已存在
                resume_byte_pos = 0
                if local_path.exists():
                    resume_byte_pos = local_path.stat().st_size
                    logger.info(f"发现已存在文件，从字节位置 {resume_byte_pos} 开始续传")
                
                # 设置请求头支持断点续传
                headers = {}
                if resume_byte_pos > 0:
                    headers['Range'] = f'bytes={resume_byte_pos}-'
                
                # 发起请求
                response = requests.get(url, headers=headers, stream=True, timeout=30)
                
                # 检查响应状态
                if response.status_code == 416:  # Range Not Satisfiable
                    logger.info("文件已完整下载")
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
                
                logger.info(f"文件下载成功: {local_path}")
                return True
                
            except Exception as e:
                logger.error(f"下载尝试 {attempt + 1}/{max_retries} 失败: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"等待 {retry_interval} 秒后重试...")
                    time.sleep(retry_interval)
                else:
                    logger.error("所有下载尝试均失败")
                    return False
        
        return False
    
    def run_command(self, command: str, desc: str = None, cwd: Path = None) -> bool:
        """运行命令"""
        if desc:
            logger.info(f"🔧 {desc}")

        try:
            # 设置环境变量以确保正确的编码
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'

            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.script_path,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',  # 替换无法解码的字符
                env=env
            )

            if result.returncode == 0:
                if result.stdout and result.stdout.strip():
                    logger.debug(f"命令输出: {result.stdout.strip()}")
                return True
            else:
                logger.error(f"命令执行失败: {command}")
                if result.stderr:
                    logger.error(f"错误输出: {result.stderr}")
                if result.stdout:
                    logger.error(f"标准输出: {result.stdout}")
                return False

        except Exception as e:
            logger.error(f"命令执行异常: {e}")
            return False
    
    def scan_existing_packages(self):
        """扫描现有虚拟环境中已安装的包"""
        if not self.venv_path.exists():
            return

        logger.info("🔍 扫描现有虚拟环境中的已安装包...")

        for package_name in self.python_packages.keys():
            if self.check_package_installed(package_name):
                logger.info(f"✅ 发现已安装的包: {package_name}")
                self.progress['python_packages'][package_name] = True

        self.save_progress()

    def create_virtual_environment(self) -> bool:
        """检查或创建虚拟环境"""
        # 检查虚拟环境是否已存在且可用
        if self.venv_path.exists():
            venv_python = self.get_venv_python()
            if Path(venv_python).exists():
                logger.info("✅ 发现现有虚拟环境，将使用现有环境")
                self.progress['venv_created'] = True
                self.save_progress()

                # 扫描现有包
                self.scan_existing_packages()
                return True
            else:
                logger.warning("⚠️ 虚拟环境目录存在但Python可执行文件缺失")

        logger.info("🔧 创建新的虚拟环境...")

        # 删除损坏的虚拟环境
        if self.venv_path.exists():
            logger.info("🗑️ 删除损坏的虚拟环境...")
            shutil.rmtree(self.venv_path)

        # 创建新的虚拟环境
        if self.run_command(f'"{sys.executable}" -m venv "{self.venv_path}"', "创建虚拟环境"):
            self.progress['venv_created'] = True
            self.save_progress()
            logger.info("✅ 虚拟环境创建成功")
            return True
        else:
            logger.error("❌ 虚拟环境创建失败")
            return False
    
    def get_venv_python(self) -> str:
        """获取虚拟环境中的 Python 路径"""
        if platform.system() == "Windows":
            return str(self.venv_path / "Scripts" / "python.exe")
        else:
            return str(self.venv_path / "bin" / "python")
    
    def get_venv_pip(self) -> str:
        """获取虚拟环境中的 pip 路径"""
        return f'"{self.get_venv_python()}" -m pip'

    def check_package_installed(self, package_name: str) -> bool:
        """检查包是否已在虚拟环境中安装"""
        try:
            pip_cmd = self.get_venv_pip()

            # 设置环境变量以确保正确的编码
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'

            result = subprocess.run(
                f'{pip_cmd} show {package_name}',
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                env=env
            )
            return result.returncode == 0
        except Exception:
            return False

    def install_python_package(self, package_name: str, package_spec: str) -> bool:
        """安装 Python 包"""
        # 首先检查进度记录
        if self.progress['python_packages'].get(package_name, False):
            logger.info(f"✅ {package_name} 已标记为已安装")
            return True

        # 检查包是否实际已安装
        if self.check_package_installed(package_name):
            logger.info(f"✅ {package_name} 已在虚拟环境中安装")
            self.progress['python_packages'][package_name] = True
            self.save_progress()
            return True

        logger.info(f"📦 安装 {package_name}...")

        # 使用更健壮的pip安装方法
        success = self.run_pip_install(package_name, package_spec)

        if success:
            self.progress['python_packages'][package_name] = True
            self.save_progress()
            logger.info(f"✅ {package_name} 安装成功")
            return True
        else:
            logger.error(f"❌ {package_name} 安装失败")
            return False

    def run_pip_install(self, package_name: str, package_spec: str) -> bool:
        """运行pip安装命令，使用更好的错误处理"""
        venv_python = self.get_venv_python()

        # 构建安装命令
        if package_name == 'torch':
            # PyTorch 需要特殊的安装命令
            cmd = [venv_python, '-m', 'pip', 'install'] + package_spec.split() + ['--prefer-binary']
        elif package_spec.startswith('http'):
            # 从 URL 安装
            cmd = [venv_python, '-m', 'pip', 'install', package_spec]
        else:
            # 普通包安装
            cmd = [venv_python, '-m', 'pip', 'install', package_spec]

        logger.info(f"🔧 执行命令: {' '.join(cmd)}")

        try:
            # 设置环境变量
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            env['PIP_DISABLE_PIP_VERSION_CHECK'] = '1'
            env['PIP_NO_CACHE_DIR'] = '1'
            env['TMPDIR'] = str(self.download_dir)
            env['TEMP'] = str(self.download_dir)
            env['TMP'] = str(self.download_dir)

            # 确保下载目录存在
            self.download_dir.mkdir(parents=True, exist_ok=True)

            # 使用Popen进行实时输出
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                env=env,
                cwd=self.script_path
            )

            # 实时显示输出
            output_lines = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    output_lines.append(line)
                    # 只显示重要的输出行
                    if any(keyword in line.lower() for keyword in ['installing', 'downloading', 'error', 'successfully']):
                        logger.info(f"  {line}")

            return_code = process.poll()

            if return_code == 0:
                logger.info(f"✅ {package_name} 安装命令执行成功")
                return True
            else:
                logger.error(f"❌ {package_name} 安装命令失败，返回码: {return_code}")
                # 显示最后几行输出用于调试
                if output_lines:
                    logger.error("最后的输出:")
                    for line in output_lines[-10:]:  # 显示最后10行
                        logger.error(f"  {line}")
                return False

        except Exception as e:
            logger.error(f"❌ 执行pip安装命令时出现异常: {e}")
            return False

    def install_torch_from_local_or_online(self) -> bool:
        """优先从本地安装PyTorch，如果不兼容则从网上下载"""
        package_name = 'torch'

        # 检查是否已安装
        if self.progress['python_packages'].get(package_name, False):
            logger.info(f"✅ {package_name} 已标记为已安装")
            return True

        if self.check_package_installed(package_name):
            logger.info(f"✅ {package_name} 已在虚拟环境中安装")
            self.progress['python_packages'][package_name] = True
            self.save_progress()
            return True

        venv_python = self.get_venv_python()

        # 获取虚拟环境的Python版本
        import subprocess
        result = subprocess.run([venv_python, '--version'], capture_output=True, text=True)
        python_version = result.stdout.strip()
        logger.info(f"🐍 虚拟环境Python版本: {python_version}")

        # 查找本地的PyTorch wheel文件
        torch_wheel = None
        for wheel_file in self.script_path.glob("torch-*.whl"):
            if "cu121" in wheel_file.name or "cu" in wheel_file.name:
                # 检查wheel文件是否与当前Python版本兼容
                if "cp310" in wheel_file.name and "3.10" in python_version:
                    torch_wheel = wheel_file
                    break
                elif "cp311" in wheel_file.name and "3.11" in python_version:
                    torch_wheel = wheel_file
                    break
                elif "cp312" in wheel_file.name and "3.12" in python_version:
                    torch_wheel = wheel_file
                    break

        if torch_wheel:
            logger.info(f"📦 从本地安装兼容的PyTorch: {torch_wheel.name}")
            # 从本地安装
            torch_commands = [
                # 先安装基础依赖
                [venv_python, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel'],
                # 从本地wheel文件安装PyTorch
                [venv_python, '-m', 'pip', 'install', str(torch_wheel), '--no-deps'],
                # 安装torchvision（指定CUDA版本，避免覆盖GPU版PyTorch）
                [venv_python, '-m', 'pip', 'install', 'torchvision', '--extra-index-url', 'https://download.pytorch.org/whl/cu121', '--no-deps'],
            ]
        else:
            logger.info("⚠️ 本地PyTorch wheel文件与当前Python版本不兼容")
            logger.info("📦 从网上下载适合的PyTorch版本...")
            # 从网上下载
            torch_commands = [
                # 先安装基础依赖
                [venv_python, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel'],
                # 从网上下载安装PyTorch GPU版本
                [venv_python, '-m', 'pip', 'install', 'torch', 'torchvision',
                 '--extra-index-url', 'https://download.pytorch.org/whl/cu121', '--no-cache-dir'],
            ]

        for i, cmd in enumerate(torch_commands, 1):
            logger.info(f"🔧 执行PyTorch安装步骤 {i}/{len(torch_commands)}")
            logger.info(f"命令: {' '.join(cmd)}")

            try:
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                env['PYTHONUTF8'] = '1'
                env['PIP_DISABLE_PIP_VERSION_CHECK'] = '1'
                env['PIP_NO_CACHE_DIR'] = '1'
                env['TMPDIR'] = str(self.download_dir)
                env['TEMP'] = str(self.download_dir)
                env['TMP'] = str(self.download_dir)

                # 确保下载目录存在
                self.download_dir.mkdir(parents=True, exist_ok=True)

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    env=env,
                    cwd=self.script_path,
                    timeout=1800  # 30分钟超时
                )

                if result.returncode == 0:
                    logger.info(f"✅ PyTorch安装步骤 {i} 完成")
                else:
                    logger.error(f"❌ PyTorch安装步骤 {i} 失败")
                    if result.stderr:
                        logger.error(f"错误: {result.stderr[:500]}...")  # 只显示前500字符
                    return False

            except subprocess.TimeoutExpired:
                logger.error(f"❌ PyTorch安装步骤 {i} 超时")
                return False
            except Exception as e:
                logger.error(f"❌ PyTorch安装步骤 {i} 异常: {e}")
                return False

        # 验证安装
        if self.check_package_installed('torch'):
            logger.info("✅ PyTorch 安装成功")
            self.progress['python_packages']['torch'] = True
            self.save_progress()
            return True
        else:
            logger.error("❌ PyTorch 安装验证失败")
            return False

    def clone_git_repository(self, repo_name: str, repo_info: Dict) -> bool:
        """克隆 Git 仓库"""
        if self.progress['git_repos'].get(repo_name, False):
            logger.info(f"✅ {repo_name} 仓库已存在")
            return True

        repo_dir = self.script_path / repo_info['dir']

        logger.info(f"📥 克隆 {repo_name} 仓库...")

        # 如果目录已存在，先删除
        if repo_dir.exists():
            shutil.rmtree(repo_dir)

        # 确保父目录存在
        repo_dir.parent.mkdir(parents=True, exist_ok=True)

        # 克隆仓库
        clone_cmd = f'git clone --config core.filemode=false "{repo_info["url"]}" "{repo_dir}"'
        if not self.run_command(clone_cmd, f"克隆 {repo_name}"):
            logger.error(f"❌ {repo_name} 克隆失败")
            return False

        # 切换到指定的提交
        if repo_info.get('commit'):
            checkout_cmd = f'git checkout {repo_info["commit"]}'
            if not self.run_command(checkout_cmd, f"切换 {repo_name} 到指定提交", repo_dir):
                logger.error(f"❌ {repo_name} 切换提交失败")
                return False

        self.progress['git_repos'][repo_name] = True
        self.save_progress()
        logger.info(f"✅ {repo_name} 仓库克隆成功")
        return True

    def install_requirements(self) -> bool:
        """安装 requirements.txt 中的依赖"""
        if self.progress.get('requirements', False):
            logger.info("✅ requirements.txt 依赖已安装")
            return True

        requirements_file = self.script_path / "requirements_versions.txt"
        if not requirements_file.exists():
            requirements_file = self.script_path / "requirements.txt"

        if not requirements_file.exists():
            logger.warning("⚠️ 未找到 requirements 文件")
            return True

        logger.info("📦 安装 requirements.txt 依赖...")

        pip_cmd = self.get_venv_pip()
        cmd = f'{pip_cmd} install -r "{requirements_file}" --prefer-binary'

        if self.run_command(cmd, "安装 requirements 依赖"):
            self.progress['requirements'] = True
            self.save_progress()
            logger.info("✅ requirements.txt 依赖安装成功")
            return True
        else:
            logger.error("❌ requirements.txt 依赖安装失败")
            return False

    def upgrade_pip(self) -> bool:
        """升级 pip"""
        logger.info("🔧 升级 pip...")
        pip_cmd = self.get_venv_pip()
        cmd = f'{pip_cmd} install --upgrade pip'

        if self.run_command(cmd, "升级 pip"):
            logger.info("✅ pip 升级成功")
            return True
        else:
            logger.warning("⚠️ pip 升级失败，继续执行")
            return True  # pip 升级失败不影响后续安装

    def check_git_available(self) -> bool:
        """检查 Git 是否可用"""
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Git 可用: {result.stdout.strip()}")
                return True
            else:
                logger.error("❌ Git 不可用")
                return False
        except FileNotFoundError:
            logger.error("❌ 未找到 Git，请先安装 Git")
            return False

    def check_python_version(self) -> bool:
        """检查 Python 版本"""
        major = sys.version_info.major
        minor = sys.version_info.minor

        logger.info(f"🐍 Python 版本: {major}.{minor}.{sys.version_info.micro}")

        if major == 3 and minor >= 8:
            logger.info("✅ Python 版本符合要求")
            return True
        else:
            logger.error("❌ Python 版本不符合要求，需要 Python 3.8 或更高版本")
            return False

    def download_all(self) -> bool:
        """下载所有必要的文件和依赖"""
        logger.info("🚀 开始下载 Stable Diffusion WebUI 所需的所有文件...")

        # 检查系统要求
        if not self.check_python_version():
            return False

        if not self.check_git_available():
            return False

        # 创建虚拟环境
        if not self.create_virtual_environment():
            return False

        # 升级 pip
        if not self.upgrade_pip():
            return False

        # 安装 Python 包
        logger.info("📦 开始安装 Python 包...")

        # 首先安装PyTorch（优先本地，不兼容则在线下载）
        logger.info("🔥 安装 PyTorch...")
        if not self.install_torch_from_local_or_online():
            logger.error("❌ PyTorch 安装失败，停止安装")
            return False

        # 安装其他包
        for package_name, package_spec in self.python_packages.items():
            if not self.install_python_package(package_name, package_spec):
                logger.error(f"❌ {package_name} 安装失败，停止安装")
                return False

        # 克隆 Git 仓库
        logger.info("📥 开始克隆 Git 仓库...")
        for repo_name, repo_info in self.git_repos.items():
            if not self.clone_git_repository(repo_name, repo_info):
                logger.error(f"❌ {repo_name} 克隆失败，停止安装")
                return False

        # 安装 requirements.txt 依赖
        if not self.install_requirements():
            return False

        logger.info("🎉 所有文件和依赖下载安装完成！")
        logger.info(f"📁 虚拟环境位置: {self.venv_path}")
        logger.info(f"📁 下载临时文件位置: {self.download_dir}")

        return True

    def show_status(self):
        """显示当前下载状态"""
        logger.info("📊 当前下载状态:")

        # 检查虚拟环境实际状态
        venv_exists = self.venv_path.exists() and Path(self.get_venv_python()).exists()
        venv_status = "✅ 已创建" if venv_exists else "❌ 未创建"
        logger.info(f"虚拟环境: {venv_status} ({self.venv_path})")

        logger.info("Python 包:")
        for package_name in self.python_packages.keys():
            # 检查实际安装状态
            if venv_exists:
                actually_installed = self.check_package_installed(package_name)
                progress_status = self.progress['python_packages'].get(package_name, False)
                if actually_installed and not progress_status:
                    status = "✅ 已安装 (未记录)"
                elif actually_installed and progress_status:
                    status = "✅ 已安装"
                else:
                    status = "❌ 未安装"
            else:
                status = "❌ 未安装 (无虚拟环境)"
            logger.info(f"  {package_name}: {status}")

        logger.info("Git 仓库:")
        for repo_name, repo_info in self.git_repos.items():
            repo_dir = self.script_path / repo_info['dir']
            actually_exists = repo_dir.exists()
            progress_status = self.progress['git_repos'].get(repo_name, False)

            if actually_exists and not progress_status:
                status = "✅ 已克隆 (未记录)"
            elif actually_exists and progress_status:
                status = "✅ 已克隆"
            else:
                status = "❌ 未克隆"
            logger.info(f"  {repo_name}: {status}")

        requirements_status = "✅ 已安装" if self.progress.get('requirements', False) else "❌ 未安装"
        logger.info(f"Requirements: {requirements_status}")

    def clean_download_cache(self):
        """清理下载缓存"""
        logger.info("🧹 清理下载缓存...")
        try:
            if self.download_dir.exists():
                shutil.rmtree(self.download_dir)
                logger.info("✅ 下载缓存清理完成")
            else:
                logger.info("ℹ️ 下载缓存目录不存在")
        except Exception as e:
            logger.error(f"❌ 清理下载缓存失败: {e}")

    def reset_progress(self):
        """重置下载进度"""
        logger.info("🔄 重置下载进度...")
        self.progress = {
            'git_repos': {},
            'python_packages': {},
            'requirements': False,
            'venv_created': False
        }
        self.save_progress()
        logger.info("✅ 下载进度已重置")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Stable Diffusion WebUI 下载程序",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python webui_downloader.py                    # 下载所有文件和依赖
  python webui_downloader.py --status           # 显示下载状态
  python webui_downloader.py --clean            # 清理下载缓存
  python webui_downloader.py --reset            # 重置下载进度
  python webui_downloader.py --retry-count 5    # 设置重试次数为5次
        """
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='显示当前下载状态'
    )

    parser.add_argument(
        '--clean',
        action='store_true',
        help='清理下载缓存'
    )

    parser.add_argument(
        '--reset',
        action='store_true',
        help='重置下载进度'
    )

    parser.add_argument(
        '--retry-count',
        type=int,
        default=RETRY_COUNT,
        help=f'设置重试次数 (默认: {RETRY_COUNT})'
    )

    parser.add_argument(
        '--retry-interval',
        type=int,
        default=RETRY_INTERVAL,
        help=f'设置重试间隔秒数 (默认: {RETRY_INTERVAL})'
    )

    parser.add_argument(
        '--download-dir',
        type=str,
        default=DOWNLOAD_DIR,
        help=f'设置下载目录 (默认: {DOWNLOAD_DIR})'
    )

    parser.add_argument(
        '--venv-dir',
        type=str,
        default=VENV_DIR,
        help=f'设置虚拟环境目录 (默认: {VENV_DIR})'
    )

    args = parser.parse_args()

    try:
        downloader = WebUIDownloader(
            venv_dir=args.venv_dir,
            download_dir=args.download_dir,
            retry_count=args.retry_count,
            retry_interval=args.retry_interval
        )

        if args.status:
            downloader.show_status()
        elif args.clean:
            downloader.clean_download_cache()
        elif args.reset:
            downloader.reset_progress()
        else:
            # 执行下载
            logger.info("🎨 Stable Diffusion WebUI 下载程序")
            logger.info("=" * 50)
            logger.info(f"📁 下载目录: {args.download_dir}")
            logger.info(f"📁 虚拟环境目录: {args.venv_dir}")
            logger.info(f"🔄 重试次数: {args.retry_count}")
            logger.info(f"⏱️ 重试间隔: {args.retry_interval} 秒")
            logger.info("=" * 50)

            success = downloader.download_all()

            if success:
                logger.info("🎉 下载完成！现在可以运行 webui-user.bat 启动 WebUI")
                sys.exit(0)
            else:
                logger.error("❌ 下载失败！请检查错误信息并重试")
                sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n⚠️ 用户中断下载，进度已保存")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 程序执行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
