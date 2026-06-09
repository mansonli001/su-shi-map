#!/usr/bin/env python3
"""
234地点全面数据质量QA扫描
- 空内容（无background/summary/events/works/foods）
- 坐标错位（超出中国范围、与modern_visit偏差大）
- 导航打不开（无modern_visit、无POI坐标）
- 数据完整性（缺必要字段）
"""

import json
import glob
import os
import math

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data-v4', 'places')

def load_json(path):
    with open(path) as f:
        return json.load(f)

def haversine_km(lat1, lng1, lat2, lng2):
    """粗略距离km"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.asin(a**0.5)

def main():
    place_files = sorted(glob.glob(os.path.join(DATA_DIR, 'P*.json')))
    
    issues = {
        'empty_content': [],      # 无任何实质内容
        'no_background': [],      # 无背景介绍
        'no_events_works': [],    # 无事迹和作品
        'coord_out_of_range': [], # 坐标超出中国范围
        'coord_poi_mismatch': [], # 地点坐标与POI偏差>10km
        'no_modern_visit': [],    # 无文旅导航信息
        'no_poi_coords': [],      # POI无坐标
        'missing_fields': [],     # 缺少必要字段
        'sub_place_coord_dup': [],# 子地点坐标完全相同
    }
    
    for pf in place_files:
        p = load_json(pf)
        pid = p['id']
        name = p.get('ancient_name', '')
        ptype = p.get('type', '')
        
        # 1. 空内容检测
        has_bg = bool(p.get('background') or p.get('summary') or p.get('extended_story'))
        has_ev = bool(p.get('global_events'))
        has_wk = bool(p.get('global_works'))
        has_fd = bool(p.get('foods'))
        
        if not has_bg and not has_ev and not has_wk:
            issues['empty_content'].append((pid, name, ptype))
        if not has_bg:
            issues['no_background'].append((pid, name, ptype))
        if not has_ev and not has_wk:
            issues['no_events_works'].append((pid, name, ptype))
        
        # 2. 坐标检测
        lat, lng = p.get('lat'), p.get('lng')
        if lat is None or lng is None:
            issues['missing_fields'].append((pid, name, '缺少lat/lng'))
        elif not (15 < lat < 55 and 70 < lng < 140):
            issues['coord_out_of_range'].append((pid, name, f'({lat},{lng})'))
        
        # 3. POI坐标偏差检测
        mv = p.get('modern_visit')
        if not mv:
            issues['no_modern_visit'].append((pid, name, ptype))
        elif isinstance(mv, dict):
            mv_lat = mv.get('lat')
            mv_lng = mv.get('lng')
            # 尝试从location字符串解析
            loc_str = mv.get('location', '')
            if isinstance(loc_str, str) and ',' in loc_str and not mv_lat:
                parts = loc_str.split(',')
                try:
                    mv_lng = float(parts[0])
                    mv_lat = float(parts[1])
                except:
                    pass
            
            if mv_lat and mv_lng and lat and lng:
                dist = haversine_km(lat, lng, mv_lat, mv_lng)
                if dist > 10:
                    issues['coord_poi_mismatch'].append((pid, name, f'偏差{dist:.1f}km place=({lat},{lng}) poi=({mv_lat},{mv_lng})'))
        
        # 4. 子地点坐标重复检测
        subs = p.get('sub_places', [])
        if len(subs) > 1:
            coords = [(s.get('lat'), s.get('lng'), s.get('name','')) for s in subs if s.get('lat')]
            for i in range(len(coords)):
                for j in range(i+1, len(coords)):
                    if coords[i][0] == coords[j][0] and coords[i][1] == coords[j][1]:
                        issues['sub_place_coord_dup'].append((pid, name, f'{coords[i][2]}和{coords[j][2]}坐标相同({coords[i][0]},{coords[i][1]})'))
    
    # 输出结果
    print('=== 234地点数据质量QA扫描 ===\n')
    
    total_issues = 0
    for key, items in issues.items():
        total_issues += len(items)
        print(f'{key}: {len(items)}')
        for item in items[:8]:
            print(f'  {item}')
        if len(items) > 8:
            print(f'  ... 还有{len(items)-8}个')
        print()
    
    print(f'总问题数: {total_issues}')

if __name__ == '__main__':
    main()
