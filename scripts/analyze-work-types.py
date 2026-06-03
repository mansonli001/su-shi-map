#!/usr/bin/env python3
"""分析当前作品类型分布并设计编号体系"""
import json
from pathlib import Path

# 加载诗词索引
with open('data-v4/poems-index.json', 'r', encoding='utf-8') as f:
    index_data = json.load(f)

poems = index_data.get('poems', [])

# 统计类型分布
type_counts = {}
type_poems = {}

for poem in poems:
    p_type = poem.get('type', 'unknown')
    if p_type not in type_counts:
        type_counts[p_type] = 0
        type_poems[p_type] = []
    type_counts[p_type] += 1
    type_poems[p_type].append(poem)

print('=== 当前作品类型分布 ===')
print('=' * 60)

total = len(poems)
for p_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
    percentage = count / total * 100
    print(f'{p_type}: {count} 首 ({percentage:.1f}%)')

print('\n' + '=' * 60)

# 设计新的编号体系
print('建议的作品类型编号体系：')
print('-' * 40)
print('| 类型 | 编号前缀 | 说明 |')
print('|------|----------|------|')
print('| 诗   | Sxxx     | 诗歌（古诗、律诗、绝句等） |')
print('| 词   | Cxxx     | 词（词牌、长短句） |')
print('| 文   | Wxxx     | 文章（论、说、传等） |')
print('| 书   | Lxxx     | 书信（书、启、帖等） |')
print('| 记   | Jxxx     | 记文（游记、杂记等） |')
print('| 赋   | Fxxx     | 赋体文 |')
print('| 策   | Zxxx     | 策论、奏疏 |')
print('| 序   | Xxxx     | 序跋 |')
print('| 铭   | Mxxx     | 铭文 |')

print('\n' + '=' * 60)
print('现有编号体系分析：')
print(f'当前编号范围: W001 - W{len(poems)}')
print(f'总作品数: {len(poems)}')

# 显示各类示例
print('\n各类作品示例：')
for p_type, poems_list in type_poems.items():
    examples = [p['title'] for p in poems_list[:3]]
    print(f'{p_type}: {", ".join(examples)}...')