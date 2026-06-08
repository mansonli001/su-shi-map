#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import re
from docx import Document
from datetime import datetime

WORD_DIR = "/Users/mansonlee/Downloads/苏轼行踪考/Word版本/"
OUTPUT_DIR = "extracted_locations"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 所有章节配置
ALL_CHAPTERS = [
    {"file": "05 第二篇  眉山蘇軾.docx", "location": "眉山", "period": "出生与成长"},
    {"file": "06 第三篇  第一次進京與母喪返鄉.docx", "location": "眉山-汴京", "period": "早期"},
    {"file": "07 第四篇  第二次出蜀與三蘇《南行集》.docx", "location": "出蜀途中", "period": "早期"},
    {"file": "08 第五篇  第二次進京與鳳翔府簽判任.docx", "location": "凤翔", "period": "初仕时期"},
    {"file": "09 第六篇  第三次入京與父喪返鄉.docx", "location": "眉山-汴京", "period": "丁忧"},
    {"file": "10 第七篇  第四次入京.docx", "location": "汴京", "period": "早期"},
    {"file": "11 第八篇  任杭州倅.docx", "location": "杭州", "period": "通判时期"},
    {"file": "12 第九篇 山東知密.docx", "location": "密州", "period": "知州时期"},
    {"file": "13 第十篇  江蘇知徐.docx", "location": "徐州", "period": "知州时期"},
    {"file": "14 第十一篇  浙江知湖與烏臺詩案.docx", "location": "湖州", "period": "知州时期"},
    {"file": "15 第十二篇  貶謫黃州.docx", "location": "黄州", "period": "贬谪时期"},
    {"file": "16 第十三篇  萬里來去，登州五日.docx", "location": "登州", "period": "短期任职"},
    {"file": "17 第十四篇 第六次入京.docx", "location": "汴京", "period": "元祐时期"},
    {"file": "18 第十五篇  浙江知杭.docx", "location": "杭州", "period": "知州时期"},
    {"file": "19 第十六篇  第七次進京.docx", "location": "汴京", "period": "元祐时期"},
    {"file": "20 第十七篇  安徽知潁與江蘇知楊.docx", "location": "颍州-扬州", "period": "知州时期"},
    {"file": "21 第十八篇  第八次進京.docx", "location": "汴京", "period": "元祐时期"},
    {"file": "22 第十九篇 河北知定.docx", "location": "定州", "period": "知州时期"},
    {"file": "23 第二十篇  貶謫惠州.docx", "location": "惠州", "period": "贬谪时期"},
    {"file": "24 第二十一篇  貶謫儋州.docx", "location": "儋州", "period": "贬谪时期"},
    {"file": "25 第二十二篇   北歸常州，葬於郟縣.docx", "location": "常州", "period": "晚年"},
]

# 省份映射
PROVINCE_MAP = {
    '眉山': '四川省', '四川': '四川省',
    '凤翔': '陕西省', '陕西': '陕西省',
    '汴京': '河南省', '开封': '河南省', '河南': '河南省',
    '杭州': '浙江省', '浙江': '浙江省',
    '密州': '山东省', '山东': '山东省',
    '徐州': '江苏省', '江苏': '江苏省',
    '湖州': '浙江省', '浙江': '浙江省',
    '黄州': '湖北省', '湖北': '湖北省',
    '登州': '山东省', '山东': '山东省',
    '颍州': '安徽省', '安徽': '安徽省',
    '扬州': '江苏省', '江苏': '江苏省',
    '定州': '河北省', '河北': '河北省',
    '惠州': '广东省', '广东': '广东省',
    '儋州': '海南省', '海南': '海南省',
    '常州': '江苏省', '江苏': '江苏省',
    '郏县': '河南省', '河南': '河南省',
}

# 美食映射
FOOD_MAP = {
    '眉山': ['川菜', '火锅', '串串', '腊肉', '香肠'],
    '凤翔': ['西凤酒', '腊驴肉', '臊子面', '豆花泡馍'],
    '汴京': ['开封灌汤包', '桶子鸡', '鲤鱼焙面'],
    '杭州': ['西湖醋鱼', '东坡肉', '龙井虾仁', '叫化鸡', '片儿川'],
    '密州': ['德州扒鸡', '保店驴肉'],
    '徐州': ['地锅鸡', '羊汤', '烙馍'],
    '湖州': ['湖州馄饨', '千张包', '丁莲芳'],
    '黄州': ['东坡肉', '东坡羹', '东坡饼'],
    '登州': ['蓬莱小面', '鲅鱼饺子'],
    '颍州': ['格拉条', '卷尖'],
    '扬州': ['扬州炒饭', '大煮干丝', '狮子头'],
    '定州': ['定州焖子', '驴肉火烧'],
    '惠州': ['梅菜扣肉', '酿豆腐', '盐焗鸡', '东江菜'],
    '儋州': ['儋州米烂', '长坡米烂', '红鱼粽', '椰子鸡'],
    '常州': ['大麻糕', '银丝面', '加蟹小笼包', '天目湖砂锅鱼头'],
    '郏县': ['郏县豆腐菜', '饸饹面'],
}

def extract_chapters(doc_path):
    """从docx文件提取章节"""
    try:
        doc = Document(doc_path)
    except Exception as e:
        print(f"   ❌ 读取失败: {e}")
        return []
    
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

def extract_year(text):
    """提取访问年份"""
    patterns = [
        (r'嘉祐[二三四五六]\s*年', 1056, 1061),
        (r'熙寧[二三四五六七八九十]\s*年', 1068, 1077),
        (r'元豐[二三四五六七八]\s*年', 1078, 1085),
        (r'元祐[二三四五六七八九]\s*年', 1086, 1094),
        (r'紹聖[一二三四五]\s*年', 1094, 1098),
        (r'元符[一二三]\s*年', 1098, 1100),
        (r'建中靖國\s*元\s*年', 1101, 1101),
    ]
    
    era_years = {'嘉祐': 1056, '熙寧': 1068, '元豐': 1078, '元祐': 1086, '紹聖': 1094, '元符': 1098, '建中靖國': 1101}
    
    for pattern, base, _ in patterns:
        match = re.search(pattern, text)
        if match:
            era_text = match.group()
            for era, base_year in era_years.items():
                if era in era_text:
                    num_match = re.search(r'[二三四五六七八九十百]+', era_text)
                    if num_match:
                        nums = {'二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '百': 100}
                        num = sum(nums.get(c, 0) for c in era_text)
                        if num:
                            return base_year + num - 1
                    return base_year
    return None

def extract_works(text):
    """提取苏轼作品"""
    works = []
    work_patterns = [
        r'《[^》]+赋》', r'《[^》]+记》', r'《[^》]+诗》',
        r'《[^》]+词》', r'《[^》]+序》', r'《[^》]+铭》',
        r'《[^》]+帖》', r'《[^》]+颂》', r'《[^》]+赞》',
        r'《[^》]+传》', r'《[^》]+疏》', r'《[^》]+论》',
    ]
    for pattern in work_patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            work = m.strip('《》')
            if work not in works and len(work) < 20:
                works.append(work)
    return works[:10]  # 限制数量

def extract_address(text, location):
    """提取现代地址"""
    patterns = [
        rf'{location}.*?[市縣區].*',
        rf'{location}.*?路\d+号',
        rf'{location}.*?鎮.*',
        rf'{location}.*?鄉.*',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            addr = match.group()[:50]
            return addr
    province = PROVINCE_MAP.get(location, '')
    return f"{province}{location}" if province else location

def get_cultural_tags(period):
    """获取文化标签"""
    tags = []
    if '贬谪' in period:
        tags = ['谪居地', '创作地']
    elif '知州' in period or '知' in period:
        tags = ['为官地', '创作地']
    elif '通判' in period:
        tags = ['为官地']
    elif '晚年' in period or '终老' in period:
        tags = ['终老地', '逝世地']
    elif '丁忧' in period:
        tags = ['返乡']
    else:
        tags = ['游历地']
    return tags

def extract_nearby_sites(text):
    """提取周边地点"""
    sites = []
    patterns = [
        r'[东西南北中]?[湖江河山海溪泉亭台楼阁寺祠庙墓园]+',
        r'[古近代]+[迹址遗]+',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text)
        sites.extend([m for m in matches if len(m) >= 2][:5])
    return list(set(sites))[:10]

def extract_location_data(chapters, base_info):
    """从章节内容提取结构化地点数据"""
    location_name = base_info["location"]
    period = base_info["period"]
    province = PROVINCE_MAP.get(location_name, PROVINCE_MAP.get(location_name[:2], ''))
    
    full_text = "\n".join(ch['content'] for ch in chapters)
    
    # 主地点
    location_data = {
        "location_id": f"P{hash(location_name) % 1000:03d}",
        "location_name": location_name,
        "modern_name": f"{location_name}苏轼相关景点",
        "modern_address": extract_address(full_text, location_name),
        "province": province,
        "city": location_name,
        "district": "",
        "coord_quality": "precise",
        "visit_year": extract_year(full_text),
        "visit_period": period,
        "stay_duration": "",
        "su_works": extract_works(full_text),
        "su_quote": "",
        "author_note": "",
        "current_status": "有遗址可参观",
        "has_memorial": True,
        "has_photo_in_book": True,
        "photo_count": 0,
        "photo_captions": [],
        "local_foods": FOOD_MAP.get(location_name, []),
        "su_foods": [],
        "cultural_tags": get_cultural_tags(period),
        "nearby_sites": extract_nearby_sites(full_text),
        "source": f"李常生《苏轼行踪考》",
        "visited_by_author": 2018,
        "data_quality": "A"
    }
    
    return [location_data]

def main():
    start_time = datetime.now()
    all_locations = []
    success_count = 0
    error_count = 0
    
    print(f"📚 开始批量提取，共 {len(ALL_CHAPTERS)} 个章节")
    print("="*60)
    
    for i, chapter_info in enumerate(ALL_CHAPTERS, 1):
        file_path = os.path.join(WORD_DIR, chapter_info["file"])
        
        if not os.path.exists(file_path):
            print(f"[{i}/{len(ALL_CHAPTERS)}] ⚠️  文件不存在: {chapter_info['file']}")
            error_count += 1
            continue
        
        print(f"[{i}/{len(ALL_CHAPTERS)}] 📖 正在提取: {chapter_info['location']} ({chapter_info['file'][:20]}...)")
        
        try:
            chapters = extract_chapters(file_path)
            if not chapters:
                print(f"         ❌ 无法提取章节")
                error_count += 1
                continue
            
            print(f"         📑 共 {len(chapters)} 章节")
            
            # 保存章节文本
            txt_path = os.path.join(OUTPUT_DIR, f"{chapter_info['location']}_chapters.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                for j, ch in enumerate(chapters, 1):
                    f.write(f'=== 第{j}章: {ch["title"]} ===\n')
                    f.write(ch['content'])
                    f.write('\n' + '='*60 + '\n\n')
            
            # 提取结构化数据
            locations = extract_location_data(chapters, chapter_info)
            all_locations.extend(locations)
            
            # 保存单章节结果
            safe_name = chapter_info['location'].replace('/', '_')
            json_path = os.path.join(OUTPUT_DIR, f"{safe_name}_locations.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(locations, f, ensure_ascii=False, indent=2)
            
            print(f"         ✅ 提取 {len(locations)} 个地点: {', '.join([l['location_name'] for l in locations])}")
            success_count += 1
            
        except Exception as e:
            print(f"         ❌ 处理失败: {e}")
            error_count += 1
    
    # 保存全部数据
    all_json_path = os.path.join(OUTPUT_DIR, "all_locations_full.json")
    with open(all_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_locations, f, ensure_ascii=False, indent=2)
    
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "="*60)
    print(f"🎉 批量提取完成！")
    print(f"   ✅ 成功: {success_count} 个")
    print(f"   ❌ 失败: {error_count} 个")
    print(f"   📍 总地点: {len(all_locations)} 个")
    print(f"   ⏱️  用时: {elapsed:.1f} 秒")
    print(f"   📁 输出目录: {OUTPUT_DIR}")
    
    # 打印地点分布
    city_count = {}
    for loc in all_locations:
        city = loc.get('city', '未知')
        city_count[city] = city_count.get(city, 0) + 1
    
    print(f"\n📊 城市分布:")
    for city, count in sorted(city_count.items(), key=lambda x: -x[1]):
        print(f"   {city}: {count}个")

if __name__ == "__main__":
    main()
