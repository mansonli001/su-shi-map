#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整数据架构分析报告
"""
import json
import os

print("="*70)
print("系统数据架构分析报告")
print("="*70)

# 数据文件路径
v3_core = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data/places-core.json'
v3_index = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data/places-index.json'
v4_dir = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places'
v4_index = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places-index.json'

# 加载数据
with open(v3_core, 'r', encoding='utf-8') as f:
    v3_core_data = json.load(f)
with open(v3_index, 'r', encoding='utf-8') as f:
    v3_index_data = json.load(f)
with open(v4_index, 'r', encoding='utf-8') as f:
    v4_index_data = json.load(f)

v4_files = sorted([f for f in os.listdir(v4_dir) if f.endswith('.json')])
with open(os.path.join(v4_dir, 'P001.json'), 'r', encoding='utf-8') as f:
    v4_sample = json.load(f)

print("\n【1】数据文件对比")
print("-"*50)
print(f"v3 places-core.json: {len(v3_core_data)} 条记录")
print(f"v3 places-index.json: {len(v3_index_data)} 条记录")
print(f"v4 places-index.json: {len(v4_index_data['places'])} 条记录")
print(f"v4 places/ 目录: {len(v4_files)} 个文件")

print("\n【2】字段映射关系")
print("-"*50)
print("┌─────────────────────────────────────────────────────────────────┐")
print("│                    v4 → v3 字段映射                            │")
print("├─────────────────────────┬───────────────────────────────────────┤")
print("│ v4 字段                  │ v3 字段                              │")
print("├─────────────────────────┼───────────────────────────────────────┤")
print("│ id                      │ id                                  │")
print("│ ancient_name            │ songName                            │")
print("│ modern_name             │ modernName                          │")
print("│ type + tags             │ type (智能映射)                     │")
print("│ related_routes[0]       │ routeId                             │")
print("│ lat/lng                 │ lat/lng                             │")
print("│ importance              │ importance                          │")
print("└─────────────────────────┴───────────────────────────────────────┘")

print("\n【3】v4特有字段（详细数据）")
print("-"*50)
v4_only = {'summary', 'background', 'global_events', 'global_works', 'foods', 
           'periods', 'memorial_sites', 'modern_visit', 'coordinate_source', 
           'amap_address', 'famous_line', 'legacy', 'transport', 'sub_places'}
print("v4特有字段（234个地点已包含）:")
field_desc = {
    'summary': '摘要',
    'background': '背景介绍',
    'global_events': '事迹/事件',
    'global_works': '诗词作品',
    'foods': '美食',
    'periods': '时期阶段',
    'memorial_sites': '文旅/纪念地',
    'modern_visit': '现代游览信息',
    'famous_line': '名句',
    'legacy': '文化遗产',
}
for field in v4_only:
    desc = field_desc.get(field, field)
    has_data = len(v4_sample.get(field, [])) > 0 if isinstance(v4_sample.get(field), list) else bool(v4_sample.get(field))
    status = '✅有数据' if has_data else '⚠️空'
    print(f"  {field:20s} → {desc:15s} {status}")

print("\n【4】数据引用架构")
print("-"*50)
print("┌─────────────────────────────────────────────────────────────────────┐")
print("│                     数据流向架构                                   │")
print("├─────────────────────────────────────────────────────────────────────┤")
print("│  data-v4/places/P001-P234.json  (234个详细地点文件)               │")
print("│              │                                                     │")
print("│              ▼                                                     │")
print("│  data-v4/places-index.json      (索引文件)                         │")
print("│              │                                                     │")
print("│              ▼                                                     │")
print("│  lib/v4-adapter.ts              (数据适配器)                       │")
print("│              │                                                     │")
print("│              ▼                                                     │")
print("│  PlaceCore[] (v3兼容格式)                                         │")
print("│              │                                                     │")
print("│        ┌─────┴─────┬──────────────┬──────────────────┐            │")
print("│        ▼           ▼              ▼                  ▼            │")
print("│   AMapContainer  LeftSidebar  Search组件      路线详情页           │")
print("└─────────────────────────────────────────────────────────────────────┘")

print("\n【5】关键数据表/文件")
print("-"*50)
print("┌──────────────────────────────────────────────────────────────────┐")
print("│ 数据表/文件                │ 用途                                  │")
print("├────────────────────────────┼──────────────────────────────────────┤")
print("│ data-v4/places/*.json      │ 234个地点详细数据（事迹/作品/美食）  │")
print("│ data-v4/places-index.json  │ 地点索引（供搜索/列表）              │")
print("│ data-v4/routes-index.json  │ 路线索引（19条路线）                 │")
print("│ data-v4/stages-index.json  │ 阶段索引（6个人生阶段）              │")
print("│ data-v4/routes/R*.json     │ 路线详情（轨迹点顺序）               │")
print("│ data-v4/foods-sushi.json   │ 苏轼特供美食数据                     │")
print("└────────────────────────────┴──────────────────────────────────────┘")

print("\n【6】字段完整性统计（v4 234个地点）")
print("-"*50)

# 统计v4数据完整性
stats = {}
fields_to_count = ['summary', 'background', 'global_events', 'global_works', 'foods', 'periods', 'memorial_sites']
for f in v4_files:
    with open(os.path.join(v4_dir, f), 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    for field in fields_to_count:
        if field not in stats:
            stats[field] = 0
        if field in data and data[field]:
            if isinstance(data[field], list):
                if len(data[field]) > 0:
                    stats[field] += 1
            else:
                stats[field] += 1

print(f"总地点数: {len(v4_files)}")
for field, count in stats.items():
    pct = count / len(v4_files) * 100
    print(f"  {field_desc.get(field, field)}: {count}/{len(v4_files)} ({pct:.1f}%)")

print("\n【7】总结")
print("-"*50)
print("✅ 现有系统通过 v4-adapter.ts 引用 v4 数据")
print("✅ 234个地点数据已存在于 data-v4/places/ 目录")
print("✅ 事迹→global_events, 诗词作品→global_works, 美食→foods")
print("✅ 文旅信息在 memorial_sites 和 modern_visit 字段中")
print("✅ 苏轼特供美食在 foods-sushi.json 中")
print("\n⚠️ 注意: public/data/places-core.json 是旧版v3数据(160条)")
print("        系统运行时优先使用v4数据，通过adapter转换")
