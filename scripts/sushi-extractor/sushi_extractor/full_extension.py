#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面扩展覆盖系统 - 针对所有234个地点进行GPS、作品、事件、文旅补充
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

def read_chapter(filepath):
    """读取章节内容"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def extract_modern_addresses(text):
    """从文本中提取现代地址"""
    addresses = []
    
    # 模式1："今XX省XX市XX区"
    pattern1 = re.compile(r'今([\u4e00-\u9fa5]{2,}省[\u4e00-\u9fa5]{2,}市[\u4e00-\u9fa5]{2,}(区|县|镇|乡)?)')
    matches = pattern1.findall(text)
    for match in matches:
        addr = ''.join(match)
        if len(addr) > 5:
            addresses.append(f'今{addr}')
    
    # 模式2："今XX市XX区"
    pattern2 = re.compile(r'今([\u4e00-\u9fa5]{2,}市[\u4e00-\u9fa5]{2,}(区|县|镇|乡)?)')
    matches = pattern2.findall(text)
    for match in matches:
        addr = ''.join(match)
        addresses.append(f'今{addr}')
    
    # 模式3："今XX省XX市"
    pattern3 = re.compile(r'今([\u4e00-\u9fa5]{2,}省[\u4e00-\u9fa5]{2,}市)')
    addresses.extend(pattern3.findall(text))
    
    # 模式4："现今属XX省XX市"
    pattern4 = re.compile(r'现今属([\u4e00-\u9fa5]{2,}省[\u4e00-\u9fa5]{2,}市)')
    addresses.extend(pattern4.findall(text))
    
    # 模式5："现址在XX"
    pattern5 = re.compile(r'现址在([\u4e00-\u9fa5]{2,}(市|区|县|镇|村)[^。，；]+)')
    for match in pattern5.findall(text):
        addr = ''.join(match)
        addresses.append(f'现址在{addr}')
    
    return list(set(addresses))

def extract_works(text):
    """从文本中提取作品"""
    works = []
    
    # 模式1："苏轼《作品名》"
    pattern1 = re.compile(r'苏轼[《「]([^》」]+)[》」]')
    for match in pattern1.findall(text):
        title = match.strip()
        if 2 < len(title) < 50:
            works.append(title)
    
    # 模式2："作《作品名》"
    pattern2 = re.compile(r'[作写赋][《「]([^》」]+)[》」]')
    for match in pattern2.findall(text):
        title = match.strip()
        if 2 < len(title) < 50:
            works.append(title)
    
    return list(set(works))

def extract_events(text):
    """从文本中提取事件"""
    events = []
    
    # 模式1："元丰三年(1080)二月一日，苏轼..."
    pattern1 = re.compile(r'([\u5143\u5B87\u5B97\u516C\u516D\u5BB6\u5341\u4E03\u4E5D][\u4E00\u4E8C\u4E09\u56DB\u4E94\u516D\u4E03\u516B\u4E5D\u5341]+年\(\d{4}\)[^\n]+苏轼[^\n]+)')
    for match in pattern1.findall(text):
        events.append(match.strip())
    
    # 模式2："XX年苏轼..."
    pattern2 = re.compile(r'(\d{4}年[^\n]+苏轼[^\n]+)')
    for match in pattern2.findall(text):
        events.append(match.strip())
    
    return list(set(events))

def extract_sites(text):
    """从文本中提取景点"""
    sites = []
    
    # 寺庙道观
    pattern1 = re.compile(r'([\u4e00-\u9fa5]{2,}寺|[\u4e00-\u9fa5]{2,}庙|[\u4e00-\u9fa5]{2,}庵|[\u4e00-\u9fa5]{2,}观)')
    sites.extend([{'name': m, 'type': 'temple'} for m in pattern1.findall(text)])
    
    # 亭台楼阁
    pattern2 = re.compile(r'([\u4e00-\u9fa5]{2,}亭|[\u4e00-\u9fa5]{2,}楼|[\u4e00-\u9fa5]{2,}阁)')
    for m in pattern2.findall(text):
        sites.append({'name': m, 'type': 'pavilion' if '亭' in m else 'tower'})
    
    # 山水景点
    pattern3 = re.compile(r'([\u4e00-\u9fa5]{2,}湖|[\u4e00-\u9fa5]{2,}山|[\u4e00-\u9fa5]{2,}泉|[\u4e00-\u9fa5]{2,}洞)')
    for m in pattern3.findall(text):
        if '湖' in m:
            sites.append({'name': m, 'type': 'lake'})
        elif '山' in m:
            sites.append({'name': m, 'type': 'mountain'})
    
    # 去重
    seen = set()
    return [s for s in sites if s['name'] not in seen and not seen.add(s['name'])]

def get_geocode(address):
    """调用高德API获取坐标"""
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
                'formatted_address': geo.get('formatted_address', '')
            }
        return None
    except Exception as e:
        return None

def load_chapter_data():
    """加载所有章节的数据"""
    chapter_files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith('.md')])
    chapter_data = {}
    
    for filename in chapter_files:
        if filename.startswith('02_') or filename.startswith('03_') or filename.startswith('04_'):
            continue
        
        filepath = os.path.join(SOURCE_DIR, filename)
        text = read_chapter(filepath)
        chapter_name = filename.replace('.md', '').replace('_', ' ')
        
        chapter_data[chapter_name] = {
            'addresses': extract_modern_addresses(text),
            'works': extract_works(text),
            'events': extract_events(text),
            'sites': extract_sites(text)
        }
    
    return chapter_data

def match_location(place, chapter_data):
    """匹配地点与章节数据"""
    matched = {
        'addresses': [],
        'works': [],
        'events': [],
        'sites': []
    }
    
    ancient_name = place['ancient_name']
    modern_name = place['modern_name']
    
    for chapter_name, data in chapter_data.items():
        # 检查地点名称是否出现在章节中
        if ancient_name in chapter_name or modern_name in chapter_name:
            matched['addresses'].extend(data['addresses'])
            matched['works'].extend(data['works'])
            matched['events'].extend(data['events'])
            matched['sites'].extend(data['sites'])
        else:
            # 检查章节中是否提到该地点
            for addr in data['addresses']:
                if ancient_name in addr or modern_name in addr:
                    matched['addresses'].append(addr)
    
    return matched

def update_place(place_id, matched_data):
    """更新单个地点的数据"""
    place_file = os.path.join(OUTPUT_DIR, f"{place_id}.json")
    if not os.path.exists(place_file):
        return None
    
    with open(place_file, 'r', encoding='utf-8') as f:
        place_data = json.load(f)
    
    updates = {}
    
    # 更新GPS坐标
    if matched_data['addresses']:
        for addr in matched_data['addresses'][:3]:  # 尝试前3个地址
            geocode = get_geocode(addr)
            if geocode:
                place_data['lat'] = geocode['lat']
                place_data['lng'] = geocode['lng']
                place_data['coordinate_source'] = 'sxzk_extracted'
                place_data['amap_address'] = geocode['formatted_address']
                updates['gps'] = True
                break
    
    # 更新作品
    existing_titles = {w.get('title', '') for w in place_data.get('global_works', [])}
    new_works = []
    for work_title in matched_data['works'][:8]:
        if work_title not in existing_titles:
            new_works.append({
                'id': f"{place_id}-work-{len(place_data.get('global_works', [])) + len(new_works) + 1}",
                'title': work_title,
                'content': '',
                'type': '词' if '·' in work_title else '诗',
                'date': '',
                'location': place_data.get('ancient_name', '')
            })
    if new_works:
        place_data.setdefault('global_works', []).extend(new_works)
        updates['works'] = len(new_works)
    
    # 更新事件
    existing_descriptions = {e.get('description', '')[:30] for e in place_data.get('global_events', [])}
    new_events = []
    for event_text in matched_data['events'][:6]:
        key = event_text[:30]
        if key not in existing_descriptions:
            new_events.append({
                'id': f"{place_id}-event-{len(place_data.get('global_events', [])) + len(new_events) + 1}",
                'title': event_text[:25] + '...' if len(event_text) > 25 else event_text,
                'description': event_text,
                'date': '',
                'significance': '重要事件'
            })
    if new_events:
        place_data.setdefault('global_events', []).extend(new_events)
        updates['events'] = len(new_events)
    
    # 更新景点
    existing_names = {s.get('name', '') for s in place_data.get('memorial_sites', [])}
    new_sites = []
    for site in matched_data['sites'][:4]:
        if site['name'] not in existing_names:
            new_sites.append({
                'name': site['name'],
                'type': site['type'],
                'description': '',
                'modern_address': ''
            })
    if new_sites:
        place_data.setdefault('memorial_sites', []).extend(new_sites)
        updates['sites'] = len(new_sites)
    
    if updates:
        with open(place_file, 'w', encoding='utf-8') as f:
            json.dump(place_data, f, ensure_ascii=False, indent=2)
    
    return updates

def main():
    print("="*60)
    print("全面扩展覆盖系统 - 处理所有234个地点")
    print("="*60)
    
    print("\n【1】加载章节数据...")
    chapter_data = load_chapter_data()
    print(f"   已加载 {len(chapter_data)} 个章节")
    
    print("\n【2】加载v4地点索引...")
    with open(V4_INDEX_PATH, 'r', encoding='utf-8') as f:
        v4_index = json.load(f)
    
    print("\n【3】开始更新所有地点...")
    stats = {
        'total': 0,
        'gps': 0,
        'works': 0,
        'events': 0,
        'sites': 0,
        'updated': 0
    }
    
    for place in v4_index['places']:
        place_id = place['id']
        ancient_name = place['ancient_name']
        
        matched_data = match_location(place, chapter_data)
        updates = update_place(place_id, matched_data)
        
        if updates:
            stats['updated'] += 1
            if 'gps' in updates:
                stats['gps'] += 1
            if 'works' in updates:
                stats['works'] += updates['works']
            if 'events' in updates:
                stats['events'] += updates['events']
            if 'sites' in updates:
                stats['sites'] += updates['sites']
            
            print(f"✅ {place_id}: {ancient_name} - {', '.join([f'{k}: {v}' for k, v in updates.items()])}")
        
        stats['total'] += 1
    
    print(f"\n📊 全面扩展覆盖完成")
    print(f"   处理地点: {stats['total']} 个")
    print(f"   更新地点: {stats['updated']} 个")
    print(f"   GPS更新: {stats['gps']} 个")
    print(f"   作品新增: {stats['works']} 篇")
    print(f"   事件新增: {stats['events']} 个")
    print(f"   景点新增: {stats['sites']} 处")
    
    print("\n✅ 所有任务完成！")

if __name__ == "__main__":
    main()
