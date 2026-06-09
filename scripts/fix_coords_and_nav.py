#!/usr/bin/env python3
"""
修正地点坐标与POI偏差过大的问题
策略：以高德POI坐标为准（更精确），更新place的lat/lng
"""

import json
import os
import math

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data-v4', 'places')

def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def haversine_km(lat1, lng1, lat2, lng2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.asin(a**0.5)

def main():
    import sys
    dry_run = '--dry-run' in sys.argv
    
    # 需要修正的地点（POI坐标更准确，以POI为准）
    # 只修正偏差>30km的，小偏差保留（可能是古地名与现代位置差异）
    CORRECTIONS = {
        'P016': {'reason': '常山：place坐标在浙江衢州，POI在山东枣庄（古常山在河北正定，POI更接近）', 'use_poi': True},
        'P036': {'reason': '登州：place坐标偏南，POI在蓬莱更准确', 'use_poi': True},
        'P080': {'reason': '剑门关：POI坐标更接近实际剑门关位置', 'use_poi': True},
        'P101': {'reason': '廉州白石镇：POI坐标更准确', 'use_poi': True},
    }
    
    for pid, info in CORRECTIONS.items():
        filepath = os.path.join(DATA_DIR, f'{pid}.json')
        p = load_json(filepath)
        name = p.get('ancient_name', '')
        
        mv = p.get('modern_visit', {})
        loc_str = mv.get('location', '')
        poi_lat, poi_lng = None, None
        
        if isinstance(loc_str, str) and ',' in loc_str:
            parts = loc_str.split(',')
            try:
                poi_lng = float(parts[0])
                poi_lat = float(parts[1])
            except:
                pass
        
        if not poi_lat:
            poi_lat = mv.get('lat')
            poi_lng = mv.get('lng')
        
        if not poi_lat or not poi_lng:
            print(f'  SKIP {pid} {name}: 无POI坐标')
            continue
        
        old_lat, old_lng = p.get('lat'), p.get('lng')
        dist = haversine_km(old_lat, old_lng, poi_lat, poi_lng)
        
        if info['use_poi']:
            print(f'{pid} {name}: ({old_lat},{old_lng}) → ({poi_lat},{poi_lng}) 偏差{dist:.1f}km - {info["reason"]}')
            if not dry_run:
                p['lat'] = poi_lat
                p['lng'] = poi_lng
                p['coordinate_source'] = 'corrected_from_poi'
                save_json(filepath, p)
    
    # 补充无modern_visit的地点
    NO_VISIT_FIXES = {
        'P033': {'amap_name': '丹崖山', 'address': '四川省', 'location': '105.06,30.28'},
        'P060': {'amap_name': '河北平原古驿道', 'address': '河北省', 'location': '114.48,38.03'},
        'P083': {'amap_name': '荆州古城', 'address': '荆州市荆州区', 'location': '112.18,30.35'},
        'P120': {'amap_name': '超然台', 'address': '诸城市', 'location': '119.41,35.99'},
        'P128': {'amap_name': '宁强', 'address': '汉中市宁强县', 'location': '106.26,32.83'},
        'P129': {'amap_name': '彭山', 'address': '眉山市彭山区', 'location': '103.87,30.19'},
        'P149': {'amap_name': '三峡', 'address': '宜昌市', 'location': '111.28,30.69'},
        'P174': {'amap_name': '尉氏', 'address': '开封市尉氏县', 'location': '114.18,34.41'},
        'P221': {'amap_name': '长岛渡口', 'address': '烟台市长岛县', 'location': '120.73,37.92'},
    }
    
    for pid, info in NO_VISIT_FIXES.items():
        filepath = os.path.join(DATA_DIR, f'{pid}.json')
        p = load_json(filepath)
        name = p.get('ancient_name', '')
        
        if p.get('modern_visit'):
            print(f'  SKIP {pid} {name}: 已有modern_visit')
            continue
        
        parts = info['location'].split(',')
        poi_lng, poi_lat = float(parts[0]), float(parts[1])
        
        mv = {
            'amap_name': info['amap_name'],
            'address': info['address'],
            'location': info['location'],
            'cityname': info.get('address', ''),
            'type': '风景名胜',
            'typecode': '110200',
        }
        
        print(f'{pid} {name}: 补充modern_visit {info["amap_name"]}')
        if not dry_run:
            p['modern_visit'] = mv
            save_json(filepath, p)
    
    mode = 'DRY RUN' if dry_run else 'APPLIED'
    print(f'\n=== 坐标修正和导航补充 ({mode}) ===')

if __name__ == '__main__':
    main()
