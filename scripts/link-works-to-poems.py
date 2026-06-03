#!/usr/bin/env python3
"""
批量关联地点作品与诗词数据
============================
功能：
1. 扫描所有地点JSON文件中的 global_works
2. 根据作品标题/年份/路线 与诗词数据库匹配
3. 为匹配成功的作品添加 poem_id 字段

使用方式：python scripts/link-works-to-poems.py
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data-v4"
PLACES_DIR = DATA_DIR / "places"
POEMS_DIR = DATA_DIR / "poems"
POEMS_INDEX = DATA_DIR / "poems-index.json"

def load_poems_index() -> Dict[str, Any]:
    """加载诗词索引"""
    with open(POEMS_INDEX, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_poems_database() -> Dict[str, Dict[str, Any]]:
    """加载所有诗词详情"""
    poems_db = {}
    for poem_file in POEMS_DIR.glob("*.json"):
        try:
            with open(poem_file, 'r', encoding='utf-8') as f:
                poem = json.load(f)
                poems_db[poem['id']] = poem
        except Exception as e:
            print(f"   ⚠️  加载诗词 {poem_file.name} 失败: {e}")
    return poems_db

def normalize_title(title: str) -> str:
    """标准化标题用于匹配"""
    # 去除空格、标点、书名号等
    t = title.strip()
    t = re.sub(r'[\[\]【】（）\(\)《》〈〉""'']', '', t)
    t = re.sub(r'\s+', '', t)
    t = re.sub(r'[·・•]', '', t)  # 去除中间的点
    return t.lower()

def extract_year(year_val: Any) -> Optional[int]:
    """提取年份数值"""
    if isinstance(year_val, int):
        return year_val
    if isinstance(year_val, str):
        match = re.search(r'(\d{4})', year_val)
        if match:
            return int(match.group(1))
    return None

def match_work_to_poem(work: Dict[str, Any], poems_index: List[Dict], poems_db: Dict) -> Optional[str]:
    """
    匹配作品到诗词
    返回匹配的 poem_id 或 None
    """
    work_title = work.get('title', '')
    work_year = extract_year(work.get('year') or work.get('date', ''))
    work_type = work.get('type', '')
    work_route = work.get('route_id', '')
    
    if not work_title:
        return None
    
    work_title_norm = normalize_title(work_title)
    
    # 1. 直接按标题匹配（完全匹配）
    for poem in poems_index:
        poem_id = poem.get('id', '')
        poem_title = poem.get('title', '')
        poem_title_norm = normalize_title(poem_title)
        
        # 完全匹配
        if work_title_norm == poem_title_norm:
            return poem_id
        
        # 标题包含匹配
        if work_title_norm in poem_title_norm or poem_title_norm in work_title_norm:
            # 进一步验证年份
            poem_year = poem.get('year')
            if work_year and poem_year and abs(work_year - poem_year) <= 2:
                return poem_id
    
    # 2. 如果有 poem_id 已存在，直接返回
    if work.get('poem_id'):
        return work.get('poem_id')
    
    # 3. 按路线+年份+类型匹配
    if work_route and work_year:
        for poem in poems_index:
            if poem.get('route_id') == work_route:
                poem_year = poem.get('year')
                if poem_year and abs(work_year - poem_year) <= 1:
                    # 类型匹配（诗/词/文/赋）
                    if work_type in ['诗', '词', '文', '赋', '策']:
                        poem_type = poem.get('type', '')
                        if work_type == poem_type or not poem_type:
                            return poem.get('id')
    
    # 4. 按年份+地点模糊匹配
    if work_year and work.get('location'):
        work_loc = work.get('location', '')
        for poem in poems_index:
            poem_year = poem.get('year')
            if poem_year and abs(work_year - poem_year) <= 2:
                # 检查诗词是否有地点信息
                poem_loc = poem.get('location', '')
                if poem_loc and (work_loc in poem_loc or poem_loc in work_loc):
                    return poem.get('id')
    
    return None

def process_place(place_file: Path, poems_index: List, poems_db: Dict) -> Tuple[int, int]:
    """
    处理单个地点文件
    返回 (处理的作品数, 成功匹配数)
    """
    with open(place_file, 'r', encoding='utf-8') as f:
        place = json.load(f)
    
    global_works = place.get('global_works', [])
    if not global_works:
        return 0, 0
    
    matched_count = 0
    total_count = len(global_works)
    
    for work in global_works:
        # 如果已有 poem_id，跳过
        if work.get('poem_id'):
            continue
        
        poem_id = match_work_to_poem(work, poems_index, poems_db)
        if poem_id:
            work['poem_id'] = poem_id
            matched_count += 1
            print(f"   ✅ {place['id']} - '{work.get('title')}' → {poem_id}")
    
    # 保存更新
    if matched_count > 0:
        with open(place_file, 'w', encoding='utf-8') as f:
            json.dump(place, f, ensure_ascii=False, indent=2)
    
    return total_count, matched_count

def main():
    print("=" * 60)
    print("批量关联地点作品与诗词数据")
    print("=" * 60)
    
    # 加载诗词数据
    print("\n📚 加载诗词索引...")
    poems_index_data = load_poems_index()
    poems_index = poems_index_data.get('poems', [])
    print(f"   索引中诗词总数: {len(poems_index)}")
    
    print("\n📚 加载诗词详情数据库...")
    poems_db = load_poems_database()
    print(f"   详情文件数: {len(poems_db)}")
    
    # 统计
    total_works = 0
    total_matched = 0
    processed_places = 0
    
    # 遍历所有地点
    print("\n🔍 扫描地点文件...")
    place_files = sorted(PLACES_DIR.glob("P*.json"))
    print(f"   地点文件总数: {len(place_files)}")
    
    for place_file in place_files:
        total, matched = process_place(place_file, poems_index, poems_db)
        if total > 0:
            total_works += total
            total_matched += matched
            processed_places += 1
    
    print("\n" + "=" * 60)
    print("📊 关联完成统计")
    print("=" * 60)
    print(f"   处理地点数: {processed_places}")
    print(f"   作品总数: {total_works}")
    print(f"   新匹配数: {total_matched}")
    print(f"   匹配率: {total_matched/total_works*100:.1f}%" if total_works > 0 else "   匹配率: N/A")
    
    return total_matched

if __name__ == "__main__":
    main()
