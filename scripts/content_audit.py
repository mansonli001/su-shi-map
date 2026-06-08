#!/usr/bin/env python3
"""内容审核：检查地点背景描述与地点名是否匹配"""
import json, os

with open('data-v4/places-index.json') as f:
    pi = json.load(f)

issues = []
for p in pi['places']:
    pf = f'data-v4/places/{p["id"]}.json'
    if not os.path.exists(pf): continue
    with open(pf) as f:
        pd = json.load(f)
    
    an = pd.get('ancient_name', '')
    mn = pd.get('modern_name', '')
    bg = pd.get('background', '')
    
    # 检查背景描述是否提到了其他城市名（可能是复制错误）
    mismatches = {
        '杭州': ['嘉州','乐山','眉山','成都','汴京','开封','黄州','惠州','儋州'],
        '黄州': ['杭州','眉山','成都','开封','惠州','儋州','嘉州'],
        '开封': ['杭州','黄州','眉山','成都','惠州','儋州','嘉州'],
        '惠州': ['杭州','黄州','眉山','成都','开封','儋州','嘉州'],
        '儋州': ['杭州','黄州','眉山','成都','开封','惠州','嘉州'],
    }
    
    for city, wrong_places in mismatches.items():
        if city in bg and an in wrong_places:
            issues.append(f'{p["id"]} {an}: 背景提到"{city}"但地点是{an}')

    # 检查坐标在中国范围内
    lat, lng = pd.get('lat', 0), pd.get('lng', 0)
    if lat != 0 and lng != 0:
        if lat < 18 or lat > 54 or lng < 73 or lng > 135:
            issues.append(f'{p["id"]} {an}: 坐标({lat},{lng})超出中国范围')

print(f'内容审核发现 {len(issues)} 个问题:')
for i in issues:
    print(f'  {i}')
