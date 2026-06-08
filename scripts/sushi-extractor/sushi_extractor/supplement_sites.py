#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文旅信息补充系统 - 从《苏轼行踪考》提取纪念地、文旅景点
"""
import json
import os
import re

# 配置
SOURCE_DIR = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4-source/行踪考-简体'
OUTPUT_DIR = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places'
V4_INDEX_PATH = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places-index.json'

# 景点类型映射
SITE_TYPES = {
    '寺': 'temple',
    '庙': 'temple',
    '庵': 'temple',
    '观': 'temple',
    '亭': 'pavilion',
    '楼': 'tower',
    '阁': 'tower',
    '堂': 'hall',
    '桥': 'bridge',
    '堤': 'embankment',
    '湖': 'lake',
    '山': 'mountain',
    '泉': 'spring',
    '洞': 'cave',
    '台': 'platform',
    '馆': 'museum',
    '故居': 'residence',
    '墓': 'tomb',
    '祠': 'shrine',
    '书院': 'academy',
    '遗址': 'ruins',
    '公园': 'park',
    '广场': 'square',
}

def read_chapter(filepath):
    """读取章节内容"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def extract_sites(text):
    """从文本中提取文旅景点"""
    sites = []
    
    # 模式1：寺庙道观
    pattern1 = re.compile(r'([\u4e00-\u9fa5]{2,}寺|[\u4e00-\u9fa5]{2,}庙|[\u4e00-\u9fa5]{2,}庵|[\u4e00-\u9fa5]{2,}观)')
    for match in pattern1.findall(text):
        sites.append({'name': match, 'type': 'temple'})
    
    # 模式2：亭台楼阁
    pattern2 = re.compile(r'([\u4e00-\u9fa5]{2,}亭|[\u4e00-\u9fa5]{2,}楼|[\u4e00-\u9fa5]{2,}阁|[\u4e00-\u9fa5]{2,}台)')
    for match in pattern2.findall(text):
        sites.append({'name': match, 'type': 'pavilion' if '亭' in match else 'tower'})
    
    # 模式3：堂、馆、故居
    pattern3 = re.compile(r'([\u4e00-\u9fa5]{2,}堂|[\u4e00-\u9fa5]{2,}馆|[\u4e00-\u9fa5]+故居)')
    for match in pattern3.findall(text):
        sites.append({'name': match, 'type': 'hall' if '堂' in match else 'museum'})
    
    # 模式4：桥、堤、湖、山
    pattern4 = re.compile(r'([\u4e00-\u9fa5]{2,}桥|[\u4e00-\u9fa5]{2,}堤|[\u4e00-\u9fa5]{2,}湖|[\u4e00-\u9fa5]{2,}山)')
    for match in pattern4.findall(text):
        if '桥' in match:
            sites.append({'name': match, 'type': 'bridge'})
        elif '堤' in match:
            sites.append({'name': match, 'type': 'embankment'})
        elif '湖' in match:
            sites.append({'name': match, 'type': 'lake'})
        elif '山' in match:
            sites.append({'name': match, 'type': 'mountain'})
    
    # 模式5：墓、祠、书院、遗址
    pattern5 = re.compile(r'([\u4e00-\u9fa5]{2,}墓|[\u4e00-\u9fa5]{2,}祠|[\u4e00-\u9fa5]{2,}书院|[\u4e00-\u9fa5]{2,}遗址)')
    for match in pattern5.findall(text):
        if '墓' in match:
            sites.append({'name': match, 'type': 'tomb'})
        elif '祠' in match:
            sites.append({'name': match, 'type': 'shrine'})
        elif '书院' in match:
            sites.append({'name': match, 'type': 'academy'})
        elif '遗址' in match:
            sites.append({'name': match, 'type': 'ruins'})
    
    # 去重
    seen = set()
    filtered = []
    for site in sites:
        if site['name'] not in seen:
            seen.add(site['name'])
            # 过滤太短的名称
            if len(site['name']) > 1:
                filtered.append(site)
    
    return filtered

def batch_extract_sites():
    """批量提取所有章节的景点"""
    chapter_files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith('.md')])
    all_sites = {}
    
    for filename in chapter_files:
        if filename.startswith('02_') or filename.startswith('03_') or filename.startswith('04_'):
            continue
        
        filepath = os.path.join(SOURCE_DIR, filename)
        text = read_chapter(filepath)
        sites = extract_sites(text)
        
        if sites:
            chapter_name = filename.replace('.md', '').replace('_', ' ')
            all_sites[chapter_name] = sites
            print(f"📄 {filename}: 提取到 {len(sites)} 处景点")
    
    return all_sites

def update_sites():
    """更新v4地点的文旅信息"""
    # 加载v4索引
    with open(V4_INDEX_PATH, 'r', encoding='utf-8') as f:
        v4_index = json.load(f)
    
    # 提取所有景点
    all_sites = batch_extract_sites()
    
    updated_count = 0
    total_added = 0
    
    for place in v4_index['places']:
        place_id = place['id']
        ancient_name = place['ancient_name']
        modern_name = place['modern_name']
        place_file = os.path.join(OUTPUT_DIR, f"{place_id}.json")
        
        if not os.path.exists(place_file):
            continue
        
        # 查找匹配的景点
        matched_sites = []
        for chapter, sites in all_sites.items():
            # 检查章节是否与地点相关
            if ancient_name in chapter or any(keyword in chapter for keyword in ancient_name.split()):
                matched_sites.extend(sites)
        
        if matched_sites:
            # 读取地点文件
            with open(place_file, 'r', encoding='utf-8') as f:
                place_data = json.load(f)
            
            # 获取已有的景点名称
            existing_names = {s.get('name', '') for s in place_data.get('memorial_sites', [])}
            
            # 添加新景点
            added_count = 0
            for site in matched_sites[:6]:  # 最多添加6处
                if site['name'] not in existing_names:
                    place_data.setdefault('memorial_sites', []).append({
                        'name': site['name'],
                        'type': site['type'],
                        'description': '',
                        'modern_address': ''
                    })
                    added_count += 1
                    existing_names.add(site['name'])
            
            if added_count > 0:
                # 保存更新
                with open(place_file, 'w', encoding='utf-8') as f:
                    json.dump(place_data, f, ensure_ascii=False, indent=2)
                
                updated_count += 1
                total_added += added_count
                print(f"✅ {place_id}: {ancient_name} - 添加 {added_count} 处景点")
    
    print(f"\n📊 文旅信息补充完成")
    print(f"   更新地点: {updated_count} 个")
    print(f"   添加景点: {total_added} 处")
    
    return updated_count, total_added

def main():
    print("="*60)
    print("文旅信息补充系统 - 从《苏轼行踪考》提取景点")
    print("="*60)
    
    print("\n【1】开始提取景点...")
    all_sites = batch_extract_sites()
    
    total_sites = sum(len(sites) for sites in all_sites.values())
    print(f"\n【2】共提取到 {total_sites} 处景点")
    
    print("\n【3】开始更新地点文旅信息...")
    update_sites()
    
    print("\n✅ 文旅信息补充完成！")

if __name__ == "__main__":
    main()
