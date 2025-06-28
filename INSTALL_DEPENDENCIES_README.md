# Stable Diffusion WebUI 依赖安装器

这是一个专为 Stable Diffusion WebUI 项目设计的智能依赖安装脚本，支持断点续传和自动重试功能。

## ✨ 主要特性

- 🔄 **断点续传**：安装过程中断后可以继续，不会重复安装已完成的组件
- 🔁 **自动重试**：网络问题或临时错误时自动重试（最多10次，间隔3秒）
- 🎯 **智能GPU检测**：自动检测NVIDIA GPU、Intel GPU或CPU环境
- 📦 **完整依赖管理**：自动安装PyTorch、所有Python包和Git仓库
- 🛡️ **虚拟环境隔离**：在`.venv`目录创建独立的Python环境
- 📊 **进度跟踪**：实时显示安装进度和状态

## 🚀 快速开始

### Windows 用户

1. **双击运行批处理文件**：
   ```cmd
   install_dependencies.bat
   ```

2. **或者手动运行**：
   ```cmd
   python install_dependencies.py
   ```

### Linux/Mac 用户

1. **运行shell脚本**：
   ```bash
   chmod +x install_dependencies.sh
   ./install_dependencies.sh
   ```

2. **或者手动运行**：
   ```bash
   python3 install_dependencies.py
   ```

## 📋 系统要求

- **Python**: 3.8 或更高版本
- **Git**: 用于克隆仓库
- **网络连接**: 用于下载依赖包
- **磁盘空间**: 至少 10GB 可用空间

### GPU 支持

- **NVIDIA GPU**: 自动安装 CUDA 版本的 PyTorch
- **Intel GPU**: 自动安装 Intel XPU 版本
- **CPU**: 安装 CPU 版本的 PyTorch

## 🔧 安装过程

脚本会按以下顺序执行：

1. **环境检测** - 检测GPU类型和Python版本
2. **虚拟环境** - 创建`.venv`虚拟环境
3. **PyTorch安装** - 根据GPU类型安装对应版本
4. **Python包** - 安装`requirements_versions.txt`中的所有包
5. **额外包** - 安装CLIP和OpenCLIP
6. **Git仓库** - 克隆必要的代码仓库
7. **验证** - 验证关键组件是否正确安装

## 📁 安装内容

### Python 包
- PyTorch + TorchVision (GPU/CPU版本)
- Gradio (Web界面)
- Transformers (AI模型)
- Accelerate (训练加速)
- SafeTensors (模型格式)
- 以及其他50+个依赖包

### Git 仓库
- stable-diffusion-webui-assets
- stable-diffusion-stability-ai
- generative-models (SDXL)
- k-diffusion
- BLIP

## 🛠️ 故障排除

### 常见问题

**Q: 安装过程中网络中断怎么办？**
A: 重新运行脚本即可，支持断点续传，不会重复安装已完成的组件。

**Q: 某个包安装失败怎么办？**
A: 脚本会自动重试10次。如果仍然失败，可以手动安装该包后重新运行脚本。

**Q: 如何重新安装某个组件？**
A: 编辑`install_progress.json`文件，删除对应的完成标记，然后重新运行脚本。

**Q: 如何完全重新安装？**
A: 删除`.venv`目录和`install_progress.json`文件，然后重新运行脚本。

### 手动修复

如果自动安装失败，可以手动执行以下步骤：

1. **激活虚拟环境**：
   ```bash
   # Windows
   .venv\Scripts\activate.bat
   
   # Linux/Mac
   source .venv/bin/activate
   ```

2. **手动安装失败的包**：
   ```bash
   pip install 包名
   ```

3. **更新进度文件**：
   在`install_progress.json`中添加已安装的包名。

## 📊 进度文件说明

`install_progress.json` 文件记录安装进度：

```json
{
  "venv_created": true,
  "torch_installed": true,
  "requirements_installed": true,
  "repos_cloned": true,
  "installed_packages": ["package1", "package2"],
  "cloned_repos": ["repo1", "repo2"]
}
```

## 🎯 使用建议

1. **网络环境**：建议在网络稳定的环境下运行
2. **磁盘空间**：确保有足够的磁盘空间（推荐15GB+）
3. **权限**：确保有写入当前目录的权限
4. **防火墙**：确保Python和Git可以访问网络

## 📞 技术支持

如果遇到问题：

1. 查看控制台输出的详细错误信息
2. 检查`install_progress.json`文件确认进度
3. 尝试手动安装失败的组件
4. 重新运行脚本（支持断点续传）

## 🔄 更新说明

- 支持最新的PyTorch 2.1.2版本
- 兼容CUDA 12.1和11.8
- 支持Intel XPU和CPU模式
- 优化了网络重试机制
- 改进了进度跟踪功能
