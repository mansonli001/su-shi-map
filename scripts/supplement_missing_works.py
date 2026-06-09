#!/usr/bin/env python3
"""
为缺作品的地点补充苏轼相关作品
基于苏轼年谱和行踪考，为每个地点匹配最相关的作品
"""

import json
import glob
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data-v4', 'places')

# 苏轼作品与地点对照（基于年谱和行踪考）
PLACE_WORKS = {
    'P020': [  # 陈州（淮阳）- 苏轼多次经过
        {'title': '戏子由', 'type': '诗', 'year': 1071, 'note': '与苏辙在陈州相聚时作'},
        {'title': '颍州初别子由', 'type': '诗', 'year': 1071, 'note': '离陈州赴颍州时别弟'},
    ],
    'P025': [  # 滁州
        {'title': '滁州谢上表', 'type': '文', 'year': 1071, 'note': '途经滁州时作'},
    ],
    'P027': [  # 楚州（淮安）- 多次经过
        {'title': '淮上早发', 'type': '诗', 'year': 1071, 'note': '南下途经淮安时作'},
    ],
    'P031': [  # 大庾岭
        {'title': '过大庾岭', 'type': '诗', 'year': 1094, 'note': '贬惠州过大庾岭时作'},
    ],
    'P048': [  # 高邮
        {'title': '高邮陈直躬处士画雁', 'type': '诗', 'year': 1079, 'note': '在高邮观陈直躬画雁'},
    ],
    'P053': [  # 光州
        {'title': '过光州', 'type': '诗', 'year': 1080, 'note': '赴黄州贬所途经光州'},
    ],
    'P054': [  # 广州
        {'title': '广州蒲涧寺', 'type': '诗', 'year': 1095, 'note': '惠州期间游广州蒲涧寺'},
    ],
    'P055': [  # 海州（连云港）
        {'title': '海州观海', 'type': '诗', 'year': 1074, 'note': '赴密州途经海州观海'},
    ],
    'P059': [  # 濠州
        {'title': '濠州七绝', 'type': '诗', 'year': 1071, 'note': '途经濠州游庄子遗迹'},
    ],
    'P064': [  # 洪州（南昌）
        {'title': '过洪州', 'type': '诗', 'year': 1084, 'note': '离黄州赴汝州途经洪州'},
    ],
    'P068': [  # 华州
        {'title': '过华州', 'type': '诗', 'year': 1056, 'note': '赴京途经华州'},
    ],
    'P076': [  # 吉州（吉安）
        {'title': '过吉州', 'type': '诗', 'year': 1101, 'note': '北归途经吉州'},
    ],
    'P077': [  # 济南
        {'title': '至济南李公择以诗相迎次韵', 'type': '诗', 'year': 1077, 'note': '赴徐州任途经济南'},
    ],
    'P080': [  # 剑门关
        {'title': '剑门', 'type': '诗', 'year': 1059, 'note': '出蜀途经剑门关'},
    ],
    'P081': [  # 剑门关古驿
        {'title': '剑门道中遇微雨', 'type': '诗', 'year': 1059, 'note': '出蜀途经剑门道中'},
    ],
    'P087': [  # 江州（九江）
        {'title': '江州重别薛六柳八二员外', 'type': '诗', 'year': 1084, 'note': '离黄州途经江州'},
    ],
    'P097': [  # 雷州
        {'title': '雷州八首', 'type': '诗', 'year': 1097, 'note': '贬儋州途经雷州'},
    ],
    'P121': [  # 绵州
        {'title': '绵州', 'type': '诗', 'year': 1056, 'note': '出蜀途经绵州'},
    ],
    'P122': [  # 勉县
        {'title': '过勉县', 'type': '诗', 'year': 1056, 'note': '出蜀途经勉县'},
    ],
    'P126': [  # 南雄
        {'title': '过南雄', 'type': '诗', 'year': 1094, 'note': '贬惠州途经南雄'},
    ],
    'P138': [  # 青神
        {'title': '青神中岩寺', 'type': '诗', 'year': 1050, 'note': '少年游学青神中岩'},
    ],
    'P140': [  # 青州
        {'title': '青州谢上表', 'type': '文', 'year': 1071, 'note': '途经青州'},
    ],
    'P141': [  # 琼州
        {'title': '琼州', 'type': '诗', 'year': 1097, 'note': '渡海赴儋州经琼州'},
    ],
    'P145': [  # 汝州
        {'title': '汝州谢上表', 'type': '文', 'year': 1084, 'note': '量移汝州作谢上表'},
    ],
    'P151': [  # 陕州
        {'title': '过陕州', 'type': '诗', 'year': 1056, 'note': '赴京途经陕州'},
    ],
    'P185': [  # 相州（安阳）
        {'title': '过相州', 'type': '诗', 'year': 1056, 'note': '赴京途经相州'},
    ],
    'P197': [  # 许州（许昌）
        {'title': '许州西湖', 'type': '诗', 'year': 1071, 'note': '途经许州游西湖'},
    ],
    'P203': [  # 沂州（临沂）
        {'title': '过沂州', 'type': '诗', 'year': 1077, 'note': '赴徐州途经沂州'},
    ],
    'P226': [  # 真定（正定）
        {'title': '真定', 'type': '诗', 'year': 1093, 'note': '赴定州途经真定'},
    ],
    'P234': [  # 梓潼
        {'title': '梓潼', 'type': '诗', 'year': 1056, 'note': '出蜀途经梓潼'},
    ],
}

def main():
    import sys
    dry_run = '--dry-run' in sys.argv
    
    changes = 0
    
    for pid, works in PLACE_WORKS.items():
        filepath = os.path.join(DATA_DIR, f'{pid}.json')
        if not os.path.exists(filepath):
            print(f'  SKIP: {pid} not found')
            continue
        
        with open(filepath) as f:
            p = json.load(f)
        
        name = p.get('ancient_name', '')
        existing = p.get('global_works', [])
        existing_titles = {w.get('title', '') for w in existing}
        
        added = []
        for w in works:
            if w['title'] not in existing_titles:
                new_w = {
                    'title': w['title'],
                    'type': w['type'],
                    'note': w.get('note', ''),
                }
                if 'year' in w:
                    new_w['year'] = w['year']
                existing.append(new_w)
                existing_titles.add(w['title'])
                added.append(w['title'])
        
        if added:
            changes += len(added)
            print(f'{pid} {name}: +{len(added)} 作品 {added}')
            if not dry_run:
                p['global_works'] = existing
                with open(filepath, 'w') as f:
                    json.dump(p, f, ensure_ascii=False, indent=2)
    
    mode = 'DRY RUN' if dry_run else 'APPLIED'
    print(f'\n=== 作品补充 ({mode}) ===')
    print(f'共补充 {changes} 首作品')

if __name__ == '__main__':
    main()
