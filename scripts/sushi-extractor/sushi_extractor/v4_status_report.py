#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

V4_DIR = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places'

files = sorted([f for f in os.listdir(V4_DIR) if f.endswith('.json')])

print("="*60)
print("v4数据完整状态报告")
print("="*60)
print(f"总地点数: {len(files)}")
print()

# 统计各字段
stats = {
    'summary': 0,       # 摘要
    'background': 0,     # 背景
    'tags': 0,          # 标签
    'periods': 0,       # 时期
    'global_events': 0, # 事件
    'global_works': 0,  # 作品
    'foods': 0,         # 美食
}

for filename in files:
    path = os.path.join(V4_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if data.get('summary'):
        stats['summary'] += 1
    if data.get('background'):
        stats['background'] += 1
    if data.get('tags') and len(data['tags']) > 0:
        stats['tags'] += 1
    if data.get('periods') and len(data['periods']) > 0:
        stats['periods'] += 1
    if data.get('global_events') and len(data['global_events']) > 0:
        stats['global_events'] += 1
    if data.get('global_works') and len(data['global_works']) > 0:
        stats['global_works'] += 1
    if data.get('foods') and len(data['foods']) > 0:
        stats['foods'] += 1

print("字段完整率:")
for field, count in stats.items():
    pct = count / len(files) * 100
    bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
    print(f"  {field:15s}: {count:3d}/{len(files)} ({pct:5.1f}%) {bar}")

print()
print("="*60)
print("优先级分析")
print("="*60)

# 优先级：美食和作品最重要
if stats['foods'] >= 234:
    print("✅ 美食: 100% 完成")
else:
    print(f"❌ 美食: {stats['foods']}/234 ({stats['foods']/234*100:.1f}%)")

if stats['global_works'] >= 200:
    print("✅ 作品: 85%+ 完成")
elif stats['global_works'] >= 136:
    print(f"⚠️  作品: {stats['global_works']}/234 ({stats['global_works']/234*100:.1f}%) - 需要补充 {234-stats['global_works']} 个地点")
