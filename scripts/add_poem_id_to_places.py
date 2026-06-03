#!/usr/bin/env python3
"""
为地点详情中的作品添加 poem_id
"""
import json
import os
from pathlib import Path
from difflib import SequenceMatcher

# 读取诗词索引
poems_index_path = Path('data-v4/poems-index.json')
with open(poems_index_path, 'r', encoding='utf-8') as f:
    poems_index = json.load(f)

# 创建标题到ID的映射
title_to_id = {}
for poem in poems_index['poems']:
    title = poem['title']
    title_to_id[title] = poem['id']

# 读取所有诗词数据
poems_dir = Path('data-v4/poems')
poems_data = {}
for poem_file in poems_dir.glob('*.json'):
    with open(poem_file, 'r', encoding='utf-8') as f:
        poem_data = json.load(f)
    poems_data[poem_data['id']] = poem_data

def similar(a, b):
    """计算字符串相似度"""
    return SequenceMatcher(None, a, b).ratio()

def find_poem_id(work_title, work_type):
    """根据作品标题和类型查找诗词ID"""
    # 1. 精确匹配
    if work_title in title_to_id:
        return title_to_id[work_title]
    
    # 2. 去掉书名号后匹配
    clean_title = work_title.replace('《', '').replace('》', '')
    if clean_title in title_to_id:
        return title_to_id[clean_title]
    
    # 3. 模糊匹配
    best_match = None
    best_ratio = 0.8  # 相似度阈值
    
    for poem_title, poem_id in title_to_id.items():
        ratio = similar(clean_title, poem_title)
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = poem_id
    
    return best_match

# 处理所有地点文件
places_dir = Path('data-v4/places')
place_files = sorted(places_dir.glob('*.json'))

updated_count = 0
no_match_count = 0

for place_file in place_files:
    with open(place_file, 'r', encoding='utf-8') as f:
        place_data = json.load(f)
    
    place_id = place_data.get('id', '')
    place_name = place_data.get('ancient_name', '')
    
    # 检查 global_works
    global_works = place_data.get('global_works', [])
    updated = False
    
    for work in global_works:
        work_title = work.get('title', '')
        work_type = work.get('type', '')
        
        # 如果已经有 poem_id，跳过
        if work.get('poem_id'):
            continue
        
        # 查找 poem_id
        poem_id = find_poem_id(work_title, work_type)
        
        if poem_id:
            work['poem_id'] = poem_id
            updated = True
            updated_count += 1
            print(f"✓ {place_name}: 《{work_title}》 -> {poem_id}")
        else:
            no_match_count += 1
            print(f"✗ {place_name}: 《{work_title}》 未找到匹配")
    
    # 如果有更新，保存文件
    if updated:
        with open(place_file, 'w', encoding='utf-8') as f:
            json.dump(place_data, f, ensure_ascii=False, indent=2)

print(f"\n总计: 更新了 {updated_count} 个作品的 poem_id")
print(f"未找到匹配: {no_match_count} 个作品")