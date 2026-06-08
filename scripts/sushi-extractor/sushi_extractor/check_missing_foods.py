#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

V4_DIR = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places'

files = sorted([f for f in os.listdir(V4_DIR) if f.endswith('.json')])

missing_foods = []
for filename in files:
    path = os.path.join(V4_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data.get('foods'):
        missing_foods.append({
            'id': data['id'],
            'ancient_name': data.get('ancient_name', ''),
            'modern_name': data.get('modern_name', '')
        })

print(f"缺少美食的地点 ({len(missing_foods)} 个):")
for p in missing_foods:
    print(f"  {p['id']}: {p['ancient_name']} ({p['modern_name']})")
