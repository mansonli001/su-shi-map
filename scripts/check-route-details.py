#!/usr/bin/env python3
"""详细检查路线简述内容"""
import json

with open('data-v4/routes-index.json', 'r', encoding='utf-8') as f:
    routes_data = json.load(f)

routes = routes_data.get('routes', [])

print('=== 20条路线简述详细检查 ===')
print('=' * 60)

for route in routes:
    rid = route.get('id', '')
    name = route.get('name', '')
    desc = route.get('description_short', '')
    period = route.get('period', '')
    
    print(f'\n【{rid}】{name}')
    print(f'时期: {period}')
    print(f'简述: {desc}')
    
    # 检查可能的问题
    issues = []
    
    # 检查长度
    if len(desc) < 10:
        issues.append('内容过短')
    
    # 检查是否有日期格式问题
    if '年' in desc and not any(str(y) in desc for y in range(1030, 1110)):
        issues.append('可能缺少具体年份')
    
    # 检查地点名称
    location_keywords = ['眉山', '汴京', '凤翔', '杭州', '密州', '徐州', '湖州', '黄州', 
                         '惠州', '儋州', '常州', '登州', '颍州', '扬州', '定州']
    has_location = any(loc in desc for loc in location_keywords)
    if not has_location:
        issues.append('未提及具体地点')
    
    if issues:
        print(f'⚠️ 注意: {", ".join(issues)}')
    else:
        print('✓ 检查通过')

print('\n' + '=' * 60)
print('完成路线简述检查')
