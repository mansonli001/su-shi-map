#!/usr/bin/env python3
"""检查诗词标题和内容的一致性"""
import json
from pathlib import Path

# 加载诗词索引
with open('data-v4/poems-index.json', 'r', encoding='utf-8') as f:
    index_data = json.load(f)

poems_index = index_data.get('poems', [])
poems_dir = Path('data-v4/poems')

print('=== 诗词标题和内容一致性检查 ===')
print('=' * 60)

inconsistencies = []

for poem in poems_index:
    pid = poem.get('id', '')
    index_title = poem.get('title', '')
    
    # 检查文件是否存在
    fpath = poems_dir / f'{pid}.json'
    if not fpath.exists():
        inconsistencies.append({
            'id': pid,
            'issue': 'file_missing',
            'detail': f'索引中有此诗词，但文件不存在'
        })
        continue
    
    # 读取详情文件
    with open(fpath, 'r', encoding='utf-8') as f:
        detail_data = json.load(f)
    
    detail_title = detail_data.get('title', '')
    
    # 检查标题一致性
    if index_title != detail_title:
        inconsistencies.append({
            'id': pid,
            'issue': 'title_mismatch',
            'detail': f'索引标题: "{index_title}"，详情标题: "{detail_title}"'
        })
    
    # 检查内容是否存在
    paragraphs = detail_data.get('paragraphs', [])
    fullText = detail_data.get('fullText', '')
    
    if not paragraphs and not fullText:
        inconsistencies.append({
            'id': pid,
            'issue': 'no_content',
            'detail': '缺少paragraphs或fullText字段'
        })
    
    # 检查年份一致性
    index_year = poem.get('year', 0)
    detail_year = detail_data.get('year', 0)
    
    if index_year != 0 and detail_year != 0 and index_year != detail_year:
        inconsistencies.append({
            'id': pid,
            'issue': 'year_mismatch',
            'detail': f'索引年份: {index_year}，详情年份: {detail_year}'
        })

if inconsistencies:
    print(f'发现 {len(inconsistencies)} 处不一致:')
    for i, issue in enumerate(inconsistencies, 1):
        print(f'\n{i}. [{issue["id"]}] {issue["issue"]}')
        print(f'   {issue["detail"]}')
else:
    print('✓ 所有诗词数据一致')

print('\n' + '=' * 60)
print(f'诗词总数: {len(poems_index)}')
print(f'详情文件数: {len(list(poems_dir.glob("*.json")))}')