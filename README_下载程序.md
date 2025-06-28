# Stable Diffusion WebUI 下载程序

## 🎯 项目概述

这是一个专门为 Stable Diffusion WebUI 设计的下载程序，参考了 `main.py` 中的下载方法，重新编写了支持断点续传和多次重试功能的下载程序。程序会自动下载 `webui-user.bat` 中涉及到的所有必要文件和依赖。

## ✨ 主要特性

- ✅ **断点续传**: 支持中断后继续下载，避免重复下载
- ✅ **自动重试**: 默认重试10次，间隔3秒，确保下载成功
- ✅ **现有环境兼容**: 自动检测并使用现有的 `venv` 虚拟环境
- ✅ **智能包检测**: 自动扫描已安装的Python包，避免重复安装
- ✅ **进度保存**: 下载进度自动保存，支持中断后继续
- ✅ **临时文件管理**: 下载临时文件统一存放在 `D:/download` 目录
- ✅ **详细日志**: 提供详细的下载和安装日志

## 📁 文件说明

| 文件名 | 说明 |
|--------|------|
| `webui_downloader.py` | 主下载程序，Python脚本 |
| `download_webui.bat` | Windows批处理启动器 |
| `test_downloader.py` | 测试程序，验证下载功能 |
| `下载程序使用说明.md` | 详细使用说明文档 |
| `README_下载程序.md` | 本文档 |

## 🚀 快速开始

### 方法一：使用批处理文件（推荐）
```bash
# 双击运行
download_webui.bat
```

### 方法二：使用Python命令
```bash
# 基本下载
python webui_downloader.py

# 查看状态
python webui_downloader.py --status

# 测试功能
python test_downloader.py
```

## 📋 下载内容清单

### Python 包
- **torch**: PyTorch深度学习框架 (CUDA 12.1)
- **clip**: OpenAI的CLIP模型
- **open_clip**: 开源CLIP实现
- **xformers**: 内存优化库

### Git 仓库
- **stable-diffusion-webui-assets**: WebUI资源文件
- **stable-diffusion-stability-ai**: Stable Diffusion核心
- **generative-models**: Stable Diffusion XL
- **k-diffusion**: K-diffusion采样器
- **BLIP**: 图像描述模型

### 依赖文件
- **requirements.txt**: Python依赖包

## 🔧 技术特点

### 参考 main.py 的下载方法
程序参考了 `main.py` 中的 `download_with_resume_and_retry` 函数：
- 支持HTTP Range请求实现断点续传
- 智能处理416状态码（Range Not Satisfiable）
- 使用tqdm显示下载进度
- 异常处理和自动重试机制

### 虚拟环境管理
- 自动检测现有的 `venv` 目录
- 扫描已安装的Python包，避免重复安装
- 支持创建新的虚拟环境（如果需要）

### 进度管理
- JSON格式保存下载进度
- 支持中断后继续下载
- 智能状态检测和显示

## 📊 测试结果

运行 `python test_downloader.py` 的测试结果：
```
🚀 开始测试下载程序...
📋 运行测试: 虚拟环境检测
✅ 虚拟环境检测 通过
📋 运行测试: Git仓库克隆  
✅ Git仓库克隆 通过
📊 测试结果: 2/2 通过
🎉 所有测试通过！
```

## 🎯 使用场景

1. **首次安装**: 全新环境下载所有依赖
2. **环境修复**: 修复损坏或缺失的依赖
3. **增量更新**: 只下载缺失的组件
4. **网络中断恢复**: 断网后继续下载

## 💡 设计亮点

### 1. 智能检测
- 检测现有虚拟环境和已安装包
- 避免重复下载和安装
- 自动更新进度记录

### 2. 容错机制
- 网络中断自动重试
- 损坏文件重新下载
- 详细错误日志记录

### 3. 用户友好
- 中文界面和提示
- 详细的进度显示
- 清晰的状态报告

## 🔍 命令行选项

```bash
python webui_downloader.py [选项]

选项:
  --status              显示当前下载状态
  --clean               清理下载缓存
  --reset               重置下载进度
  --retry-count N       设置重试次数 (默认: 10)
  --retry-interval N    设置重试间隔秒数 (默认: 3)
  --download-dir PATH   设置下载目录 (默认: D:/download)
  --venv-dir PATH       设置虚拟环境目录 (默认: venv)
```

## 📝 更新日志

- **v1.0**: 初始版本
  - 参考 main.py 实现断点续传下载
  - 支持现有 venv 虚拟环境
  - 智能包检测和进度管理
  - 完整的测试覆盖

## 🤝 技术支持

如遇问题，请：
1. 查看 `webui_downloader.log` 日志
2. 运行 `python webui_downloader.py --status` 检查状态
3. 运行 `python test_downloader.py` 测试功能
4. 使用 `--reset` 选项重置进度后重试

## 📄 许可证

本项目遵循与 Stable Diffusion WebUI 相同的许可证。
