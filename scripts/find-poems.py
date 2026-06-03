#!/usr/bin/env python3
"""查找诗词数据库中是否存在这些作品"""
import json
from pathlib import Path

# 加载诗词索引
with open('data-v4/poems-index.json', 'r', encoding='utf-8') as f:
    poems_data = json.load(f)

poems = poems_data.get('poems', [])

# 需要查找的作品
target_works = [
    "海南日记",
    "留题仙游潭中兴寺",
    "泊船瓜洲",
    "初入庐山",
    "别子由三首",
    "定州中山怀古",
    "平山堂怀古"
]

print('=== 查找诗词数据库 ===')
print('=' * 60)

for target in target_works:
    found = False
    for poem in poems:
        title = poem.get('title', '')
        if target in title or title in target:
            print(f'✅ "{target}" 找到: {title} (ID: {poem.get("id")})')
            found = True
            break
    
    if not found:
        print(f'⚠️ "{target}" 未找到')

print('\n' + '=' * 60)
print('查找完成')