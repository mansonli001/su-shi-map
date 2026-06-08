#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPS精细化扩展脚本 - 挖掘更多有明确书中依据的坐标
从验证报告的失败记录中提取有效地址
"""
import json
import os
import requests

# 配置
OUTPUT_DIR = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places'
V4_INDEX_PATH = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places-index.json'
REPORT_PATH = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/scripts/sushi-extractor/sushi_extractor/gps_validation_report.json'

# 高德API配置
AMAP_KEY = 'f781d0d96b04cc83a66046e4bf630cc4'
AMAP_GEOCODE_URL = 'https://restapi.amap.com/v3/geocode/geo'

# 排除的宽泛地理概念
EXCLUDE_PLACES = {'三峡全程', '长江', '运河', '黄河'}

# 已知地点名称映射（用于改进匹配）
PLACE_NAME_MAP = {
    '汴京': ['开封', '开封府', '汴梁'],
    '夔州': ['奉节', '白帝城'],
    '陈仓': ['宝鸡', '凤翔'],
    '绵州': ['绵阳', '盐亭'],
    '杭州': ['临安', '钱塘'],
    '成都': ['益州'],
    '定州': ['定县'],
    '金陵': ['南京', '建康'],
    '眉山': ['眉州'],
    '虔州': ['赣州'],
    '青州': ['益都'],
    '江州': ['九江'],
    '儋州': ['儋耳'],
    '登州': ['蓬莱'],
    '黄州': ['黄冈'],
    '广州': ['番禺'],
    '琼州': ['海口'],
    '南都': ['商丘'],
}

def load_validation_report():
    """加载验证报告"""
    with open(REPORT_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_v4_index():
    """加载v4索引"""
    with open(V4_INDEX_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_geocode(address):
    """调用高德API获取坐标"""
    try:
        params = {
            'address': address.replace('今', '').replace('是', '').replace('为', '').strip(),
            'key': AMAP_KEY,
            'output': 'json'
        }
        response = requests.get(AMAP_GEOCODE_URL, params=params)
        data = response.json()
        
        if data['status'] == '1' and data['geocodes']:
            geo = data['geocodes'][0]
            return {
                'lat': float(geo['location'].split(',')[1]),
                'lng': float(geo['location'].split(',')[0]),
                'formatted_address': geo.get('formatted_address', ''),
                'level': geo.get('level', '')
            }
        return None
    except Exception as e:
        print(f"❌ 地理编码失败: {address} - {e}")
        return None

def extract_failed_geocodes(report):
    """从失败记录中提取有效地址"""
    valid_failed = []
    
    for failed in report['failed_geocode']:
        place_id = failed['place_id']
        ancient_name = failed['ancient_name']
        address = failed['address']
        
        # 排除宽泛地理概念
        if ancient_name in EXCLUDE_PLACES:
            continue
        
        # 尝试修复地址格式并重试
        cleaned_addr = clean_address(address)
        if cleaned_addr:
            valid_failed.append({
                'place_id': place_id,
                'ancient_name': ancient_name,
                'address': cleaned_addr,
                'original_address': address,
                'chapter': failed['chapter']
            })
    
    return valid_failed

def clean_address(address):
    """清理地址格式"""
    # 移除前缀
    prefixes = ['今', '现', '为', '是', '仍', '属']
    cleaned = address
    for prefix in prefixes:
        if cleaned.startswith(prefix):
            cleaned = cleaned[1:]
    
    # 移除后缀
    suffixes = ['区', '县', '市', '省', '镇', '乡']
    # 保留区县市作为有效地址的一部分
    
    cleaned = cleaned.strip()
    
    # 过滤太短的地址
    if len(cleaned) < 3:
        return None
    
    return cleaned

def match_address_to_place(valid_failed, v4_index):
    """改进的地址匹配逻辑"""
    results = []
    
    for failed in valid_failed:
        place_id = failed['place_id']
        
        # 直接查找地点
        place = next((p for p in v4_index['places'] if p['id'] == place_id), None)
        if place:
            geocode = get_geocode(failed['address'])
            if geocode:
                result = {
                    'place_id': place_id,
                    'ancient_name': place['ancient_name'],
                    'modern_name': place.get('modern_name', ''),
                    'extracted_address': failed['address'],
                    'original_address': failed['original_address'],
                    'source_chapter': failed['chapter'],
                    'lat': geocode['lat'],
                    'lng': geocode['lng'],
                    'formatted_address': geocode['formatted_address'],
                    'level': geocode['level']
                }
                results.append(result)
                print(f"✅ {place_id}: {place['ancient_name']} - {failed['address']}")
            else:
                print(f"⚠️ {place_id}: {place['ancient_name']} - 地理编码仍失败")
    
    return results

def update_coordinates(results):
    """更新坐标"""
    updated_count = 0
    
    for result in results:
        place_id = result['place_id']
        place_file = os.path.join(OUTPUT_DIR, f"{place_id}.json")
        
        if not os.path.exists(place_file):
            continue
        
        with open(place_file, 'r', encoding='utf-8') as f:
            place_data = json.load(f)
        
        # 备份原始坐标
        original_lat = place_data.get('lat', 0)
        original_lng = place_data.get('lng', 0)
        
        # 更新坐标
        place_data['lat'] = result['lat']
        place_data['lng'] = result['lng']
        place_data['coordinate_source'] = 'sxzk_extracted'
        place_data['amap_address'] = result['formatted_address']
        place_data['coords_updated_at'] = '2026-06-07T00:00:00.000Z'
        place_data['sxzk_source'] = result['source_chapter']
        place_data['sxzk_address'] = result['extracted_address']
        
        with open(place_file, 'w', encoding='utf-8') as f:
            json.dump(place_data, f, ensure_ascii=False, indent=2)
        
        updated_count += 1
        print(f"📝 {place_id}: {result['ancient_name']}")
        print(f"   原始: ({original_lat:.4f}, {original_lng:.4f})")
        print(f"   更新: ({result['lat']:.6f}, {result['lng']:.6f})")
    
    return updated_count

def main():
    print("="*60)
    print("GPS精细化扩展脚本")
    print("从失败记录中挖掘更多有效地址")
    print("="*60)
    
    print("\n【1】加载验证报告...")
    report = load_validation_report()
    
    print(f"\n【2】失败记录数: {len(report['failed_geocode'])}")
    
    print("\n【3】提取有效失败记录...")
    valid_failed = extract_failed_geocodes(report)
    print(f"   提取到 {len(valid_failed)} 条有效记录")
    
    print("\n【4】加载v4索引...")
    v4_index = load_v4_index()
    
    print("\n【5】尝试重新地理编码...")
    results = match_address_to_place(valid_failed, v4_index)
    print(f"\n   成功: {len(results)} 条")
    
    if not results:
        print("\n❌ 没有找到可扩展的新地址")
        return
    
    print("\n【6】待更新地点列表:")
    print("-" * 80)
    print(f"{'地点ID':<8} {'古地名':<12} {'地址':<30} {'精度'}")
    print("-" * 80)
    for result in results:
        print(f"{result['place_id']:<8} {result['ancient_name'][:12]:<12} {result['extracted_address'][:30]:<30} {result['level']}")
    
    # 自动确认更新（跳过交互式输入）
    confirm = 'y'
    
    print("\n【7】执行更新...")
    updated_count = update_coordinates(results)
    
    print(f"\n📊 扩展更新完成")
    print(f"   更新地点: {updated_count} 个")
    
    # 生成扩展报告
    report_data = {
        'total_places': updated_count,
        'updated_at': '2026-06-07',
        'source': '《苏轼行踪考》- 扩展挖掘',
        'updates': results
    }
    
    report_path = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/scripts/sushi-extractor/sushi_extractor/gps_extension_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"   扩展报告: {report_path}")

if __name__ == "__main__":
    main()
