#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stable Diffusion WebUI 模型下载器
支持断点续传和多次重试
"""

import os
import sys
import requests
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelDownloader:
    def __init__(self, base_dir: str = ".", download_dir: str = "D:/download"):
        self.base_dir = Path(base_dir)
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        # 模型配置
        self.models = {
            # 必需模型
            "sd_1_5": {
                "name": "Stable Diffusion 1.5",
                "url": "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors",
                "target": "models/Stable-diffusion/v1-5-pruned-emaonly.safetensors",
                "size": "3.97GB",
                "priority": 1,
                "required": True
            },
            
            # 推荐模型
            "vae_mse": {
                "name": "VAE MSE",
                "url": "https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors",
                "target": "models/VAE/vae-ft-mse-840000-ema-pruned.safetensors",
                "size": "335MB",
                "priority": 2,
                "required": False
            },
            
            "realesrgan": {
                "name": "RealESRGAN 4x",
                "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
                "target": "models/ESRGAN/RealESRGAN_x4plus.pth",
                "size": "67MB",
                "priority": 3,
                "required": False
            },
            
            "gfpgan": {
                "name": "GFPGAN v1.4",
                "url": "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth",
                "target": "models/GFPGAN/GFPGANv1.4.pth",
                "size": "348MB",
                "priority": 4,
                "required": False
            }
        }
    
    def download_with_resume(self, url: str, target_path: Path, max_retries: int = 10) -> bool:
        """支持断点续传的下载函数"""
        target_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.download_dir / f"{target_path.name}.tmp"
        
        # 检查已下载的大小
        resume_pos = 0
        if temp_path.exists():
            resume_pos = temp_path.stat().st_size
            logger.info(f"发现临时文件，从 {resume_pos} 字节处继续下载")
        
        headers = {}
        if resume_pos > 0:
            headers['Range'] = f'bytes={resume_pos}-'
        
        for attempt in range(max_retries):
            try:
                logger.info(f"开始下载 {url} (尝试 {attempt + 1}/{max_retries})")
                
                response = requests.get(url, headers=headers, stream=True, timeout=30)
                
                # 检查是否支持断点续传
                if resume_pos > 0 and response.status_code not in [206, 200]:
                    logger.warning("服务器不支持断点续传，重新开始下载")
                    resume_pos = 0
                    headers = {}
                    temp_path.unlink(missing_ok=True)
                    continue
                
                response.raise_for_status()
                
                # 获取文件总大小
                if 'content-length' in response.headers:
                    total_size = int(response.headers['content-length'])
                    if resume_pos > 0:
                        total_size += resume_pos
                else:
                    total_size = None
                
                # 下载文件
                mode = 'ab' if resume_pos > 0 else 'wb'
                downloaded = resume_pos
                
                with open(temp_path, mode) as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # 显示进度
                            if total_size:
                                progress = (downloaded / total_size) * 100
                                print(f"\r下载进度: {downloaded:,} / {total_size:,} 字节 ({progress:.1f}%)", end='')
                            else:
                                print(f"\r已下载: {downloaded:,} 字节", end='')
                
                print()  # 换行
                
                # 下载完成，移动到目标位置
                target_path.parent.mkdir(parents=True, exist_ok=True)
                temp_path.rename(target_path)
                logger.info(f"✅ 下载完成: {target_path}")
                return True
                
            except requests.exceptions.RequestException as e:
                logger.error(f"下载失败 (尝试 {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    logger.info("3秒后重试...")
                    import time
                    time.sleep(3)
                else:
                    logger.error(f"❌ 下载失败，已达到最大重试次数: {url}")
                    return False
            except Exception as e:
                logger.error(f"下载异常: {e}")
                return False
        
        return False
    
    def check_model_exists(self, model_key: str) -> bool:
        """检查模型是否已存在"""
        model = self.models[model_key]
        target_path = self.base_dir / model["target"]
        return target_path.exists()
    
    def download_model(self, model_key: str) -> bool:
        """下载单个模型"""
        if model_key not in self.models:
            logger.error(f"未知模型: {model_key}")
            return False
        
        model = self.models[model_key]
        target_path = self.base_dir / model["target"]
        
        if self.check_model_exists(model_key):
            logger.info(f"✅ 模型已存在: {model['name']}")
            return True
        
        logger.info(f"📦 开始下载: {model['name']} ({model['size']})")
        logger.info(f"📍 目标位置: {target_path}")
        
        return self.download_with_resume(model["url"], target_path)
    
    def download_required_models(self) -> bool:
        """下载所有必需的模型"""
        logger.info("🚀 开始下载必需模型...")
        
        required_models = [k for k, v in self.models.items() if v["required"]]
        required_models.sort(key=lambda k: self.models[k]["priority"])
        
        success_count = 0
        for model_key in required_models:
            if self.download_model(model_key):
                success_count += 1
            else:
                logger.error(f"❌ 必需模型下载失败: {self.models[model_key]['name']}")
                return False
        
        logger.info(f"🎉 必需模型下载完成: {success_count}/{len(required_models)}")
        return True
    
    def download_all_models(self) -> bool:
        """下载所有模型"""
        logger.info("🚀 开始下载所有模型...")
        
        all_models = list(self.models.keys())
        all_models.sort(key=lambda k: self.models[k]["priority"])
        
        success_count = 0
        for model_key in all_models:
            if self.download_model(model_key):
                success_count += 1
        
        logger.info(f"🎉 模型下载完成: {success_count}/{len(all_models)}")
        return success_count == len(all_models)
    
    def show_status(self):
        """显示模型状态"""
        logger.info("📊 模型状态:")
        
        for model_key, model in self.models.items():
            status = "✅ 已安装" if self.check_model_exists(model_key) else "❌ 未安装"
            required = "必需" if model["required"] else "可选"
            logger.info(f"  {model['name']}: {status} ({required}, {model['size']})")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Stable Diffusion WebUI 模型下载器")
    parser.add_argument("--all", action="store_true", help="下载所有模型")
    parser.add_argument("--required", action="store_true", help="只下载必需模型")
    parser.add_argument("--status", action="store_true", help="显示模型状态")
    parser.add_argument("--model", type=str, help="下载指定模型")
    parser.add_argument("--base-dir", type=str, default=".", help="WebUI基础目录")
    parser.add_argument("--download-dir", type=str, default="D:/download", help="临时下载目录")
    
    args = parser.parse_args()
    
    downloader = ModelDownloader(args.base_dir, args.download_dir)
    
    if args.status:
        downloader.show_status()
    elif args.all:
        downloader.download_all_models()
    elif args.required:
        downloader.download_required_models()
    elif args.model:
        downloader.download_model(args.model)
    else:
        logger.info("使用 --help 查看帮助信息")
        downloader.show_status()

if __name__ == "__main__":
    main()
