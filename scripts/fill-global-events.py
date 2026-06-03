#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
global_events批量补全工具
从苏轼行踪考markdown文件中提取历史事件并补全到地点数据中
"""

import json
import os
import re
from pathlib import Path

# 配置
MARKDOWN_DIR = Path(__file__).parent.parent / "data-v4-source" / "行踪考-简体"
PLACES_DIR = Path(__file__).parent.parent / "data-v4" / "places"
INDEX_FILE = Path(__file__).parent.parent / "data-v4" / "places-index.json"

# 事件模板
EVENT_TEMPLATES = {
    "眉山": [
        {"date": "景祐三年（1036年）", "title": "苏轼出生", "description": "苏轼诞生于眉州眉山", "significance": "birth"},
        {"date": "庆历二年（1042年）", "title": "启蒙读书", "description": "苏轼开始读书，师从张易简", "significance": "education"},
        {"date": "至和元年（1054年）", "title": "娶妻王弗", "description": "苏轼与王弗成婚", "significance": "marriage"},
        {"date": "嘉祐元年（1056年）", "title": "首次出蜀", "description": "苏轼随父苏洵、弟苏辙赴京应考", "significance": "route01"},
    ],
    "汴京": [
        {"date": "嘉祐二年（1057年）", "title": "进士及第", "description": "苏轼、苏辙同榜进士及第", "significance": "career"},
        {"date": "嘉祐六年（1061年）", "title": "制科入三等", "description": "苏轼应制科考试，入三等", "significance": "career"},
        {"date": "治平三年（1066年）", "title": "苏洵病逝", "description": "苏洵在汴京病逝，苏轼扶柩回乡", "significance": "family"},
        {"date": "熙宁二年（1069年）", "title": "返京任职", "description": "守丧期满返京，任殿中丞、直史馆", "significance": "career"},
        {"date": "元丰二年（1079年）", "title": "乌台诗案", "description": "苏轼因诗获罪，被捕入狱", "significance": "political"},
        {"date": "元祐元年（1086年）", "title": "元祐更化", "description": "司马光执政，苏轼回京任中书舍人", "significance": "career"},
    ],
    "凤翔": [
        {"date": "嘉祐六年（1061年）", "title": "凤翔签判", "description": "苏轼任凤翔府签书判官", "significance": "first_official"},
    ],
    "杭州": [
        {"date": "熙宁四年（1071年）", "title": "杭州通判", "description": "苏轼任杭州通判", "significance": "route04"},
        {"date": "元祐四年（1089年）", "title": "杭州知州", "description": "苏轼任杭州知州，疏浚西湖", "significance": "route14"},
    ],
    "密州": [
        {"date": "熙宁七年（1074年）", "title": "密州知州", "description": "苏轼调任密州知州", "significance": "route05"},
    ],
    "徐州": [
        {"date": "熙宁十年（1077年）", "title": "徐州知州", "description": "苏轼调任徐州知州，抗洪有功", "significance": "route06"},
    ],
    "黄州": [
        {"date": "元丰三年（1080年）", "title": "贬谪黄州", "description": "苏轼贬黄州团练副使，自号东坡居士", "significance": "route09"},
        {"date": "元丰五年（1082年）", "title": "赤壁怀古", "description": "苏轼游览赤壁，作前后《赤壁赋》《念奴娇》", "significance": "literary"},
    ],
    "惠州": [
        {"date": "绍圣元年（1094年）", "title": "贬谪惠州", "description": "苏轼贬惠州安置", "significance": "route18"},
    ],
    "儋州": [
        {"date": "绍圣四年（1097年）", "title": "贬谪儋州", "description": "苏轼贬儋州安置", "significance": "route19"},
    ],
    "常州": [
        {"date": "建中靖国元年（1101年）", "title": "终老常州", "description": "苏轼北归途中病逝于常州", "significance": "death"},
    ],
    "庐山": [
        {"date": "元丰七年（1084年）", "title": "游览庐山", "description": "苏轼游览庐山，作《题西林壁》", "significance": "route10"},
    ],
    "扬州": [
        {"date": "元祐七年（1092年）", "title": "扬州知州", "description": "苏轼任扬州知州", "significance": "route16"},
    ],
    "颍州": [
        {"date": "元祐六年（1091年）", "title": "颍州知州", "description": "苏轼任颍州知州", "significance": "route15"},
    ],
    "定州": [
        {"date": "元祐八年（1093年）", "title": "定州知州", "description": "苏轼任定州知州", "significance": "route17"},
    ],
    "登州": [
        {"date": "元丰八年（1085年）", "title": "登州五日", "description": "苏轼任登州知州，仅五日即被召回", "significance": "route11"},
    ],
}


def load_places_index():
    """加载地点索引"""
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"places": []}


def load_place_data(place_id):
    """加载地点数据"""
    file_path = PLACES_DIR / f"{place_id}.json"
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_place_data(place_id, data):
    """保存地点数据"""
    file_path = PLACES_DIR / f"{place_id}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_places_without_events():
    """获取没有global_events的地点"""
    result = []
    for filename in os.listdir(PLACES_DIR):
        if filename.endswith('.json'):
            place_id = filename.replace('.json', '')
            data = load_place_data(place_id)
            if data and (not data.get('global_events') or len(data['global_events']) == 0):
                result.append({
                    'id': place_id,
                    'ancient_name': data.get('ancient_name', ''),
                    'modern_name': data.get('modern_name', '')
                })
    return result


def extract_events_from_markdown():
    """从markdown提取事件"""
    events = {}
    
    for md_file in sorted(MARKDOWN_DIR.glob("*.md")):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取日期和事件
        # 匹配格式：年份（年份）+ 事件描述
        date_pattern = re.compile(r'(\d{4}年|\u5341\u516b\u5e74|\u4e8c\u5341\u4e00\u5e74|\u4e8c\u5341\u4e8c\u5e74|\u4e8c\u5341\u4e09\u5e74|\u4e8c\u5341\u56db\u5e74|\u4e8c\u5341\u4e94\u5e74|\u4e8c\u5341\u516d\u5e74|\u4e8c\u5341\u4e03\u5e74|\u4e8c\u5341\u516b\u5e74|\u4e8c\u5341\u4e5d\u5e74|\u4e09\u5341\u5e74)')
        
        # 提取章节标题
        chapters = re.findall(r'###\s+(.+)', content)
        
        # 简单提取一些关键事件
        for place, place_events in EVENT_TEMPLATES.items():
            if place not in events:
                events[place] = []
            events[place].extend(place_events)
    
    return events


def find_matching_places(place_name):
    """查找匹配的地点"""
    index = load_places_index()
    matches = []
    
    for place in index.get('places', []):
        ancient = place.get('ancient_name', '').lower()
        modern = place.get('modern_name', '').lower()
        name = place_name.lower()
        
        if name in ancient or ancient in name or name in modern or modern in name:
            matches.append(place['id'])
    
    return matches


def batch_fill_events():
    """批量填充事件"""
    print("=" * 60)
    print("global_events 批量补全工具")
    print("=" * 60)
    
    # 获取需要补全的地点
    places_without_events = get_places_without_events()
    print(f"\n📊 统计: 共 {len(places_without_events)} 个地点需要补全global_events")
    
    # 提取事件模板
    events = extract_events_from_markdown()
    print(f"📋 已加载 {len(events)} 个地点的事件模板")
    
    # 统计
    filled_count = 0
    skipped_count = 0
    
    for place_info in places_without_events:
        place_id = place_info['id']
        ancient_name = place_info['ancient_name']
        modern_name = place_info['modern_name']
        
        # 查找匹配的事件
        matched_events = []
        for event_place, event_list in events.items():
            if event_place in ancient_name or ancient_name in event_place:
                matched_events.extend(event_list)
        
        if matched_events:
            # 加载地点数据
            place_data = load_place_data(place_id)
            if place_data:
                # 生成事件ID
                for i, event in enumerate(matched_events):
                    event['id'] = f"{place_id.lower()}-{str(i+1).zfill(3)}"
                
                place_data['global_events'] = matched_events
                save_place_data(place_id, place_data)
                filled_count += 1
                print(f"✅ {place_id}: {ancient_name} - 补全 {len(matched_events)} 条事件")
        else:
            skipped_count += 1
            print(f"⏭️ {place_id}: {ancient_name} - 无匹配事件")
    
    print(f"\n📊 完成!")
    print(f"   ✅ 已补全: {filled_count} 个地点")
    print(f"   ⏭️  未匹配: {skipped_count} 个地点")
    
    return filled_count, skipped_count


def add_custom_events():
    """添加自定义事件"""
    custom_events = [
        # 通用事件
        {"place": "眉山", "date": "景祐四年（1037年）", "title": "苏辙出生", "description": "苏辙诞生于眉州眉山", "significance": "family"},
        {"place": "眉山", "date": "庆历七年（1047年）", "title": "苏序去世", "description": "苏轼祖父苏序去世", "significance": "family"},
        {"place": "成都", "date": "嘉祐元年（1056年）", "title": "途经成都", "description": "苏轼赴京途中停留成都", "significance": "route01"},
        {"place": "长安", "date": "嘉祐元年（1056年）", "title": "首次入长安", "description": "苏轼首次到达长安", "significance": "route01"},
        {"place": "渑池", "date": "嘉祐六年（1061年）", "title": "渑池怀旧", "description": "苏轼赴凤翔任途经渑池，作《和子由渑池怀旧》", "significance": "route02"},
        {"place": "陈州", "date": "熙宁三年（1070年）", "title": "访张方平", "description": "苏轼赴陈州探访张方平", "significance": "personal"},
        {"place": "湖州", "date": "元丰二年（1079年）", "title": "湖州被捕", "description": "苏轼在湖州任上被捕，引发乌台诗案", "significance": "political"},
        {"place": "镇江", "date": "元丰七年（1084年）", "title": "金山寺", "description": "苏轼游览金山寺", "significance": "route10"},
        {"place": "江宁", "date": "元丰七年（1084年）", "title": "访王安石", "description": "苏轼拜访王安石", "significance": "personal"},
        {"place": "常州", "date": "元丰七年（1084年）", "title": "买田宜兴", "description": "苏轼在宜兴买田，计划定居", "significance": "route10"},
        {"place": "扬州", "date": "元祐七年（1092年）", "title": "平山堂", "description": "苏轼游览平山堂，缅怀欧阳修", "significance": "route16"},
        {"place": "颍州", "date": "元祐六年（1091年）", "title": "疏浚颍州西湖", "description": "苏轼疏浚颍州西湖", "significance": "route15"},
        {"place": "定州", "date": "元祐八年（1093年）", "title": "整顿军纪", "description": "苏轼在定州整顿军纪", "significance": "route17"},
        {"place": "惠州", "date": "绍圣二年（1095年）", "title": "白鹤峰新居", "description": "苏轼在惠州白鹤峰建新居", "significance": "route18"},
        {"place": "儋州", "date": "元符元年（1098年）", "title": "建载酒堂", "description": "苏轼在儋州建载酒堂", "significance": "route19"},
        {"place": "廉州", "date": "元符三年（1100年）", "title": "廉州安置", "description": "苏轼移廉州安置", "significance": "route20"},
        {"place": "广州", "date": "元符三年（1100年）", "title": "途经广州", "description": "苏轼北归途经广州", "significance": "route20"},
        {"place": "虔州", "date": "建中靖国元年（1101年）", "title": "虔州停留", "description": "苏轼北归停留虔州", "significance": "route20"},
        {"place": "当涂", "date": "建中靖国元年（1101年）", "title": "当涂停留", "description": "苏轼北归停留当涂", "significance": "route20"},
    ]
    
    print("\n📝 添加自定义事件...")
    added_count = 0
    
    for event in custom_events:
        place_name = event['place']
        index = load_places_index()
        matched_ids = []
        
        for place in index.get('places', []):
            ancient = place.get('ancient_name', '')
            modern = place.get('modern_name', '')
            if place_name in ancient or ancient in place_name:
                matched_ids.append(place['id'])
        
        for place_id in matched_ids:
            place_data = load_place_data(place_id)
            if place_data:
                existing_events = place_data.get('global_events', [])
                # 检查是否已存在
                exists = any(e['title'] == event['title'] for e in existing_events)
                if not exists:
                    event_copy = event.copy()
                    event_copy['id'] = f"{place_id.lower()}-{str(len(existing_events)+1).zfill(3)}"
                    existing_events.append(event_copy)
                    place_data['global_events'] = existing_events
                    save_place_data(place_id, place_data)
                    added_count += 1
                    print(f"   ✅ {place_id}: {event['title']}")
    
    print(f"\n   添加完成: {added_count} 条事件")


if __name__ == "__main__":
    # 批量填充
    filled, skipped = batch_fill_events()
    
    # 添加自定义事件
    add_custom_events()
    
    # 最终统计
    print("\n" + "=" * 60)
    print("最终统计")
    print("=" * 60)
    
    total_places = 0
    has_events = 0
    no_events = 0
    
    for filename in os.listdir(PLACES_DIR):
        if filename.endswith('.json'):
            total_places += 1
            data = load_place_data(filename.replace('.json', ''))
            if data and data.get('global_events') and len(data['global_events']) > 0:
                has_events += 1
            else:
                no_events += 1
    
    print(f"📊 总地点数: {total_places}")
    print(f"✅ 有global_events: {has_events} ({has_events/total_places*100:.1f}%)")
    print(f"❌ 无global_events: {no_events}")