#!/usr/bin/env python3
"""
从v4原始数据补充缺失的主坐标
"""

import json
import os
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(SCRIPT_DIR, '..', '..', '..')
PLACES_DIR = os.path.join(PROJECT_DIR, 'data-v4', 'places')
STAGING_DIR = os.path.join(SCRIPT_DIR, 'staging')

def infer_residence_name(ancient_name):
    scenic_keywords = ['寺', '观', '庙', '亭', '阁', '台', '楼', '山', '湖', '江', '河', '泉', '洞', '峰', '岭', '矶', '滩', '峡', '潭', '溪']
    for kw in scenic_keywords:
        if kw in ancient_name:
            return f'{ancient_name}附近驿馆', True
    city_suffixes = ['州', '府', '军', '县', '城', '都', '镇']
    for suffix in city_suffixes:
        if ancient_name.endswith(suffix):
            return f'{ancient_name}官署', False
    return f'{ancient_name}居所', True

def main():
    updated = 0
    no_coords_at_all = 0
    
    for f in sorted(glob.glob(os.path.join(STAGING_DIR, 'P*.json'))):
        with open(f, 'r', encoding='utf-8') as fh:
            staging = json.load(fh)
        
        if staging.get('main_coords'):
            continue
        
        place_id = staging['place_id']
        ancient_name = staging.get('ancient_name', '')
        residence_name, is_inferred = infer_residence_name(ancient_name)
        
        # 从v4原始数据获取坐标
        place_file = os.path.join(PLACES_DIR, f"{place_id}.json")
        with open(place_file, 'r', encoding='utf-8') as fh:
            place_data = json.load(fh)
        
        lat = None
        lng = None
        address = ''
        source = ''
        
        # 优先用modern_visit
        visit = place_data.get('modern_visit', {})
        if visit.get('location'):
            loc = visit['location']
            if ',' in loc:
                parts = loc.split(',')
                lng = float(parts[0])
                lat = float(parts[1])
            address = visit.get('address', '')
            source = 'amap_poi_original'
        
        # 其次用lat/lng
        if lat is None and place_data.get('lat') is not None:
            lat = place_data['lat']
            lng = place_data.get('lng')
            address = place_data.get('modern_visit', {}).get('address', '')
            source = 'original'
        
        if lat is not None and lng is not None:
            staging['main_coords'] = {
                'name': residence_name,
                'lat': lat,
                'lng': lng,
                'modern_address': address,
                'coordinate_source': source,
                'reason': f"{residence_name}为{'推断的' if is_inferred else ''}居住地（使用原始坐标）"
            }
            
            # 更新居住地子地点坐标
            for sp in staging.get('sub_places', []):
                if sp.get('type') == 'residence' and sp.get('lat') is None:
                    sp['lat'] = lat
                    sp['lng'] = lng
                    sp['modern_address'] = address
                    sp['coordinate_source'] = source
            
            staging['report']['main_coords_source'] = residence_name
            staging['report']['methodology'] = 'sxzk-gps-methodology v1.0'
            if is_inferred:
                staging['report']['data_quality_note'] = '居住地为推断，需进一步验证'
            
            with open(f, 'w', encoding='utf-8') as fh:
                json.dump(staging, fh, ensure_ascii=False, indent=2)
            
            updated += 1
        else:
            no_coords_at_all += 1
    
    print(f"补充完成: 更新={updated}, 完全无坐标={no_coords_at_all}")

if __name__ == '__main__':
    main()
