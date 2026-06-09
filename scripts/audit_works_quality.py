#!/usr/bin/env python3
"""
作品数据质量审计脚本
1. 检测同一地点内的重复作品（标题相同/相似、内容相同/相似）
2. 检测跨地点的重复作品（同一作品出现在多个地点，判断归属是否正确）
3. 检测作品与地点的归属问题（如题西林壁应在庐山而非黄州）
"""

import json
import glob
import re
import os
from difflib import SequenceMatcher

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data-v4', 'places')

# 苏轼名作与归属地对照表（用于验证作品归属）
FAMOUS_WORKS_LOCATION = {
    '题西林壁': '庐山',
    '念奴娇·赤壁怀古': '黄州',
    '前赤壁赋': '黄州',
    '后赤壁赋': '黄州',
    '定风波·莫听穿林打叶声': '黄州',
    '卜算子·缺月挂疏桐': '黄州',
    '卜算子·黄州定慧院寓居作': '黄州',
    '水调歌头·明月几时有': '密州',
    '江城子·密州出猎': '密州',
    '江城子·乙卯正月二十日夜记梦': '密州',
    '饮湖上初晴后雨': '杭州',
    '六月二十七日望湖楼醉书': '杭州',
    '惠崇春江晚景': '开封',
    '赠刘景文': '杭州',
    '蝶恋花·春景': '开封',
    '记承天寺夜游': '黄州',
    '赤壁赋': '黄州',  # 即前赤壁赋
    '石钟山记': '石钟山',
    '方山子传': '黄州',
}

# 同一首作品的不同标题映射
TITLE_ALIASES = {
    '卜算子·缺月挂疏桐': ['卜算子·黄州定慧院寓居作'],
    '前赤壁赋': ['赤壁赋'],
    '水调歌头·黄州快哉亭': ['水调歌头·黄州快哉亭赠张偓佺'],
    '水调歌头·明月几时有': ['水调歌头·丙辰中秋'],
    '念奴娇·赤壁怀古': ['念奴娇·大江东去'],
}

def similarity(a, b):
    if not a or not b:
        return 0
    return SequenceMatcher(None, a, b).ratio()

def are_same_work(w1, w2):
    """判断两个作品是否是同一首"""
    t1, t2 = w1.get('title', ''), w2.get('title', '')
    
    # 标题完全相同
    if t1 == t2 and t1:
        return True, '标题完全相同'
    
    # 检查别名表
    for canonical, aliases in TITLE_ALIASES.items():
        all_names = [canonical] + aliases
        if t1 in all_names and t2 in all_names:
            return True, f'别名关系: {t1} = {t2}'
    
    # 内容/摘录相同
    c1 = w1.get('content', '') or w1.get('fullText', '') or w1.get('description', '')
    c2 = w2.get('content', '') or w2.get('fullText', '') or w2.get('description', '')
    if c1 and c2 and c1 == c2:
        return True, '内容完全相同'
    
    # 摘录相同
    e1 = w1.get('excerpt', '')
    e2 = w2.get('excerpt', '')
    if e1 and e2 and e1 == e2 and len(e1) > 5:
        return True, '摘录相同'
    
    # 标题高度相似（>0.85）
    if t1 and t2 and similarity(t1, t2) > 0.85:
        return True, f'标题高度相似({similarity(t1,t2):.0%})'
    
    # 标题包含关系 + 同类型
    type1, type2 = w1.get('type', ''), w2.get('type', '')
    if type1 and type2 and type1 == type2:
        if t1 in t2 or t2 in t1:
            # 但要排除"首次"和"二次"这类
            if similarity(t1, t2) > 0.7:
                return True, f'同类型+标题包含'
    
    return False, ''

def work_richness(w):
    """衡量作品信息丰富度"""
    score = 0
    if w.get('title'): score += 1
    if w.get('content') or w.get('fullText'): score += 3
    if w.get('excerpt'): score += 1
    if w.get('date') or w.get('year'): score += 1
    if w.get('type'): score += 1
    if w.get('note'): score += 1
    if w.get('poem_id'): score += 1
    # 内容长度
    content = w.get('content', '') or w.get('fullText', '') or ''
    score += min(len(content) // 30, 3)
    return score

def audit_place(filepath):
    """审计单个地点的作品数据"""
    with open(filepath) as f:
        p = json.load(f)
    
    pid = p['id']
    name = p.get('ancient_name', '')
    issues = []
    
    works = p.get('global_works', [])
    
    # === 1. 同一地点内重复检测 ===
    for i in range(len(works)):
        for j in range(i + 1, len(works)):
            same, reason = are_same_work(works[i], works[j])
            if same:
                issues.append({
                    'type': 'duplicate_work',
                    'works': [works[i], works[j]],
                    'reason': reason,
                    'indices': [i, j]
                })
    
    # === 2. 作品归属验证 ===
    for i, w in enumerate(works):
        title = w.get('title', '')
        if title in FAMOUS_WORKS_LOCATION:
            expected = FAMOUS_WORKS_LOCATION[title]
            # 检查当前地点名是否包含期望地点
            modern = p.get('modern_name', '')
            if expected not in name and expected not in modern:
                issues.append({
                    'type': 'wrong_location',
                    'work': w,
                    'expected_location': expected,
                    'current_location': f'{name}/{modern}',
                    'index': i
                })
    
    return pid, name, issues

def main():
    import sys
    
    files = sorted(glob.glob(os.path.join(DATA_DIR, 'P*.json')))
    
    total_issues = 0
    places_with_issues = []
    all_works_by_title = {}  # 跨地点重复检测
    
    for f in files:
        pid, name, issues = audit_place(f)
        if issues:
            places_with_issues.append((pid, name, issues))
            total_issues += len(issues)
        
        # 收集所有作品按标题分组（跨地点检测）
        with open(f) as fh:
            p = json.load(fh)
        for w in p.get('global_works', []):
            title = w.get('title', '')
            if title:
                if title not in all_works_by_title:
                    all_works_by_title[title] = []
                all_works_by_title[title].append((p['id'], p.get('ancient_name', '')))
    
    print(f'=== 作品数据质量审计 ===')
    print(f'总地点: {len(files)}')
    print(f'有问题地点: {len(places_with_issues)}')
    print(f'总问题数: {total_issues}')
    print()
    
    # 按问题类型统计
    type_counts = {}
    for pid, name, issues in places_with_issues:
        for issue in issues:
            t = issue['type']
            type_counts[t] = type_counts.get(t, 0) + 1
    
    print('问题类型统计:')
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f'  {t}: {c}')
    print()
    
    # 跨地点重复
    cross_dup = {t: locs for t, locs in all_works_by_title.items() if len(locs) > 1}
    print(f'跨地点重复作品: {len(cross_dup)} 首')
    for title, locs in sorted(cross_dup.items(), key=lambda x: -len(x[1]))[:20]:
        print(f'  "{title}": {len(locs)}个地点 - {[(p,n) for p,n in locs[:5]]}')
    print()
    
    # 详细输出
    for pid, name, issues in places_with_issues:
        print(f'\n--- {pid} {name} ({len(issues)}个问题) ---')
        for issue in issues:
            if issue['type'] == 'duplicate_work':
                w1, w2 = issue['works']
                print(f'  [重复] {issue["reason"]}')
                print(f'    作品1: {w1.get("title","?")} (richness={work_richness(w1)})')
                print(f'    作品2: {w2.get("title","?")} (richness={work_richness(w2)})')
            elif issue['type'] == 'wrong_location':
                w = issue['work']
                print(f'  [归属错误] "{w.get("title","?")}" 应在{issue["expected_location"]}，当前在{issue["current_location"]}')

if __name__ == '__main__':
    main()
