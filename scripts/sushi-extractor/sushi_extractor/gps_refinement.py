#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPS精细化系统 - 从《苏轼行踪考》提取现代地址并获取精确坐标
"""
import json
import os
import re
import requests
from pathlib import Path

# 配置
SOURCE_DIR = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4-source/行踪考-简体'
OUTPUT_DIR = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places'
V4_INDEX_PATH = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places-index.json'

# 高德API配置
AMAP_KEY = 'f781d0d96b04cc83a66046e4bf630cc4'  # 从.env.local获取的Web服务Key
AMAP_GEOCODE_URL = 'https://restapi.amap.com/v3/geocode/geo'

def read_chapter(filepath):
    """读取章节内容"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def extract_modern_addresses(text):
    """从文本中提取现代地址"""
    addresses = []
    
    # 模式1："今XX省XX市" 或 "今XX市XX区"
    pattern1 = re.compile(r'今([\u4e00-\u9fa5]{2,}省[\u4e00-\u9fa5]{2,}市[\u4e00-\u9fa5]{2,}(区|县|镇)?)')
    matches = pattern1.findall(text)
    for match in matches:
        addr = ''.join(match)
        if len(addr) > 5:  # 过滤太短的匹配
            addresses.append(f'今{addr}')
    
    # 模式2："现今属XX省XX市"
    pattern2 = re.compile(r'现今属([\u4e00-\u9fa5]{2,}省[\u4e00-\u9fa5]{2,}市)')
    matches = pattern2.findall(text)
    addresses.extend(matches)
    
    # 模式3："今在XX市XX区"
    pattern3 = re.compile(r'今在([\u4e00-\u9fa5]{2,}市[\u4e00-\u9fa5]{2,}(区|县))')
    matches = pattern3.findall(text)
    for match in matches:
        addr = ''.join(match)
        addresses.append(f'今{addr}')
    
    # 模式4："现址在XX"
    pattern4 = re.compile(r'现址在([\u4e00-\u9fa5]{2,}(市|区|县|镇|村).*?[。，；])')
    matches = pattern4.findall(text)
    for match in matches:
        addr = ''.join(match).rstrip('。，；')
        if len(addr) > 4:
            addresses.append(f'现址在{addr}')
    
    return list(set(addresses))  # 去重

def get_geocode(address):
    """调用高德API获取坐标"""
    if not AMAP_KEY or AMAP_KEY == 'your_amap_key_here':
        print(f"⚠️  未配置高德API密钥，跳过地址: {address}")
        return None
    
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
        else:
            return None
    except Exception as e:
        print(f"❌ 地理编码失败: {address} - {e}")
        return None

def batch_extract_addresses():
    """批量提取所有章节的地址"""
    chapter_files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith('.md')])
    all_addresses = {}
    
    for filename in chapter_files:
        if filename.startswith('02_') or filename.startswith('03_') or filename.startswith('04_'):
            continue
        
        filepath = os.path.join(SOURCE_DIR, filename)
        text = read_chapter(filepath)
        addresses = extract_modern_addresses(text)
        
        if addresses:
            chapter_name = filename.replace('.md', '').replace('_', ' ')
            all_addresses[chapter_name] = addresses
            print(f"📄 {filename}: 提取到 {len(addresses)} 个地址")
    
    return all_addresses

def update_gps_coordinates():
    """更新v4地点的GPS坐标"""
    # 加载v4索引
    with open(V4_INDEX_PATH, 'r', encoding='utf-8') as f:
        v4_index = json.load(f)
    
    # 提取所有地址
    all_addresses = batch_extract_addresses()
    
    updated_count = 0
    skipped_count = 0
    
    for place in v4_index['places']:
        place_id = place['id']
        ancient_name = place['ancient_name']
        modern_name = place['modern_name']
        place_file = os.path.join(OUTPUT_DIR, f"{place_id}.json")
        
        if not os.path.exists(place_file):
            continue
        
        # 查找匹配的地址
        matched_addr = None
        for chapter, addresses in all_addresses.items():
            for addr in addresses:
                # 检查地址是否与地点名称匹配
                if ancient_name in addr or any(keyword in addr for keyword in ancient_name.split()):
                    matched_addr = addr
                    break
            if matched_addr:
                break
        
        if matched_addr:
            # 获取坐标
            geocode = get_geocode(matched_addr)
            if geocode:
                # 更新地点文件
                with open(place_file, 'r', encoding='utf-8') as f:
                    place_data = json.load(f)
                
                # 更新坐标
                place_data['lat'] = geocode['lat']
                place_data['lng'] = geocode['lng']
                place_data['coordinate_source'] = 'sxzk_extracted'
                place_data['amap_address'] = geocode['formatted_address']
                place_data['coords_updated_at'] = '2026-06-07T00:00:00.000Z'
                
                with open(place_file, 'w', encoding='utf-8') as f:
                    json.dump(place_data, f, ensure_ascii=False, indent=2)
                
                updated_count += 1
                print(f"✅ {place_id}: {ancient_name} → {matched_addr} → ({geocode['lat']:.4f}, {geocode['lng']:.4f})")
            else:
                skipped_count += 1
                print(f"⚠️ {place_id}: {ancient_name} → 地址获取失败")
    
    print(f"\n📊 GPS精细化完成")
    print(f"   更新: {updated_count} 个地点")
    print(f"   跳过: {skipped_count} 个地点")
    
    return updated_count

def main():
    print("="*60)
    print("GPS精细化系统 - 从《苏轼行踪考》提取坐标")
    print("="*60)
    
    # 检查API密钥
    if not AMAP_KEY or AMAP_KEY == 'your_amap_key_here':
        print("\n⚠️  警告：未配置高德API密钥")
        print("   请设置环境变量: export AMAP_KEY=your_key")
        print("   或直接在脚本中修改AMAP_KEY变量")
    
    print("\n【1】开始提取现代地址...")
    all_addresses = batch_extract_addresses()
    
    print(f"\n【2】共提取到 {sum(len(addrs) for addrs in all_addresses.values())} 个地址")
    
    print("\n【3】开始更新GPS坐标...")
    update_gps_coordinates()
    
    print("\n✅ GPS精细化完成！")

if __name__ == "__main__":
    main()
