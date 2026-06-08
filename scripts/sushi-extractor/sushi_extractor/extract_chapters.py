#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from docx import Document

# 读取黄州章节
doc = Document('/Users/mansonlee/Downloads/苏轼行踪考/Word版本/15 第十二篇  貶謫黃州.docx')

chapters = []
current = {'title': '前言', 'content': ''}

for para in doc.paragraphs:
    text = para.text.strip()
    if not text:
        continue
    
    # 检测章节标题
    if '第' in text and ('章' in text or '篇' in text):
        if current['content']:
            chapters.append(current)
        current = {'title': text, 'content': text + '\n'}
    else:
        current['content'] += text + '\n'

if current['content']:
    chapters.append(current)

print(f'共 {len(chapters)} 章节')
for i, ch in enumerate(chapters[:8], 1):
    print(f'[{i}] {ch["title"][:40]}... ({len(ch["content"])} 字)')

# 保存章节内容
with open('huangzhou_chapters.txt', 'w', encoding='utf-8') as f:
    for i, ch in enumerate(chapters, 1):
        f.write(f'=== 第{i}章: {ch["title"]} ===\n')
        f.write(ch['content'])
        f.write('\n' + '='*60 + '\n\n')

print('\n章节内容已保存到 huangzhou_chapters.txt')
