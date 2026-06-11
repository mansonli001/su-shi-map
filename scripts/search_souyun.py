#!/usr/bin/env python3
"""
Search sou-yun.cn for Su Shi poems matching empty entries.
Uses the search API to find poem texts by title keywords.
"""
import json, glob, re, os, time, urllib.request, urllib.parse

BASE = "/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data-v4/poems"

# Load empty entries
empty = []
for f in sorted(glob.glob(f'{BASE}/*.json')):
    with open(f) as fp:
        d = json.load(fp)
    if not d.get('paragraphs') or len(d.get('paragraphs', [])) == 0:
        empty.append(d)

print(f"Empty entries: {len(empty)}")

# Known verified fills from chinese-poetry
# S232: 高邮陈直躬处士画雁 ✓
# S330: 净行院 → 雨夜宿净行院 ✓
# S335: 平山堂次韵 → 平山堂次王居卿祠部韵 ✓

# For each empty entry, try to find the poem on sou-yun.cn
# The sou-yun search URL format: https://www.sou-yun.cn/api/poem/search?...
# Or we can use the character search: https://sou-yun.cn/CharInClause.aspx?c=潼

# Let's try fetching poem pages directly
# Format: https://www.sou-yun.cn/Query.aspx?type=poem1&id=XXXXX

# First, let's build a mapping of title keywords to search
search_list = []
for d in empty:
    fid = d['id']
    title = d['title']
    location = d.get('location', '')
    search_list.append({
        'id': fid,
        'title': title,
        'location': location,
        'type': d.get('type', '')
    })

# Print search list for manual web search
for item in search_list:
    print(f"{item['id']}: {item['title']} @ {item['location']}")
