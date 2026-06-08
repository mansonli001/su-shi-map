#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证提取结果并生成统计报告
"""
import json
import os

OUTPUT_DIR = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places'

# 统计更新后的v4数据
files = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.json')])

stats = {
    'events': 0,
    'works': 0,
    'sites': 0,
    'places_with_events': 0,
    'places_with_works': 0,
    'places_with_sites': 0,
}

sample_places = []

for filename in files[:50]:
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    events = data.get('global_events', [])
    works = data.get('global_works', [])
    sites = data.get('memorial_sites', [])
    
    if events:
        stats['events'] += len(events)
        stats['places_with_events'] += 1
    if works:
        stats['works'] += len(works)
        stats['places_with_works'] += 1
    if sites:
        stats['sites'] += len(sites)
        stats['places_with_sites'] += 1
    
    # 收集样本
    if len(sample_places) < 5 and (events or works):
        sample_places.append({
            'id': data['id'],
            'ancient_name': data.get('ancient_name', ''),
            'events': events[:2],
            'works': works[:2],
            'sites': sites[:2]
        })

print("="*60)
print("提取结果验证报告")
print("="*60)
print(f"总地点数: {len(files)}")
print("\n【事件统计】")
print(f"  有事件的地点: {stats['places_with_events']}/{len(files)}")
print(f"  事件总数: {stats['events']}")
print("\n【作品统计】")
print(f"  有作品的地点: {stats['places_with_works']}/{len(files)}")
print(f"  作品总数: {stats['works']}")
print("\n【纪念地统计】")
print(f"  有纪念地的地点: {stats['places_with_sites']}/{len(files)}")
print(f"  纪念地总数: {stats['sites']}")

print("\n【样本展示】")
for place in sample_places:
    print(f"\n📍 {place['id']}: {place['ancient_name']}")
    if place['events']:
        print("  事件:")
        for e in place['events']:
            print(f"    - {e['description'][:50]}...")
    if place['works']:
        print("  作品:")
        for w in place['works']:
            print(f"    - 《{w['title']}》")
    if place['sites']:
        print("  纪念地:")
        for s in place['sites']:
            print(f"    - {s['name']}")
