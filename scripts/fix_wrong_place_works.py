#!/usr/bin/env python3
"""
修复错误添加的作品：移除错误地点的作品，补充到正确地点
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data-v4', 'places')

def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 需要从错误地点移除的作品标题
REMOVE_FROM = {
    'P089': ['六月二十七日望湖楼醉书', '望湖楼醉书', '吉祥寺赏牡丹', '吉祥寺僧求阁名',
             '湖上夜归', '孤山二首', '次韵子由柳湖感物', '送郑户曹',
             '与莫同年雨中饮湖上', '次韵曹辅寄壑源试焙新茶'],
    'P041': ['永遇乐·明月如霜', '浣溪沙·簌簌衣巾落枣花', '浣溪沙·软草平莎过雨新',
             '登云龙山', '放鹤亭记'],
    'P057': ['惠州一绝', '食荔枝', '荔枝叹', '记游松风亭'],
}

# 需要补充到正确地点的作品
ADD_TO = {
    'P058': {  # 杭州
        'works': [
            {'title': '六月二十七日望湖楼醉书', 'type': '诗'},
            {'title': '望湖楼醉书', 'type': '诗'},
            {'title': '吉祥寺赏牡丹', 'type': '诗'},
            {'title': '吉祥寺僧求阁名', 'type': '诗'},
            {'title': '湖上夜归', 'type': '诗'},
            {'title': '孤山二首', 'type': '诗'},
            {'title': '次韵子由柳湖感物', 'type': '诗'},
            {'title': '送郑户曹', 'type': '诗'},
            {'title': '与莫同年雨中饮湖上', 'type': '诗'},
            {'title': '次韵曹辅寄壑源试焙新茶', 'type': '诗'},
        ]
    },
    'P195': {  # 徐州
        'works': [
            {'title': '永遇乐·明月如霜', 'type': '词'},
            {'title': '浣溪沙·簌簌衣巾落枣花', 'type': '词'},
            {'title': '浣溪沙·软草平莎过雨新', 'type': '词'},
            {'title': '登云龙山', 'type': '诗'},
            {'title': '放鹤亭记', 'type': '文'},
        ]
    },
    'P074': {  # 惠州
        'works': [
            {'title': '惠州一绝', 'type': '诗'},
            {'title': '食荔枝', 'type': '诗'},
            {'title': '荔枝叹', 'type': '诗'},
            {'title': '记游松风亭', 'type': '文'},
        ]
    },
    'P119': {  # 密州
        'works': [
            {'title': '江城子·乙卯正月二十日夜记梦', 'type': '词'},
            {'title': '江城子·密州出猎', 'type': '词'},
            {'title': '水调歌头·明月几时有', 'type': '词'},
        ]
    },
    'P038': {  # 定州
        'works': [
            {'title': '定州谢到任表', 'type': '文'},
        ]
    },
}

# 加载诗文库索引用于匹配poem_id
import glob
poems_index = load_json(os.path.join(os.path.dirname(__file__), '..', 'data-v4', 'poems-index.json'))
poem_by_title = {}
for p in poems_index['poems']:
    poem_by_title[p['title']] = p['id']

def main():
    # 1. 从错误地点移除
    for pid, titles in REMOVE_FROM.items():
        filepath = os.path.join(DATA_DIR, f'{pid}.json')
        p = load_json(filepath)
        name = p.get('ancient_name', '')
        before = len(p.get('global_works', []))
        p['global_works'] = [w for w in p.get('global_works', []) if w.get('title') not in titles]
        after = len(p['global_works'])
        removed = before - after
        if removed > 0:
            print(f'REMOVE: {pid} {name}: -{removed} 作品')
            save_json(filepath, p)

    # 2. 补充到正确地点
    for pid, data in ADD_TO.items():
        filepath = os.path.join(DATA_DIR, f'{pid}.json')
        p = load_json(filepath)
        name = p.get('ancient_name', '')
        existing_titles = {w.get('title') for w in p.get('global_works', [])}
        added = []
        for w in data['works']:
            if w['title'] not in existing_titles:
                new_w = {'title': w['title'], 'type': w['type']}
                if w['title'] in poem_by_title:
                    new_w['poem_id'] = poem_by_title[w['title']]
                p['global_works'].append(new_w)
                existing_titles.add(w['title'])
                added.append(w['title'])
        if added:
            print(f'ADD: {pid} {name}: +{len(added)} {added}')
            save_json(filepath, p)

    print('\n=== 修复完成 ===')

if __name__ == '__main__':
    main()
