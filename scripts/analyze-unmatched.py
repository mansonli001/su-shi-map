#!/usr/bin/env python3
"""分析未匹配的作品类型"""
import json
from pathlib import Path

places_dir = Path('data-v4/places')
place_files = sorted(places_dir.glob('P*.json'))

poem_types = ['诗', '词', 'poem']
article_types = ['文', '书', '记', '赋', '策', '跋', '序']

poem_unmatched = []
article_unmatched = []
other_unmatched = []

for pf in place_files:
    with open(pf, 'r', encoding='utf-8') as f:
        place_data = json.load(f)
    
    place_id = place_data.get('id', '')
    place_name = place_data.get('ancient_name', place_data.get('name', ''))
    works = place_data.get('global_works', [])
    
    for work in works:
        work_title = work.get('title', '')
        work_type = work.get('type', '')
        poem_id = work.get('poem_id', '')
        
        # 如果没有poem_id
        if not poem_id:
            if work_type in poem_types:
                poem_unmatched.append({
                    'place_id': place_id,
                    'place_name': place_name,
                    'work_title': work_title,
                    'work_type': work_type
                })
            elif work_type in article_types:
                article_unmatched.append({
                    'place_id': place_id,
                    'place_name': place_name,
                    'work_title': work_title,
                    'work_type': work_type
                })
            else:
                other_unmatched.append({
                    'place_id': place_id,
                    'place_name': place_name,
                    'work_title': work_title,
                    'work_type': work_type
                })

print('=== 未匹配作品分类统计 ===')
print('=' * 60)
print(f'诗词类型（需要匹配）: {len(poem_unmatched)} 个')
print(f'文章类型（无需匹配）: {len(article_unmatched)} 个')
print(f'其他类型: {len(other_unmatched)} 个')

if poem_unmatched:
    print('\n\n=== 需要匹配的诗词作品 ===')
    for i, w in enumerate(poem_unmatched, 1):
        print(f'{i}. [{w["place_id"]}] {w["place_name"]}: "{w["work_title"]}" ({w["work_type"]})')

if article_unmatched:
    print('\n\n=== 文章类型（无需匹配poem_id） ===')
    for i, w in enumerate(article_unmatched[:10], 1):
        print(f'{i}. [{w["place_id"]}] {w["place_name"]}: "{w["work_title"]}" ({w["work_type"]})')
    if len(article_unmatched) > 10:
        print(f'... 还有 {len(article_unmatched) - 10} 个')

if other_unmatched:
    print('\n\n=== 其他类型 ===')
    for i, w in enumerate(other_unmatched, 1):
        print(f'{i}. [{w["place_id"]}] {w["place_name"]}: "{w["work_title"]}" ({w["work_type"]})')