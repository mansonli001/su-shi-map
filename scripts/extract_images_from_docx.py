#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
苏轼行踪考 docx 内嵌图片提取工具
从docx文件中提取图片并建立与地点的关联
"""

import os
import zipfile
import shutil
import re
from pathlib import Path
from typing import List, Dict, Tuple

class DocxImageExtractor:
    """从docx文件提取图片"""
    
    def __init__(self, docx_dir: str, output_dir: str):
        self.docx_dir = Path(docx_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.stats = {
            "total_docx": 0,
            "total_images": 0,
            "extracted_images": 0,
            "failed_docx": 0,
        }
        
        # 图片类型映射
        self.image_ext_map = {
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/gif": ".gif",
            "image/bmp": ".bmp",
            "image/tiff": ".tif",
        }
        
    def _get_image_extension(self, content_type: str) -> str:
        """获取图片扩展名"""
        return self.image_ext_map.get(content_type, ".jpg")
    
    def _extract_docx_images(self, docx_path: Path) -> List[Tuple[str, bytes]]:
        """从单个docx文件提取图片"""
        images = []
        
        try:
            with zipfile.ZipFile(docx_path, 'r') as zip_ref:
                # 查找所有图片文件
                for name in zip_ref.namelist():
                    if name.startswith('word/media/'):
                        # 获取文件内容
                        with zip_ref.open(name) as f:
                            content = f.read()
                            # 从文件名获取扩展名
                            ext = os.path.splitext(name)[1]
                            images.append((name, content, ext))
        except Exception as e:
            print(f"   ❌ 读取 {docx_path.name} 失败: {e}")
            self.stats["failed_docx"] += 1
            
        return images
    
    def _parse_docx_title(self, docx_path: Path) -> str:
        """解析docx文件名，提取标题信息"""
        name = docx_path.stem
        # 移除编号前缀（如 "01 封面" -> "封面"）
        match = re.match(r'^\d+\s+(.*)$', name)
        if match:
            return match.group(1)
        return name
    
    def extract_all(self):
        """提取所有docx文件中的图片"""
        print("=" * 80)
        print("苏轼行踪考 - docx内嵌图片提取工具")
        print("=" * 80)
        print(f"📁 源目录: {self.docx_dir}")
        print(f"📂 输出目录: {self.output_dir}")
        print()
        
        # 获取所有docx文件
        docx_files = sorted(self.docx_dir.glob("*.docx"))
        self.stats["total_docx"] = len(docx_files)
        
        print(f"📦 找到 {len(docx_files)} 个docx文件")
        print()
        
        # 提取图片记录
        image_records = []
        
        for i, docx_path in enumerate(docx_files, 1):
            title = self._parse_docx_title(docx_path)
            print(f"[{i}/{len(docx_files)}] {docx_path.name}")
            
            images = self._extract_docx_images(docx_path)
            if images:
                print(f"   🖼️  找到 {len(images)} 张图片")
                
                # 创建章节目录
                chapter_dir = self.output_dir / f"{i:02d}_{title}"
                chapter_dir.mkdir(exist_ok=True)
                
                for j, (name, content, ext) in enumerate(images, 1):
                    # 生成文件名
                    image_name = f"{i:02d}_{j:03d}{ext}"
                    image_path = chapter_dir / image_name
                    
                    # 保存图片
                    with open(image_path, 'wb') as f:
                        f.write(content)
                    
                    # 记录图片信息
                    image_records.append({
                        "chapter": title,
                        "chapter_num": i,
                        "image_num": j,
                        "original_name": name,
                        "saved_path": str(image_path.relative_to(self.output_dir)),
                        "file_size": len(content),
                    })
                    
                    self.stats["extracted_images"] += 1
                    print(f"      ✅ {image_name} ({len(content)//1024}KB)")
            
            print()
        
        # 保存图片记录
        self._save_image_records(image_records)
        
        # 打印统计
        self._print_stats()
        
        return image_records
    
    def _save_image_records(self, records: List[Dict]):
        """保存图片记录到JSON文件"""
        import json
        
        records_file = self.output_dir / "image_records.json"
        with open(records_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        print(f"📋 图片记录已保存到: {records_file}")
    
    def _print_stats(self):
        """打印统计信息"""
        print("\n" + "=" * 80)
        print("提取完成！")
        print("=" * 80)
        print(f"📁 处理docx文件: {self.stats['total_docx']}")
        print(f"🖼️  提取图片: {self.stats['extracted_images']}")
        print(f"❌ 失败文件: {self.stats['failed_docx']}")
        print(f"📂 输出目录: {self.output_dir}")


if __name__ == "__main__":
    import sys
    
    # 默认路径
    default_docx_dir = "/Users/mansonlee/Downloads/苏轼行踪考/Word版本"
    default_output_dir = "/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4-source/行踪考图片"
    
    docx_dir = sys.argv[1] if len(sys.argv) > 1 else default_docx_dir
    output_dir = sys.argv[2] if len(sys.argv) > 2 else default_output_dir
    
    extractor = DocxImageExtractor(docx_dir, output_dir)
    extractor.extract_all()