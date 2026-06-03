#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诗词数据整合工具
从 chinese-poetry 仓库提取苏轼作品，整合到 v4 数据体系
@author: 行吟山河
"""
import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


class PoetryIntegrator:
    """诗词整合器"""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            # 默认从当前目录向上找
            project_root = self._find_project_root()
        
        self.project_root = Path(project_root)
        self.data_v4 = self.project_root / "data-v4"
        self.chinese_poetry = self.project_root / "data-v4-source" / "chinese-poetry"
        
        # 加载现有数据
        self.existing_poems_index = self._load_existing_index()
        self.existing_poems_detail = self._load_existing_detail()
        
        # 统计信息
        self.stats = {
            "total_found_su_shi": 0,
            "new_added": 0,
            "updated": 0,
            "duplicates": 0,
            "ci_poems": 0,  # 词
            "shi_poems": 0,  # 诗
            "fu_poems": 0,  # 赋
        }
        
    def _find_project_root(self) -> Path:
        """寻找项目根目录"""
        current = Path.cwd()
        # 检查几个标志性文件
        for parent in [current] + list(current.parents):
            if (parent / "README.md").exists() or (parent / "data-v4").exists():
                return parent
        return current
    
    def _load_existing_index(self) -> Dict[str, Any]:
        """加载现有诗词索引"""
        index_path = self.data_v4 / "poems-index.json"
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"schema_version": "v4.1", "total": 0, "poems": []}
    
    def _load_existing_detail(self) -> Dict[str, Any]:
        """加载现有诗词详情（可选）"""
        # 当前data-v4/poems目录下的文件
        poems_dir = self.data_v4 / "poems"
        if not poems_dir.exists():
            return {}
        
        details = {}
        for file in poems_dir.glob("W*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    details[file.stem] = json.load(f)
            except Exception as e:
                print(f"加载 {file} 失败: {e}")
        return details
    
    def _extract_su_shi_poems(self) -> List[Dict[str, Any]]:
        """从 chinese-poetry 中提取苏轼作品"""
        all_poems = []
        
        # 宋词目录
        ci_dir = self.chinese_poetry / "宋词"
        if ci_dir.exists():
            print(f"处理宋词目录: {ci_dir}")
            ci_poems = self._read_poems_from_dir(ci_dir, "词")
            all_poems.extend(ci_poems)
            print(f"找到 {len(ci_poems)} 首苏轼词")
        
        # 全唐诗
        tang_dir = self.chinese_poetry / "全唐诗"
        if tang_dir.exists():
            print(f"处理全唐诗目录: {tang_dir}")
            tang_poems = self._read_poems_from_dir(tang_dir, "诗")
            all_poems.extend(tang_poems)
            print(f"找到 {len(tang_poems)} 首苏轼诗（全唐诗）")
        
        # 宋诗（五代诗词或者其他目录）
        song_dir = self.chinese_poetry / "宋诗" if (self.chinese_poetry / "宋诗").exists() else None
        if not song_dir:
            # 尝试在五代诗词或者其他目录找
            song_dir = self.chinese_poetry / "全宋诗"
        
        if song_dir and song_dir.exists():
            print(f"处理宋诗目录: {song_dir}")
            song_poems = self._read_poems_from_dir(song_dir, "诗")
            all_poems.extend(song_poems)
            print(f"找到 {len(song_poems)} 首苏轼诗（宋诗）")
        
        return all_poems
    
    def _read_poems_from_dir(self, dir_path: Path, default_type: str) -> List[Dict[str, Any]]:
        """从目录读取诗词"""
        poems = []
        for file in dir_path.rglob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 可能是单个对象或数组
                if isinstance(data, dict):
                    data = [data]
                
                for poem in data:
                    author = poem.get("author", "").strip()
                    if author in ["苏轼", "苏东坡", "东坡居士"]:
                        # 苏轼作品！
                        poem["_type"] = default_type
                        
                        # 处理词牌名
                        if "rhythmic" in poem:
                            poem["_type"] = "词"
                            self.stats["ci_poems"] += 1
                        elif poem["_type"] == "诗":
                            self.stats["shi_poems"] += 1
                        
                        poems.append(poem)
                        self.stats["total_found_su_shi"] += 1
                        
            except Exception as e:
                print(f"读取 {file} 失败: {e}")
        
        return poems
    
    def _normalize_title(self, title: str) -> str:
        """标准化标题"""
        # 移除一些常见前缀后缀
        title = title.strip()
        title = re.sub(r'^(苏轼|东坡|苏东坡)[·・]?', '', title)
        title = re.sub(r'[·・]?[序跋记传]$', '', title)
        return title.strip()
    
    def _find_route_id(self, title: str, content: str) -> Optional[str]:
        """根据诗词内容寻找可能的路线ID"""
        # 这里可以根据关键词匹配
        # 简化版本，实际可以更复杂
        route_keywords = {
            "R00": ["眉山", "故乡", "中岩", "蟆颐"],
            "R01": ["嘉祐", "汴京", "开封"],
            "R02": ["嘉州", "犍为", "戎州", "泸州", "渝州", "三峡"],
            "R03": ["凤翔", "签判", "石鼓"],
            "R04": ["嘉祐", "治平", "父丧", "返蜀"],
            "R05": ["熙宁", "变法", "进京"],
            "R06": ["杭州", "西湖", "通判", "望湖"],
            "R07": ["密州", "超然", "江城子", "水调歌头"],
            "R08": ["徐州", "黄楼", "百步洪"],
            "R09": ["湖州", "乌台", "诗案"],
            "R10": ["黄州", "东坡", "赤壁", "定风波", "念奴娇"],
            "R11": ["筠州", "金陵", "中山"],
            "R12": ["登州", "海市"],
            "R13": ["汴京", "元祐", "玉堂"],
            "R14": ["杭州", "苏堤", "再知"],
            "R15": ["颍州", "扬州", "平山堂"],
            "R16": ["第七次", "汴京"],
            "R17": ["定州", "雪浪石"],
            "R18": ["惠州", "儋州", "贬谪", "荔枝"],
            "R19": ["常州", "遇赦", "渡海", "北归"],
        }
        
        combined_text = title + " " + " ".join(content) if isinstance(content, list) else str(content)
        
        best_match = None
        max_matches = 0
        
        for route_id, keywords in route_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in combined_text)
            if matches > max_matches and matches > 0:
                max_matches = matches
                best_match = route_id
        
        return best_match
    
    def integrate(self):
        """执行整合"""
        print("=" * 80)
        print("行吟山河 - 诗词数据整合工具")
        print("=" * 80)
        
        # 提取苏轼作品
        print("\n[1/4] 从 chinese-poetry 提取苏轼作品...")
        su_shi_poems = self._extract_su_shi_poems()
        
        # 分析现有标题，建立索引
        print(f"\n[2/4] 分析现有 {self.existing_poems_index['total']} 首诗词...")
        existing_titles = {}
        for poem in self.existing_poems_index["poems"]:
            key = self._normalize_title(poem.get("title", ""))
            if key:
                existing_titles[key] = poem
        
        # 整合新作品
        print(f"\n[3/4] 整合 {len(su_shi_poems)} 首作品...")
        
        new_poems_list = list(self.existing_poems_index["poems"])
        next_id = int(self.existing_poems_index["poems"][-1]["id"][1:]) + 1 if self.existing_poems_index["poems"] else 1
        
        for poem in su_shi_poems:
            title = poem.get("title", "")
            normalized_title = self._normalize_title(title)
            
            # 查重
            duplicate_found = False
            if normalized_title in existing_titles:
                # 可能是重复作品，检查内容
                existing = existing_titles[normalized_title]
                # 这里可以做更详细的比较，暂时先跳过重复
                self.stats["duplicates"] += 1
                continue
            
            # 确定路线ID
            paragraphs = poem.get("paragraphs", [])
            paragraph_str = " ".join(paragraphs)
            route_id = self._find_route_id(title, paragraph_str)
            
            # 创建新的诗词对象
            core_verse = ""
            if paragraphs and len(paragraphs) > 0:
                core_verse = paragraphs[0]
                # 如果第一句很长，截取前20个字符
                if len(core_verse) > 50:
                    core_verse = core_verse[:50] + "..."
            
            poem_id = f"W{next_id:03d}"
            new_poem = {
                "id": poem_id,
                "title": title,
                "type": poem.get("_type", "诗"),
                "year": None,  # 暂时无法精确获取
                "route_id": route_id,
                "related_route_ids": [route_id] if route_id else [],
                "has_full_text": True,
                "coreVerse": core_verse,
                # 新增字段，详细内容
                "author": "苏轼",
                "rhythmic": poem.get("rhythmic", ""),
                "paragraphs": paragraphs,
            }
            
            new_poems_list.append(new_poem)
            
            # 同时保存详情文件
            self._save_poem_detail(new_poem)
            
            self.stats["new_added"] += 1
            next_id += 1
        
        # 更新索引
        self.existing_poems_index["poems"] = new_poems_list
        self.existing_poems_index["total"] = len(new_poems_list)
        
        # 统计已有全文的数量
        has_full_text_count = sum(1 for poem in new_poems_list if poem.get("has_full_text", False))
        self.existing_poems_index["has_full_text"] = has_full_text_count
        self.existing_poems_index["pending_full_text"] = len(new_poems_list) - has_full_text_count
        
        print(f"\n[4/4] 保存更新后的数据...")
        self._save_data()
        
        # 打印统计
        self._print_stats()
    
    def _save_poem_detail(self, poem: Dict[str, Any]):
        """保存诗词详情文件"""
        poem_detail_dir = self.data_v4 / "poems"
        poem_detail_dir.mkdir(parents=True, exist_ok=True)
        
        poem_file = poem_detail_dir / f"{poem['id']}.json"
        
        with open(poem_file, 'w', encoding='utf-8') as f:
            json.dump({
                "id": poem["id"],
                "title": poem["title"],
                "type": poem["type"],
                "author": "苏轼",
                "rhythmic": poem.get("rhythmic", ""),
                "paragraphs": poem.get("paragraphs", []),
                "coreVerse": poem.get("coreVerse", ""),
                "route_id": poem.get("route_id"),
                "related_route_ids": poem.get("related_route_ids", []),
                "source": "chinese-poetry",
            }, f, ensure_ascii=False, indent=2)
    
    def _save_data(self):
        """保存索引"""
        index_path = self.data_v4 / "poems-index.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(self.existing_poems_index, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 索引已保存到 {index_path}")
    
    def _print_stats(self):
        """打印统计结果"""
        print("\n" + "=" * 80)
        print("整合完成！统计信息")
        print("=" * 80)
        print(f"🔍 共找到苏轼作品: {self.stats['total_found_su_shi']} 首")
        print(f"✅ 新增诗词: {self.stats['new_added']} 首")
        print(f"⚠️  跳过重复: {self.stats['duplicates']} 首")
        print(f"📖 词: {self.stats['ci_poems']} 首")
        print(f"📖 诗: {self.stats['shi_poems']} 首")
        print(f"🎯 当前诗词总数: {self.existing_poems_index['total']} 首")
        print(f"📚 已全文: {self.existing_poems_index['has_full_text']} 首")
        print(f"🔄 待补全: {self.existing_poems_index['pending_full_text']} 首")


if __name__ == "__main__":
    integrator = PoetryIntegrator()
    integrator.integrate()
