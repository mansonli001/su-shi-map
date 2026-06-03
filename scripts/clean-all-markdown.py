#!/usr/bin/env python3
"""全面清理路线文件中所有字段的markdown格式符号"""
import json
from pathlib import Path
import re

def clean_markdown(text):
    """清理文本中的markdown格式符号"""
    if not isinstance(text, str):
        return text
    
    # 移除markdown加粗
    text = text.replace('**', '')
    # 移除markdown斜体
    text = text.replace('*', '')
    # 移除非必要的markdown格式
    text = text.replace('`', '')
    text = text.replace('__', '')
    text = text.replace('~~', '')
    
    # 清理多余的空行
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def clean_dict_recursively(data):
    """递归清理字典中的所有字符串字段"""
    if isinstance(data, dict):
        return {k: clean_dict_recursively(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_dict_recursively(item) for item in data]
    elif isinstance(data, str):
        return clean_markdown(data)
    else:
        return data

routes_dir = Path('data-v4/routes')
route_files = sorted(routes_dir.glob('R*.json'))

print('=== 全面清理路线文件中的markdown格式 ===')
print('=' * 60)

for rf in route_files:
    with open(rf, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    rid = data.get('id', '')
    name = data.get('name', '')
    
    # 清理所有字段
    cleaned_data = clean_dict_recursively(data)
    
    # 保存到源目录（v6.1: 删除 public 双写）
    with open(rf, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    print(f'✅ [{rid}] {name} - 已清理')

print('\n' + '=' * 60)
print(f'已清理 {len(route_files)} 条路线')

# 验证结果
print('\n\n=== 验证清理结果 ===')
has_markdown = False
for rf in route_files:
    with open(rf, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '**' in content or '__' in content or '`' in content:
        has_markdown = True
        rid = rf.stem
        print(f'⚠️ [{rid}] 仍有markdown格式')

if not has_markdown:
    print('✓ 所有路线文件已清理干净')

# v6.1: 一次性把 data-v4 同步到 public/data-v4
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
from lib_sync import sync_public
sync_public()
