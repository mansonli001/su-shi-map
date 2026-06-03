#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全的苏轼诗词提取器
从chinese-poetry中提取高质量候选，经过验证系统审核
@author: 行吟山河
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any
from poetry_validator import PoetryValidator


class SafePoetryExtractor:
    """安全的诗词提取器"""
    
    def __init__(self, project_root: Path = None):
        if project_root is None:
            project_root = Path.cwd()
        
        self.project_root = project_root
        self.chinese_poetry_dir = project_root / "data-v4-source" / "chinese-poetry"
        self.validator = PoetryValidator(project_root)
        
        # 苏轼的已知笔名
        self.su_shi_names = ["苏轼", "苏东坡", "东坡居士"]
        
        # 高质量苏轼词列表（可确认是真作）
        self.high_confidence_poems = [
            "念奴娇·赤壁怀古",
            "水调歌头·明月几时有",
            "江城子·十年生死两茫茫",
            "江城子·密州出猎",
            "定风波·莫听穿林打叶声",
            "赤壁赋",
            "后赤壁赋"
        ]
    
    def clone_repository(self):
        """克隆chinese-poetry仓库"""
        if not self.chinese_poetry_dir.exists():
            import subprocess
            print("📥 正在克隆 chinese-poetry 仓库...")
            subprocess.run([
                "git", "clone",
                "https://github.com/chinese-poetry/chinese-poetry",
                str(self.chinese_poetry_dir)
            ], check=True, capture_output=True)
            print("✅ 克隆完成")
    
    def extract_from_song_ci(self) -> List[Dict[str, Any]]:
        """从宋词库中提取苏轼词"""
        candidates = []
        ci_dir = self.chinese_poetry_dir / "宋词"
        
        if not ci_dir.exists():
            print(f"⚠️ 宋词目录不存在: {ci_dir}")
            return candidates
        
        # 读取所有ci.song.*.json文件
        for json_file in ci_dir.glob("ci.song.*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, dict):
                    data = [data]
                
                for poem in data:
                    author = poem.get("author", "").strip()
                    if author in self.su_shi_names:
                        # 增强的标题处理
                        title = self._extract_title(poem)
                        if title:
                            poem["title"] = title
                        candidates.append(poem)
                        
            except Exception as e:
                print(f"⚠️ 读取文件 {json_file} 出错: {e}")
        
        print(f"📝 从宋词库提取到 {len(candidates)} 首苏轼词")
        return candidates
    
    def _extract_title(self, poem: Dict[str, Any]) -> str:
        """智能提取标题"""
        # 优先使用已有的title字段
        if "title" in poem and poem["title"]:
            return poem["title"].strip()
        
        # 尝试从词牌名+内容生成标题
        rhythmic = poem.get("rhythmic", "")
        paragraphs = poem.get("paragraphs", [])
        
        title = ""
        if rhythmic:
            title = rhythmic
        
        # 尝试从第一句提取关键词
        if paragraphs and len(paragraphs) > 0:
            first_line = paragraphs[0]
            # 取第一句前10个字
            if len(first_line) > 10:
                title = f"{title}·{first_line[:10]}"
        
        return title.strip()
    
    def filter_high_confidence(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤高置信度候选"""
        filtered = []
        
        for poem in candidates:
            title = poem.get("title", "")
            paragraphs = poem.get("paragraphs", [])
            
            # 基本质量检查
            if not paragraphs or len(paragraphs) == 0:
                continue
            
            # 检查是否是知名作品
            is_high_profile = any(known in title for known in self.high_confidence_poems)
            
            # 检查内容长度
            total_chars = sum(len(p) for p in paragraphs)
            if total_chars < 20:
                continue
            
            # 通过验证
            if is_high_profile or total_chars > 50:
                filtered.append(poem)
        
        print(f"🎯 过滤后剩余 {len(filtered)} 首高质量候选")
        return filtered
    
    def process_candidates(self, candidates: List[Dict[str, Any]]):
        """处理候选并保存到验证系统"""
        print()
        print("🔍 开始验证流程...")
        print()
        
        for i, poem_data in enumerate(candidates, 1):
            print(f"[{i}/{len(candidates)}] 处理中...", end="\r")
            
            # 创建候选
            candidate = self.validator.create_candidate(poem_data, "chinese-poetry")
            
            # 保存候选
            self.validator.save_candidate(candidate)
        
        print()
        print(f"✅ 所有候选已保存到: {self.validator.candidates_dir}")
        print()
    
    def run_safe_extraction(self):
        """运行安全提取流程"""
        print("=" * 80)
        print("行吟山河 - 苏轼诗词安全提取器")
        print("=" * 80)
        print()
        
        # 1. 克隆仓库（如果需要）
        self.clone_repository()
        
        # 2. 从宋词库提取
        print()
        print("📚 阶段1: 从宋词库提取")
        candidates = self.extract_from_song_ci()
        
        if not candidates:
            print("❌ 未找到任何苏轼词，检查数据目录")
            return
        
        # 3. 过滤高质量候选
        print()
        print("🎯 阶段2: 质量过滤")
        filtered = self.filter_high_confidence(candidates)
        
        # 4. 验证系统处理
        print()
        print("✅ 阶段3: 验证系统处理")
        self.process_candidates(filtered)
        
        # 5. 生成审核报告
        print()
        print("📋 阶段4: 生成审核报告")
        stats = self.validator.generate_review_report()
        
        print()
        print("=" * 80)
        print("📊 提取完成！统计信息:")
        print("=" * 80)
        print(f"  原始提取: {len(candidates)}")
        print(f"  质量过滤: {len(filtered)}")
        print(f"  高置信度: {stats['high_confidence']}")
        print(f"  可直接审核: {stats['ready_for_review']}")
        print()
        print("📍 下一步:")
        print("  1. 查看审核报告: data-v4-source/诗词验证/审核报告.json")
        print("  2. 人工审核候选: data-v4-source/诗词验证/候选/")
        print("  3. 确认无误后再批量入库")
        print()
        print("⚠️  重要: 没有人工审核确认之前，不要执行任何入库操作！")
        print("=" * 80)


if __name__ == "__main__":
    extractor = SafePoetryExtractor()
    extractor.run_safe_extraction()
