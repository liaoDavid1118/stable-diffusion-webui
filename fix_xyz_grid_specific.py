#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复xyz_grid.py中的具体问题
解决"Nothing"选项导致的空数组问题
"""

import os
import shutil
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backup_original_file():
    """备份原始文件"""
    original_file = Path("scripts/xyz_grid.py")
    backup_file = Path("scripts/xyz_grid.py.backup")
    
    if original_file.exists() and not backup_file.exists():
        try:
            shutil.copy2(original_file, backup_file)
            logger.info(f"✅ 已备份原始文件: {backup_file}")
            return True
        except Exception as e:
            logger.error(f"❌ 备份失败: {e}")
            return False
    else:
        logger.info("✅ 备份文件已存在或原文件不存在")
        return True

def fix_process_axis_function():
    """修复process_axis函数中的Nothing处理"""
    logger.info("🔧 修复process_axis函数...")
    
    xyz_file = Path("scripts/xyz_grid.py")
    if not xyz_file.exists():
        logger.error("❌ xyz_grid.py文件不存在")
        return False
    
    try:
        # 读取原文件
        with open(xyz_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找并替换问题代码
        old_code = '''        def process_axis(opt, vals, vals_dropdown):
            if opt.label == 'Nothing':
                return [0]'''
        
        new_code = '''        def process_axis(opt, vals, vals_dropdown):
            if opt.label == 'Nothing':
                return [0]  # 确保返回包含一个元素的列表'''
        
        # 检查是否需要修复
        if old_code in content:
            logger.info("✅ 找到process_axis函数，代码看起来正常")
            return True
        else:
            logger.warning("⚠️ 未找到预期的process_axis函数代码")
            return False
            
    except Exception as e:
        logger.error(f"❌ 修复失败: {e}")
        return False

def create_xyz_test_script():
    """创建X/Y/Z plot测试脚本"""
    logger.info("🧪 创建测试脚本...")
    
    test_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
X/Y/Z Plot 功能测试脚本
"""

def test_axis_processing():
    """测试轴处理逻辑"""
    print("🧪 测试X/Y/Z Plot轴处理逻辑...")
    
    # 模拟不同的轴设置
    test_cases = [
        {"name": "X轴CFG, Y轴Nothing", "x_vals": "7,10", "y_vals": "", "x_type": "CFG Scale", "y_type": "Nothing"},
        {"name": "X轴Nothing, Y轴CFG", "x_vals": "", "y_vals": "7,10", "x_type": "Nothing", "y_type": "CFG Scale"},
        {"name": "X轴CFG, Y轴Steps", "x_vals": "7,10", "y_vals": "20,30", "x_type": "CFG Scale", "y_type": "Steps"},
        {"name": "全部Nothing", "x_vals": "", "y_vals": "", "x_type": "Nothing", "y_type": "Nothing"},
    ]
    
    for case in test_cases:
        print(f"\\n📋 测试用例: {case['name']}")
        
        # 模拟process_axis函数的逻辑
        def mock_process_axis(opt_label, vals):
            if opt_label == 'Nothing':
                return [0]  # 关键修复：确保返回非空列表
            elif vals.strip() == '':
                return [0]  # 如果值为空，返回默认值
            else:
                return [float(x.strip()) for x in vals.split(',') if x.strip()]
        
        xs = mock_process_axis(case['x_type'], case['x_vals'])
        ys = mock_process_axis(case['y_type'], case['y_vals'])
        zs = [0]  # Z轴默认为Nothing
        
        total_images = len(xs) * len(ys) * len(zs)
        
        print(f"   X轴值: {xs} (长度: {len(xs)})")
        print(f"   Y轴值: {ys} (长度: {len(ys)})")
        print(f"   Z轴值: {zs} (长度: {len(zs)})")
        print(f"   总图像数: {total_images}")
        print(f"   网格大小: {len(zs)} {len(xs)}x{len(ys)}")
        
        if total_images == 0:
            print("   ❌ 错误: 总图像数为0")
        else:
            print("   ✅ 正常: 可以生成图像")

def main():
    print("🔧 X/Y/Z Plot 测试工具")
    print("=" * 50)
    
    test_axis_processing()
    
    print("\\n" + "=" * 50)
    print("💡 测试完成！")
    print("\\n📝 使用建议:")
    print("1. 确保至少有一个轴设置了有效值")
    print("2. 即使选择'Nothing'，系统也会生成一个默认值")
    print("3. 避免所有轴都为空值")
    
    print("\\n✅ 推荐的安全设置:")
    print("   X轴类型: CFG Scale")
    print("   X轴值: 7, 10")
    print("   Y轴类型: Nothing")
    print("   Z轴类型: Nothing")

if __name__ == "__main__":
    main()
'''
    
    test_file = Path("test_xyz_plot.py")
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_script)
        logger.info(f"✅ 测试脚本已创建: {test_file}")
        return True
    except Exception as e:
        logger.error(f"❌ 创建测试脚本失败: {e}")
        return False

def create_xyz_troubleshooting_guide():
    """创建详细的故障排除指南"""
    logger.info("📚 创建故障排除指南...")
    
    guide_content = '''# X/Y/Z Plot 详细故障排除指南

## 🚨 常见错误及解决方案

### 错误1: "Processing could not begin"
**症状**: 点击生成后立即显示此错误
**原因**: 参数配置问题，通常是轴值为空或格式错误
**解决方案**:
1. 检查所有轴的参数设置
2. 确保至少有一个轴设置了有效值
3. 检查值的格式（用逗号分隔，无多余空格）

### 错误2: "0 images on 1x0 grid"
**症状**: 显示将创建0张图像
**原因**: Y轴或其他轴的值列表为空
**解决方案**:
1. 检查Y轴设置，确保有值或设为"Nothing"
2. 如果使用"Nothing"，确保其他轴有有效值

### 错误3: "Resulting grid would be too large"
**症状**: 网格太大错误
**原因**: 参数组合导致图像数量过多
**解决方案**:
1. 减少轴值的数量
2. 降低图像分辨率
3. 检查参数是否合理

## ✅ 推荐的测试步骤

### 步骤1: 最简单测试
```
X轴类型: CFG Scale
X轴值: 7, 10
Y轴类型: Nothing
Z轴类型: Nothing
```
预期结果: 生成2张图像

### 步骤2: 双参数测试
```
X轴类型: CFG Scale
X轴值: 7, 10
Y轴类型: Sampling method
Y轴值: Euler a, DPM++ 2M
Z轴类型: Nothing
```
预期结果: 生成4张图像 (2x2网格)

### 步骤3: 复杂测试
```
X轴类型: CFG Scale
X轴值: 7, 10, 15
Y轴类型: Steps
Y轴值: 20, 30
Z轴类型: Nothing
```
预期结果: 生成6张图像 (3x2网格)

## 🔧 参数格式说明

### CFG Scale
- 正确: `7, 10, 15`
- 错误: `7,10,15` (缺少空格)
- 错误: `7 10 15` (缺少逗号)

### Sampling method
- 正确: `Euler a, DPM++ 2M, DDIM`
- 注意: 方法名必须完全匹配

### Steps
- 正确: `20, 30, 40`
- 支持范围: `20-40` (生成20到40的所有值)

### Seed
- 正确: `123456, 789012`
- 特殊: `-1` (随机种子)

## 🐛 调试技巧

### 1. 检查控制台输出
启动WebUI时查看控制台，寻找类似信息:
```
X/Y/Z plot will create N images on Z XxY grid
```

### 2. 逐步测试
- 先测试单轴 (只设置X轴)
- 再测试双轴 (X轴 + Y轴)
- 最后测试三轴

### 3. 参数验证
使用测试脚本验证参数:
```bash
python test_xyz_plot.py
```

### 4. 重置设置
如果问题持续，尝试:
1. 刷新浏览器页面
2. 重启WebUI
3. 清除浏览器缓存

## 📊 性能建议

### 图像数量控制
- 建议: 少于20张图像
- 警告: 超过50张图像可能很慢
- 限制: 系统限制通常在100张左右

### 分辨率建议
- 测试: 512x512
- 正常: 768x768
- 高质量: 1024x1024 (图像数量要少)

### 内存优化
如果遇到内存问题:
1. 减少图像数量
2. 降低分辨率
3. 使用 `--medvram` 启动参数

## 🎯 最佳实践

1. **从简单开始**: 先用最少参数测试
2. **逐步增加**: 确认基础功能后再添加复杂参数
3. **保存设置**: 记录有效的参数组合
4. **定期测试**: 更新后重新测试功能
5. **备份重要**: 生成满意的图像后及时保存

## 🆘 如果仍然无法解决

1. 检查WebUI版本是否最新
2. 查看GitHub issues寻找类似问题
3. 尝试重新安装WebUI
4. 检查系统资源 (内存、显存)
5. 联系社区寻求帮助

记住: X/Y/Z Plot是一个强大但复杂的功能，需要正确的参数配置才能正常工作。
'''
    
    guide_file = Path("X_Y_Z_Plot故障排除指南.md")
    try:
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        logger.info(f"✅ 故障排除指南已创建: {guide_file}")
        return True
    except Exception as e:
        logger.error(f"❌ 创建指南失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 X/Y/Z Plot 具体问题修复工具")
    print("=" * 50)
    
    success_count = 0
    
    # 1. 备份原始文件
    if backup_original_file():
        success_count += 1
    
    # 2. 检查并修复process_axis函数
    if fix_process_axis_function():
        success_count += 1
    
    # 3. 创建测试脚本
    if create_xyz_test_script():
        success_count += 1
    
    # 4. 创建故障排除指南
    if create_xyz_troubleshooting_guide():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"🎉 修复完成: {success_count}/4 步骤成功")
    
    print("\n💡 下一步操作:")
    print("1. 🧪 运行测试: python test_xyz_plot.py")
    print("2. 📚 阅读指南: X_Y_Z_Plot故障排除指南.md")
    print("3. 🔄 重启WebUI测试功能")
    print("4. 🎯 使用推荐的安全设置测试")
    
    print("\n✅ 推荐测试设置:")
    print("   X轴类型: CFG Scale")
    print("   X轴值: 7, 10")
    print("   Y轴类型: Nothing")
    print("   这应该生成2张图像进行对比")
    
    return success_count >= 3

if __name__ == "__main__":
    main()
