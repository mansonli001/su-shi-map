#!/usr/bin/env python3
"""
事迹数据修复脚本
1. global_events 去重（保留信息最完整的那条）
2. global_events 按时间排序
3. 统一时间格式（提取年份用于排序，保留原始日期字符串）
4. global_events 与 route_events 去重（route_events 保留，global_events 删除重复）
"""

import json
import glob
import re
import os
import copy
from difflib import SequenceMatcher

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data-v4', 'places')

def extract_year(date_str):
    """从日期字符串提取年份"""
    if not date_str:
        return None
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

def extract_sort_key(date_str):
    """提取排序键 (year, month)"""
    y = extract_year(date_str) or 9999
    m = 0
    if date_str:
        mm = re.search(r'[正一二三四五六七八九十冬]{1,2}月', date_str)
        if mm:
            month_map = {'正': 1, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
                         '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '冬': 11}
            ms = mm.group()
            for k, v in month_map.items():
                if k in ms:
                    m = v
                    break
        else:
            mm = re.search(r'(\d{1,2})月', date_str)
            if mm:
                m = int(mm.group(1))
    return (y, m)

def similarity(a, b):
    if not a or not b:
        return 0
    return SequenceMatcher(None, a, b).ratio()

def is_duplicate_event(e1, e2, strict=False):
    """判断两个事件是否重复
    strict=True 时用于 global→route 替换，需要更严格的判断
    """
    t1, t2 = e1.get('title', ''), e2.get('title', '')
    d1, d2 = e1.get('description', ''), e2.get('description', '')
    
    # 标题完全相同
    if t1 == t2 and t1:
        return True, '标题完全相同'
    
    # 标题高度相似（严格模式0.85，普通模式0.8）
    threshold = 0.85 if strict else 0.8
    if t1 and t2 and similarity(t1, t2) > threshold:
        # 额外检查：如果年份不同，不算重复
        y1 = extract_year(e1.get('date', ''))
        y2 = extract_year(e2.get('date', ''))
        if y1 and y2 and y1 != y2:
            return False, f'标题相似但年份不同({y1} vs {y2})'
        return True, f'标题相似({similarity(t1,t2):.0%})'
    
    # 描述高度相似（严格模式0.9，普通模式0.85）
    desc_threshold = 0.9 if strict else 0.85
    if d1 and d2 and similarity(d1, d2) > desc_threshold:
        return True, f'描述相似({similarity(d1,d2):.0%})'
    
    # 标题包含关系 + 同年 + 其中一个是另一个的子串
    y1 = extract_year(e1.get('date', ''))
    y2 = extract_year(e2.get('date', ''))
    if y1 and y2 and y1 == y2:
        # 短标题是长标题的子串，且短标题长度>2（避免"过X"匹配"过X赴Y"）
        if t1 in t2 and len(t1) > 2 and similarity(t1, t2) > 0.6:
            return True, f'同年+标题包含'
        if t2 in t1 and len(t2) > 2 and similarity(t1, t2) > 0.6:
            return True, f'同年+标题包含'
    
    return False, ''

def event_richness(e):
    """衡量事件信息丰富度，用于去重时保留更好的那条"""
    score = 0
    if e.get('title'): score += 1
    if e.get('description') and len(e.get('description', '')) > 10: score += 2
    if e.get('significance'): score += 1
    if e.get('date') and extract_year(e.get('date', '')): score += 1
    if e.get('place'): score += 1
    # 更长的描述更有价值
    score += min(len(e.get('description', '')) // 50, 3)
    return score

def deduplicate_events(events):
    """去重一组事件，保留信息最完整的"""
    if len(events) <= 1:
        return events, []
    
    removed = []
    keep = list(range(len(events)))
    
    for i in range(len(events)):
        if i not in keep:
            continue
        for j in range(i + 1, len(events)):
            if j not in keep:
                continue
            dup, reason = is_duplicate_event(events[i], events[j])
            if dup:
                # 保留信息更丰富的
                ri, rj = event_richness(events[i]), event_richness(events[j])
                if ri >= rj:
                    remove_idx = j
                    kept = i
                else:
                    remove_idx = i
                    kept = j
                
                if remove_idx in keep:
                    keep.remove(remove_idx)
                    removed.append({
                        'removed': events[remove_idx],
                        'kept': events[kept],
                        'reason': reason
                    })
    
    result = [events[i] for i in sorted(keep)]
    return result, removed

def sort_events(events):
    """按时间排序事件"""
    def sort_key(e):
        return extract_sort_key(e.get('date', ''))
    return sorted(events, key=sort_key)

def fix_place(filepath, dry_run=False):
    """修复单个地点的事迹数据"""
    with open(filepath) as f:
        p = json.load(f)
    
    pid = p['id']
    name = p.get('ancient_name', '')
    changes = []
    
    # === 1. global_events 去重 ===
    events = p.get('global_events', [])
    if len(events) > 1:
        deduped, removed = deduplicate_events(events)
        if removed:
            changes.append(f'global_events 去重: {len(events)}→{len(deduped)} (删除{len(removed)}条重复)')
            for r in removed:
                changes.append(f'  删除: [{r["removed"].get("date","?")}] {r["removed"].get("title","?")} ({r["reason"]})')
                changes.append(f'  保留: [{r["kept"].get("date","?")}] {r["kept"].get("title","?")}')
            p['global_events'] = deduped
    
    # === 2. global_events 按时间排序 ===
    events = p.get('global_events', [])
    if len(events) > 1:
        sorted_events = sort_events(events)
        if [e.get('date') for e in events] != [e.get('date') for e in sorted_events]:
            changes.append('global_events 按时间排序')
            p['global_events'] = sorted_events
    
    # === 3. global_events vs route_events 去重 ===
    route_events = p.get('route_events', {})
    events = p.get('global_events', [])
    to_remove = set()
    
    for route_key, route_data in route_events.items():
        if not isinstance(route_data, list):
            continue
        for re in route_data:
            for i, ge in enumerate(events):
                if i in to_remove:
                    continue
                dup, reason = is_duplicate_event(re, ge, strict=True)
                if dup:
                    # route_events 是路线特定的事迹，global_events 是全局汇总
                    # 如果重复，保留 global_events 中更完整的，删除 route_events 中的
                    # 但实际上 global_events 应该是汇总，route_events 是路线视角
                    # 策略：保留两者，但 global_events 中的应该更完整
                    # 如果 global_events 的信息不如 route_events，用 route_events 替换
                    ri_ge = event_richness(ge)
                    ri_re = event_richness(re)
                    if ri_re > ri_ge:
                        # route_event 更丰富，替换 global_event
                        changes.append(f'global→route替换: [{ge.get("date","?")}] {ge.get("title","?")} → [{re.get("date","?")}] {re.get("title","?")} ({reason})')
                        events[i] = copy.deepcopy(re)
                    # 如果 global 更丰富，保留 global，不操作
                    # 两者信息相当，保留 global（避免重复显示）
    
    if to_remove:
        p['global_events'] = [e for i, e in enumerate(events) if i not in to_remove]
    
    # === 4. 重新排序 ===
    events = p.get('global_events', [])
    if len(events) > 1:
        p['global_events'] = sort_events(events)
    
    # === 5. 重新编号 ID ===
    for i, e in enumerate(p.get('global_events', [])):
        if not e.get('id') or not e['id'].startswith(f'{pid.lower()}-'):
            e['id'] = f'{pid.lower()}-{i+1:03d}'
    
    if not dry_run and changes:
        with open(filepath, 'w') as f:
            json.dump(p, f, ensure_ascii=False, indent=2)
    
    return pid, name, changes

def main():
    import sys
    dry_run = '--dry-run' in sys.argv
    
    files = sorted(glob.glob(os.path.join(DATA_DIR, 'P*.json')))
    
    total_changes = 0
    places_changed = []
    
    for f in files:
        pid, name, changes = fix_place(f, dry_run=dry_run)
        if changes:
            places_changed.append((pid, name, changes))
            total_changes += len(changes)
    
    mode = 'DRY RUN' if dry_run else 'APPLIED'
    print(f'=== 事迹数据修复 ({mode}) ===')
    print(f'总地点: {len(files)}')
    print(f'修改地点: {len(places_changed)}')
    print(f'总变更: {total_changes}')
    print()
    
    for pid, name, changes in places_changed:
        print(f'\n--- {pid} {name} ---')
        for c in changes:
            print(f'  {c}')

if __name__ == '__main__':
    main()
