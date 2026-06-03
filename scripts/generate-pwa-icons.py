#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PWA图标生成工具 - 使用Pillow
根据SVG源图标生成多种尺寸的PNG图标
支持普通图标和maskable图标
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

try:
    from PIL import ImageFont
except ImportError:
    ImageFont = None

# 输出目录
OUTPUT_DIR = Path(__file__).parent.parent / "public" / "icons"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 颜色配置
BG_COLOR = "#1A1008"  # 墨黑色背景
TEXT_COLOR = "#FAC775"  # 金色文字
GRADIENT_COLORS = ["#FAC775", "#BA7517", "#1A1008"]


def get_font(size):
    """获取合适大小的字体"""
    if ImageFont is None:
        return None
    
    # 尝试常见的中文字体路径
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Arial.ttf",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, int(size * 0.6))
            except:
                continue
    
    # 使用默认字体
    try:
        return ImageFont.truetype("/System/Library/Fonts/Arial.ttf", int(size * 0.6))
    except:
        return ImageFont.load_default()


def create_gradient_background(size, is_maskable=False):
    """创建渐变背景"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if is_maskable:
        # maskable: 四周透明，只有中心70%有内容
        padding = int(size * 0.15)  # 15%的边距
        center_size = size - padding * 2
        
        # 创建中心区域
        for y in range(size):
            for x in range(size):
                # 计算是否在中心区域内
                if padding <= x < size - padding and padding <= y < size - padding:
                    cx, cy = x - padding, y - padding
                    # 渐变色从左到右
                    ratio = cx / center_size
                    r = int(250 - ratio * (250 - 186))  # FAC775 -> BA7517
                    g = int(199 - ratio * (199 - 117))
                    b = int(117 - ratio * (117 - 23))
                    img.putpixel((x, y), (r, g, b, 255))
                else:
                    # 透明
                    img.putpixel((x, y), (0, 0, 0, 0))
    else:
        # 普通图标：实心背景带渐变
        for y in range(size):
            ratio = y / size
            r = int(250 - ratio * (250 - 186))
            g = int(199 - ratio * (199 - 117))
            b = int(117 - ratio * (117 - 23))
            draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
    
    return img


def create_icon(size, output_path, is_maskable=False):
    """创建单个尺寸的图标"""
    # 创建带圆角矩形背景
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制渐变背景
    for y in range(size):
        ratio = y / size
        r = int(250 - ratio * (250 - 186))
        g = int(199 - ratio * (199 - 117))
        b = int(117 - ratio * (117 - 23))
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
    
    # 绘制圆角蒙版（中心区域）
    if is_maskable:
        # maskable: 中心70%显示图标
        padding = int(size * 0.15)
        corner_radius = int(size * 0.08)
    else:
        # 普通: 全区域显示
        padding = 0
        corner_radius = int(size * 0.12)
    
    # 创建圆角蒙版
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    
    # 绘制圆角矩形（白色=显示，透明=隐藏）
    if is_maskable:
        mask_draw.rounded_rectangle(
            [padding, padding, size - padding, size - padding],
            radius=corner_radius,
            fill=255
        )
    else:
        mask_draw.rounded_rectangle(
            [0, 0, size, size],
            radius=corner_radius,
            fill=255
        )
    
    # 应用蒙版
    img.putalpha(mask)
    
    # 绘制"山"字
    font = get_font(size)
    if font:
        try:
            # 获取文字边界框
            bbox = draw.textbbox((0, 0), "山", font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 计算居中位置
            text_x = (size - text_width) // 2
            text_y = (size - text_height) // 2 - int(size * 0.05)
            
            # 绘制阴影
            shadow_offset = int(size * 0.015)
            draw.text((text_x + shadow_offset, text_y + shadow_offset), "山", 
                     font=font, fill=(26, 16, 8, 200))
            
            # 绘制文字
            draw.text((text_x, text_y), "山", font=font, fill=(250, 199, 117, 255))
        except Exception as e:
            print(f"   ⚠️  文字绘制失败: {e}")
    
    # 保存
    img.save(output_path, "PNG")
    return True


def main():
    print("=" * 60)
    print("PWA图标生成工具 (Pillow版)")
    print("=" * 60)
    
    # 生成标准PWA图标
    print("\n📦 生成标准PWA图标...")
    for size in [192, 512]:
        output_path = OUTPUT_DIR / f"pwa-{size}.png"
        try:
            create_icon(size, str(output_path), is_maskable=False)
            print(f"   ✅ {output_path.name} ({size}x{size})")
        except Exception as e:
            print(f"   ❌ 生成 {output_path.name} 失败: {e}")
    
    # 生成maskable图标
    print("\n🎭 生成maskable图标...")
    for size in [512]:
        output_path = OUTPUT_DIR / f"pwa-maskable-{size}.png"
        try:
            create_icon(size, str(output_path), is_maskable=True)
            print(f"   ✅ {output_path.name} ({size}x{size})")
        except Exception as e:
            print(f"   ❌ 生成 {output_path.name} 失败: {e}")
    
    # 列出生成的文件
    print("\n📁 输出目录:", OUTPUT_DIR)
    print("生成的文件:")
    for f in sorted(OUTPUT_DIR.glob("pwa*.png")):
        size_kb = f.stat().st_size // 1024
        print(f"   - {f.name} ({size_kb}KB)")
    
    print("\n✅ 完成！")


if __name__ == "__main__":
    main()