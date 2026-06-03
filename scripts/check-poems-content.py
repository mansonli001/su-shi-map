#!/usr/bin/env python3
"""检查诗词全文完整性"""
import json
from pathlib import Path

# 加载索引
with open('data-v4/poems-index.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

poems = data.get('poems', [])
total = len(poems)

# 统计
has_text = 0
no_file = 0
no_paragraphs = 0

missing_list = []

for poem in poems:
    pid = poem.get('id', '')
    fpath = Path(f'data-v4/poems/{pid}.json')

    if not fpath.exists():
        no_file += 1
        missing_list.append({'id': pid, 'title': poem.get('title', ''), 'reason': 'no_file'})
        continue

    with open(fpath, 'r', encoding='utf-8') as f:
        pdata = json.load(f)

    paragraphs = pdata.get('paragraphs', [])
    fullText = pdata.get('fullText', '')

    if not paragraphs and not fullText:
        no_paragraphs += 1
        missing_list.append({'id': pid, 'title': poem.get('title', ''), 'year': poem.get('year', ''), 'reason': 'no_content'})
    else:
        has_text += 1

print(f'=== 诗词全文统计 ===')
print(f'总数: {total}')
print(f'有全文: {has_text}')
print(f'无全文文件: {no_file}')
print(f'有文件无内容: {no_paragraphs}')
print(f'\n=== 无全文的诗词 (前30个) ===')
for m in missing_list[:30]:
    year_info = m.get('year', '?')
    print(f'{m["id"]}: {m["title"]} ({year_info}年) - {m["reason"]}')
