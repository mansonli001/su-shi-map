#!/usr/bin/env python3
"""为地点作品批量匹配poem_id"""
import json
from pathlib import Path
import re

# 加载诗词索引
with open('data-v4/poems-index.json', 'r', encoding='utf-8') as f:
    poems_data = json.load(f)

poems = poems_data.get('poems', [])

# 构建诗词查找索引
poem_index = {}
for poem in poems:
    pid = poem.get('id', '')
    title = poem.get('title', '')
    poem_index[pid] = poem

# 标准化标题的函数
def normalize_title(title):
    """标准化标题用于匹配"""
    if not title:
        return ''
    # 移除空格、标点
    normalized = re.sub(r'[··•·\s]', '', title)
    return normalized.lower()

# 为所有作品匹配poem_id
places_dir = Path('data-v4/places')
place_files = sorted(places_dir.glob('P*.json'))

matched_count = 0
unmatched_works = []

print('=== 批量匹配地点作品与诗词 ===')
print('=' * 60)

for pf in place_files:
    with open(pf, 'r', encoding='utf-8') as f:
        place_data = json.load(f)
    
    place_id = place_data.get('id', '')
    place_name = place_data.get('ancient_name', place_data.get('name', ''))
    works = place_data.get('global_works', [])
    
    for work in works:
        work_title = work.get('title', '')
        work_type = work.get('type', '')
        
        # 如果已经有poem_id，验证是否有效
        if 'poem_id' in work and work['poem_id']:
            if work['poem_id'] in poem_index:
                continue  # 已有有效poem_id，跳过
            else:
                # poem_id无效，尝试重新匹配
                pass
        
        # 尝试匹配
        work_normalized = normalize_title(work_title)
        matched_poem_id = None
        
        # 方法1：精确匹配标题
        for pid, poem in poem_index.items():
            poem_normalized = normalize_title(poem.get('title', ''))
            if work_normalized == poem_normalized:
                matched_poem_id = pid
                break
        
        # 方法2：模糊匹配（包含关系）
        if not matched_poem_id:
            for pid, poem in poem_index.items():
                poem_title = poem.get('title', '')
                if work_title in poem_title or poem_title in work_title:
                    matched_poem_id = pid
                    break
        
        if matched_poem_id:
            work['poem_id'] = matched_poem_id
            matched_count += 1
            print(f'✅ [{place_id}] {place_name}: "{work_title}" → {matched_poem_id}')
        else:
            unmatched_works.append({
                'place_id': place_id,
                'place_name': place_name,
                'work_title': work_title,
                'work_type': work_type
            })
            print(f'⚠️ [{place_id}] {place_name}: "{work_title}" 未匹配到诗词')
    
    # 保存更新（v6.1: 删除 public 双写，改由末尾 sync_public 统一同步）
    with open(pf, 'w', encoding='utf-8') as f:
        json.dump(place_data, f, ensure_ascii=False, indent=2)

print('\n' + '=' * 60)
print(f'成功匹配: {matched_count} 个作品')
print(f'未匹配: {len(unmatched_works)} 个作品')

if unmatched_works:
    print('\n未匹配的作品列表：')
    for i, w in enumerate(unmatched_works, 1):
        print(f'{i}. [{w["place_id"]}] {w["place_name"]}: "{w["work_title"]}" ({w["work_type"]})')

# v6.1: 一次性把 data-v4 同步到 public/data-v4
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
from lib_sync import sync_public
sync_public()