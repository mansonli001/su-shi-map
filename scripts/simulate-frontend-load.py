#!/usr/bin/env python3
"""模拟前端加载逻辑，检查为什么只显示68首"""
import json

# 模拟前端加载
with open('data-v4/poems-index.json', 'r', encoding='utf-8') as f:
    poems_data = json.load(f)

with open('data-v4/routes-index.json', 'r', encoding='utf-8') as f:
    routes_data = json.load(f)

poems = poems_data.get('poems', [])
routes = routes_data.get('routes', [])

# 创建路线Map
routes_map = {r['id']: r for r in routes}

print(f'诗词总数: {len(poems)}')
print(f'路线数: {len(routes)}')

# 模拟前端过滤逻辑
activeFilter = '全部'
searchQuery = ''

filteredPoems = []
for poem in poems:
    # 类型筛选
    if activeFilter != '全部' and poem.get('type') != activeFilter:
        continue
    # 搜索筛选
    if searchQuery:
        q = searchQuery.lower()
        if not (poem.get('title', '').lower().find(q) != -1 or 
                (poem.get('coreVerse') and poem.get('coreVerse').lower().find(q) != -1)):
            continue
    filteredPoems.append(poem)

print(f'\n过滤后诗词数: {len(filteredPoems)}')

# 按路线分组
groupedByRoute = {}
for poem in filteredPoems:
    key = poem.get('route_id') or 'unassigned'
    if key not in groupedByRoute:
        groupedByRoute[key] = []
    groupedByRoute[key].append(poem)

print(f'\n分组数: {len(groupedByRoute)}')

# 检查哪些路线没有数据
print('\n各路线诗词数:')
for route_id, route_poems in sorted(groupedByRoute.items()):
    route_info = routes_map.get(route_id)
    route_name = route_info['name'] if route_info else '未分配'
    print(f'  {route_id}: {route_name} - {len(route_poems)}首')

# 检查是否有路线在索引中但没有诗词
print('\n索引中有但诗词中没有的路线:')
for route in routes:
    if route['id'] not in groupedByRoute:
        print(f'  {route["id"]}: {route["name"]}')
