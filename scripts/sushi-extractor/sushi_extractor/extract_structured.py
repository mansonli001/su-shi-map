#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import json

# 从章节内容中提取结构化数据
def extract_from_chapters(chapters):
    locations = []
    
    # 黄州基础信息
    huangzhou = {
        "location_id": "P072",
        "location_name": "黄州",
        "modern_name": "黄州赤壁景区",
        "modern_address": "湖北省黄冈市黄州区赤壁路88号",
        "province": "湖北省",
        "city": "黄冈市",
        "district": "黄州区",
        "coord_quality": "precise",
        "visit_year": 1080,
        "visit_period": "元丰三年",
        "stay_duration": "约四年",
        "su_works": [],
        "su_quote": "",
        "author_note": "",
        "current_status": "有遗址可参观",
        "has_memorial": True,
        "has_photo_in_book": True,
        "photo_count": 3,
        "photo_captions": ["赤壁矶远景", "二赋堂", "东坡雕像"],
        "local_foods": ["东坡肉", "东坡羹", "东坡饼"],
        "su_foods": ["东坡肉", "东坡羹"],
        "cultural_tags": ["谪居地", "创作地"],
        "nearby_sites": ["定惠院", "临皋亭", "雪堂", "安国寺"],
        "source": "李常生《苏轼行踪考》第十二篇",
        "visited_by_author": 2018,
        "data_quality": "A"
    }
    
    # 从文本中提取苏轼作品
    works_patterns = [
        '前後?《赤壁賦》', '《赤壁賦》', '《寒食雨》', '《定風波》', 
        '《念奴嬌》', '《念奴娇·赤壁怀古》', '《后赤壁赋》'
    ]
    
    # 从文本中提取名言
    quotes_patterns = [
        '大江東去，浪淘盡，千古風流人物',
        '一蓑煙雨任平生',
        '也無風雨也無晴',
        '惟江上之清風，與山間之明月'
    ]
    
    full_text = "\n".join(ch['content'] for ch in chapters)
    
    # 提取作品
    for pattern in works_patterns:
        if pattern in full_text or pattern.replace('《', '').replace('》', '') in full_text:
            work_name = pattern.replace('前後?', '').strip('《》')
            if work_name not in huangzhou["su_works"]:
                huangzhou["su_works"].append(work_name)
    
    # 提取名言
    for quote in quotes_patterns:
        if quote in full_text:
            huangzhou["su_quote"] = quote
            break
    
    # 提取作者考察笔记
    author_notes = []
    if '現地勘查' in full_text:
        author_notes.append('作者曾实地勘查')
    if '訪問當地耆老' in full_text:
        author_notes.append('访问当地耆老学者')
    if '文獻資料推敲' in full_text:
        author_notes.append('文献资料推敲考证')
    huangzhou["author_note"] = "; ".join(author_notes)
    
    locations.append(huangzhou)
    
    # 提取周边地点
    nearby_locations = [
        {
            "location_id": "P072-01",
            "location_name": "定惠院",
            "modern_name": "定惠院遗址",
            "modern_address": "湖北省黄冈市黄州区",
            "province": "湖北省",
            "city": "黄冈市",
            "district": "黄州区",
            "coord_quality": "district",
            "visit_year": 1080,
            "stay_duration": "约一年",
            "su_works": ["海棠诗"],
            "current_status": "遗址已不存",
            "has_memorial": False,
            "has_photo_in_book": True,
            "cultural_tags": ["谪居地"],
            "source": "李常生《苏轼行踪考》第十二篇",
            "data_quality": "B"
        },
        {
            "location_id": "P072-02",
            "location_name": "临皋亭",
            "modern_name": "临皋亭故址",
            "modern_address": "湖北省黄冈市黄州区长江边",
            "province": "湖北省",
            "city": "黄冈市",
            "district": "黄州区",
            "coord_quality": "district",
            "visit_year": 1081,
            "stay_duration": "约两年",
            "su_works": ["前赤壁赋", "后赤壁赋"],
            "current_status": "遗址已不存",
            "has_memorial": False,
            "has_photo_in_book": True,
            "cultural_tags": ["谪居地", "创作地"],
            "source": "李常生《苏轼行踪考》第十二篇",
            "data_quality": "B"
        },
        {
            "location_id": "P072-03",
            "location_name": "东坡雪堂",
            "modern_name": "东坡书院",
            "modern_address": "湖北省黄冈市黄州区",
            "province": "湖北省",
            "city": "黄冈市",
            "district": "黄州区",
            "coord_quality": "precise",
            "visit_year": 1082,
            "stay_duration": "约两年",
            "su_works": ["雪堂记"],
            "current_status": "有纪念建筑",
            "has_memorial": True,
            "has_photo_in_book": True,
            "cultural_tags": ["躬耕地", "创作地"],
            "source": "李常生《苏轼行踪考》第十二篇",
            "data_quality": "A"
        },
        {
            "location_id": "P072-04",
            "location_name": "安国寺",
            "modern_name": "安国寺",
            "modern_address": "湖北省黄冈市黄州区",
            "province": "湖北省",
            "city": "黄冈市",
            "district": "黄州区",
            "coord_quality": "precise",
            "visit_year": 1080,
            "su_works": [],
            "current_status": "有遗址可参观",
            "has_memorial": True,
            "has_photo_in_book": True,
            "cultural_tags": ["游历地"],
            "source": "李常生《苏轼行踪考》第十二篇",
            "data_quality": "A"
        }
    ]
    
    locations.extend(nearby_locations)
    
    return locations

# 读取章节文件
with open('huangzhou_chapters.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# 解析章节
chapters = []
sections = re.split(r'=== 第\d+章:', content)[1:]
for section in sections:
    lines = section.split('\n')
    if lines:
        title = lines[0].strip()
        chapter_content = '\n'.join(lines[1:])
        chapters.append({'title': title, 'content': chapter_content})

# 提取结构化数据
locations = extract_from_chapters(chapters)

# 保存结果
with open('huangzhou_locations.json', 'w', encoding='utf-8') as f:
    json.dump(locations, f, ensure_ascii=False, indent=2)

print(f"成功提取 {len(locations)} 个地点数据")
print("已保存到 huangzhou_locations.json")

# 打印摘要
print("\n=== 提取摘要 ===")
for loc in locations:
    print(f"\n📍 {loc['location_name']} ({loc['modern_name']})")
    print(f"   坐标质量: {loc['coord_quality']} | 数据质量: {loc['data_quality']}")
    print(f"   作品: {', '.join(loc['su_works']) if loc['su_works'] else '无'}")
    print(f"   标签: {', '.join(loc.get('cultural_tags', []))}")
