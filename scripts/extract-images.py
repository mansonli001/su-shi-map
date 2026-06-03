#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片提取工具
从《苏轼行踪考》Word文档中提取内嵌图片
@author: 行吟山河
"""
import zipfile
import shutil
from pathlib import Path
import re
import json
from typing import List, Dict, Any


class ImageExtractor:
    """图片提取器"""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            project_root = self._find_project_root()
        
        self.project_root = Path(project_root)
        self.data_v4_source = self.project_root / "data-v4-source"
        
        # 图片输出目录
        self.output_dir = self.data_v4_source / "行踪考-图片"
        
        # 统计信息
        self.stats = {
            "total_docs": 0,
            "total_images": 0,
            "success": 0,
            "failed": 0,
            "by_extension": {}
        }
    
    def _find_project_root(self) -> Path:
        """寻找项目根目录"""
        current = Path.cwd()
        for parent in [current] + list(current.parents):
            if (parent / "README.md").exists() or (parent / "data-v4").exists():
                return parent
        return current
    
    def extract_from_directory(self, docx_dir: str = None):
        """从目录批量提取"""
        if docx_dir is None:
            # 尝试几个可能的位置
            docx_dir = self.project_root.parent / "Downloads" / "苏轼行踪考" / "Word版本"
        
        if not Path(docx_dir).exists():
            print(f"⚠️  未找到Word目录: {docx_dir}")
            print("请指定正确的Word文档目录")
            return
        
        print("=" * 80)
        print("行吟山河 - 图片提取工具")
        print("=" * 80)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        docx_files = list(Path(docx_dir).glob("*.docx"))
        
        if not docx_files:
            print(f"⚠️  目录中没有找到 .docx 文件: {docx_dir}")
            return
        
        print(f"\n找到 {len(docx_files)} 个Word文档\n")
        
        for i, docx_file in enumerate(docx_files, 1):
            print(f"[{i}/{len(docx_files)}] 处理: {docx_file.name}")
            self.extract_from_single(docx_file)
        
        self._save_report()
        self._print_stats()
    
    def extract_from_single(self, docx_path: Path) -> List[Path]:
        """从单个Word文档提取图片"""
        extracted = []
        docx_name = docx_path.stem
        
        # 每个文档单独一个子目录
        doc_dir = self.output_dir / docx_name
        
        try:
            # docx本质是zip文件
            with zipfile.ZipFile(docx_path, 'r') as zip_ref:
                # Word文档中的图片在 word/media/ 目录
                media_files = [f for f in zip_ref.namelist() if f.startswith('word/media/')]
                
                if len(media_files) == 0:
                    print(f"   📭 没有找到图片")
                    self.stats["failed"] += 1
                    return []
                
                doc_dir.mkdir(parents=True, exist_ok=True)
                
                for media_file in media_files:
                    # 获取文件扩展名
                    ext = Path(media_file).suffix.lower()
                    
                    if ext not in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                        continue  # 只提取图片文件
                    
                    # 输出文件名
                    filename = Path(media_file).name
                    output_path = doc_dir / filename
                    
                    # 提取
                    with zip_ref.open(media_file) as source, open(output_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                    
                    extracted.append(output_path)
                    
                    # 统计
                    self.stats["total_images"] += 1
                    self.stats["by_extension"][ext] = self.stats["by_extension"].get(ext, 0) + 1
                
                self.stats["success"] += 1
                self.stats["total_docs"] += 1
                
                print(f"   ✅ 提取了 {len(media_files)} 个图片文件到 {doc_dir}")
                
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            self.stats["failed"] += 1
        
        return extracted
    
    def _save_report(self):
        """保存提取报告"""
        report = {
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "stats": self.stats,
        }
        
        report_path = self.output_dir / "extraction-report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 报告已保存到 {report_path}")
    
    def _print_stats(self):
        """打印统计"""
        print("\n" + "=" * 80)
        print("提取完成！")
        print("=" * 80)
        print(f"📁 处理文档: {self.stats['total_docs']} 个")
        print(f"✅ 成功: {self.stats['success']} 个")
        print(f"❌ 失败: {self.stats['failed']} 个")
        print(f"🖼️  提取图片: {self.stats['total_images']} 张")
        
        if self.stats["by_extension"]:
            print("\n📊 按格式统计:")
            for ext, count in sorted(self.stats["by_extension"].items()):
                print(f"   {ext.upper()}: {count} 张")


if __name__ == "__main__":
    import sys
    
    extractor = ImageExtractor()
    
    if len(sys.argv) > 1:
        # 从命令行参数获取目录
        docx_dir = sys.argv[1]
        extractor.extract_from_directory(docx_dir)
    else:
        # 使用默认位置
        print("使用默认位置，请根据需要修改...")
        extractor.extract_from_directory()
