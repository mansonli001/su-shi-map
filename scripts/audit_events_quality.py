#!/usr/bin/env python3
"""
事迹数据质量审计脚本
1. 检测 global_events 中的重复事迹（标题/描述相似）
2. 检测时间排序问题（时间格式不统一、顺序错乱）
3. 检测 global_events 与 route_events 之间的重复
4. 输出修复建议
"""

import json
import glob
import re
import os
from difflib import SequenceMatcher

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data-v4', 'places')

def extract_year(date_str):
    """从日期字符串提取年份（支持多种格式）"""
    if not date_str:
        return None
    # 匹配 "1101年" 或 "(1101)" 或 "1101"
    m = re.search(r'(\d{3,4})年', date_str)
    if m:
        return int(m.group(1))
    m = re.search(r'[（(](\d{3,4})[）)]', date_str)
    if m:
        return int(m.group(1))
    m = re.search(r'^(\d{3,4})', date_str)
    if m:
        return int(m.group(1))
    return None

def extract_month(date_str):
    """从日期字符串提取月份（用于同年内排序）"""
    if not date_str:
        return 0
    m = re.search(r'[正一二三四五六七八九十冬]{1,2}月', date_str)
    if m:
        month_map = {'正': 1, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
                     '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '冬': 11}
        ms = m.group()
        for k, v in month_map.items():
            if k in ms:
                return v
    m = re.search(r'(\d{1,2})月', date_str)
    if m:
        return int(m.group(1))
    return 0

def similarity(a, b):
    """计算两个字符串的相似度"""
    if not a or not b:
        return 0
    return SequenceMatcher(None, a, b).ratio()

def is_duplicate_event(e1, e2):
    """判断两个事件是否重复"""
    t1, t2 = e1.get('title', ''), e2.get('title', '')
    d1, d2 = e1.get('description', ''), e2.get('description', '')
    
    # 标题完全相同
    if t1 == t2 and t1:
        return True, '标题完全相同'
    
    # 标题高度相似
    if t1 and t2 and similarity(t1, t2) > 0.7:
        return True, f'标题相似({similarity(t1,t2):.0%}): "{t1}" vs "{t2}"'
    
    # 描述高度相似
    if d1 and d2 and similarity(d1, d2) > 0.8:
        return True, f'描述相似({similarity(d1,d2):.0%})'
    
    # 标题包含关系 + 同年
    y1, y2 = extract_year(e1.get('date', '')), extract_year(e2.get('date', ''))
    if y1 and y2 and y1 == y2:
        if t1 in t2 or t2 in t1:
            return True, f'同年+标题包含: "{t1}" vs "{t2}"'
    
    return False, ''

def audit_place(filepath):
    """审计单个地点的事迹数据"""
    with open(filepath) as f:
        p = json.load(f)
    
    pid = p['id']
    name = p.get('ancient_name', '')
    issues = []
    
    # === 1. global_events 重复检测 ===
    events = p.get('global_events', [])
    for i in range(len(events)):
        for j in range(i + 1, len(events)):
            dup, reason = is_duplicate_event(events[i], events[j])
            if dup:
                issues.append({
                    'type': 'duplicate_global',
                    'events': [events[i], events[j]],
                    'reason': reason,
                    'indices': [i, j]
                })
    
    # === 2. 时间排序检测 ===
    if len(events) > 1:
        years = []
        for e in events:
            y = extract_year(e.get('date', ''))
            m = extract_month(e.get('date', ''))
            years.append((y, m, e.get('date', '')))
        
        for i in range(len(years) - 1):
            y1, m1, d1 = years[i]
            y2, m2, d2 = years[i + 1]
            if y1 and y2 and y1 > y2:
                issues.append({
                    'type': 'time_order',
                    'msg': f'时间倒序: [{d1}] 在 [{d2}] 之前',
                    'indices': [i, i + 1]
                })
            elif y1 and y2 and y1 == y2 and m1 and m2 and m1 > m2:
                issues.append({
                    'type': 'time_order',
                    'msg': f'同年月份倒序: [{d1}] 在 [{d2}] 之前',
                    'indices': [i, i + 1]
                })
    
    # === 3. 时间格式不统一 ===
    for i, e in enumerate(events):
        date = e.get('date', '')
        if date and not extract_year(date):
            issues.append({
                'type': 'date_format',
                'msg': f'无法解析年份: "{date}"',
                'index': i
            })
    
    # === 4. global_events vs route_events 重复 ===
    route_events = p.get('route_events', {})
    for route_key, route_data in route_events.items():
        if not isinstance(route_data, list):
            continue
        for re in route_data:
            for i, ge in enumerate(events):
                dup, reason = is_duplicate_event(re, ge)
                if dup:
                    issues.append({
                        'type': 'global_route_dup',
                        'route': route_key,
                        'global_index': i,
                        'reason': reason,
                        'global_event': ge,
                        'route_event': re
                    })
    
    return pid, name, issues

def main():
    files = sorted(glob.glob(os.path.join(DATA_DIR, 'P*.json')))
    
    total_issues = 0
    places_with_issues = []
    
    for f in files:
        pid, name, issues = audit_place(f)
        if issues:
            places_with_issues.append((pid, name, issues))
            total_issues += len(issues)
    
    print(f'=== 事迹数据质量审计 ===')
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
    
    # 详细输出
    for pid, name, issues in places_with_issues:
        print(f'\n--- {pid} {name} ({len(issues)}个问题) ---')
        for issue in issues:
            if issue['type'] == 'duplicate_global':
                e1, e2 = issue['events']
                print(f'  [重复] {issue["reason"]}')
                print(f'    事件1: [{e1.get("date","?")}] {e1.get("title","?")}')
                print(f'    事件2: [{e2.get("date","?")}] {e2.get("title","?")}')
            elif issue['type'] == 'time_order':
                print(f'  [时序] {issue["msg"]}')
            elif issue['type'] == 'date_format':
                print(f'  [格式] {issue["msg"]}')
            elif issue['type'] == 'global_route_dup':
                print(f'  [全局/路线重复] route={issue["route"]} {issue["reason"]}')
                ge = issue['global_event']
                re = issue['route_event']
                print(f'    全局: [{ge.get("date","?")}] {ge.get("title","?")}')
                print(f'    路线: [{re.get("date","?")}] {re.get("title","?")}')

if __name__ == '__main__':
    main()
