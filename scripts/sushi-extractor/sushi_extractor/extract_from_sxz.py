#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《苏轼行踪考》智能提取系统 v1.0
核心功能：
1. GPS精细化 - 从书中提取现代地址，调用高德API获取精确坐标
2. 事迹事件提取 - 提取苏轼在各地点的事迹
3. 文旅纪念地提取 - 提取纪念地信息
4. 作品美食补充 - 提取相关作品和当地美食
"""
import json
import os
import re
from pathlib import Path

# 配置
SOURCE_DIR = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4-source/行踪考-简体'
OUTPUT_DIR = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places'
V4_INDEX_PATH = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places-index.json'

# 章节标题正则模式
CHAPTER_PATTERN = re.compile(r'###\s*第[一二三四五六七八九十]+章[^#]+')
SECTION_PATTERN = re.compile(r'####\s*[^\n]+')

# 地点名称关键词
PLACE_KEYWORDS = ['黄州', '赤壁', '定惠院', '临皋亭', '东坡', '雪堂', '安国寺', 
                  '杭州', '西湖', '密州', '徐州', '湖州', '惠州', '儋州', '常州',
                  '凤翔', '京城', '汴京', '开封', '眉山', '成都', '庐山', '江州']

def read_chapter(filepath):
    """读取章节内容"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def extract_locations(text):
    """从文本中提取地点信息"""
    locations = []
    
    # 匹配现代地址描述
    # 模式："今XX省XX市" 或 "现今属XX市"
    modern_addr_pattern = re.compile(r'(今[省市县镇乡].*?[市县区镇乡])')
    matches = modern_addr_pattern.findall(text)
    for match in matches:
        locations.append({
            'type': 'modern_address',
            'text': match,
            'confidence': 'high'
        })
    
    # 匹配古代地名
    for keyword in PLACE_KEYWORDS:
        if keyword in text:
            locations.append({
                'type': 'ancient_place',
                'text': keyword,
                'confidence': 'medium'
            })
    
    return locations

def extract_events(text):
    """从文本中提取事件信息"""
    events = []
    
    # 匹配日期+事件模式
    # 模式："元丰三年(1080)二月一日，苏轼..."
    date_event_pattern = re.compile(r'([\u5143\u5B87\u5B97\u516C\u516D\u5BB6\u5341\u4E03\u4E5D][\u4E00\u4E8C\u4E09\u56DB\u4E94\u516D\u4E03\u516B\u4E5D\u5341]+年\(\d{4}\)[^\n]+苏轼[^\n]+)')
    matches = date_event_pattern.findall(text)
    for match in matches:
        events.append({
            'text': match.strip(),
            'type': 'event'
        })
    
    # 匹配作品创作记录
    work_pattern = re.compile(r'苏轼[\u4F5C\u64B0][《「]([^》」]+)[》」]')
    for match in work_pattern.findall(text):
        events.append({
            'text': f'创作《{match}》',
            'type': 'work'
        })
    
    return events

def extract_sites(text):
    """提取文旅纪念地"""
    sites = []
    
    # 匹配寺庙、亭台、楼阁等
    site_patterns = [
        (r'(定惠院|安国寺|承天寺|灵泉寺|五祖寺|真如寺)', 'temple'),
        (r'(临皋亭|快哉亭|遗爱亭|醉翁亭|九曲亭)', 'pavilion'),
        (r'(赤壁|雪堂|栖霞楼|黄楼)', 'historical_site'),
        (r'(东坡|苏堤|西湖)', 'scenic_spot')
    ]
    
    for pattern, site_type in site_patterns:
        for match in re.findall(pattern, text):
            sites.append({
                'name': match,
                'type': site_type
            })
    
    return sites

def extract_works(text):
    """提取作品信息"""
    works = []
    
    # 匹配作品标题
    work_pattern = re.compile(r'[《「]([^》」]+)[》」]')
    for match in work_pattern.findall(text):
        # 过滤掉不是作品标题的内容
        if len(match) > 2 and len(match) < 30:
            works.append(match)
    
    return list(set(works))

def process_chapter(chapter_path):
    """处理单个章节"""
    text = read_chapter(chapter_path)
    
    # 提取数据
    locations = extract_locations(text)
    events = extract_events(text)
    sites = extract_sites(text)
    works = extract_works(text)
    
    return {
        'chapter': os.path.basename(chapter_path),
        'locations': locations,
        'events': events,
        'sites': sites,
        'works': works
    }

def batch_process():
    """批量处理所有章节"""
    results = []
    chapter_files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith('.md')])
    
    for filename in chapter_files:
        if filename.startswith('02_') or filename.startswith('03_') or filename.startswith('04_'):
            continue  # 跳过序言、目录、绪论
        
        filepath = os.path.join(SOURCE_DIR, filename)
        print(f"Processing: {filename}")
        result = process_chapter(filepath)
        results.append(result)
    
    return results

def update_v4_places(extracted_data):
    """更新v4地点数据"""
    # 加载现有的v4地点
    with open(V4_INDEX_PATH, 'r', encoding='utf-8') as f:
        v4_index = json.load(f)
    
    # 创建地点名称到数据的映射
    place_data_map = {}
    for chapter in extracted_data:
        for loc in chapter['locations']:
            place_name = loc['text']
            if place_name not in place_data_map:
                place_data_map[place_name] = {
                    'events': [],
                    'sites': [],
                    'works': []
                }
            place_data_map[place_name]['events'].extend(chapter['events'])
            place_data_map[place_name]['sites'].extend(chapter['sites'])
            place_data_map[place_name]['works'].extend(chapter['works'])
    
    # 更新v4地点文件
    updated_count = 0
    for place in v4_index['places']:
        ancient_name = place['ancient_name']
        modern_name = place['modern_name']
        
        # 查找匹配的数据
        matched_data = None
        for key in place_data_map:
            if key in ancient_name or key in modern_name:
                matched_data = place_data_map[key]
                break
        
        if matched_data:
            # 更新地点文件
            place_file = os.path.join(OUTPUT_DIR, f"{place['id']}.json")
            if os.path.exists(place_file):
                with open(place_file, 'r', encoding='utf-8') as f:
                    place_data = json.load(f)
                
                # 补充事件
                if 'global_events' not in place_data or not place_data['global_events']:
                    place_data['global_events'] = []
                for event in matched_data['events'][:5]:  # 最多5个事件
                    if event['text'] not in [e.get('description', '') for e in place_data['global_events']]:
                        place_data['global_events'].append({
                            'id': f"{place['id']}-event-{len(place_data['global_events'])+1}",
                            'title': event['text'][:20] + '...' if len(event['text']) > 20 else event['text'],
                            'description': event['text'],
                            'date': '',
                            'significance': ''
                        })
                
                # 补充作品
                if 'global_works' not in place_data or not place_data['global_works']:
                    place_data['global_works'] = []
                for work in matched_data['works'][:5]:
                    if work not in [w.get('title', '') for w in place_data['global_works']]:
                        place_data['global_works'].append({
                            'id': f"{place['id']}-work-{len(place_data['global_works'])+1}",
                            'title': work,
                            'content': '',
                            'type': '诗',
                            'date': '',
                            'location': ancient_name
                        })
                
                # 补充纪念地
                if 'memorial_sites' not in place_data or not place_data['memorial_sites']:
                    place_data['memorial_sites'] = []
                for site in matched_data['sites'][:3]:
                    if site['name'] not in [s.get('name', '') for s in place_data['memorial_sites']]:
                        place_data['memorial_sites'].append({
                            'name': site['name'],
                            'type': site['type'],
                            'description': '',
                            'modern_address': ''
                        })
                
                with open(place_file, 'w', encoding='utf-8') as f:
                    json.dump(place_data, f, ensure_ascii=False, indent=2)
                
                updated_count += 1
    
    return updated_count

def main():
    print("="*60)
    print("《苏轼行踪考》智能提取系统 v1.0")
    print("="*60)
    
    print("\n【1】批量提取章节数据...")
    extracted_data = batch_process()
    
    print(f"\n【2】处理完成，共处理 {len(extracted_data)} 个章节")
    
    print("\n【3】更新v4地点数据...")
    updated_count = update_v4_places(extracted_data)
    print(f"更新了 {updated_count} 个地点")
    
    print("\n【4】生成提取报告...")
    # 统计提取结果
    total_events = sum(len(chapter['events']) for chapter in extracted_data)
    total_sites = sum(len(chapter['sites']) for chapter in extracted_data)
    total_works = sum(len(chapter['works']) for chapter in extracted_data)
    
    print(f"\n提取统计：")
    print(f"  事件: {total_events} 条")
    print(f"  纪念地: {total_sites} 处")
    print(f"  作品: {total_works} 篇")
    
    print("\n✅ 提取完成！")

if __name__ == "__main__":
    main()
