#!/usr/bin/env python3
"""
为主地点补充该时期全部作品
主地点 = 苏轼长期居住/为官的重要地点（非途径）
"""

import json
import glob
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data-v4')
PLACES_DIR = os.path.join(DATA_DIR, 'places')
POEMS_DIR = os.path.join(DATA_DIR, 'poems')

def load_json(path):
    with open(path) as f:
        return json.load(f)

# 苏轼主要时期与地点对照
# 每个主地点对应一个时期，列出该时期的主要作品
MAJOR_PERIOD_WORKS = {
    'P072': {  # 黄州（1080-1084，贬谪时期）
        'period': '黄州时期 (1080-1084)',
        'works': [
            # 已有poem_id的不重复添加，只补充缺失的
            {'title': '初到黄州', 'type': '诗', 'poem_id': None},
            {'title': '东坡', 'type': '诗', 'poem_id': None},
            {'title': '东坡八首', 'type': '诗', 'poem_id': None},
            {'title': '雪后书北台壁', 'type': '诗', 'poem_id': None},
            {'title': '正月二十日往岐亭郡人潘古郭三人送余于女王城东禅庄院', 'type': '诗', 'poem_id': None},
            {'title': '寒食雨二首', 'type': '诗', 'poem_id': None},
            {'title': '琴诗', 'type': '诗', 'poem_id': None},
            {'title': '洗儿戏作', 'type': '诗', 'poem_id': None},
            {'title': '海棠', 'type': '诗', 'poem_id': None},
            {'title': '和子由苦寒见寄', 'type': '诗', 'poem_id': None},
            {'title': '黄州上文潞公书', 'type': '文', 'poem_id': None},
        ]
    },
    'P089': {  # 杭州（1089-1091，知州时期 + 1071-1074通判时期）
        'period': '杭州时期 (1071-1074, 1089-1091)',
        'works': [
            {'title': '六月二十七日望湖楼醉书', 'type': '诗', 'poem_id': None},
            {'title': '望湖楼醉书', 'type': '诗', 'poem_id': None},
            {'title': '吉祥寺赏牡丹', 'type': '诗', 'poem_id': None},
            {'title': '吉祥寺僧求阁名', 'type': '诗', 'poem_id': None},
            {'title': '湖上夜归', 'type': '诗', 'poem_id': None},
            {'title': '孤山二首', 'type': '诗', 'poem_id': None},
            {'title': '次韵子由柳湖感物', 'type': '诗', 'poem_id': None},
            {'title': '送郑户曹', 'type': '诗', 'poem_id': None},
            {'title': '与莫同年雨中饮湖上', 'type': '诗', 'poem_id': None},
            {'title': '次韵曹辅寄壑源试焙新茶', 'type': '诗', 'poem_id': None},
        ]
    },
    'P034': {  # 儋州（1097-1100，贬谪时期）
        'period': '儋州时期 (1097-1100)',
        'works': [
            {'title': '别海南黎民表', 'type': '诗', 'poem_id': None},
            {'title': '儋耳山', 'type': '诗', 'poem_id': None},
            {'title': '儋耳夜书', 'type': '诗', 'poem_id': None},
            {'title': '被酒独行遍至子云威徽先觉四黎之舍', 'type': '诗', 'poem_id': None},
            {'title': '试笔自书', 'type': '文', 'poem_id': None},
            {'title': '书上元夜游', 'type': '文', 'poem_id': None},
            {'title': '与程秀才书', 'type': '文', 'poem_id': None},
        ]
    },
    'P008': {  # 汴京（多次，主要是京官时期）
        'period': '汴京时期 (多段)',
        'works': [
            {'title': '上神宗皇帝书', 'type': '策', 'poem_id': 'Z002'},
            {'title': '刑赏忠厚之至论', 'type': '策', 'poem_id': 'Z001'},
            {'title': '策略', 'type': '策', 'poem_id': None},
            {'title': '思治论', 'type': '文', 'poem_id': None},
            {'title': '进策', 'type': '策', 'poem_id': None},
            {'title': '留侯论', 'type': '文', 'poem_id': None},
            {'title': '贾谊论', 'type': '文', 'poem_id': None},
        ]
    },
    'P039': {  # 密州（1074-1076）
        'period': '密州时期 (1074-1076)',
        'works': [
            {'title': '江城子·乙卯正月二十日夜记梦', 'type': '词', 'poem_id': None},
            {'title': '江城子·密州出猎', 'type': '词', 'poem_id': None},
            {'title': '水调歌头·明月几时有', 'type': '词', 'poem_id': None},
        ]
    },
    'P041': {  # 徐州（1077-1079）
        'period': '徐州时期 (1077-1079)',
        'works': [
            {'title': '永遇乐·明月如霜', 'type': '词', 'poem_id': None},
            {'title': '浣溪沙·簌簌衣巾落枣花', 'type': '词', 'poem_id': None},
            {'title': '浣溪沙·软草平莎过雨新', 'type': '词', 'poem_id': None},
            {'title': '登云龙山', 'type': '诗', 'poem_id': None},
            {'title': '放鹤亭记', 'type': '文', 'poem_id': None},
        ]
    },
    'P057': {  # 惠州（1094-1097）
        'period': '惠州时期 (1094-1097)',
        'works': [
            {'title': '惠州一绝', 'type': '诗', 'poem_id': None},
            {'title': '食荔枝', 'type': '诗', 'poem_id': None},
            {'title': '荔枝叹', 'type': '诗', 'poem_id': None},
            {'title': '记游松风亭', 'type': '文', 'poem_id': None},
        ]
    },
    'P039': {  # 定州（1093-1094）
        'period': '定州时期 (1093-1094)',
        'works': [
            {'title': '定州谢到任表', 'type': '文', 'poem_id': None},
        ]
    },
}

def main():
    import sys
    dry_run = '--dry-run' in sys.argv
    
    # 加载诗文库索引用于匹配poem_id
    poems_index = load_json(os.path.join(DATA_DIR, 'poems-index.json'))
    poem_by_title = {}
    for p in poems_index['poems']:
        poem_by_title[p['title']] = p['id']
    
    total_added = 0
    
    for pid, period_data in MAJOR_PERIOD_WORKS.items():
        filepath = os.path.join(PLACES_DIR, f'{pid}.json')
        if not os.path.exists(filepath):
            print(f'  SKIP: {pid} not found')
            continue
        
        p = load_json(filepath)
        name = p.get('ancient_name', '')
        existing = p.get('global_works', [])
        existing_titles = {w.get('title', '') for w in existing}
        
        added = []
        for w in period_data['works']:
            if w['title'] in existing_titles:
                continue
            
            new_w = {
                'title': w['title'],
                'type': w['type'],
            }
            # 匹配poem_id
            if w.get('poem_id'):
                new_w['poem_id'] = w['poem_id']
            elif w['title'] in poem_by_title:
                new_w['poem_id'] = poem_by_title[w['title']]
            
            existing.append(new_w)
            existing_titles.add(w['title'])
            added.append(w['title'])
        
        if added:
            total_added += len(added)
            print(f'{pid} {name} [{period_data["period"]}]: +{len(added)} {added}')
            if not dry_run:
                p['global_works'] = existing
                with open(filepath, 'w') as f:
                    json.dump(p, f, ensure_ascii=False, indent=2)
    
    mode = 'DRY RUN' if dry_run else 'APPLIED'
    print(f'\n=== 主地点作品补充 ({mode}) ===')
    print(f'共补充 {total_added} 首')

if __name__ == '__main__':
    main()
