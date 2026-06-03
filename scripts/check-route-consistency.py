#!/usr/bin/env python3
"""检查路线索引和诗词索引的一致性"""
import json

# 加载路线索引
with open('data-v4/routes-index.json', 'r', encoding='utf-8') as f:
    routes_data = json.load(f)

routes = routes_data.get('routes', [])
route_ids_in_index = set(r['id'] for r in routes)

print(f'路线索引中的路线数: {len(routes)}')
print(f'路线索引中的路线ID: {sorted(route_ids_in_index)}')

# 加载诗词索引
with open('data-v4/poems-index.json', 'r', encoding='utf-8') as f:
    poems_data = json.load(f)

poems = poems_data.get('poems', [])
poem_route_ids = set(p.get('route_id') for p in poems if p.get('route_id'))

print(f'\n诗词中的路线ID数: {len(poem_route_ids)}')
print(f'诗词中的路线ID: {sorted(poem_route_ids)}')

# 检查是否有缺失
missing_in_routes = poem_route_ids - route_ids_in_index
print(f'\n诗词中有但路线索引中没有的: {missing_in_routes}')

# 统计每个路线的诗词数
route_poem_counts = {}
for poem in poems:
    rid = poem.get('route_id')
    if rid:
        route_poem_counts[rid] = route_poem_counts.get(rid, 0) + 1

print(f'\n各路线诗词数:')
for rid in sorted(route_poem_counts.keys()):
    print(f'  {rid}: {route_poem_counts[rid]}首')

# 计算总诗词数
total = sum(route_poem_counts.values())
print(f'\n统计总数: {total}')
