#!/usr/bin/env python3
"""排查路径简述中的问题"""
import json

# 加载路线索引
with open('data-v4/routes-index.json', 'r', encoding='utf-8') as f:
    routes_data = json.load(f)

routes = routes_data.get('routes', [])
print(f'=== 路线简述排查 ===')
print(f'共 {len(routes)} 条路线\n')

issues = []

for route in routes:
    rid = route.get('id', '')
    name = route.get('name', '')
    desc = route.get('description_short', '')
    
    # 检查**号
    if '**' in desc:
        issues.append({
            'route_id': rid,
            'route_name': name,
            'issue_type': 'markdown_bold',
            'content': desc
        })
    
    # 检查其他常见问题
    if 'TODO' in desc or 'todo' in desc.lower():
        issues.append({
            'route_id': rid,
            'route_name': name,
            'issue_type': 'todo_mark',
            'content': desc
        })
    
    # 检查是否有不应该显示的标点
    bad_chars = ['```', '---', '>>>', '<<<']
    for char in bad_chars:
        if char in desc:
            issues.append({
                'route_id': rid,
                'route_name': name,
                'issue_type': 'bad_punctuation',
                'content': desc,
                'bad_char': char
            })

if issues:
    print(f'发现 {len(issues)} 个问题：')
    for i, issue in enumerate(issues, 1):
        print(f'\n{i}. [{issue["route_id"]}] {issue["route_name"]}')
        print(f'   问题类型: {issue["issue_type"]}')
        print(f'   内容: {issue["content"]}')
        if 'bad_char' in issue:
            print(f'   问题字符: {issue["bad_char"]}')
else:
    print('✓ 路线简述检查通过，未发现问题')

# 检查诗词的paragraphs字段覆盖情况
print('\n\n=== 诗词paragraphs字段检查 ===')
with open('data-v4/poems-index.json', 'r', encoding='utf-8') as f:
    poems_data = json.load(f)

poems = poems_data.get('poems', [])
from pathlib import Path

missing_paragraphs = []
has_paragraphs = []

for poem in poems:
    pid = poem.get('id', '')
    fpath = Path(f'data-v4/poems/{pid}.json')
    
    if not fpath.exists():
        missing_paragraphs.append({'id': pid, 'title': poem.get('title', ''), 'reason': 'file_missing'})
        continue
    
    with open(fpath, 'r', encoding='utf-8') as f:
        pdata = json.load(f)
    
    paragraphs = pdata.get('paragraphs', [])
    fullText = pdata.get('fullText', '')
    
    if paragraphs and len(paragraphs) > 0:
        has_paragraphs.append(pid)
    elif fullText and fullText.strip():
        has_paragraphs.append(pid)
    else:
        missing_paragraphs.append({'id': pid, 'title': poem.get('title', ''), 'reason': 'no_content'})

print(f'诗词总数: {len(poems)}')
print(f'有内容(paragraphs/fullText): {len(has_paragraphs)}')
print(f'缺少内容: {len(missing_paragraphs)}')

if missing_paragraphs:
    print(f'\n缺少内容的诗词（前20个）:')
    for m in missing_paragraphs[:20]:
        print(f'  {m["id"]}: {m["title"]} - {m["reason"]}')
