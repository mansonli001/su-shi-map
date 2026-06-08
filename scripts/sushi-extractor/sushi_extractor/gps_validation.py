#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPS精细化验证系统 - 严格从《苏轼行踪考》提取真实坐标
要求：每个坐标必须有明确的书中原文依据，不能推断
"""
import json
import os
import re
import requests

# 配置
SOURCE_DIR = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4-source/行踪考-简体'
OUTPUT_DIR = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places'
V4_INDEX_PATH = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places-index.json'

# 高德API配置
AMAP_KEY = 'f781d0d96b04cc83a66046e4bf630cc4'
AMAP_GEOCODE_URL = 'https://restapi.amap.com/v3/geocode/geo'

# 精确地址模式 - 必须包含明确的现代行政区划
PRECISE_PATTERNS = [
    # 模式1: "今XX省XX市XX区XX街道" - 最精确
    re.compile(r'今([\u4e00-\u9fa5]{2,}省[\u4e00-\u9fa5]{2,}市[\u4e00-\u9fa5]{2,}区[\u4e00-\u9fa5]{2,}街道)'),
    # 模式2: "今XX省XX市XX区"
    re.compile(r'今([\u4e00-\u9fa5]{2,}省[\u4e00-\u9fa5]{2,}市[\u4e00-\u9fa5]{2,}区)'),
    # 模式3: "今XX省XX市XX县"
    re.compile(r'今([\u4e00-\u9fa5]{2,}省[\u4e00-\u9fa5]{2,}市[\u4e00-\u9fa5]{2,}县)'),
    # 模式4: "今XX市XX区" (省级市)
    re.compile(r'今([\u4e00-\u9fa5]{2,}市[\u4e00-\u9fa5]{2,}区)'),
    # 模式5: "今XX市XX县"
    re.compile(r'今([\u4e00-\u9fa5]{2,}市[\u4e00-\u9fa5]{2,}县)'),
    # 模式6: "现今属XX省XX市XX区"
    re.compile(r'现今属([\u4e00-\u9fa5]{2,}省[\u4e00-\u9fa5]{2,}市[\u4e00-\u9fa5]{2,}区)'),
    # 模式7: "现址在XX市XX区XX路"
    re.compile(r'现址在([\u4e00-\u9fa5]{2,}市[\u4e00-\u9fa5]{2,}区[\u4e00-\u9fa5]{2,}路)'),
]

def read_chapter(filepath):
    """读取章节内容"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def extract_precise_addresses(text, chapter_name):
    """严格提取书中明确的现代地址"""
    addresses = []
    
    for pattern in PRECISE_PATTERNS:
        matches = pattern.findall(text)
        for match in matches:
            full_addr = match if pattern.pattern.startswith('今') else f'今{match}'
            addresses.append({
                'address': full_addr,
                'pattern': pattern.pattern[:30] + '...',
                'chapter': chapter_name
            })
    
    return addresses

def extract_all_precise_addresses():
    """提取所有章节中的精确地址"""
    chapter_files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith('.md')])
    all_addresses = []
    
    for filename in chapter_files:
        if filename.startswith('02_') or filename.startswith('03_') or filename.startswith('04_'):
            continue
        
        filepath = os.path.join(SOURCE_DIR, filename)
        text = read_chapter(filepath)
        chapter_name = filename.replace('.md', '').replace('_', ' ')
        
        addresses = extract_precise_addresses(text, chapter_name)
        if addresses:
            all_addresses.extend(addresses)
            print(f"📄 {filename}: 提取到 {len(addresses)} 个精确地址")
    
    return all_addresses

def get_geocode(address):
    """调用高德API获取精确坐标"""
    try:
        params = {
            'address': address.replace('今', ''),
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
                'confidence': float(geo.get('confidence', '0')),
                'level': geo.get('level', '')
            }
        return None
    except Exception as e:
        print(f"❌ 地理编码失败: {address} - {e}")
        return None

def match_address_to_place(address, v4_index):
    """将地址匹配到对应的地点"""
    addr_text = address['address']
    
    for place in v4_index['places']:
        ancient_name = place['ancient_name']
        modern_name = place['modern_name']
        
        # 检查地点名称是否在地址中
        if ancient_name in addr_text or modern_name in addr_text:
            return place
    
    # 反向检查地址是否在地点名称中
    for place in v4_index['places']:
        if addr_text.replace('今', '') in place['modern_name']:
            return place
    
    return None

def generate_validation_report():
    """生成GPS验证报告"""
    print("="*60)
    print("GPS精细化验证系统")
    print("规则：只提取书中明确提到的现代地址，不推断")
    print("="*60)
    
    print("\n【1】提取所有精确地址...")
    all_addresses = extract_all_precise_addresses()
    print(f"\n   共提取到 {len(all_addresses)} 个精确地址")
    
    print("\n【2】加载v4地点索引...")
    with open(V4_INDEX_PATH, 'r', encoding='utf-8') as f:
        v4_index = json.load(f)
    
    print("\n【3】匹配地址到地点并获取坐标...")
    
    # 创建验证结果
    validation_results = {
        'matched': [],
        'unmatched': [],
        'failed_geocode': []
    }
    
    for address in all_addresses:
        place = match_address_to_place(address, v4_index)
        
        if place:
            geocode = get_geocode(address['address'])
            
            if geocode:
                result = {
                    'place_id': place['id'],
                    'ancient_name': place['ancient_name'],
                    'modern_name': place['modern_name'],
                    'extracted_address': address['address'],
                    'source_chapter': address['chapter'],
                    'pattern': address['pattern'],
                    'lat': geocode['lat'],
                    'lng': geocode['lng'],
                    'formatted_address': geocode['formatted_address'],
                    'confidence': geocode['confidence'],
                    'level': geocode['level']
                }
                validation_results['matched'].append(result)
                print(f"✅ {place['id']}: {place['ancient_name']} - {address['address']}")
            else:
                validation_results['failed_geocode'].append({
                    'address': address['address'],
                    'chapter': address['chapter'],
                    'place_id': place['id'],
                    'ancient_name': place['ancient_name']
                })
                print(f"⚠️  {place['id']}: {place['ancient_name']} - 地理编码失败")
        else:
            validation_results['unmatched'].append({
                'address': address['address'],
                'chapter': address['chapter'],
                'pattern': address['pattern']
            })
            print(f"❓ 未匹配到地点: {address['address']}")
    
    # 生成验证报告文件
    report_path = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/scripts/sushi-extractor/sushi_extractor/gps_validation_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 验证报告已生成: {report_path}")
    print(f"\n【验证统计】")
    print(f"   匹配成功: {len(validation_results['matched'])} 个")
    print(f"   未匹配地点: {len(validation_results['unmatched'])} 个")
    print(f"   地理编码失败: {len(validation_results['failed_geocode'])} 个")
    
    # 打印详细匹配结果
    print("\n【详细匹配结果】")
    for result in validation_results['matched']:
        print(f"\n📍 {result['place_id']}: {result['ancient_name']}")
        print(f"   原始地址: {result['extracted_address']}")
        print(f"   来源章节: {result['source_chapter']}")
        print(f"   坐标: ({result['lat']:.6f}, {result['lng']:.6f})")
        print(f"   置信度: {result['confidence']} | 精度: {result['level']}")
    
    return validation_results

def preview_changes():
    """预览待更新的GPS坐标（不实际修改）"""
    print("\n【4】预览待更新的GPS坐标（不实际修改）")
    
    report_path = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/scripts/sushi-extractor/sushi_extractor/gps_validation_report.json'
    with open(report_path, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print("\n待更新的地点列表（需人工验证）:")
    print("-" * 80)
    print(f"{'地点ID':<8} {'古地名':<12} {'现代地址':<25} {'坐标':<20} {'置信度'}")
    print("-" * 80)
    
    for result in results['matched']:
        print(f"{result['place_id']:<8} {result['ancient_name']:<12} {result['extracted_address'][:25]:<25} ({result['lat']:.4f}, {result['lng']:.4f}) {result['confidence']}")
    
    print("\n⚠️  注意：以上坐标均来自《苏轼行踪考》原文提取")
    print("   如需实际更新数据，请运行 update_gps.py")

if __name__ == "__main__":
    generate_validation_report()
    preview_changes()
