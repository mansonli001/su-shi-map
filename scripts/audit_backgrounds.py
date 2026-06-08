#!/usr/bin/env python3
"""检查地点background描述是否与地点名匹配"""
import json, os, re

with open('data-v4/places-index.json') as f:
    pi = json.load(f)

# 关键词冲突检测：如果背景描述提到了另一个城市名，可能有问题
CITY_NAMES = {
    '杭州': ['西湖', '钱塘', '临安'],
    '黄州': ['黄冈'],
    '开封': ['汴京', '汴梁', '东京'],
    '惠州': [],
    '儋州': [],
    '眉山': [],
    '成都': ['蜀都'],
    '洛阳': [],
    '长安': ['西安'],
    '徐州': ['彭城'],
    '湖州': [],
    '密州': ['诸城'],
    '登州': ['蓬莱'],
    '颍州': ['阜阳'],
    '扬州': ['广陵'],
    '赣州': [],
    '嘉州': ['乐山'],
}

issues = []
for p in pi['places']:
    pf = f'data-v4/places/{p["id"]}.json'
    if not os.path.exists(pf): continue
    with open(pf) as f:
        pd = json.load(f)
    
    an = pd.get('ancient_name', '')
    bg = pd.get('background', '')
    
    # 检查：如果地点名是A，但background主要描述的是B
    for city, aliases in CITY_NAMES.items():
        if city in an or any(a in an for a in aliases):
            continue  # 地点名包含这个城市，跳过
        # 地点名不包含这个城市，但background提到了
        if city in bg:
            # 排除合理的提及（如"途经杭州"等）
            # 只在background开头就提到这个城市时才报警
            bg_start = bg[:20]
            if city in bg_start:
                issues.append(f'{p["id"]} {an}: background开头提到"{city}"但地点不是{city}')

print(f'背景描述与地点不匹配: {len(issues)}个')
for i in issues:
    print(f'  {i}')

if not issues:
    print('所有地点背景描述与名称匹配，无问题')
