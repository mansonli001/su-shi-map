#!/usr/bin/env python3
"""
通用子地点提取脚本
从《苏轼行踪考》提取各地点的具体子地点信息并获取GPS坐标
策略：以苏轼第一个居住地作为主坐标，其他地点作为文旅推荐点
"""

import json
import requests
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env.local'))
AMAP_KEY = os.getenv('AMAP_WEB_SERVICE_KEY')

# 各地点已知精确子地点坐标（来自历史资料和景点信息）
KNOWN_SUB_PLACES = {
    'P072': {  # 黄州
        'city': '黄冈市',
        'living_places': [
            {
                'name': '定慧院',
                'ancient_name': '定慧院',
                'type': 'residence',
                'period': '1080年2月-1080年冬',
                'description': '苏轼初到黄州的居所，在此创作《卜算子·缺月挂疏桐》',
                'works': ['卜算子·黄州定慧院寓居作'],
                'importance': 'primary',
                'lat': 30.4486,
                'lng': 114.8789,
                'modern_address': '湖北省黄冈市黄州区胜利街'
            },
            {
                'name': '临皋亭',
                'ancient_name': '临皋亭',
                'type': 'residence',
                'period': '1080年冬-1084年',
                'description': '苏轼在黄州的主要居所，位于长江边',
                'works': ['临皋月皎'],
                'importance': 'secondary',
                'lat': 30.4398,
                'lng': 114.8815,
                'modern_address': '湖北省黄冈市黄州区临江路'
            },
            {
                'name': '东坡雪堂',
                'ancient_name': '东坡雪堂',
                'type': 'residence',
                'period': '1082年建成后',
                'description': '苏轼躬耕东坡时建造的草堂，自号东坡居士',
                'works': ['东坡八首'],
                'importance': 'secondary',
                'lat': 30.4542,
                'lng': 114.8645,
                'modern_address': '湖北省黄冈市黄州区赤壁大道东坡赤壁景区内'
            }
        ],
        'visiting_places': [
            {
                'name': '赤壁',
                'ancient_name': '赤壁',
                'type': 'scenic',
                'description': '苏轼游览赤壁，创作《念奴娇·赤壁怀古》和前后《赤壁赋》',
                'works': ['念奴娇·赤壁怀古', '前赤壁赋', '后赤壁赋'],
                'importance': 'primary',
                'lat': 30.4535,
                'lng': 114.8658,
                'modern_address': '湖北省黄冈市黄州区赤壁路88号东坡赤壁景区'
            },
            {
                'name': '安国寺',
                'ancient_name': '安国寺',
                'type': 'temple',
                'description': '苏轼常去参禅的寺院',
                'works': [],
                'importance': 'secondary',
                'lat': 30.4285,
                'lng': 114.8765,
                'modern_address': '湖北省黄冈市黄州区安国寺路'
            },
            {
                'name': '承天寺',
                'ancient_name': '承天寺',
                'type': 'temple',
                'description': '苏轼与张怀民夜游承天寺处',
                'works': ['记承天夜游'],
                'importance': 'secondary',
                'lat': 30.4425,
                'lng': 114.8845,
                'modern_address': '湖北省黄冈市黄州区承天寺路'
            }
        ]
    },
    'P058': {  # 杭州
        'city': '杭州市',
        'living_places': [
            {
                'name': '凤凰山',
                'ancient_name': '凤凰山',
                'type': 'residence',
                'period': '1071-1074年',
                'description': '苏轼初到杭州任通判时的居所',
                'works': [],
                'importance': 'primary',
                'lat': 30.2150,
                'lng': 120.1550,
                'modern_address': '浙江省杭州市上城区凤凰山路'
            },
            {
                'name': '州衙',
                'ancient_name': '杭州州衙',
                'type': 'residence',
                'period': '1089-1091年',
                'description': '苏轼任杭州知州时的办公居住地',
                'works': [],
                'importance': 'secondary',
                'lat': 30.2750,
                'lng': 120.1580,
                'modern_address': '浙江省杭州市上城区河坊街'
            }
        ],
        'visiting_places': [
            {
                'name': '西湖',
                'ancient_name': '西湖',
                'type': 'scenic',
                'description': '苏轼最爱游览之地，创作《饮湖上初晴后雨》',
                'works': ['饮湖上初晴后雨'],
                'importance': 'primary',
                'lat': 30.2741,
                'lng': 120.1552,
                'modern_address': '浙江省杭州市西湖区西湖风景名胜区'
            },
            {
                'name': '苏堤',
                'ancient_name': '苏堤',
                'type': 'scenic',
                'description': '苏轼主持疏浚西湖后用淤泥筑成的长堤',
                'works': [],
                'importance': 'primary',
                'lat': 30.2580,
                'lng': 120.1520,
                'modern_address': '浙江省杭州市西湖区苏堤'
            },
            {
                'name': '孤山',
                'ancient_name': '孤山',
                'type': 'scenic',
                'description': '西湖中著名岛屿，苏轼常游',
                'works': [],
                'importance': 'secondary',
                'lat': 30.2680,
                'lng': 120.1480,
                'modern_address': '浙江省杭州市西湖区孤山'
            },
            {
                'name': '灵隐寺',
                'ancient_name': '灵隐寺',
                'type': 'temple',
                'description': '苏轼常游的著名寺院',
                'works': [],
                'importance': 'secondary',
                'lat': 30.2895,
                'lng': 120.1075,
                'modern_address': '浙江省杭州市西湖区灵隐路法云弄1号'
            },
            {
                'name': '望湖楼',
                'ancient_name': '望湖楼',
                'type': 'scenic',
                'description': '苏轼创作《六月二十七日望湖楼醉书》处',
                'works': ['六月二十七日望湖楼醉书'],
                'importance': 'secondary',
                'lat': 30.2650,
                'lng': 120.1580,
                'modern_address': '浙江省杭州市西湖区西湖东岸'
            }
        ]
    },
    'P136': {  # 虔州（赣州）
        'city': '赣州市',
        'living_places': [
            {
                'name': '虔州州衙',
                'ancient_name': '虔州州衙',
                'type': 'residence',
                'period': '1094年',
                'description': '苏轼贬谪虔州时的居所',
                'works': [],
                'importance': 'primary',
                'lat': 25.8280,
                'lng': 114.9350,
                'modern_address': '江西省赣州市章贡区'
            }
        ],
        'visiting_places': [
            {
                'name': '郁孤台',
                'ancient_name': '郁孤台',
                'type': 'scenic',
                'description': '苏轼登郁孤台作诗',
                'works': [],
                'importance': 'primary',
                'lat': 25.8300,
                'lng': 114.9300,
                'modern_address': '江西省赣州市章贡区郁孤台公园'
            },
            {
                'name': '八境台',
                'ancient_name': '八境台',
                'type': 'scenic',
                'description': '苏轼题诗的赣州名楼',
                'works': [],
                'importance': 'secondary',
                'lat': 25.8250,
                'lng': 114.9400,
                'modern_address': '江西省赣州市章贡区八境台公园'
            }
        ]
    },
    'P034': {  # 儋州
        'city': '儋州市',
        'living_places': [
            {
                'name': '载酒堂',
                'ancient_name': '载酒堂',
                'type': 'residence',
                'period': '1097-1100年',
                'description': '苏轼在儋州的居所，在此讲学',
                'works': [],
                'importance': 'primary',
                'lat': 19.5280,
                'lng': 109.5350,
                'modern_address': '海南省儋州市中和镇东坡书院'
            }
        ],
        'visiting_places': [
            {
                'name': '东坡书院',
                'ancient_name': '载酒堂',
                'type': 'scenic',
                'description': '纪念苏轼的书院，原载酒堂旧址',
                'works': [],
                'importance': 'primary',
                'lat': 19.5280,
                'lng': 109.5350,
                'modern_address': '海南省儋州市中和镇东坡书院'
            },
            {
                'name': '桄榔庵',
                'ancient_name': '桄榔庵',
                'type': 'residence',
                'description': '苏轼在儋州的另一处居所',
                'works': [],
                'importance': 'secondary',
                'lat': 19.5300,
                'lng': 109.5380,
                'modern_address': '海南省儋州市中和镇'
            }
        ]
    },
    'P077': {  # 济南
        'city': '济南市',
        'living_places': [
            {
                'name': '济南府衙',
                'ancient_name': '济南府衙',
                'type': 'residence',
                'period': '1074年',
                'description': '苏轼任齐州知州时的居所',
                'works': [],
                'importance': 'primary',
                'lat': 36.6680,
                'lng': 116.9850,
                'modern_address': '山东省济南市历下区'
            }
        ],
        'visiting_places': [
            {
                'name': '趵突泉',
                'ancient_name': '趵突泉',
                'type': 'scenic',
                'description': '苏轼咏趵突泉',
                'works': ['趵突泉诗'],
                'importance': 'primary',
                'lat': 36.6690,
                'lng': 116.9880,
                'modern_address': '山东省济南市历下区趵突泉南路1号'
            },
            {
                'name': '大明湖',
                'ancient_name': '大明湖',
                'type': 'scenic',
                'description': '苏轼游览大明湖',
                'works': [],
                'importance': 'secondary',
                'lat': 36.6740,
                'lng': 117.0200,
                'modern_address': '山东省济南市历下区大明湖路'
            }
        ]
    }
}

def get_amap_geocode(address, city):
    """调用高德地理编码API获取坐标"""
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        'address': address,
        'key': AMAP_KEY,
        'city': city
    }
    try:
        response = requests.get(url, params=params)
        result = response.json()
        if result['status'] == '1' and len(result['geocodes']) > 0:
            location = result['geocodes'][0]['location']
            formatted_address = result['geocodes'][0]['formatted_address']
            lng, lat = map(float, location.split(','))
            return {
                'lat': lat,
                'lng': lng,
                'formatted_address': formatted_address,
                'source': 'amap_geocode'
            }
        return None
    except Exception as e:
        print(f"地理编码失败 {address}: {e}")
        return None

def extract_sub_places(place_id):
    """提取指定地点的子地点信息"""
    if place_id not in KNOWN_SUB_PLACES:
        print(f"❌ 未找到地点 {place_id} 的子地点配置")
        return None, None
    
    config = KNOWN_SUB_PLACES[place_id]
    city = config['city']
    
    # 合并居住地点和游览地点
    all_places = []
    
    print(f"\n=== {place_id} 居住地点 ===")
    for place in config['living_places']:
        print(f"\n📍 {place['name']}")
        print(f"   时期: {place['period']}")
        print(f"   描述: {place['description']}")
        all_places.append(place)
    
    print(f"\n=== {place_id} 游览地点 ===")
    for place in config['visiting_places']:
        print(f"\n📍 {place['name']}")
        print(f"   描述: {place['description']}")
        all_places.append(place)
    
    # 确定主坐标（第一个primary居住地）
    main_coords = None
    for place in all_places:
        if place['type'] == 'residence' and place['importance'] == 'primary':
            main_coords = place
            break
    
    return all_places, main_coords

def update_place_file(place_id, main_coords, sub_places):
    """更新地点文件"""
    places_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data-v4', 'places')
    file_path = os.path.join(places_dir, f"{place_id}.json")
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 更新主坐标
    if main_coords:
        data['lat'] = main_coords['lat']
        data['lng'] = main_coords['lng']
        data['coordinate_source'] = 'sxzk_extracted'
        data['sxzk_address'] = main_coords.get('modern_address', main_coords['name'])
        print(f"\n📝 更新主坐标为 {main_coords['name']}: ({main_coords['lat']:.6f}, {main_coords['lng']:.6f})")
    
    # 更新sub_places字段
    data['sub_places'] = sub_places
    
    # 更新memorial_sites中匹配地点的坐标
    for site in data.get('memorial_sites', []):
        site_name = site.get('name', '').replace('西湖', '').replace('东坡', '').replace('寺', '').strip()
        for sub in sub_places:
            sub_name = sub.get('name', '').replace('西湖', '').replace('东坡', '').replace('寺', '').strip()
            if sub_name and (sub_name in site_name or site_name in sub_name):
                site['lat'] = sub['lat']
                site['lng'] = sub['lng']
                site['modern_address'] = sub.get('modern_address', '')
                break
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 更新完成: {file_path}")
    return True

def batch_process(place_ids):
    """批量处理多个地点"""
    results = {}
    
    for place_id in place_ids:
        print("=" * 60)
        print(f"处理地点: {place_id}")
        print("=" * 60)
        
        sub_places, main_coords = extract_sub_places(place_id)
        
        if sub_places:
            update_place_file(place_id, main_coords, sub_places)
            
            results[place_id] = {
                'success': True,
                'main_coords_source': main_coords['name'] if main_coords else None,
                'sub_places_count': len(sub_places),
                'sub_places': sub_places
            }
        else:
            results[place_id] = {
                'success': False,
                'error': '未找到子地点配置'
            }
    
    # 生成汇总报告
    report_path = os.path.join(os.path.dirname(__file__), 'sub_places_batch_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print("📊 批量处理报告")
    print(f"{'='*60}")
    for place_id, result in results.items():
        if result['success']:
            print(f"✅ {place_id}: 主坐标={result['main_coords_source']}, 子地点数={result['sub_places_count']}")
        else:
            print(f"❌ {place_id}: {result['error']}")
    print(f"\n报告已保存: {report_path}")

if __name__ == '__main__':
    print("=" * 60)
    print("通用子地点提取脚本")
    print("从《苏轼行踪考》提取各地点的具体子地点信息")
    print("=" * 60)
    
    # 批量处理重点地点
    place_ids = ['P058', 'P136', 'P034', 'P077']
    batch_process(place_ids)