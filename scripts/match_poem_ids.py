#!/usr/bin/env python3
"""
为地点作品匹配诗文库poem_id
策略：按标题精确匹配 → 标题去标点匹配 → 模糊匹配
"""

import json
import glob
import os
import re

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data-v4')
PLACES_DIR = os.path.join(DATA_DIR, 'places')
POEMS_DIR = os.path.join(DATA_DIR, 'poems')

def load_json(path):
    with open(path) as f:
        return json.load(f)

def normalize_title(t):
    """去除标点、空格，统一比较"""
    t = re.sub(r'[·\-\s·,，。、：:；;！!？?（）()《》""''\u3000]', '', t)
    return t

def main():
    import sys
    dry_run = '--dry-run' in sys.argv
    
    # 加载诗文库索引
    poems_index = load_json(os.path.join(DATA_DIR, 'poems-index.json'))
    poem_by_title = {}  # 精确标题 → id
    poem_by_norm = {}   # 去标点标题 → id
    
    for p in poems_index['poems']:
        title = p['title']
        pid = p['id']
        poem_by_title[title] = pid
        norm = normalize_title(title)
        if norm not in poem_by_norm:
            poem_by_norm[norm] = pid
    
    print(f'诗文库: {len(poem_by_title)} 首标题索引')

    # 加载地点数据
    place_files = sorted(glob.glob(os.path.join(PLACES_DIR, 'P*.json')))
    
    matched = 0
    unmatched = []
    already_has = 0
    total_works = 0
    
    for pf in place_files:
        p = load_json(pf)
        pid = p['id']
        name = p.get('ancient_name', '')
        changed = False
        
        for w in p.get('global_works', []):
            total_works += 1
            if w.get('poem_id'):
                already_has += 1
                continue
            
            title = w.get('title', '')
            if not title:
                continue
            
            # 精确匹配
            if title in poem_by_title:
                w['poem_id'] = poem_by_title[title]
                matched += 1
                changed = True
                continue
            
            # 去标点匹配
            norm = normalize_title(title)
            if norm in poem_by_norm:
                w['poem_id'] = poem_by_norm[norm]
                matched += 1
                changed = True
                continue
            
            # 子标题匹配（如"前赤壁赋"在诗文库中可能是"赤壁赋"）
            # 尝试去掉前缀/后缀
            for prefix in ['前', '后', '其一', '其二', '其三', '其四', '其一·', '其二·']:
                if title.startswith(prefix):
                    sub = title[len(prefix):]
                    if sub in poem_by_title:
                        w['poem_id'] = poem_by_title[sub]
                        matched += 1
                        changed = True
                        break
                    sub_norm = normalize_title(sub)
                    if sub_norm in poem_by_norm:
                        w['poem_id'] = poem_by_norm[sub_norm]
                        matched += 1
                        changed = True
                        break
            else:
                unmatched.append((pid, name, title))
                continue
        
        if changed and not dry_run:
            with open(pf, 'w') as f:
                json.dump(p, f, ensure_ascii=False, indent=2)
    
    mode = 'DRY RUN' if dry_run else 'APPLIED'
    print(f'\n=== 作品-诗文库匹配 ({mode}) ===')
    print(f'总作品: {total_works}')
    print(f'已有poem_id: {already_has}')
    print(f'新匹配: {matched}')
    print(f'未匹配: {len(unmatched)}')
    
    if unmatched:
        print(f'\n未匹配作品（前30个）:')
        for pid, name, title in unmatched[:30]:
            print(f'  {pid} {name}: "{title}"')

if __name__ == '__main__':
    main()
