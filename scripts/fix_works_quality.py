#!/usr/bin/env python3
"""
作品数据修复脚本
1. 同一地点内去重（保留信息最完整的）
2. 归属错误的作品移到正确地点
3. 跨地点重复：子地点保留引用，主地点保留完整内容
"""

import json
import glob
import re
import os
import copy
from difflib import SequenceMatcher

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data-v4', 'places')

TITLE_ALIASES = {
    '卜算子·缺月挂疏桐': ['卜算子·黄州定慧院寓居作'],
    '前赤壁赋': ['赤壁赋'],
    '水调歌头·黄州快哉亭': ['水调歌头·黄州快哉亭赠张偓佺'],
    '水调歌头·明月几时有': ['水调歌头·丙辰中秋'],
    '念奴娇·赤壁怀古': ['念奴娇·大江东去'],
    '六月二十日夜渡海': ['渡海'],
}

def similarity(a, b):
    if not a or not b:
        return 0
    return SequenceMatcher(None, a, b).ratio()

def are_same_work(w1, w2):
    """判断两个作品是否是同一首"""
    t1, t2 = w1.get('title', ''), w2.get('title', '')
    
    if t1 == t2 and t1:
        return True, '标题完全相同'
    
    for canonical, aliases in TITLE_ALIASES.items():
        all_names = [canonical] + aliases
        if t1 in all_names and t2 in all_names:
            return True, f'别名关系: {t1} = {t2}'
    
    c1 = w1.get('content', '') or w1.get('fullText', '') or w1.get('description', '')
    c2 = w2.get('content', '') or w2.get('fullText', '') or w2.get('description', '')
    if c1 and c2 and c1 == c2:
        return True, '内容完全相同'
    
    e1 = w1.get('excerpt', '')
    e2 = w2.get('excerpt', '')
    if e1 and e2 and e1 == e2 and len(e1) > 5:
        return True, '摘录相同'
    
    if t1 and t2 and similarity(t1, t2) > 0.85:
        return True, f'标题高度相似({similarity(t1,t2):.0%})'
    
    type1, type2 = w1.get('type', ''), w2.get('type', '')
    if type1 and type2 and type1 == type2:
        if t1 in t2 or t2 in t1:
            if similarity(t1, t2) > 0.7:
                return True, f'同类型+标题包含'
    
    return False, ''

def work_richness(w):
    score = 0
    if w.get('title'): score += 1
    if w.get('content') or w.get('fullText'): score += 3
    if w.get('excerpt'): score += 1
    if w.get('date') or w.get('year'): score += 1
    if w.get('type'): score += 1
    if w.get('note'): score += 1
    if w.get('poem_id'): score += 1
    content = w.get('content', '') or w.get('fullText', '') or ''
    score += min(len(content) // 30, 3)
    return score

def deduplicate_works(works):
    """去重一组作品，保留信息最完整的"""
    if len(works) <= 1:
        return works, []
    
    removed = []
    keep = list(range(len(works)))
    
    for i in range(len(works)):
        if i not in keep:
            continue
        for j in range(i + 1, len(works)):
            if j not in keep:
                continue
            same, reason = are_same_work(works[i], works[j])
            if same:
                ri, rj = work_richness(works[i]), work_richness(works[j])
                if ri >= rj:
                    remove_idx = j
                    kept = i
                else:
                    remove_idx = i
                    kept = j
                
                if remove_idx in keep:
                    keep.remove(remove_idx)
                    removed.append({
                        'removed': works[remove_idx],
                        'kept': works[kept],
                        'reason': reason
                    })
    
    result = [works[i] for i in sorted(keep)]
    return result, removed

def load_all_places():
    """加载所有地点数据"""
    places = {}
    for f in sorted(glob.glob(os.path.join(DATA_DIR, 'P*.json'))):
        with open(f) as fh:
            p = json.load(fh)
        places[p['id']] = p
    return places

def save_place(p):
    """保存地点数据"""
    filepath = os.path.join(DATA_DIR, f"{p['id']}.json")
    with open(filepath, 'w') as f:
        json.dump(p, f, ensure_ascii=False, indent=2)

def main():
    import sys
    dry_run = '--dry-run' in sys.argv
    
    places = load_all_places()
    changes_log = []
    
    # === 1. 每个地点内去重 ===
    for pid, p in places.items():
        works = p.get('global_works', [])
        if len(works) <= 1:
            continue
        
        deduped, removed = deduplicate_works(works)
        if removed:
            name = p.get('ancient_name', '')
            changes_log.append(f'{pid} {name}: 作品去重 {len(works)}→{len(deduped)}')
            for r in removed:
                changes_log.append(f'  删除: "{r["removed"].get("title","?")}" (richness={work_richness(r["removed"])}) → 保留: "{r["kept"].get("title","?")}" (richness={work_richness(r["kept"])}) [{r["reason"]}]')
            p['global_works'] = deduped
    
    # === 2. 归属错误修正 ===
    # 只修正明确错误的归属，子地点/关联地点的引用保留
    # 例如：赤壁是黄州子地点，赤壁赋在赤壁是合理的
    # 沙湖是黄州附近，定风波在沙湖是合理的
    WRONG_LOCATION_FIXES = {
        # 题西林壁不应在黄州/金陵（应在庐山）
        ('P072', '题西林壁'): 'remove',
        ('P090', '题西林壁'): 'remove',
        # 江城子·密州出猎不应在湖州/青神（应在密州）
        ('P065', '江城子·密州出猎'): 'remove',
        ('P138', '江城子·密州出猎'): 'remove',
        # 泊船瓜洲不应在金陵（应在瓜洲）
        ('P089', '泊船瓜洲'): 'remove',
        ('P090', '泊船瓜洲'): 'remove',
        ('P091', '泊船瓜洲'): 'remove',
        # 赠刘景文不应在扬州（应在杭州）
        ('P198', '赠刘景文'): 'remove',
        # 饮湖上初晴后雨不应在颍州（应在杭州）
        ('P208', '饮湖上初晴后雨'): 'remove',
        # 六月二十七日望湖楼醉书不应在颍州（应在杭州）
        ('P208', '六月二十七日望湖楼醉书'): 'remove',
        # 蝶恋花·春景不应在黄州东坡雪堂（应在开封）
        ('P073', '蝶恋花·春景'): 'remove',
        # 石钟山记不应在庐山（应在石钟山）
        ('P108', '石钟山记'): 'remove',
        # 水调歌头·明月几时有不应在海州花果山（应在密州）
        ('P056', '水调歌头·明月几时有'): 'remove',
    }
    
    for (pid, title), action in WRONG_LOCATION_FIXES.items():
        if pid not in places:
            continue
        p = places[pid]
        works = p.get('global_works', [])
        before = len(works)
        p['global_works'] = [w for w in works if w.get('title') != title]
        after = len(p['global_works'])
        if before != after:
            name = p.get('ancient_name', '')
            changes_log.append(f'{pid} {name}: 移除归属错误作品 "{title}"')
    
    # === 3. 保存 ===
    if not dry_run:
        for pid, p in places.items():
            save_place(p)
    
    mode = 'DRY RUN' if dry_run else 'APPLIED'
    print(f'=== 作品数据修复 ({mode}) ===')
    print(f'总变更: {len(changes_log)}')
    print()
    for c in changes_log:
        print(c)

if __name__ == '__main__':
    main()
