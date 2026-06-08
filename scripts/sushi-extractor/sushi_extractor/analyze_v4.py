#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

v4_dir = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places'
files = sorted([f for f in os.listdir(v4_dir) if f.endswith('.json')])

print(f"v4地点数量: {len(files)}")
print("="*60)

# 分析一个示例的结构
with open(os.path.join(v4_dir, 'P001.json'), 'r') as f:
    sample = json.load(f)

print("字段列表:")
for key in sample.keys():
    val = sample[key]
    if isinstance(val, list):
        print(f"  {key}: list[{len(val)}]")
    elif isinstance(val, dict):
        print(f"  {key}: dict[{len(val)}]")
    else:
        print(f"  {key}: {type(val).__name__} = {str(val)[:50]}...")

# 统计字段完整性
print("\n统计字段完整性:")
fields = ['summary', 'background', 'tags', 'periods', 'global_events', 'global_works', 'foods']
field_counts = {}
for field in fields:
    count = 0
    for f in files:
        with open(os.path.join(v4_dir, f), 'r') as fp:
            data = json.load(fp)
        if field in data and data[field]:
            if isinstance(data[field], list):
                count += len(data[field])
            else:
                count += 1
    field_counts[field] = count
    print(f"  {field}: {count} 条")

# 显示几个示例
print("\n示例地点:")
for i, f in enumerate(files[:5]):
    with open(os.path.join(v4_dir, f), 'r') as fp:
        data = json.load(fp)
    works_count = len(data.get('global_works', []))
    print(f"  {data['id']}: {data['ancient_name']} ({data['modern_name']}) - 作品{works_count}篇")
