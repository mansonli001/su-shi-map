#!/usr/bin/env python3
"""检查缺少全文的诗词"""
import json
from pathlib import Path

# 加载诗词索引
with open('data-v4/poems-index.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

poems = data.get('poems', [])

# 检查哪些诗词缺少全文
missing_content = []

for poem in poems:
    pid = poem.get('id', '')
    fpath = Path(f'data-v4/poems/{pid}.json')
    
    if not fpath.exists():
        missing_content.append({'id': pid, 'title': poem.get('title', ''), 'reason': 'no_file'})
        continue
    
    with open(fpath, 'r', encoding='utf-8') as f:
        pdata = json.load(f)
    
    paragraphs = pdata.get('paragraphs', [])
    fullText = pdata.get('fullText', '')
    
    if not paragraphs and not fullText:
        missing_content.append({'id': pid, 'title': poem.get('title', ''), 'year': poem.get('year', ''), 'reason': 'no_content'})

print(f'=== 缺少全文的诗词 ===')
print(f'总数: {len(missing_content)}')
print(f'\n前30个:')
for m in missing_content[:30]:
    year_info = m.get('year', '?')
    print(f'{m["id"]}: {m["title"]} ({year_info}年) - {m["reason"]}')
