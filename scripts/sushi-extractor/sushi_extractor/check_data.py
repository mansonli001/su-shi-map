#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

data_dir = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data'

print("📁 检查所有数据文件")
print("="*60)

for filename in os.listdir(data_dir):
    if filename.endswith('.json'):
        path = os.path.join(data_dir, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                print(f"  {filename}: {len(data)} 条记录")
            elif isinstance(data, dict):
                print(f"  {filename}: {len(data)} 个键")
        except Exception as e:
            print(f"  {filename}: 读取失败 - {e}")

# 检查src目录
src_dir = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/src'
print(f"\n📁 检查src目录")
print("="*60)
for root, dirs, files in os.walk(src_dir):
    for f in files:
        if f.endswith('.json'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                if isinstance(data, list):
                    print(f"  {path}: {len(data)} 条记录")
            except:
                pass

# 检查routes目录
routes_dir = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/routes'
print(f"\n📁 检查routes目录")
print("="*60)
if os.path.exists(routes_dir):
    for f in os.listdir(routes_dir):
        if f.endswith('.json'):
            path = os.path.join(routes_dir, f)
            try:
                with open(path, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                if isinstance(data, list):
                    print(f"  {f}: {len(data)} 条记录")
            except:
                pass
