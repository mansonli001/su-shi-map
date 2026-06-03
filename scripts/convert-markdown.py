#!/usr/bin/env python3
"""将路线详述中的markdown加粗转换为HTML strong标签"""
import json
from pathlib import Path
import re

def markdown_to_html(text):
    """将markdown格式转换为HTML"""
    if not isinstance(text, str):
        return text
    
    # 将 **内容** 转换为 <strong>内容</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # 将 *内容* 转换为 <em>内容</em>
    text = re.sub(r'(?<!\*)\*(.*?)\*(?!\*)', r'<em>\1</em>', text)
    
    return text

def convert_dict_recursively(data):
    """递归转换字典中的所有字符串字段"""
    if isinstance(data, dict):
        return {k: convert_dict_recursively(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_dict_recursively(item) for item in data]
    elif isinstance(data, str):
        return markdown_to_html(data)
    else:
        return data

routes_dir = Path('data-v4/routes')
route_files = sorted(routes_dir.glob('R*.json'))

print('=== 将markdown格式转换为HTML ===')
print('=' * 60)

for rf in route_files:
    with open(rf, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    rid = data.get('id', '')
    name = data.get('name', '')
    
    # 转换所有字段
    converted_data = convert_dict_recursively(data)
    
    # 保存到源目录（v6.1: 删除 public 双写）
    with open(rf, 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, ensure_ascii=False, indent=2)

    print(f'✅ [{rid}] {name} - 已转换')

print('\n' + '=' * 60)
print(f'已转换 {len(route_files)} 条路线')

# 验证结果
print('\n\n=== 验证转换结果 ===')
has_markdown = False
for rf in route_files:
    with open(rf, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '**' in content or '__' in content:
        has_markdown = True
        rid = rf.stem
        print(f'⚠️ [{rid}] 仍有未转换的markdown格式')

if not has_markdown:
    print('✓ 所有markdown格式已转换为HTML')
# v6.1: 一次性把 data-v4 同步到 public/data-v4
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
from lib_sync import sync_public
sync_public()
