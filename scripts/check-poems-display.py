#!/usr/bin/env python3
"""检查诗词列表显示问题"""
import json

# 加载诗词索引
with open('data-v4/poems-index.json', 'r', encoding='utf-8') as f:
    poems_data = json.load(f)

poems = poems_data.get('poems', [])
print(f'诗词总数: {len(poems)}')

# 统计类型分布
type_counts = {}
for poem in poems:
    ptype = poem.get('type', '')
    type_counts[ptype] = type_counts.get(ptype, 0) + 1

print('\n类型分布:')
for ptype, cnt in type_counts.items():
    print(f'  {ptype}: {cnt}首')

# 统计路线分布
route_counts = {}
for poem in poems:
    rid = poem.get('route_id', '')
    route_counts[rid] = route_counts.get(rid, 0) + 1

print('\n路线分布:')
for rid, cnt in sorted(route_counts.items()):
    print(f'  {rid}: {cnt}首')

# 检查是否有诗词的route_id为空
no_route = sum(1 for p in poems if not p.get('route_id'))
print(f'\n无route_id的诗词数: {no_route}')
