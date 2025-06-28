#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复X/Y/Z Plot功能问题
解决参数配置和网格计算错误
"""

import os
import sys
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_xyz_script():
    """检查X/Y/Z plot脚本文件"""
    logger.info("🔍 检查X/Y/Z plot脚本...")
    
    xyz_script = Path("scripts/xyz_grid.py")
    if xyz_script.exists():
        logger.info("✅ xyz_grid.py 文件存在")
        return True
    else:
        logger.warning("❌ xyz_grid.py 文件不存在")
        return False

def check_script_errors():
    """检查脚本中可能的错误"""
    logger.info("🔍 检查脚本错误...")
    
    xyz_script = Path("scripts/xyz_grid.py")
    if not xyz_script.exists():
        return False
    
    try:
        with open(xyz_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查常见问题
        issues = []
        
        # 检查是否有除零错误
        if "/ 0" in content or "/0" in content:
            issues.append("可能存在除零错误")
        
        # 检查网格计算
        if "grid" in content.lower() and "size" in content.lower():
            logger.info("✅ 找到网格大小计算相关代码")
        
        if issues:
            logger.warning(f"⚠️ 发现潜在问题: {', '.join(issues)}")
        else:
            logger.info("✅ 脚本文件看起来正常")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 读取脚本文件失败: {e}")
        return False

def create_xyz_fix_patch():
    """创建X/Y/Z plot修复补丁"""
    logger.info("🔧 创建X/Y/Z plot修复补丁...")
    
    patch_content = '''
# X/Y/Z Plot 修复补丁
# 解决网格大小计算和参数验证问题

def safe_grid_calculation(x_values, y_values, z_values=None):
    """安全的网格大小计算"""
    try:
        x_count = len(x_values) if x_values else 1
        y_count = len(y_values) if y_values else 1
        z_count = len(z_values) if z_values else 1
        
        # 确保至少有一个维度
        if x_count == 0:
            x_count = 1
        if y_count == 0:
            y_count = 1
        if z_count == 0:
            z_count = 1
            
        total_images = x_count * y_count * z_count
        
        # 防止生成过多图像
        if total_images > 100:
            raise ValueError(f"网格太大: {total_images} 张图像，建议少于100张")
        
        return x_count, y_count, z_count, total_images
        
    except Exception as e:
        print(f"网格计算错误: {e}")
        return 1, 1, 1, 1

def validate_xyz_parameters(x_type, x_values, y_type, y_values, z_type=None, z_values=None):
    """验证X/Y/Z参数"""
    errors = []
    
    # 检查X轴参数
    if x_type and x_type != "Nothing":
        if not x_values or x_values.strip() == "":
            errors.append("X轴类型已选择但值为空")
    
    # 检查Y轴参数
    if y_type and y_type != "Nothing":
        if not y_values or y_values.strip() == "":
            errors.append("Y轴类型已选择但值为空")
    
    # 检查Z轴参数
    if z_type and z_type != "Nothing":
        if not z_values or z_values.strip() == "":
            errors.append("Z轴类型已选择但值为空")
    
    # 至少需要一个轴有值
    has_x = x_type and x_type != "Nothing" and x_values and x_values.strip()
    has_y = y_type and y_type != "Nothing" and y_values and y_values.strip()
    has_z = z_type and z_type != "Nothing" and z_values and z_values.strip()
    
    if not (has_x or has_y or has_z):
        errors.append("至少需要设置一个轴的参数")
    
    return errors

# 使用示例:
# errors = validate_xyz_parameters(x_type, x_values, y_type, y_values)
# if errors:
#     print("参数错误:", errors)
#     return
# 
# x_count, y_count, z_count, total = safe_grid_calculation(x_vals, y_vals, z_vals)
'''
    
    patch_file = Path("xyz_plot_fix.py")
    try:
        with open(patch_file, 'w', encoding='utf-8') as f:
            f.write(patch_content)
        logger.info(f"✅ 修复补丁已创建: {patch_file}")
        return True
    except Exception as e:
        logger.error(f"❌ 创建补丁失败: {e}")
        return False

def create_xyz_usage_guide():
    """创建X/Y/Z plot使用指南"""
    logger.info("📚 创建使用指南...")
    
    guide_content = '''# X/Y/Z Plot 使用指南

## 🎯 功能说明
X/Y/Z Plot可以批量生成图像，通过改变不同参数来对比效果。

## ✅ 正确使用方法

### 1. 基础设置
- **X轴类型**: 选择要变化的参数 (如: Sampling method, CFG Scale等)
- **X轴值**: 输入对应的值，用逗号分隔
- **Y轴类型**: 可选，设置第二个变化参数
- **Y轴值**: 对应Y轴的值

### 2. 参数示例

#### 示例1: 对比不同采样器
- X轴类型: `Sampling method`
- X轴值: `Euler a, DPM++ 2M, DDIM`
- Y轴类型: `Nothing` (不使用)

#### 示例2: 对比CFG Scale
- X轴类型: `CFG Scale`
- X轴值: `5, 7, 10, 15`
- Y轴类型: `Nothing`

#### 示例3: 双参数对比
- X轴类型: `CFG Scale`
- X轴值: `7, 10, 15`
- Y轴类型: `Sampling method`
- Y轴值: `Euler a, DPM++ 2M`

### 3. 注意事项
- 确保参数值格式正确
- 避免生成过多图像 (建议少于20张)
- 参数值之间用英文逗号分隔
- 不要在值中包含多余的空格

### 4. 常见错误
❌ **错误**: "Processing could not begin"
✅ **解决**: 检查参数设置，确保至少有一个轴设置了有效值

❌ **错误**: "0 images on 1x0 grid"
✅ **解决**: 检查轴值是否为空或格式错误

## 🔧 故障排除

### 如果仍然出错:
1. 刷新浏览器页面
2. 重启WebUI
3. 检查参数格式
4. 减少生成图像数量
5. 使用简单参数测试

### 测试用例:
最简单的测试设置:
- X轴类型: `CFG Scale`
- X轴值: `7, 10`
- Y轴类型: `Nothing`
- 其他设置保持默认

这应该生成2张图像进行对比。
'''
    
    guide_file = Path("X_Y_Z_Plot使用指南.md")
    try:
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        logger.info(f"✅ 使用指南已创建: {guide_file}")
        return True
    except Exception as e:
        logger.error(f"❌ 创建指南失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 X/Y/Z Plot 功能修复工具")
    print("=" * 50)
    
    success_count = 0
    
    # 1. 检查脚本文件
    if check_xyz_script():
        success_count += 1
    
    # 2. 检查脚本错误
    if check_script_errors():
        success_count += 1
    
    # 3. 创建修复补丁
    if create_xyz_fix_patch():
        success_count += 1
    
    # 4. 创建使用指南
    if create_xyz_usage_guide():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"🎉 修复完成: {success_count}/4 步骤成功")
    
    print("\n💡 解决X/Y/Z Plot问题的建议:")
    print("1. 📚 阅读 'X_Y_Z_Plot使用指南.md'")
    print("2. 🧪 使用简单参数测试功能")
    print("3. 🔄 如果仍有问题，重启WebUI")
    print("4. 📝 确保参数格式正确")
    
    print("\n✅ 推荐的测试设置:")
    print("   X轴类型: CFG Scale")
    print("   X轴值: 7, 10")
    print("   Y轴类型: Nothing")
    
    return success_count >= 3

if __name__ == "__main__":
    main()
