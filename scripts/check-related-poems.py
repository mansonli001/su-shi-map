#!/usr/bin/env python3
"""检查这些作品是否应该存在于诗词数据库中"""
import json
from pathlib import Path

# 加载诗词索引
with open('data-v4/poems-index.json', 'r', encoding='utf-8') as f:
    poems_data = json.load(f)

poems = poems_data.get('poems', [])

# 检查诗词数据库中是否有相关作品
print('=== 检查相关诗词 ===')
print('=' * 60)

# 检查"别子由"
print('检查"别子由"相关诗词:')
for poem in poems:
    title = poem.get('title', '')
    if '别子由' in title:
        print(f'  {title} (ID: {poem.get("id")})')

# 检查"瓜洲"
print('\n检查"瓜洲"相关诗词:')
for poem in poems:
    title = poem.get('title', '')
    if '瓜洲' in title:
        print(f'  {title} (ID: {poem.get("id")})')

# 检查"庐山"
print('\n检查"庐山"相关诗词:')
庐山_poems = [p for p in poems if '庐山' in p.get('title', '')]
for poem in 庐山_poems[:5]:
    print(f'  {poem.get("title")} (ID: {poem.get("id")})')
if len(庐山_poems) > 5:
    print(f'  ... 还有 {len(庐山_poems) - 5} 首')

# 检查"仙游潭"
print('\n检查"仙游潭"相关诗词:')
for poem in poems:
    title = poem.get('title', '')
    if '仙游' in title or '中兴寺' in title:
        print(f'  {title} (ID: {poem.get("id")})')

print('\n' + '=' * 60)