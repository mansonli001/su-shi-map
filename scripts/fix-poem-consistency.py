#!/usr/bin/env python3
"""修复诗词索引和详情的不一致问题"""
import json
from pathlib import Path

# 需要修复的问题映射
FIXES = {
    "W005": {"title": "江淮行旅杂咏"},
    "W006": {"title": "上神宗皇帝书"},
    "W007": {"year": 1089},
    "W009": {"title": "六月二十七日望湖楼醉书五首"},
    "W010": {"title": "饮湖上初晴后雨二首"},
    "W011": {"year": 1089},
    "W017": {"year": 1074},
    "W029": {"year": 1083},
    "W030": {"year": 1083},
    "W043": {"year": 1091},
    "W047": {"year": 1092},
    "W048": {"year": 1092},
    "W050": {"year": 1084},
    "W053": {"year": 1089},
    "W054": {"year": 1082},
    "W056": {"year": 1094},
    "W062": {"year": 1096}
}

def main():
    # 修复索引文件
    with open('data-v4/poems-index.json', 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    poems = index_data.get('poems', [])
    
    for poem in poems:
        pid = poem.get('id', '')
        if pid in FIXES:
            fixes = FIXES[pid]
            if 'title' in fixes:
                poem['title'] = fixes['title']
                print(f'✅ [{pid}] 索引标题修正为: "{fixes["title"]}"')
            if 'year' in fixes:
                poem['year'] = fixes['year']
                print(f'✅ [{pid}] 索引年份修正为: {fixes["year"]}')
    
    # 保存索引文件（v6.1: 删除 public 双写，改由 sync_public 统一同步）
    with open('data-v4/poems-index.json', 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print('\n' + '=' * 60)
    print('索引文件已修复')

    import sys as _sys
    from pathlib import Path as _Path
    _sys.path.insert(0, str(_Path(__file__).resolve().parent))
    from lib_sync import sync_public
    sync_public()

if __name__ == "__main__":
    main()