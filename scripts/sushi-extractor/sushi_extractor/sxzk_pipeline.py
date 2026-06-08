#!/usr/bin/env python3
"""
《苏轼行踪考》子地点精细化Pipeline
严格遵循 sxzk-gps-methodology 方法论

Pipeline流程：
1. 从v4 JSON提取子地点信息
2. 查找现代地址和GPS坐标
3. 坐标验证（城市范围检查、同名异地检查）
4. 仅验证通过的数据写入staging目录
5. 生成验证报告，需人工确认后才可合并到正式数据

使用方式：
  python3 sxzk_pipeline.py --place P072          # 处理单个地点
  python3 sxzk_pipeline.py --place P072 P058      # 处理多个地点
  python3 sxzk_pipeline.py --all                  # 处理所有地点
  python3 sxzk_pipeline.py --verify P072          # 验证已处理数据
  python3 sxzk_pipeline.py --commit P072          # 确认并合并到正式数据
  python3 sxzk_pipeline.py --status               # 查看整体进度
"""

import json
import os
import sys
import argparse
import requests
from datetime import datetime
from dotenv import load_dotenv

# 项目路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(SCRIPT_DIR, '..', '..', '..')
PLACES_DIR = os.path.join(PROJECT_DIR, 'data-v4', 'places')
STAGING_DIR = os.path.join(SCRIPT_DIR, 'staging')
REPORTS_DIR = os.path.join(SCRIPT_DIR, 'reports')

# 确保目录存在
os.makedirs(STAGING_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# 加载环境变量
load_dotenv(os.path.join(PROJECT_DIR, '.env.local'))
AMAP_KEY = os.getenv('AMAP_WEB_SERVICE_KEY')

# ============================================================
# 城市中心坐标和范围（用于验证）
# ============================================================
CITY_BOUNDS = {
    '黄冈市': {'center': (30.45, 114.87), 'range': 0.5},
    '杭州市': {'center': (30.25, 120.15), 'range': 0.5},
    '赣州市': {'center': (25.83, 114.93), 'range': 0.5},
    '儋州市': {'center': (19.52, 109.54), 'range': 0.5},
    '济南市': {'center': (36.67, 117.00), 'range': 0.5},
    '开封市': {'center': (34.80, 114.35), 'range': 0.5},
    '成都市': {'center': (30.67, 104.07), 'range': 0.5},
    '眉山市': {'center': (30.08, 103.85), 'range': 0.5},
    '广州市': {'center': (23.13, 113.27), 'range': 0.5},
    '南京市': {'center': (32.06, 118.80), 'range': 0.5},
    '商丘市': {'center': (34.41, 115.66), 'range': 0.5},
    '奉节县': {'center': (31.02, 109.40), 'range': 0.5},
    '绵阳市': {'center': (31.47, 104.73), 'range': 0.5},
    '海口市': {'center': (20.02, 110.35), 'range': 0.5},
    '惠州市': {'center': (23.11, 114.42), 'range': 0.5},
    '凤翔区': {'center': (34.52, 107.40), 'range': 0.5},
}


def get_city_for_place(place_data):
    """从place数据推断所属城市"""
    modern_name = place_data.get('modern_name', '')
    # 从modern_name中提取城市名
    for city in CITY_BOUNDS:
        if city.replace('市', '').replace('县', '').replace('区', '') in modern_name:
            return city
    # 尝试从amap_address获取
    amap_addr = place_data.get('amap_address', '')
    for city in CITY_BOUNDS:
        if city in amap_addr:
            return city
    return None


def validate_coordinate(lat, lng, city_name):
    """验证坐标是否在合理城市范围内"""
    if city_name not in CITY_BOUNDS:
        return True, "未知城市，跳过范围验证"
    
    bounds = CITY_BOUNDS[city_name]
    center_lat, center_lng = bounds['center']
    max_range = bounds['range']
    
    lat_diff = abs(lat - center_lat)
    lng_diff = abs(lng - center_lng)
    
    if lat_diff > max_range or lng_diff > max_range:
        return False, f"坐标偏离{city_name}中心: 纬度差{lat_diff:.3f}°, 经度差{lng_diff:.3f}°"
    
    return True, f"坐标在{city_name}范围内"


def call_amap_geocode(address, city=''):
    """调用高德地理编码API"""
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        'address': address,
        'key': AMAP_KEY,
        'city': city
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        result = response.json()
        if result['status'] == '1' and len(result['geocodes']) > 0:
            geo = result['geocodes'][0]
            lng, lat = map(float, geo['location'].split(','))
            return {
                'lat': lat,
                'lng': lng,
                'formatted_address': geo['formatted_address'],
                'level': geo['level'],
                'source': 'amap_geocode'
            }
        return None
    except Exception as e:
        print(f"  ⚠️ 地理编码失败 {address}: {e}")
        return None


def call_amap_poi(keywords, city=''):
    """调用高德POI搜索API"""
    url = "https://restapi.amap.com/v3/place/text"
    params = {
        'keywords': keywords,
        'key': AMAP_KEY,
        'city': city,
        'citylimit': 'true',  # 限制在指定城市
        'offset': 5
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        result = response.json()
        if result['status'] == '1' and len(result['pois']) > 0:
            pois = []
            for poi in result['pois'][:3]:
                lng, lat = map(float, poi['location'].split(','))
                pois.append({
                    'lat': lat,
                    'lng': lng,
                    'name': poi['name'],
                    'address': poi.get('address', ''),
                    'type': poi.get('type', ''),
                    'cityname': poi.get('cityname', ''),
                    'adname': poi.get('adname', ''),
                    'source': 'amap_poi'
                })
            return pois
        return []
    except Exception as e:
        print(f"  ⚠️ POI搜索失败 {keywords}: {e}")
        return []


# ============================================================
# Step 1: 从v4 JSON提取子地点信息
# ============================================================
def extract_sub_places_from_data(place_data):
    """从v4 JSON数据中提取子地点信息"""
    sub_places = []
    place_id = place_data['id']
    ancient_name = place_data.get('ancient_name', '')
    
    # 1. 从global_events提取居住信息
    for event in place_data.get('global_events', []):
        desc = event.get('description', '')
        title = event.get('title', '')
        
        # 匹配居住模式
        residence_keywords = ['寓居', '居住', '移居', '迁居', '住', '居']
        for keyword in residence_keywords:
            if keyword in desc or keyword in title:
                # 尝试提取地点名
                for word in desc + title:
                    pass  # 需要更复杂的NLP提取
                break
    
    # 2. 从global_works提取创作地点
    seen_locations = set()
    for work in place_data.get('global_works', []):
        location = work.get('location', '')
        if location and location not in seen_locations:
            seen_locations.add(location)
            # 去掉城市名前缀
            loc_name = location.replace(ancient_name, '').strip()
            if loc_name:
                sub_places.append({
                    'name': loc_name,
                    'ancient_name': loc_name,
                    'type': 'scenic',
                    'period': work.get('date', work.get('year', '')),
                    'description': f"创作《{work.get('title', '')}》处",
                    'works': [work.get('title', '')],
                    'importance': 'secondary',
                    'lat': None,
                    'lng': None,
                    'modern_address': '',
                    'coordinate_source': '',
                    'verification_status': 'pending'
                })
    
    # 3. 从memorial_sites提取已有景点
    for site in place_data.get('memorial_sites', []):
        name = site.get('name', '')
        if name and not any(sp['name'] == name for sp in sub_places):
            sub_places.append({
                'name': name,
                'ancient_name': name,
                'type': site.get('type', 'scenic'),
                'period': '',
                'description': site.get('description', ''),
                'works': [],
                'importance': 'primary' if 'scenic' in site.get('type', '') else 'secondary',
                'lat': site.get('lat'),
                'lng': site.get('lng'),
                'modern_address': site.get('modern_address', site.get('location', '')),
                'coordinate_source': 'memorial_site' if site.get('lat') else '',
                'verification_status': 'verified' if site.get('lat') else 'pending'
            })
    
    return sub_places


# ============================================================
# Step 2: 查找现代地址和GPS坐标
# ============================================================
def find_coordinates(sub_place, city_name):
    """为子地点查找GPS坐标"""
    name = sub_place['name']
    modern_addr = sub_place.get('modern_address', '')
    
    # 如果已有坐标，跳过
    if sub_place.get('lat') and sub_place.get('lng'):
        return sub_place
    
    print(f"  🔍 查找坐标: {name}")
    
    # 优先级1: 高德POI搜索（限制城市范围）
    pois = call_amap_poi(name, city_name)
    if pois:
        poi = pois[0]
        # 验证POI是否在正确城市
        poi_city = poi.get('cityname', '')
        if city_name in poi_city or poi_city in city_name:
            sub_place['lat'] = poi['lat']
            sub_place['lng'] = poi['lng']
            sub_place['modern_address'] = poi.get('address', '') or modern_addr
            sub_place['coordinate_source'] = 'amap_poi'
            sub_place['verification_status'] = 'pending'
            print(f"    ✅ POI: {poi['name']} ({poi['lat']:.6f}, {poi['lng']:.6f})")
            return sub_place
        else:
            print(f"    ⚠️ POI城市不匹配: 期望{city_name}, 实际{poi_city}")
    
    # 优先级2: 高德地理编码
    if modern_addr:
        geo = call_amap_geocode(modern_addr, city_name)
        if geo:
            sub_place['lat'] = geo['lat']
            sub_place['lng'] = geo['lng']
            sub_place['modern_address'] = geo['formatted_address']
            sub_place['coordinate_source'] = 'amap_geocode'
            sub_place['verification_status'] = 'pending'
            print(f"    ✅ 地理编码: {geo['formatted_address']} ({geo['lat']:.6f}, {geo['lng']:.6f})")
            return sub_place
    
    # 优先级3: 用城市名+地点名搜索
    geo = call_amap_geocode(f"{city_name} {name}", city_name)
    if geo:
        sub_place['lat'] = geo['lat']
        sub_place['lng'] = geo['lng']
        sub_place['modern_address'] = geo['formatted_address']
        sub_place['coordinate_source'] = 'amap_geocode'
        sub_place['verification_status'] = 'pending'
        print(f"    ✅ 组合搜索: {geo['formatted_address']} ({geo['lat']:.6f}, {geo['lng']:.6f})")
        return sub_place
    
    print(f"    ❌ 未找到坐标")
    sub_place['verification_status'] = 'no_result'
    return sub_place


# ============================================================
# Step 3: 坐标验证
# ============================================================
def verify_sub_places(sub_places, city_name):
    """验证所有子地点坐标"""
    verified = []
    rejected = []
    
    for sp in sub_places:
        if not sp.get('lat') or not sp.get('lng'):
            sp['verification_status'] = 'no_coordinates'
            verified.append(sp)
            continue
        
        # 城市范围验证
        is_valid, msg = validate_coordinate(sp['lat'], sp['lng'], city_name)
        
        if is_valid:
            sp['verification_status'] = 'verified'
            verified.append(sp)
            print(f"  ✅ {sp['name']}: {msg}")
        else:
            sp['verification_status'] = 'rejected'
            sp['reject_reason'] = msg
            rejected.append(sp)
            print(f"  ❌ {sp['name']}: {msg}")
    
    return verified, rejected


# ============================================================
# Step 4: 写入staging目录
# ============================================================
def write_staging(place_id, place_data, sub_places, main_coords, report):
    """将处理结果写入staging目录（不直接修改正式数据）"""
    staging_file = os.path.join(STAGING_DIR, f"{place_id}.json")
    
    staging_data = {
        'place_id': place_id,
        'ancient_name': place_data.get('ancient_name', ''),
        'modern_name': place_data.get('modern_name', ''),
        'city': report.get('city', ''),
        'processed_at': datetime.now().isoformat(),
        'main_coords': main_coords,
        'sub_places': sub_places,
        'report': report,
        'status': 'staging'  # staging → verified → committed
    }
    
    with open(staging_file, 'w', encoding='utf-8') as f:
        json.dump(staging_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📦 Staging数据已保存: {staging_file}")
    return staging_file


# ============================================================
# Step 5: 确认并合并到正式数据
# ============================================================
def commit_to_production(place_id):
    """将staging数据合并到正式v4 JSON文件"""
    staging_file = os.path.join(STAGING_DIR, f"{place_id}.json")
    place_file = os.path.join(PLACES_DIR, f"{place_id}.json")
    
    if not os.path.exists(staging_file):
        print(f"❌ Staging文件不存在: {staging_file}")
        return False
    
    if not os.path.exists(place_file):
        print(f"❌ 地点文件不存在: {place_file}")
        return False
    
    with open(staging_file, 'r', encoding='utf-8') as f:
        staging = json.load(f)
    
    # 检查staging状态
    if staging.get('status') != 'verified':
        print(f"❌ Staging数据尚未验证，请先运行 --verify {place_id}")
        return False
    
    with open(place_file, 'r', encoding='utf-8') as f:
        place_data = json.load(f)
    
    # 更新主坐标
    main_coords = staging.get('main_coords')
    if main_coords:
        place_data['lat'] = main_coords['lat']
        place_data['lng'] = main_coords['lng']
        place_data['coordinate_source'] = main_coords.get('coordinate_source', 'sxzk_extracted')
        place_data['sxzk_address'] = main_coords.get('modern_address', '')
    
    # 更新sub_places
    place_data['sub_places'] = staging['sub_places']
    
    # 更新memorial_sites坐标
    for site in place_data.get('memorial_sites', []):
        site_name = site.get('name', '')
        for sub in staging['sub_places']:
            if sub.get('name') and (sub['name'] in site_name or site_name in sub['name']):
                if sub.get('lat') and sub.get('verification_status') == 'verified':
                    site['lat'] = sub['lat']
                    site['lng'] = sub['lng']
                    site['modern_address'] = sub.get('modern_address', '')
                break
    
    with open(place_file, 'w', encoding='utf-8') as f:
        json.dump(place_data, f, ensure_ascii=False, indent=2)
    
    # 更新staging状态
    staging['status'] = 'committed'
    staging['committed_at'] = datetime.now().isoformat()
    with open(staging_file, 'w', encoding='utf-8') as f:
        json.dump(staging, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已合并到正式数据: {place_file}")
    return True


# ============================================================
# 主处理流程
# ============================================================
def process_place(place_id):
    """处理单个地点的完整pipeline"""
    place_file = os.path.join(PLACES_DIR, f"{place_id}.json")
    
    if not os.path.exists(place_file):
        print(f"❌ 地点文件不存在: {place_file}")
        return
    
    with open(place_file, 'r', encoding='utf-8') as f:
        place_data = json.load(f)
    
    ancient_name = place_data.get('ancient_name', '')
    modern_name = place_data.get('modern_name', '')
    
    print("=" * 60)
    print(f"📍 {place_id}: {ancient_name}（{modern_name}）")
    print("=" * 60)
    
    # Step 1: 提取子地点
    print("\n【Step 1】从v4数据提取子地点...")
    sub_places = extract_sub_places_from_data(place_data)
    print(f"  提取到 {len(sub_places)} 个子地点")
    
    # 确定城市
    city_name = get_city_for_place(place_data)
    if not city_name:
        # 从modern_name推断
        city_name = modern_name.replace('市', '').replace('省', '') + '市'
    print(f"  所属城市: {city_name}")
    
    # Step 2: 查找坐标
    print(f"\n【Step 2】查找GPS坐标...")
    for sp in sub_places:
        find_coordinates(sp, city_name)
    
    # Step 3: 验证坐标
    print(f"\n【Step 3】验证坐标...")
    verified, rejected = verify_sub_places(sub_places, city_name)
    
    # 确定主坐标（第一个verified的residence）
    main_coords = None
    for sp in verified:
        if sp.get('type') == 'residence' and sp.get('importance') == 'primary':
            main_coords = sp
            break
    if not main_coords:
        # 退而求其次：任何verified的residence
        for sp in verified:
            if sp.get('type') == 'residence' and sp.get('lat'):
                main_coords = sp
                break
    
    # 生成报告
    report = {
        'place_id': place_id,
        'ancient_name': ancient_name,
        'city': city_name,
        'total_sub_places': len(sub_places),
        'verified_count': len([sp for sp in verified if sp.get('verification_status') == 'verified']),
        'rejected_count': len(rejected),
        'pending_count': len([sp for sp in verified if sp.get('verification_status') == 'pending']),
        'no_coords_count': len([sp for sp in verified if sp.get('verification_status') in ('no_coordinates', 'no_result')]),
        'main_coords_source': main_coords['name'] if main_coords else None,
        'rejected_details': [{'name': r['name'], 'reason': r.get('reject_reason', '')} for r in rejected]
    }
    
    # Step 4: 写入staging
    print(f"\n【Step 4】写入Staging...")
    staging_file = write_staging(place_id, place_data, sub_places, main_coords, report)
    
    # 打印摘要
    print(f"\n{'='*60}")
    print(f"📊 处理摘要: {place_id} {ancient_name}")
    print(f"{'='*60}")
    print(f"  子地点总数: {report['total_sub_places']}")
    print(f"  ✅ 已验证: {report['verified_count']}")
    print(f"  ❌ 已拒绝: {report['rejected_count']}")
    print(f"  ⏳ 待验证: {report['pending_count']}")
    print(f"  🚫 无坐标: {report['no_coords_count']}")
    print(f"  📍 主坐标来源: {report['main_coords_source'] or '未确定'}")
    
    if rejected:
        print(f"\n  ⚠️ 被拒绝的坐标:")
        for r in report['rejected_details']:
            print(f"    - {r['name']}: {r['reason']}")
    
    print(f"\n  📦 Staging: {staging_file}")
    print(f"  下一步: python3 sxzk_pipeline.py --verify {place_id}")
    
    # 保存报告
    report_file = os.path.join(REPORTS_DIR, f"{place_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report


def verify_staging(place_id):
    """验证staging数据"""
    staging_file = os.path.join(STAGING_DIR, f"{place_id}.json")
    
    if not os.path.exists(staging_file):
        print(f"❌ Staging文件不存在: {staging_file}")
        return
    
    with open(staging_file, 'r', encoding='utf-8') as f:
        staging = json.load(f)
    
    print("=" * 60)
    print(f"🔍 验证Staging: {place_id} {staging.get('ancient_name', '')}")
    print("=" * 60)
    
    city_name = staging.get('city', '')
    sub_places = staging.get('sub_places', [])
    
    # 重新验证
    verified, rejected = verify_sub_places(sub_places, city_name)
    
    # 更新staging
    staging['sub_places'] = verified
    staging['report']['verified_count'] = len([sp for sp in verified if sp.get('verification_status') == 'verified'])
    staging['report']['rejected_count'] = len(rejected)
    
    # 如果没有rejected，标记为verified
    if not rejected and all(sp.get('verification_status') == 'verified' for sp in verified if sp.get('lat')):
        staging['status'] = 'verified'
        print(f"\n✅ 验证通过！可以执行: python3 sxzk_pipeline.py --commit {place_id}")
    else:
        print(f"\n⚠️ 存在被拒绝的坐标，请检查后重新处理")
    
    with open(staging_file, 'w', encoding='utf-8') as f:
        json.dump(staging, f, ensure_ascii=False, indent=2)


def show_status():
    """显示整体处理进度"""
    print("=" * 60)
    print("📊 《苏轼行踪考》GPS精细化进度")
    print("=" * 60)
    
    # 统计所有地点
    total = 0
    has_sub_places = 0
    staging_count = 0
    committed_count = 0
    
    for filename in os.listdir(PLACES_DIR):
        if not filename.endswith('.json'):
            continue
        total += 1
        filepath = os.path.join(PLACES_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data.get('sub_places'):
            has_sub_places += 1
    
    for filename in os.listdir(STAGING_DIR):
        if not filename.endswith('.json'):
            continue
        filepath = os.path.join(STAGING_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data.get('status') == 'committed':
            committed_count += 1
        else:
            staging_count += 1
    
    print(f"  总地点数: {total}")
    print(f"  已有sub_places: {has_sub_places}")
    print(f"  Staging中: {staging_count}")
    print(f"  已提交: {committed_count}")
    print(f"  待处理: {total - has_sub_places - committed_count}")


# ============================================================
# CLI入口
# ============================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='《苏轼行踪考》子地点精细化Pipeline')
    parser.add_argument('--place', nargs='+', help='处理指定地点（如 P072 P058）')
    parser.add_argument('--all', action='store_true', help='处理所有地点')
    parser.add_argument('--verify', nargs='+', help='验证staging数据')
    parser.add_argument('--commit', nargs='+', help='确认并合并到正式数据')
    parser.add_argument('--status', action='store_true', help='查看整体进度')
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    elif args.place:
        for place_id in args.place:
            process_place(place_id)
    elif args.verify:
        for place_id in args.verify:
            verify_staging(place_id)
    elif args.commit:
        for place_id in args.commit:
            commit_to_production(place_id)
    elif args.all:
        for filename in sorted(os.listdir(PLACES_DIR)):
            if filename.endswith('.json'):
                place_id = filename.replace('.json', '')
                process_place(place_id)
    else:
        parser.print_help()
