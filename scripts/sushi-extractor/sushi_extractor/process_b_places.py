#!/usr/bin/env python3
"""
为B级地点自动补充居住地信息并设置主坐标
基于v4数据中的global_events和periods推断居住地
"""

import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(SCRIPT_DIR, '..', '..', '..')
PLACES_DIR = os.path.join(PROJECT_DIR, 'data-v4', 'places')
STAGING_DIR = os.path.join(SCRIPT_DIR, 'staging')

# 居住地关键词模式
RESIDENCE_PATTERNS = [
    (r'寓居(.+?)[，。]', 'residence'),
    (r'居住(.+?)[，。]', 'residence'),
    (r'移居(.+?)[，。]', 'residence'),
    (r'迁居(.+?)[，。]', 'residence'),
    (r'住(.+?)[，。]', 'residence'),
    (r'居于(.+?)[，。]', 'residence'),
    (r'贬(.+?)[，。]', 'office'),
    (r'任(.+?)(知州|通判|知县)', 'office'),
    (r'到(.+?)任', 'office'),
]

def extract_residence_from_events(place_data):
    """从global_events和periods中提取居住地"""
    residences = []
    ancient_name = place_data.get('ancient_name', '')
    
    # 从global_events提取
    for event in place_data.get('global_events', []):
        desc = event.get('description', '')
        title = event.get('title', '')
        date = event.get('date', '')
        
        for pattern, rtype in RESIDENCE_PATTERNS:
            match = re.search(pattern, desc + title)
            if match:
                loc = match.group(1).strip()
                if loc and loc != ancient_name:
                    residences.append({
                        'name': loc,
                        'type': rtype,
                        'period': date,
                        'source': 'event',
                        'event_title': title
                    })
    
    # 从periods提取
    for period in place_data.get('periods', []):
        desc = period.get('description', '')
        title = period.get('title', '')
        period_str = period.get('period', '')
        
        for pattern, rtype in RESIDENCE_PATTERNS:
            match = re.search(pattern, desc + title)
            if match:
                loc = match.group(1).strip()
                if loc and loc != ancient_name:
                    residences.append({
                        'name': loc,
                        'type': rtype,
                        'period': period_str,
                        'source': 'period',
                        'period_title': title
                    })
    
    return residences

def infer_main_residence(place_data):
    """推断主居住地"""
    ancient_name = place_data.get('ancient_name', '')
    modern_name = place_data.get('modern_name', '')
    place_type = place_data.get('type', '')
    
    # 先尝试从事件中提取具体居住地
    residences = extract_residence_from_events(place_data)
    if residences:
        return {
            'name': residences[0]['name'],
            'type': residences[0]['type'],
            'period': residences[0]['period'],
            'description': f'苏轼在{ancient_name}的居住地',
            'importance': 'primary'
        }
    
    # 根据地点类型推断
    if place_type == 'official':
        # 官方任职地，居住在官署
        return {
            'name': f'{ancient_name}官署',
            'type': 'residence',
            'period': '',
            'description': f'苏轼任{ancient_name}官职时的居所',
            'importance': 'primary'
        }
    elif place_type == 'stay':
        return {
            'name': f'{ancient_name}寓所',
            'type': 'residence',
            'period': '',
            'description': f'苏轼在{ancient_name}的居住地',
            'importance': 'primary'
        }
    elif place_type == 'death':
        return {
            'name': f'{ancient_name}居所',
            'type': 'residence',
            'period': '',
            'description': f'苏轼在{ancient_name}的终老居所',
            'importance': 'primary'
        }
    
    # 默认：使用ancient_name
    return {
        'name': f'{ancient_name}居所',
        'type': 'residence',
        'period': '',
        'description': f'苏轼在{ancient_name}的居所',
        'importance': 'primary'
    }

def process_b_places():
    """处理所有B级地点"""
    # 读取分析结果
    analysis_file = os.path.join(SCRIPT_DIR, 'reports', 'place_richness_analysis.json')
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    b_places = [r for r in analysis if r['grade'] == 'B']
    
    print(f"处理 {len(b_places)} 个B级地点")
    
    for bp in b_places:
        place_id = bp['place_id']
        staging_file = os.path.join(STAGING_DIR, f"{place_id}.json")
        
        if not os.path.exists(staging_file):
            print(f"  ⚠️ Staging不存在: {place_id}")
            continue
        
        with open(staging_file, 'r', encoding='utf-8') as f:
            staging = json.load(f)
        
        # 读取v4数据
        place_file = os.path.join(PLACES_DIR, f"{place_id}.json")
        with open(place_file, 'r', encoding='utf-8') as f:
            place_data = json.load(f)
        
        # 推断主居住地
        main_residence = infer_main_residence(place_data)
        
        # 提取更多居住地
        extra_residences = extract_residence_from_events(place_data)
        
        # 更新staging
        existing_names = [sp['name'] for sp in staging.get('sub_places', [])]
        
        # 添加主居住地（如果不存在）
        if main_residence['name'] not in existing_names:
            main_residence['ancient_name'] = main_residence['name']
            main_residence['lat'] = None
            main_residence['lng'] = None
            main_residence['modern_address'] = ''
            main_residence['coordinate_source'] = ''
            main_residence['verification_status'] = 'pending'
            staging['sub_places'].insert(0, main_residence)
        
        # 添加额外居住地
        for res in extra_residences:
            if res['name'] not in existing_names and res['name'] not in [sp['name'] for sp in staging['sub_places']]:
                staging['sub_places'].append({
                    'name': res['name'],
                    'ancient_name': res['name'],
                    'type': res['type'],
                    'period': res['period'],
                    'description': f"从{res.get('event_title', res.get('period_title', ''))}中提取",
                    'works': [],
                    'importance': 'secondary',
                    'lat': None,
                    'lng': None,
                    'modern_address': '',
                    'coordinate_source': '',
                    'verification_status': 'pending'
                })
        
        # 设置主坐标
        if not staging.get('main_coords'):
            # 使用第一个居住地或现有坐标
            first_residence = None
            for sp in staging['sub_places']:
                if sp.get('type') == 'residence':
                    first_residence = sp
                    break
            
            if first_residence and first_residence.get('lat'):
                staging['main_coords'] = {
                    'name': first_residence['name'],
                    'lat': first_residence['lat'],
                    'lng': first_residence['lng'],
                    'modern_address': first_residence.get('modern_address', ''),
                    'coordinate_source': first_residence.get('coordinate_source', ''),
                    'reason': f"第一个居住地"
                }
            elif place_data.get('lat') and place_data.get('lng'):
                staging['main_coords'] = {
                    'name': main_residence['name'],
                    'lat': place_data['lat'],
                    'lng': place_data['lng'],
                    'modern_address': place_data.get('modern_visit', {}).get('address', ''),
                    'coordinate_source': 'original',
                    'reason': f"使用原始坐标，待精细化"
                }
        
        # 更新报告
        staging['report']['main_coords_source'] = main_residence['name']
        staging['report']['methodology'] = 'sxzk-gps-methodology v1.0'
        
        # 保存
        with open(staging_file, 'w', encoding='utf-8') as f:
            json.dump(staging, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ {place_id} {bp['ancient_name']}: 主居住地={main_residence['name']}, 子地点={len(staging['sub_places'])}个")

if __name__ == '__main__':
    process_b_places()
