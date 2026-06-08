#!/usr/bin/env python3
"""
批量处理D级地点：根据v4数据自动推断居住地并设置主坐标
"""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(SCRIPT_DIR, '..', '..', '..')
PLACES_DIR = os.path.join(PROJECT_DIR, 'data-v4', 'places')
STAGING_DIR = os.path.join(SCRIPT_DIR, 'staging')

def infer_residence_from_ancient_name(ancient_name, modern_name):
    """从古地名推断居住地"""
    scenic_keywords = ['寺', '观', '庙', '亭', '阁', '台', '楼', '山', '湖', '江', '河', '泉', '洞', '峰', '岭', '矶', '滩', '峡', '潭', '溪']
    
    for kw in scenic_keywords:
        if kw in ancient_name:
            return {
                'name': f'{ancient_name}附近驿馆',
                'type': 'residence',
                'is_inferred': True
            }
    
    city_suffixes = ['州', '府', '军', '县', '城', '都', '镇']
    for suffix in city_suffixes:
        if ancient_name.endswith(suffix):
            return {
                'name': f'{ancient_name}官署',
                'type': 'residence',
                'is_inferred': False
            }
    
    return {
        'name': f'{ancient_name}居所',
        'type': 'residence',
        'is_inferred': True
    }

def process_d_places():
    analysis_file = os.path.join(SCRIPT_DIR, 'reports', 'place_richness_analysis.json')
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    d_places = [r for r in analysis if r['grade'] == 'D']
    success = 0
    no_staging = 0
    no_coords = 0
    
    for dp in d_places:
        place_id = dp['place_id']
        staging_file = os.path.join(STAGING_DIR, f"{place_id}.json")
        
        if not os.path.exists(staging_file):
            no_staging += 1
            continue
        
        with open(staging_file, 'r', encoding='utf-8') as f:
            staging = json.load(f)
        
        ancient_name = staging.get('ancient_name', '')
        modern_name = staging.get('modern_name', '')
        
        # 推断居住地
        residence_info = infer_residence_from_ancient_name(ancient_name, modern_name)
        
        # 设置主坐标
        if not staging.get('main_coords') and staging.get('sub_places'):
            first_sp = staging['sub_places'][0]
            if first_sp.get('lat'):
                staging['main_coords'] = {
                    'name': residence_info['name'],
                    'lat': first_sp['lat'],
                    'lng': first_sp['lng'],
                    'modern_address': first_sp.get('modern_address', ''),
                    'coordinate_source': first_sp.get('coordinate_source', ''),
                    'reason': f"{residence_info['name']}为{'推断的' if residence_info.get('is_inferred') else ''}居住地"
                }
            else:
                no_coords += 1
        elif not staging.get('main_coords'):
            no_coords += 1
        
        # 添加居住地子地点
        existing_residence = [sp for sp in staging.get('sub_places', []) if sp.get('type') == 'residence']
        if not existing_residence:
            residence_sp = {
                'name': residence_info['name'],
                'ancient_name': residence_info['name'],
                'type': 'residence',
                'period': '',
                'description': f"苏轼在{ancient_name}的居所",
                'works': [],
                'importance': 'primary',
                'lat': staging['main_coords']['lat'] if staging.get('main_coords') else None,
                'lng': staging['main_coords']['lng'] if staging.get('main_coords') else None,
                'modern_address': staging['main_coords'].get('modern_address', '') if staging.get('main_coords') else '',
                'coordinate_source': staging['main_coords'].get('coordinate_source', '') if staging.get('main_coords') else '',
                'verification_status': 'pending'
            }
            staging['sub_places'].insert(0, residence_sp)
        
        # 更新报告
        staging['report']['main_coords_source'] = residence_info['name']
        staging['report']['methodology'] = 'sxzk-gps-methodology v1.0'
        if residence_info.get('is_inferred'):
            staging['report']['data_quality_note'] = '居住地为推断，需进一步验证'
        
        with open(staging_file, 'w', encoding='utf-8') as f:
            json.dump(staging, f, ensure_ascii=False, indent=2)
        
        success += 1
    
    print(f"处理完成: 成功={success}, 无Staging={no_staging}, 无坐标={no_coords}")

if __name__ == '__main__':
    process_d_places()
