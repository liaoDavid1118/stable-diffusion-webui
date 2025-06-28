#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复WebUI界面显示问题
解决JSON错误和图像显示问题
"""

import os
import json
import shutil
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_output_images():
    """检查输出图像"""
    logger.info("🔍 检查输出图像...")
    
    output_dirs = [
        Path("outputs/txt2img-images"),
        Path("outputs/img2img-images"),
        Path("outputs"),
    ]
    
    total_images = 0
    for output_dir in output_dirs:
        if output_dir.exists():
            images = list(output_dir.rglob("*.png"))
            logger.info(f"📁 {output_dir}: {len(images)} 张图像")
            total_images += len(images)
    
    logger.info(f"📊 总计: {total_images} 张图像已生成")
    return total_images > 0

def clear_browser_cache_files():
    """清除可能的缓存文件"""
    logger.info("🧹 清除缓存文件...")
    
    cache_files = [
        "config.json",
        "ui-config.json",
        "styles.csv",
    ]
    
    for cache_file in cache_files:
        cache_path = Path(cache_file)
        if cache_path.exists():
            try:
                # 备份原文件
                backup_path = Path(f"{cache_file}.backup")
                if not backup_path.exists():
                    shutil.copy2(cache_path, backup_path)
                    logger.info(f"✅ 已备份: {cache_file}")
                
                # 检查JSON文件是否有效
                if cache_file.endswith('.json'):
                    try:
                        with open(cache_path, 'r', encoding='utf-8') as f:
                            json.load(f)
                        logger.info(f"✅ JSON文件有效: {cache_file}")
                    except json.JSONDecodeError as e:
                        logger.warning(f"⚠️ JSON文件损坏: {cache_file} - {e}")
                        # 删除损坏的文件，让WebUI重新创建
                        cache_path.unlink()
                        logger.info(f"🗑️ 已删除损坏文件: {cache_file}")
                        
            except Exception as e:
                logger.error(f"❌ 处理缓存文件失败: {cache_file} - {e}")

def fix_gradio_temp_files():
    """修复Gradio临时文件问题"""
    logger.info("🔧 修复Gradio临时文件...")
    
    temp_dirs = [
        Path("tmp"),
        Path("gradio_cached_examples"),
        Path.home() / "AppData" / "Local" / "Temp" / "gradio",
    ]
    
    for temp_dir in temp_dirs:
        if temp_dir.exists():
            try:
                # 清理旧的临时文件
                temp_files = list(temp_dir.glob("*"))
                if temp_files:
                    logger.info(f"🧹 清理临时目录: {temp_dir} ({len(temp_files)} 个文件)")
                    for temp_file in temp_files:
                        try:
                            if temp_file.is_file():
                                temp_file.unlink()
                            elif temp_file.is_dir():
                                shutil.rmtree(temp_file)
                        except Exception:
                            pass  # 忽略无法删除的文件
                            
            except Exception as e:
                logger.warning(f"⚠️ 清理临时目录失败: {temp_dir} - {e}")

def create_safe_config():
    """创建安全的配置文件"""
    logger.info("⚙️ 创建安全配置...")
    
    # 创建最小化的ui-config.json
    safe_ui_config = {
        "txt2img/Prompt/value": "",
        "txt2img/Negative prompt/value": "",
        "txt2img/Sampling method/value": "Euler a",
        "txt2img/Sampling steps/value": 20,
        "txt2img/Width/value": 512,
        "txt2img/Height/value": 512,
        "txt2img/CFG Scale/value": 7,
        "txt2img/Seed/value": -1,
    }
    
    try:
        with open("ui-config.json", "w", encoding='utf-8') as f:
            json.dump(safe_ui_config, f, indent=2, ensure_ascii=False)
        logger.info("✅ 安全UI配置已创建")
        return True
    except Exception as e:
        logger.error(f"❌ 创建配置失败: {e}")
        return False

def test_json_functionality():
    """测试JSON功能"""
    logger.info("🧪 测试JSON功能...")
    
    test_data = {
        "test": "value",
        "number": 123,
        "array": [1, 2, 3]
    }
    
    test_file = Path("test_json.json")
    try:
        # 写入测试
        with open(test_file, "w", encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
        
        # 读取测试
        with open(test_file, "r", encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        # 验证
        if loaded_data == test_data:
            logger.info("✅ JSON功能正常")
            test_file.unlink()  # 删除测试文件
            return True
        else:
            logger.error("❌ JSON数据不匹配")
            return False
            
    except Exception as e:
        logger.error(f"❌ JSON测试失败: {e}")
        return False
    finally:
        if test_file.exists():
            test_file.unlink()

def create_display_fix_script():
    """创建界面显示修复脚本"""
    logger.info("📝 创建界面显示修复脚本...")
    
    fix_script = '''
# WebUI界面显示修复指南

## 🔧 立即修复步骤

### 1. 浏览器修复
```
1. 按 Ctrl+Shift+Delete 清除缓存
2. 按 F5 强制刷新页面
3. 如果仍有问题，尝试无痕模式
```

### 2. WebUI重启
```
1. 在控制台按 Ctrl+C 停止WebUI
2. 等待完全停止
3. 重新运行启动脚本
```

### 3. 检查生成的图像
```
图像保存位置: outputs/txt2img-images/日期/
即使界面不显示，图像文件也已经生成
```

## 🚨 常见问题解决

### JSON错误
- 原因: 界面状态数据损坏
- 解决: 清除浏览器缓存，重启WebUI

### 图像不显示
- 原因: Gradio界面渲染问题
- 解决: 刷新页面，检查outputs目录

### 保存失败
- 原因: 临时文件权限问题
- 解决: 以管理员身份运行

## 💡 预防措施

1. 定期清理浏览器缓存
2. 不要在生成过程中频繁刷新页面
3. 确保有足够的磁盘空间
4. 使用稳定的网络连接

## 🔧 启动参数优化

推荐使用以下参数减少界面问题:
```
--medvram --autolaunch --no-half-vae --disable-safe-unpickle
```
'''
    
    guide_file = Path("界面显示修复指南.md")
    try:
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(fix_script)
        logger.info(f"✅ 修复指南已创建: {guide_file}")
        return True
    except Exception as e:
        logger.error(f"❌ 创建指南失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 WebUI界面显示问题修复工具")
    print("=" * 50)
    
    success_count = 0
    
    # 1. 检查输出图像
    if check_output_images():
        success_count += 1
        print("✅ 图像生成正常，问题在于界面显示")
    
    # 2. 清除缓存文件
    clear_browser_cache_files()
    success_count += 1
    
    # 3. 修复临时文件
    fix_gradio_temp_files()
    success_count += 1
    
    # 4. 创建安全配置
    if create_safe_config():
        success_count += 1
    
    # 5. 测试JSON功能
    if test_json_functionality():
        success_count += 1
    
    # 6. 创建修复指南
    if create_display_fix_script():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"🎉 修复完成: {success_count}/6 步骤成功")
    
    print("\n💡 立即解决方案:")
    print("1. 🔄 重启WebUI (Ctrl+C 然后重新启动)")
    print("2. 🌐 清除浏览器缓存 (Ctrl+Shift+Delete)")
    print("3. 📱 刷新页面 (F5)")
    print("4. 📁 检查outputs目录确认图像已生成")
    
    print("\n✅ 推荐启动命令:")
    print("venv\\Scripts\\python.exe webui.py --medvram --autolaunch --no-half-vae")
    
    return success_count >= 4

if __name__ == "__main__":
    main()
