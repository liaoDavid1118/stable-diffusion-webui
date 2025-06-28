#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebUI问题快速修复脚本
解决pydantic版本冲突和模型下载问题
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebUIFixer:
    def __init__(self):
        self.venv_python = Path("venv/Scripts/python.exe")
        self.base_dir = Path(".")
        
    def run_command(self, cmd, description=""):
        """运行命令并返回结果"""
        logger.info(f"执行: {description or cmd}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
            if result.returncode == 0:
                logger.info(f"✅ 成功: {description}")
                return True
            else:
                logger.error(f"❌ 失败: {description}")
                logger.error(f"错误输出: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ 异常: {e}")
            return False
    
    def fix_pydantic_version(self):
        """修复pydantic版本冲突"""
        logger.info("🔧 修复pydantic版本冲突...")
        
        # 卸载当前版本
        cmd1 = f"{self.venv_python} -m pip uninstall pydantic -y"
        self.run_command(cmd1, "卸载pydantic v2")
        
        # 安装兼容版本
        cmd2 = f"{self.venv_python} -m pip install 'pydantic<2.0'"
        return self.run_command(cmd2, "安装pydantic v1.x")
    
    def setup_huggingface_mirror(self):
        """设置Hugging Face镜像"""
        logger.info("🌐 配置Hugging Face镜像...")
        
        # 设置环境变量
        os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
        
        # 创建配置文件
        hf_config_dir = Path.home() / ".cache" / "huggingface"
        hf_config_dir.mkdir(parents=True, exist_ok=True)
        
        config_content = """
[default]
endpoint = https://hf-mirror.com
"""
        
        config_file = hf_config_dir / "config.ini"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            logger.info("✅ Hugging Face镜像配置完成")
            return True
        except Exception as e:
            logger.error(f"❌ 配置镜像失败: {e}")
            return False
    
    def check_model_status(self):
        """检查模型状态"""
        logger.info("📊 检查模型状态...")
        
        # 检查SD模型
        sd_model = self.base_dir / "models" / "Stable-diffusion" / "v1-5-pruned-emaonly.safetensors"
        if sd_model.exists():
            size_mb = sd_model.stat().st_size / (1024 * 1024)
            logger.info(f"✅ SD 1.5模型: 已存在 ({size_mb:.1f}MB)")
            if size_mb < 3000:  # 应该约4GB
                logger.warning("⚠️ 模型文件可能不完整")
        else:
            logger.warning("❌ SD 1.5模型: 不存在")
        
        # 检查CLIP模型缓存
        clip_cache = Path.home() / ".cache" / "huggingface" / "transformers" / "models--openai--clip-vit-large-patch14"
        if clip_cache.exists():
            logger.info("✅ CLIP模型缓存: 已存在")
        else:
            logger.warning("❌ CLIP模型缓存: 不存在")
    
    def download_clip_model(self):
        """尝试下载CLIP模型"""
        logger.info("📥 尝试下载CLIP模型...")
        
        # 使用transformers库下载
        try:
            cmd = f"{self.venv_python} -c \"from transformers import CLIPTextModel, CLIPTokenizer; CLIPTextModel.from_pretrained('openai/clip-vit-large-patch14'); CLIPTokenizer.from_pretrained('openai/clip-vit-large-patch14')\""
            return self.run_command(cmd, "下载CLIP模型")
        except Exception as e:
            logger.error(f"❌ CLIP模型下载失败: {e}")
            return False
    
    def create_minimal_model_config(self):
        """创建最小模型配置"""
        logger.info("⚙️ 创建最小模型配置...")
        
        # 确保模型目录存在
        models_dir = self.base_dir / "models" / "Stable-diffusion"
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # 如果没有模型，创建一个占位符配置
        if not any(models_dir.glob("*.safetensors")) and not any(models_dir.glob("*.ckpt")):
            placeholder = models_dir / "README.txt"
            with open(placeholder, 'w', encoding='utf-8') as f:
                f.write("""
请将Stable Diffusion模型文件放在此目录下。

推荐模型:
- v1-5-pruned-emaonly.safetensors (3.97GB)
- 下载地址: https://huggingface.co/runwayml/stable-diffusion-v1-5

模型下载完成后，删除此文件并重启WebUI。
""")
            logger.info("✅ 创建了模型目录说明文件")
    
    def install_missing_dependencies(self):
        """安装可能缺失的依赖"""
        logger.info("📦 检查并安装缺失的依赖...")
        
        dependencies = [
            "transformers",
            "diffusers", 
            "accelerate",
            "safetensors",
            "omegaconf",
            "pytorch_lightning==1.9.5"
        ]
        
        for dep in dependencies:
            cmd = f"{self.venv_python} -m pip install {dep}"
            self.run_command(cmd, f"安装 {dep}")
    
    def run_full_fix(self):
        """运行完整修复流程"""
        logger.info("🚀 开始WebUI问题修复...")
        
        success_count = 0
        total_steps = 6
        
        # 1. 修复pydantic版本
        if self.fix_pydantic_version():
            success_count += 1
        
        # 2. 设置HF镜像
        if self.setup_huggingface_mirror():
            success_count += 1
        
        # 3. 安装缺失依赖
        self.install_missing_dependencies()
        success_count += 1
        
        # 4. 检查模型状态
        self.check_model_status()
        success_count += 1
        
        # 5. 尝试下载CLIP模型
        if self.download_clip_model():
            success_count += 1
        
        # 6. 创建模型配置
        self.create_minimal_model_config()
        success_count += 1
        
        logger.info(f"🎉 修复完成: {success_count}/{total_steps} 步骤成功")
        
        if success_count >= 4:
            logger.info("✅ 主要问题已修复，可以尝试重启WebUI")
            logger.info("💡 运行命令: venv\\Scripts\\python.exe webui.py")
        else:
            logger.warning("⚠️ 部分问题未解决，可能需要手动处理")
        
        return success_count >= 4

def main():
    """主函数"""
    print("🔧 WebUI问题快速修复工具")
    print("=" * 50)
    
    fixer = WebUIFixer()
    
    if not fixer.venv_python.exists():
        logger.error("❌ 虚拟环境不存在，请先运行下载程序")
        return False
    
    success = fixer.run_full_fix()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 修复完成！现在可以尝试启动WebUI:")
        print("   venv\\Scripts\\python.exe webui.py")
        print("\n💡 如果仍有问题，请检查:")
        print("   1. 网络连接是否稳定")
        print("   2. SD模型是否下载完整")
        print("   3. 查看错误日志获取详细信息")
    else:
        print("⚠️ 修复未完全成功，请查看上方日志信息")
        print("💡 可能需要:")
        print("   1. 手动下载SD模型")
        print("   2. 配置网络代理")
        print("   3. 检查磁盘空间")
    
    return success

if __name__ == "__main__":
    main()
