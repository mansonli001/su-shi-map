#!/usr/bin/env python3
"""Roll back inaccurate Level 4 matches and keep only verified ones."""
import json, os

BASE = "/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data-v4/poems"

# Verified correct matches (title clearly corresponds)
VERIFIED = {
    'S232': True,   # 高邮陈直躬处士画雁 → 高邮陈直躬处士画雁二首 ✓
    'S330': True,   # 净行院 → 雨夜宿净行院 ✓
    'S335': True,   # 平山堂次韵 → 平山堂次王居卿祠部韵 ✓
}

# Incorrect matches - need rollback
ROLLBACK = [
    'S260',  # 至济南李公择以诗相迎次韵 → 次韵刘贡父李公择见寄 ✗ wrong poem
    'S266',  # 江州重别薛六柳八二员外 → 赠江州景德长老 ✗ wrong poem
    'S270',  # 雷州八首 → 东坡八首 ✗ WRONG (雷州八首 is by 秦观!)
    'S273',  # 白石镇题诗 → 书李公择白石山房 ✗ wrong poem
    'S276',  # 次韵卢山五咏 → 次韵水官诗 ✗ wrong
    'S279',  # 洛阳次韵 → 次韵水官诗 ✗ wrong
    'S305',  # 泗水亭怀古 → 城南县尉水亭得长字 ✗ wrong
    'S307',  # 次韵苏州王太守 → 次韵水官诗 ✗ wrong
    'S313',  # 潼关次韵 → 次韵水官诗 ✗ wrong
    'S342',  # 益州官署怀古 → 赠黄州官妓 ✗ wrong
    'W227',  # 登州文庙 → 登州孙氏万松堂 ✗ wrong
]

rolled_back = 0
kept = 0

for fid in ROLLBACK:
    fpath = f'{BASE}/{fid}.json'
    with open(fpath) as f:
        d = json.load(f)
    
    # Remove incorrect data
    d['paragraphs'] = []
    for key in ['coreVerse', 'has_full_text', 'full_text_source', 'full_text_match_level', 'matched_title']:
        d.pop(key, None)
    
    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    
    rolled_back += 1
    print(f"  Rolled back: {fid}: {d['title']}")

for fid in VERIFIED:
    kept += 1
    print(f"  Kept: {fid}")

print(f"\nRolled back: {rolled_back}, Kept: {kept}")
