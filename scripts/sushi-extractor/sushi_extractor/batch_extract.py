#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import re
from docx import Document

# 核心章节配置
CORE_CHAPTERS = [
    {"file": "11 第八篇  任杭州倅.docx", "location": "杭州", "period": "通判时期"},
    {"file": "18 第十五篇  浙江知杭.docx", "location": "杭州", "period": "知州时期"},
    {"file": "23 第二十篇  貶謫惠州.docx", "location": "惠州", "period": "贬谪时期"},
    {"file": "24 第二十一篇  貶謫儋州.docx", "location": "儋州", "period": "贬谪时期"},
    {"file": "25 第二十二篇   北歸常州，葬於郟縣.docx", "location": "常州", "period": "晚年"},
    {"file": "08 第五篇  第二次進京與鳳翔府簽判任.docx", "location": "凤翔", "period": "初仕时期"},
]

WORD_DIR = "/Users/mansonlee/Downloads/苏轼行踪考/Word版本/"
OUTPUT_DIR = "extracted_locations"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 通用提取函数
def extract_chapters(doc_path):
    """从docx文件提取章节"""
    doc = Document(doc_path)
    chapters = []
    current = {'title': '前言', 'content': ''}
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        
        if '第' in text and ('章' in text or '篇' in text):
            if current['content']:
                chapters.append(current)
            current = {'title': text, 'content': text + '\n'}
        else:
            current['content'] += text + '\n'
    
    if current['content']:
        chapters.append(current)
    
    return chapters

def extract_location_data(chapters, base_info):
    """从章节内容提取结构化地点数据"""
    location_name = base_info["location"]
    period = base_info["period"]
    
    locations = []
    full_text = "\n".join(ch['content'] for ch in chapters)
    
    # 基础地点信息
    location_data = {
        "location_id": f"P{len(locations):03d}",
        "location_name": location_name,
        "modern_name": f"{location_name}苏轼相关景点",
        "modern_address": "",
        "province": "",
        "city": location_name,
        "district": "",
        "coord_quality": "precise",
        "visit_year": extract_year(full_text),
        "visit_period": period,
        "stay_duration": extract_duration(full_text),
        "su_works": extract_works(full_text),
        "su_quote": extract_quote(full_text),
        "author_note": extract_author_note(full_text),
        "current_status": "有遗址可参观",
        "has_memorial": True,
        "has_photo_in_book": True,
        "photo_count": 0,
        "photo_captions": [],
        "local_foods": extract_local_foods(location_name),
        "su_foods": extract_su_foods(location_name),
        "cultural_tags": get_cultural_tags(period),
        "nearby_sites": extract_nearby_sites(full_text),
        "source": f"李常生《苏轼行踪考》",
        "visited_by_author": 2018,
        "data_quality": "A"
    }
    
    # 设置省份
    location_data["province"] = get_province(location_name)
    
    # 从文本提取现代地址
    location_data["modern_address"] = extract_address(full_text, location_name)
    
    locations.append(location_data)
    
    # 提取子地点
    sub_locations = extract_sub_locations(chapters, location_name)
    locations.extend(sub_locations)
    
    return locations

def extract_year(text):
    """提取访问年份"""
    year_pattern = r'(元豐|元祐|熙寧|嘉祐|紹聖|元符|建中靖國)\s*(\d+年?|元年|二年|三年|四年|五年|六年|七年|八年|九年|十年)'
    match = re.search(year_pattern, text)
    if match:
        era_map = {'元豐': 1078, '元祐': 1086, '熙寧': 1068, '嘉祐': 1056, '紹聖': 1094, '元符': 1098, '建中靖國': 1101}
        era = match.group(1)
        year_part = match.group(2)
        base_year = era_map.get(era, 1080)
        if year_part == '元年':
            return base_year
        num_match = re.search(r'(\d+)', year_part)
        if num_match:
            return base_year + int(num_match.group(1)) - 1
    return None

def extract_duration(text):
    """提取停留时长"""
    duration_patterns = [
        r'(\d+)\s*年有餘',
        r'(\d+)\s*年餘',
        r'(\d+)\s*年',
        r'數年',
        r'數月',
        r'數十日'
    ]
    for pattern in duration_patterns:
        match = re.search(pattern, text)
        if match:
            if match.group(1):
                return f"{match.group(1)}年"
            return pattern.replace(r'(\d+)\s*', '')
    return ""

def extract_works(text):
    """提取苏轼作品"""
    works = []
    work_patterns = [
        r'《赤壁賦》|《前赤壁賦》|《後赤壁賦》',
        r'《念奴嬌》|《念奴嬌·赤壁懷古》',
        r'《定風波》',
        r'《寒食帖》|《黄州寒食帖》',
        r'《水調歌頭》',
        r'《飲湖上初晴後雨》',
        r'《六月二十七日望湖樓醉書》',
        r'《東坡》',
        r'《江城子》',
        r'《浣溪沙》',
        r'《臨江仙》',
        r'《滿庭芳》',
    ]
    for pattern in work_patterns:
        match = re.search(pattern, text)
        if match:
            work = match.group()
            if work not in works:
                works.append(work.strip('《》'))
    return works

def extract_quote(text):
    """提取名言"""
    quotes = [
        '大江東去，浪淘盡，千古風流人物',
        '一蓑煙雨任平生',
        '也無風雨也無晴',
        '惟江上之清風，與山間之明月',
        '欲把西湖比西子，淡妝濃抹總相宜',
        '不識廬山真面目，只緣身在此山中',
        '明月幾時有，把酒問青天',
    ]
    for quote in quotes:
        if quote in text:
            return quote
    return ""

def extract_author_note(text):
    """提取作者考察笔记"""
    notes = []
    if '現地勘查' in text:
        notes.append('作者实地勘查')
    if '訪問' in text:
        notes.append('访问当地人士')
    if '文獻' in text:
        notes.append('文献考证')
    return "; ".join(notes)

def extract_local_foods(location):
    """提取当地特色美食"""
    food_map = {
        '杭州': ['西湖醋鱼', '东坡肉', '龙井虾仁', '叫化鸡', '片儿川'],
        '惠州': ['梅菜扣肉', '酿豆腐', '盐焗鸡', '东江菜'],
        '儋州': ['儋州米烂', '长坡米烂', '红鱼粽', '椰子鸡'],
        '常州': ['大麻糕', '银丝面', '加蟹小笼包', '天目湖砂锅鱼头'],
        '凤翔': ['西凤酒', '腊驴肉', '臊子面', '豆花泡馍'],
    }
    return food_map.get(location, [])

def extract_su_foods(location):
    """提取苏轼相关美食"""
    su_foods_map = {
        '杭州': ['东坡肉', '东坡羹'],
        '黄州': ['东坡肉', '东坡羹', '东坡饼'],
        '惠州': ['东坡羹', '荔枝'],
        '儋州': ['东坡羹'],
    }
    return su_foods_map.get(location, [])

def get_cultural_tags(period):
    """获取文化标签"""
    if '贬谪' in period:
        return ['谪居地', '创作地']
    elif '知州' in period or '签判' in period:
        return ['为官地', '创作地']
    elif '晚年' in period:
        return ['终老地']
    return ['游历地', '创作地']

def extract_nearby_sites(text):
    """提取周边地点"""
    site_patterns = [
        '定惠院|臨皋亭|雪堂|東坡',
        '西湖|孤山|蘇堤|白堤',
        '豐樂亭|醉翁亭',
        '白雲樓|朝雲墓',
        '桄榔庵|載酒堂',
    ]
    sites = []
    for pattern in site_patterns:
        match = re.search(pattern, text)
        if match:
            sites.append(match.group())
    return list(set(sites))

def get_province(city):
    """获取省份"""
    province_map = {
        '杭州': '浙江省',
        '惠州': '广东省',
        '儋州': '海南省',
        '常州': '江苏省',
        '凤翔': '陕西省',
        '黄州': '湖北省',
    }
    return province_map.get(city, "")

def extract_address(text, city):
    """提取现代地址"""
    addr_patterns = [
        rf'{city}[市區縣].*?路\d+號',
        rf'{city}.*?景區',
        rf'{city}.*?公園',
        rf'{city}.*?寺',
        rf'{city}.*?廟',
    ]
    for pattern in addr_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()
    return f"{get_province(city)}{city}市"

def extract_sub_locations(chapters, main_location):
    """提取子地点"""
    sub_locations = []
    location_keywords = {
        '杭州': ['西湖', '孤山', '蘇堤', '白堤', '靈隱寺', '淨慈寺'],
        '惠州': ['白雲樓', '朝雲墓', '豐湖', '東江'],
        '儋州': ['桄榔庵', '載酒堂', '東坡書院'],
        '常州': ['東坡公園', '舣舟亭'],
        '凤翔': ['东湖', '苏公祠'],
    }
    
    keywords = location_keywords.get(main_location, [])
    full_text = "\n".join(ch['content'] for ch in chapters)
    
    for keyword in keywords:
        if keyword in full_text:
            sub_loc = {
                "location_id": f"P000-{keyword}",
                "location_name": keyword,
                "modern_name": f"{keyword}",
                "modern_address": f"{get_province(main_location)}{main_location}市",
                "province": get_province(main_location),
                "city": main_location,
                "coord_quality": "district",
                "visit_year": None,
                "stay_duration": "",
                "su_works": [],
                "su_quote": "",
                "author_note": "",
                "current_status": "有遗址可参观" if '寺' in keyword or '樓' in keyword else "遗址已不存",
                "has_memorial": True,
                "has_photo_in_book": True,
                "cultural_tags": ["关联地点"],
                "source": "李常生《苏轼行踪考》",
                "data_quality": "B"
            }
            sub_locations.append(sub_loc)
    
    return sub_locations

# 主函数
def main():
    all_locations = []
    
    for chapter_info in CORE_CHAPTERS:
        file_path = os.path.join(WORD_DIR, chapter_info["file"])
        if not os.path.exists(file_path):
            print(f"⚠️  文件不存在: {file_path}")
            continue
        
        print(f"📖 正在提取: {chapter_info['file']}")
        chapters = extract_chapters(file_path)
        print(f"   共 {len(chapters)} 章节")
        
        # 保存章节文本
        txt_path = os.path.join(OUTPUT_DIR, f"{chapter_info['location']}_chapters.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            for i, ch in enumerate(chapters, 1):
                f.write(f'=== 第{i}章: {ch["title"]} ===\n')
                f.write(ch['content'])
                f.write('\n' + '='*60 + '\n\n')
        
        # 提取结构化数据
        locations = extract_location_data(chapters, chapter_info)
        all_locations.extend(locations)
        
        # 保存单章节结果
        json_path = os.path.join(OUTPUT_DIR, f"{chapter_info['location']}_locations.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(locations, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ 提取 {len(locations)} 个地点\n")
    
    # 保存全部数据
    all_json_path = os.path.join(OUTPUT_DIR, "all_locations.json")
    with open(all_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_locations, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 批量提取完成！共 {len(all_locations)} 个地点")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    
    # 打印摘要
    print("\n=== 提取摘要 ===")
    for loc in all_locations:
        print(f"📍 {loc['location_name']} - {loc['modern_name']}")
        print(f"   坐标质量: {loc['coord_quality']} | 数据质量: {loc['data_quality']}")
        print(f"   作品: {', '.join(loc['su_works']) if loc['su_works'] else '无'}")
        print()

if __name__ == "__main__":
    main()
