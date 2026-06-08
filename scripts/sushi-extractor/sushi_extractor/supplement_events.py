#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事件补充系统 - 从《苏轼行踪考》提取苏轼事迹事件
"""
import json
import os
import re

# 配置
SOURCE_DIR = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4-source/行踪考-简体'
OUTPUT_DIR = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places'
V4_INDEX_PATH = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places-index.json'

# 朝代纪年转换
DYNASTY_YEARS = {
    '仁宗': {'景祐': 1034, '宝元': 1038, '康定': 1040, '庆历': 1041, '皇祐': 1049, '至和': 1054, '嘉祐': 1056},
    '英宗': {'治平': 1064},
    '神宗': {'熙宁': 1068, '元丰': 1078},
    '哲宗': {'元祐': 1086, '绍圣': 1094, '元符': 1098},
    '徽宗': {'建中靖国': 1101}
}

def read_chapter(filepath):
    """读取章节内容"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def extract_events(text):
    """从文本中提取事件信息"""
    events = []
    
    # 模式1："元丰三年(1080)二月一日，苏轼..."
    pattern1 = re.compile(r'([\u5143\u5B87\u5B97\u516C\u516D\u5BB6\u5341\u4E03\u4E5D][\u4E00\u4E8C\u4E09\u56DB\u4E94\u516D\u4E03\u516B\u4E5D\u5341]+年\(\d{4}\)[^\n]+苏轼[^\n]+)')
    for match in pattern1.findall(text):
        events.append({
            'text': match.strip(),
            'type': 'event'
        })
    
    # 模式2："XX年苏轼..."
    pattern2 = re.compile(r'(\d{4}年[^\n]+苏轼[^\n]+)')
    for match in pattern2.findall(text):
        events.append({
            'text': match.strip(),
            'type': 'event'
        })
    
    # 模式3："苏轼XX事件"
    pattern3 = re.compile(r'(苏轼[^\n]{10,50}[。，；])')
    for match in pattern3.findall(text):
        # 过滤掉作品标题
        if '《' not in match or '》' not in match:
            events.append({
                'text': match.strip().rstrip('。，；'),
                'type': 'event'
            })
    
    # 模式4：任职/贬谪信息
    pattern4 = re.compile(r'(苏轼[贬谪调任移任改任].*?[州府军县].*?[。，])')
    for match in pattern4.findall(text):
        events.append({
            'text': match.strip().rstrip('。，'),
            'type': 'official'
        })
    
    # 去重
    seen = set()
    filtered = []
    for event in events:
        key = event['text'][:30]
        if key not in seen:
            seen.add(key)
            filtered.append(event)
    
    return filtered

def batch_extract_events():
    """批量提取所有章节的事件"""
    chapter_files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith('.md')])
    all_events = {}
    
    for filename in chapter_files:
        if filename.startswith('02_') or filename.startswith('03_') or filename.startswith('04_'):
            continue
        
        filepath = os.path.join(SOURCE_DIR, filename)
        text = read_chapter(filepath)
        events = extract_events(text)
        
        if events:
            chapter_name = filename.replace('.md', '').replace('_', ' ')
            all_events[chapter_name] = events
            print(f"📄 {filename}: 提取到 {len(events)} 个事件")
    
    return all_events

def update_events():
    """更新v4地点的事件信息"""
    # 加载v4索引
    with open(V4_INDEX_PATH, 'r', encoding='utf-8') as f:
        v4_index = json.load(f)
    
    # 提取所有事件
    all_events = batch_extract_events()
    
    updated_count = 0
    total_added = 0
    
    for place in v4_index['places']:
        place_id = place['id']
        ancient_name = place['ancient_name']
        modern_name = place['modern_name']
        place_file = os.path.join(OUTPUT_DIR, f"{place_id}.json")
        
        if not os.path.exists(place_file):
            continue
        
        # 查找匹配的事件
        matched_events = []
        for chapter, events in all_events.items():
            # 检查章节是否与地点相关
            if ancient_name in chapter or any(keyword in chapter for keyword in ancient_name.split()):
                matched_events.extend(events)
        
        if matched_events:
            # 读取地点文件
            with open(place_file, 'r', encoding='utf-8') as f:
                place_data = json.load(f)
            
            # 获取已有的事件描述
            existing_descriptions = {e.get('description', '')[:30] for e in place_data.get('global_events', [])}
            
            # 添加新事件
            added_count = 0
            for event in matched_events[:8]:  # 最多添加8个事件
                key = event['text'][:30]
                if key not in existing_descriptions:
                    place_data.setdefault('global_events', []).append({
                        'id': f"{place_id}-event-{len(place_data['global_events'])+1}",
                        'title': event['text'][:25] + '...' if len(event['text']) > 25 else event['text'],
                        'description': event['text'],
                        'date': '',
                        'significance': '重要事件' if event['type'] == 'official' else '事迹'
                    })
                    added_count += 1
                    existing_descriptions.add(key)
            
            if added_count > 0:
                # 保存更新
                with open(place_file, 'w', encoding='utf-8') as f:
                    json.dump(place_data, f, ensure_ascii=False, indent=2)
                
                updated_count += 1
                total_added += added_count
                print(f"✅ {place_id}: {ancient_name} - 添加 {added_count} 个事件")
    
    print(f"\n📊 事件补充完成")
    print(f"   更新地点: {updated_count} 个")
    print(f"   添加事件: {total_added} 个")
    
    return updated_count, total_added

def main():
    print("="*60)
    print("事件补充系统 - 从《苏轼行踪考》提取事迹")
    print("="*60)
    
    print("\n【1】开始提取事件...")
    all_events = batch_extract_events()
    
    total_events = sum(len(events) for events in all_events.values())
    print(f"\n【2】共提取到 {total_events} 个事件")
    
    print("\n【3】开始更新地点事件...")
    update_events()
    
    print("\n✅ 事件补充完成！")

if __name__ == "__main__":
    main()
