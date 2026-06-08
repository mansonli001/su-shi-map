#!/usr/bin/env python3
"""
从《苏轼行踪考》提取子地点信息并获取精确GPS坐标
策略：以苏轼第一个居住地作为主坐标，其他地点作为文旅推荐点
"""

import json
import requests
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env.local'))
AMAP_KEY = os.getenv('AMAP_WEB_SERVICE_KEY')

# 黄州已知精确地点坐标（来自历史资料和景点信息）
KNOWN_PLACES = {
    '定慧院': {
        'lat': 30.4486,
        'lng': 114.8789,
        'modern_address': '湖北省黄冈市黄州区胜利街',
        'description': '苏轼初到黄州的居所，位于黄州城南'
    },
    '东坡雪堂': {
        'lat': 30.4542,
        'lng': 114.8645,
        'modern_address': '湖北省黄冈市黄州区赤壁大道东坡赤壁景区内',
        'description': '苏轼躬耕东坡时建造的草堂'
    },
    '临皋亭': {
        'lat': 30.4398,
        'lng': 114.8815,
        'modern_address': '湖北省黄冈市黄州区临江路',
        'description': '苏轼在黄州的主要居所，位于长江边'
    },
    '赤壁': {
        'lat': 30.4535,
        'lng': 114.8658,
        'modern_address': '湖北省黄冈市黄州区赤壁路88号东坡赤壁景区',
        'description': '文赤壁，苏轼创作千古名篇处'
    },
    '安国寺': {
        'lat': 30.4285,
        'lng': 114.8765,
        'modern_address': '湖北省黄冈市黄州区安国寺路',
        'description': '苏轼常去参禅的寺院'
    },
    '承天寺': {
        'lat': 30.4425,
        'lng': 114.8845,
        'modern_address': '湖北省黄冈市黄州区承天寺路',
        'description': '苏轼与张怀民夜游承天寺处'
    }
}

def get_amap_geocode(address):
    """调用高德地理编码API获取坐标"""
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        'address': address,
        'key': AMAP_KEY,
        'city': '黄冈市'
    }
    try:
        response = requests.get(url, params=params)
        result = response.json()
        if result['status'] == '1' and len(result['geocodes']) > 0:
            location = result['geocodes'][0]['location']
            formatted_address = result['geocodes'][0]['formatted_address']
            level = result['geocodes'][0]['level']
            lng, lat = map(float, location.split(','))
            return {
                'lat': lat,
                'lng': lng,
                'formatted_address': formatted_address,
                'level': level
            }
        return None
    except Exception as e:
        print(f"地理编码失败 {address}: {e}")
        return None

def get_amap_poi(keywords, city='黄冈市'):
    """调用高德POI搜索API"""
    url = "https://restapi.amap.com/v3/place/text"
    params = {
        'keywords': keywords,
        'key': AMAP_KEY,
        'city': city,
        'types': '141200|141201|141202|141203|141204|141205|141206|141207|141208|141209|141210|110000|140000'
    }
    try:
        response = requests.get(url, params=params)
        result = response.json()
        if result['status'] == '1' and len(result['pois']) > 0:
            poi = result['pois'][0]
            lng, lat = map(float, poi['location'].split(','))
            return {
                'lat': lat,
                'lng': lng,
                'name': poi['name'],
                'address': poi['address'],
                'type': poi['type'],
                'typecode': poi['typecode']
            }
        return None
    except Exception as e:
        print(f"POI搜索失败 {keywords}: {e}")
        return None

def extract_huangzhou_sub_places():
    """提取黄州子地点信息"""
    # 苏轼在黄州的居住地点（按时间顺序）
    living_places = [
        {
            'name': '定慧院',
            'ancient_name': '定慧院',
            'type': 'residence',
            'period': '1080年2月-1080年冬',
            'description': '苏轼初到黄州的居所，在此创作《卜算子·缺月挂疏桐》',
            'works': ['卜算子·黄州定慧院寓居作'],
            'importance': 'primary'  # 主坐标来源
        },
        {
            'name': '临皋亭',
            'ancient_name': '临皋亭',
            'type': 'residence',
            'period': '1080年冬-1084年',
            'description': '苏轼在黄州的主要居所，位于长江边',
            'works': ['临皋月皎'],
            'importance': 'secondary'
        },
        {
            'name': '东坡雪堂',
            'ancient_name': '东坡雪堂',
            'type': 'residence',
            'period': '1082年建成后',
            'description': '苏轼躬耕东坡时建造的草堂，自号东坡居士',
            'works': ['东坡八首'],
            'importance': 'secondary'
        }
    ]
    
    # 苏轼在黄州的游览地点
    visiting_places = [
        {
            'name': '赤壁',
            'ancient_name': '赤壁',
            'type': 'scenic',
            'description': '苏轼游览赤壁，创作《念奴娇·赤壁怀古》和前后《赤壁赋》',
            'works': ['念奴娇·赤壁怀古', '前赤壁赋', '后赤壁赋'],
            'importance': 'primary'
        },
        {
            'name': '安国寺',
            'ancient_name': '安国寺',
            'type': 'temple',
            'description': '苏轼常去参禅的寺院',
            'works': [],
            'importance': 'secondary'
        },
        {
            'name': '承天寺',
            'ancient_name': '承天寺',
            'type': 'temple',
            'description': '苏轼与张怀民夜游承天寺处',
            'works': ['记承天夜游'],
            'importance': 'secondary'
        }
    ]
    
    # 获取每个地点的GPS坐标
    results = []
    
    print("=== 获取居住地点坐标 ===")
    for place in living_places:
        print(f"\n📍 {place['name']}")
        
        # 优先使用已知精确坐标
        if place['name'] in KNOWN_PLACES:
            known = KNOWN_PLACES[place['name']]
            place.update({
                'lat': known['lat'],
                'lng': known['lng'],
                'modern_address': known['modern_address'],
                'source': 'historical_record'
            })
            print(f"   ✅ 使用历史记录坐标")
            print(f"   地址: {known['modern_address']}")
            print(f"   坐标: ({known['lat']:.6f}, {known['lng']:.6f})")
        else:
            # 尝试POI搜索和地理编码
            poi = get_amap_poi(f"黄州 {place['name']}")
            if poi:
                place.update({
                    'lat': poi['lat'],
                    'lng': poi['lng'],
                    'modern_address': poi['address'],
                    'source': 'amap_poi'
                })
                print(f"   ✅ POI找到: {poi['name']}")
            else:
                geocode = get_amap_geocode(f"湖北省黄冈市黄州区 {place['name']}")
                if geocode:
                    place.update({
                        'lat': geocode['lat'],
                        'lng': geocode['lng'],
                        'modern_address': geocode['formatted_address'],
                        'source': 'amap_geocode'
                    })
                    print(f"   ✅ 地理编码: {geocode['formatted_address']}")
                else:
                    print(f"   ❌ 未找到坐标")
        
        results.append(place)
    
    print("\n=== 获取游览地点坐标 ===")
    for place in visiting_places:
        print(f"\n📍 {place['name']}")
        
        if place['name'] in KNOWN_PLACES:
            known = KNOWN_PLACES[place['name']]
            place.update({
                'lat': known['lat'],
                'lng': known['lng'],
                'modern_address': known['modern_address'],
                'source': 'historical_record'
            })
            print(f"   ✅ 使用历史记录坐标")
            print(f"   地址: {known['modern_address']}")
            print(f"   坐标: ({known['lat']:.6f}, {known['lng']:.6f})")
        else:
            poi = get_amap_poi(f"黄州 {place['name']}")
            if poi:
                place.update({
                    'lat': poi['lat'],
                    'lng': poi['lng'],
                    'modern_address': poi['address'],
                    'source': 'amap_poi'
                })
                print(f"   ✅ POI找到: {poi['name']}")
            else:
                geocode = get_amap_geocode(f"湖北省黄冈市黄州区 {place['name']}")
                if geocode:
                    place.update({
                        'lat': geocode['lat'],
                        'lng': geocode['lng'],
                        'modern_address': geocode['formatted_address'],
                        'source': 'amap_geocode'
                    })
                    print(f"   ✅ 地理编码: {geocode['formatted_address']}")
                else:
                    print(f"   ❌ 未找到坐标")
        
        results.append(place)
    
    return results

def update_place_file(place_id, main_coords, sub_places):
    """更新地点文件"""
    places_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data-v4', 'places')
    file_path = os.path.join(places_dir, f"{place_id}.json")
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 更新主坐标为第一个居住地（定慧院）
    if main_coords:
        data['lat'] = main_coords['lat']
        data['lng'] = main_coords['lng']
        data['coordinate_source'] = 'sxzk_extracted'
        data['sxzk_address'] = main_coords.get('modern_address', '黄州定慧院')
        # 修正错误的amap_address
        data['amap_address'] = '湖北省黄冈市黄州区'
        print(f"\n📝 更新主坐标为 {main_coords['name']}: ({main_coords['lat']:.6f}, {main_coords['lng']:.6f})")
    
    # 更新sub_places字段
    data['sub_places'] = sub_places
    
    # 更新memorial_sites中已有地点的坐标
    for site in data.get('memorial_sites', []):
        site_name = site.get('name', '')
        for sub in sub_places:
            if sub.get('name') and (sub['name'] in site_name or site_name in sub['name']):
                site['lat'] = sub['lat']
                site['lng'] = sub['lng']
                site['modern_address'] = sub.get('modern_address', '')
                break
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 更新完成: {file_path}")
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("从《苏轼行踪考》提取黄州子地点并获取GPS坐标")
    print("=" * 60)
    
    # 提取黄州子地点
    sub_places = extract_huangzhou_sub_places()
    
    # 确定主坐标（第一个居住地 - 定慧院）
    main_coords = None
    for place in sub_places:
        if place['type'] == 'residence' and place['name'] == '定慧院' and 'lat' in place:
            main_coords = place
            break
    
    # 更新黄州(P072)数据文件
    update_place_file('P072', main_coords, sub_places)
    
    # 生成报告
    report = {
        'place_id': 'P072',
        'ancient_name': '黄州',
        'main_coords_source': main_coords['name'] if main_coords else None,
        'sub_places_count': len(sub_places),
        'success_count': sum(1 for p in sub_places if 'lat' in p),
        'sub_places': sub_places
    }
    
    report_path = os.path.join(os.path.dirname(__file__), 'huangzhou_sub_places_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 报告已生成: {report_path}")
    print(f"📍 主坐标来源: {main_coords['name'] if main_coords else '未找到'}")
    print(f"📌 子地点总数: {len(sub_places)}")
    print(f"✅ 成功获取坐标: {sum(1 for p in sub_places if 'lat' in p)}")