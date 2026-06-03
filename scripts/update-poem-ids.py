#!/usr/bin/env python3
"""为地点作品更新poem_id"""
import json
from pathlib import Path

# 作品标题到poem_id的映射
WORK_TO_POEM_ID = {
    "初入庐山": "W322",
    "泊船瓜洲": "W323",
    "别子由三首": "W324",
    "留题仙游潭中兴寺": "W325",
    "定州中山怀古": "W326",
    "平山堂怀古": "W327",
    "海南日记": "W328"
}

places_dir = Path('data-v4/places')
place_files = sorted(places_dir.glob('P*.json'))

updated_count = 0

print('=== 更新地点作品的poem_id ===')
print('=' * 60)

for pf in place_files:
    with open(pf, 'r', encoding='utf-8') as f:
        place_data = json.load(f)
    
    place_id = place_data.get('id', '')
    place_name = place_data.get('ancient_name', place_data.get('name', ''))
    works = place_data.get('global_works', [])
    
    for work in works:
        work_title = work.get('title', '')
        
        if work_title in WORK_TO_POEM_ID:
            poem_id = WORK_TO_POEM_ID[work_title]
            work['poem_id'] = poem_id
            updated_count += 1
            print(f'✅ [{place_id}] {place_name}: "{work_title}" → {poem_id}')
    
    # 保存更新（v6.1: 删除 public 双写，由末尾 sync_public 兜底）
    with open(pf, 'w', encoding='utf-8') as f:
        json.dump(place_data, f, ensure_ascii=False, indent=2)

print('\n' + '=' * 60)
print(f'已更新 {updated_count} 个作品的poem_id')
# v6.1: 一次性把 data-v4 同步到 public/data-v4
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
from lib_sync import sync_public
sync_public()
