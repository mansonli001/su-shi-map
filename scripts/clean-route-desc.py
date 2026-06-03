#!/usr/bin/env python3
"""检查并清理所有路线的详述内容中的markdown格式符号"""
import json
from pathlib import Path

routes_dir = Path('data-v4/routes')
route_files = sorted(routes_dir.glob('R*.json'))

issues_found = []
cleaned_count = 0

print('=== 路线详述清理检查 ===')
print('=' * 60)

for rf in route_files:
    with open(rf, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    rid = data.get('id', '')
    name = data.get('name', '')
    desc_long = data.get('description_long', '')
    
    issues = []
    
    # 检查各种markdown格式
    if '**' in desc_long:
        issues.append('markdown加粗')
        desc_long_clean = desc_long.replace('**', '')
    
    if '`' in desc_long:
        issues.append('markdown代码')
        desc_long_clean = desc_long.replace('`', '')
    
    if '__' in desc_long:
        issues.append('markdown下划线')
        desc_long_clean = desc_long.replace('__', '')
    
    if issues:
        issues_found.append({
            'route_id': rid,
            'route_name': name,
            'issues': issues,
            'original': desc_long[:50] + '...' if len(desc_long) > 50 else desc_long
        })
        
        # 清理并保存（v6.1: 删除 public 双写）
        data['description_long'] = desc_long_clean
        with open(rf, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        cleaned_count += 1
        print(f'✅ [{rid}] {name} - 已清理 {", ".join(issues)}')
    else:
        print(f'✓ [{rid}] {name} - 检查通过')

print('\n' + '=' * 60)
print(f'发现问题: {len(issues_found)} 条路线')
print(f'已清理: {cleaned_count} 条路线')

# 检查核心精华字段
print('\n\n=== 核心精华字段检查 ===')
for rf in route_files:
    with open(rf, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rid = data.get('id', '')
    name = data.get('name', '')
    core_essence = data.get('core_essence', '')

    if '**' in core_essence:
        issues_found.append({
            'route_id': rid,
            'route_name': name,
            'issues': ['core_essence含markdown加粗'],
            'original': core_essence[:50] + '...' if len(core_essence) > 50 else core_essence
        })

        data['core_essence'] = core_essence.replace('**', '')
        with open(rf, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        cleaned_count += 1
        print(f'✅ [{rid}] {name} - 已清理 core_essence 中的 markdown加粗')

# v6.1: 一次性把 data-v4 同步到 public/data-v4
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
from lib_sync import sync_public
sync_public()
