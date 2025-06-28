# Stable Diffusion WebUI 启动模型下载清单

## 📋 从启动日志分析的模型需求

### 🎯 主要模型文件

#### 1. **Stable Diffusion 1.5 基础模型** ⚠️ (下载中断)
- **文件名**: `v1-5-pruned-emaonly.safetensors`
- **下载地址**: `https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors`
- **目标位置**: `D:\david\sd-webui\models\Stable-diffusion\v1-5-pruned-emaonly.safetensors`
- **文件大小**: 3.97GB
- **状态**: 下载中断 (已下载约241MB/1.72GB)
- **错误**: ChunkedEncodingError - 网络连接中断
- **用途**: 主要的图像生成模型

#### 2. **CLIP文本编码器模型** ❌ (下载失败)
- **模型类型**: CLIPTextModel
- **下载地址**: `https://huggingface.co/openai/clip-vit-large-patch14/resolve/main/`
- **相关文件**:
  - `config.json`
  - `model.safetensors` 或 `pytorch_model.bin`
  - `tokenizer.json`
  - `tokenizer_config.json`
  - `vocab.json`
  - `merges.txt`
- **目标位置**: `~/.cache/huggingface/transformers/` (自动缓存)
- **错误**: RepositoryNotFoundError - 仓库访问失败
- **用途**: 文本到图像的编码器

#### 3. **CLIP Vision模型** (推断需要)
- **模型名称**: `clip-vit-large-patch14`
- **下载地址**: `https://huggingface.co/openai/clip-vit-large-patch14/resolve/main/`
- **目标位置**: `~/.cache/huggingface/transformers/`
- **用途**: 图像理解和文本匹配

## 📁 模型存放目录结构

```
D:\david\sd-webui\models\
├── Stable-diffusion\           # 主模型目录
│   ├── v1-5-pruned-emaonly.safetensors  # SD 1.5基础模型 ✅
│   └── [其他SD模型文件]
├── VAE\                        # VAE模型目录
│   └── [VAE模型文件]
├── Lora\                       # LoRA模型目录
│   └── [LoRA模型文件]
├── ControlNet\                 # ControlNet模型目录
│   └── [ControlNet模型文件]
├── ESRGAN\                     # 超分辨率模型目录
│   └── [ESRGAN模型文件]
├── GFPGAN\                     # 面部修复模型目录
│   └── [GFPGAN模型文件]
├── BLIP\                       # 图像描述模型目录
│   └── [BLIP模型文件]
├── Codeformer\                 # 面部修复模型目录
│   └── [Codeformer模型文件]
└── embeddings\                 # 文本嵌入目录
    └── [embedding文件]
```

## 🔍 其他可能需要的模型

### 2. **VAE模型** (可选但推荐)
- **文件名**: `vae-ft-mse-840000-ema-pruned.safetensors`
- **下载地址**: `https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors`
- **目标位置**: `D:\david\sd-webui\models\VAE\vae-ft-mse-840000-ema-pruned.safetensors`
- **文件大小**: ~335MB
- **用途**: 改善图像质量和色彩

### 3. **CLIP模型** (自动下载)
- **来源**: Hugging Face transformers
- **缓存位置**: `~/.cache/huggingface/transformers/`
- **用途**: 文本编码

### 4. **超分辨率模型** (可选)
- **ESRGAN模型**:
  - `RealESRGAN_x4plus.pth`
  - 下载地址: `https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth`
  - 目标位置: `D:\david\sd-webui\models\ESRGAN\RealESRGAN_x4plus.pth`

### 5. **面部修复模型** (可选)
- **GFPGAN模型**:
  - `GFPGANv1.4.pth`
  - 下载地址: `https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth`
  - 目标位置: `D:\david\sd-webui\models\GFPGAN\GFPGANv1.4.pth`

## 🚨 当前问题分析

### 1. **网络连接问题** ⚠️
- **错误**: `ChunkedEncodingError` - 连接中断
- **影响**: SD 1.5模型下载中断 (241MB/1.72GB)
- **原因**: 网络不稳定或服务器连接问题
- **解决方案**: 使用断点续传或更换网络

### 2. **Hugging Face访问问题** ❌
- **错误**: `RepositoryNotFoundError: 401 Client Error`
- **影响**: CLIP模型无法下载
- **原因**:
  - 网络访问Hugging Face受限
  - 可能需要代理或镜像站点
  - 模型仓库路径错误 (`https://huggingface.co/None/`)
- **解决方案**:
  - 配置Hugging Face镜像
  - 手动下载CLIP模型
  - 检查网络连接

### 3. **pydantic版本冲突** ⚠️
- **错误**: `AttributeError: __config__`
- **原因**: pydantic v2与gradio v3.41.2不兼容
- **解决方案**: 降级pydantic到v1.x

### 4. **模型加载失败** ❌
- **错误**: `No checkpoints found` 和 `FileNotFoundError`
- **原因**: 主模型下载未完成
- **解决方案**: 完成模型下载后重启

## 💡 建议的下载策略

### 方法一：等待自动下载完成
```bash
# 让WebUI继续运行，等待模型下载完成
# 下载完成后重启WebUI
```

### 方法二：手动下载核心模型
```bash
# 使用下载工具下载SD 1.5模型
# 放置到正确的目录后重启WebUI
```

### 方法三：使用下载脚本
```python
# 创建专门的模型下载脚本
# 支持断点续传和多线程下载
```

## 📊 下载优先级

### 🔥 必需模型 (启动必须)
1. **Stable Diffusion 1.5**: 3.97GB ⭐⭐⭐⭐⭐

### 🌟 推荐模型 (提升体验)
2. **VAE模型**: 335MB ⭐⭐⭐⭐
3. **ESRGAN超分**: 67MB ⭐⭐⭐
4. **GFPGAN面部修复**: 348MB ⭐⭐⭐

### 📦 可选模型 (扩展功能)
5. **ControlNet模型**: 各种大小 ⭐⭐
6. **LoRA模型**: 各种大小 ⭐⭐
7. **其他SD模型**: 各种大小 ⭐

## 🔧 下载建议

1. **网络要求**: 稳定的网络连接，建议使用有线网络
2. **存储空间**: 至少10GB可用空间
3. **下载时间**: SD 1.5模型约需30-60分钟（取决于网速）
4. **断点续传**: 支持中断后继续下载

## 📝 下载状态监控

当前SD 1.5模型下载进度：
- **已下载**: ~139MB / 3.97GB (约3.5%)
- **预计剩余时间**: 约30-45分钟
- **下载速度**: 约4-6MB/s

建议等待下载完成后再重启WebUI，或者手动下载模型文件以加快进度。
