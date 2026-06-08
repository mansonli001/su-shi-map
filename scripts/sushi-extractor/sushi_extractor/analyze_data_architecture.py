#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析现有项目数据架构，对比v4数据结构
"""
import json
import os

# 现有项目数据文件
core_path = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data/places-core.json'
index_path = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data/places-index.json'
v4_dir = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places'

print("="*70)
print("系统数据架构分析")
print("="*70)

# 1. 分析 places-core.json 结构
print("\n【1】places-core.json - 核心地点数据")
print("-"*50)
with open(core_path, 'r', encoding='utf-8') as f:
    core_data = json.load(f)
print(f"记录数: {len(core_data)}")
print("\n字段结构:")
sample = core_data[0]
for key, val in sample.items():
    if isinstance(val, list):
        print(f"  {key}: list[{len(val)}]")
    else:
        print(f"  {key}: {type(val).__name__} = {str(val)[:40]}...")

# 2. 分析 places-index.json 结构
print("\n【2】places-index.json - 地点索引")
print("-"*50)
with open(index_path, 'r', encoding='utf-8') as f:
    index_data = json.load(f)
print(f"记录数: {len(index_data)}")
print("\n字段结构:")
sample = index_data[0]
for key, val in sample.items():
    if isinstance(val, list):
        print(f"  {key}: list[{len(val)}]")
    else:
        print(f"  {key}: {type(val).__name__} = {str(val)[:40]}...")

# 3. 分析 v4 数据结构
print("\n【3】v4数据 (data-v4/places/) - 详细地点数据")
print("-"*50)
v4_files = sorted([f for f in os.listdir(v4_dir) if f.endswith('.json')])
print(f"记录数: {len(v4_files)}")

with open(os.path.join(v4_dir, 'P001.json'), 'r', encoding='utf-8') as f:
    v4_sample = json.load(f)
print("\n字段结构:")
for key, val in v4_sample.items():
    if isinstance(val, list):
        print(f"  {key}: list[{len(val)}]")
    elif isinstance(val, dict):
        print(f"  {key}: dict")
    else:
        print(f"  {key}: {type(val).__name__} = {str(val)[:40]}...")

# 4. 对比分析
print("\n【4】数据结构对比")
print("-"*50)
core_fields = set(core_data[0].keys())
v4_fields = set(v4_sample.keys())

print("core特有字段:", core_fields - v4_fields)
print("v4特有字段:", v4_fields - core_fields)
print("共同字段:", core_fields & v4_fields)

# 5. 查找系统中引用这些数据的文件
print("\n【5】查找系统中的数据引用")
print("-"*50)
import subprocess
result = subprocess.run(
    ['grep', '-r', 'places-core\\|places-index\\|data-v4', 
     '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/src',
     '--include=*.ts', '--include=*.tsx', '-l'],
    capture_output=True, text=True
)
print("引用数据的文件:")
for f in result.stdout.strip().split('\n')[:10]:
    if f:
        print(f"  {f}")
