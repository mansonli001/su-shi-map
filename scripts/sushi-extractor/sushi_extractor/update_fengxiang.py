#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

# 更新凤翔数据，添加子地点
def update_fengxiang_locations():
    output_dir = "extracted_locations"
    input_path = os.path.join(output_dir, "凤翔_locations.json")
    all_path = os.path.join(output_dir, "all_locations.json")
    
    # 读取现有数据
    with open(input_path, 'r', encoding='utf-8') as f:
        locations = json.load(f)
    
    # 凤翔主地点信息增强
    if locations:
        locations[0].update({
            "location_name": "凤翔",
            "modern_name": "凤翔苏轼文化景区",
            "modern_address": "陕西省宝鸡市凤翔区",
            "coord_quality": "precise",
            "visit_year": 1061,
            "visit_period": "初仕时期",
            "stay_duration": "约三年",
            "su_works": ["喜雨亭记", "凌虚台记", "凤翔八观"],
            "su_quote": "",
            "author_note": "苏轼初仕之地，任凤翔府签判，创作大量诗文",
            "current_status": "有遗址可参观",
            "has_memorial": True,
            "has_photo_in_book": True,
            "photo_count": 5,
            "photo_captions": ["东湖", "喜雨亭", "凌虚台", "苏公祠", "秦穆公墓"],
            "local_foods": ["西凤酒", "腊驴肉", "臊子面", "豆花泡馍"],
            "su_foods": [],
            "cultural_tags": ["为官地", "创作地"],
            "nearby_sites": ["东湖", "喜雨亭", "凌虚台", "苏公祠", "大像寺"],
            "data_quality": "A"
        })
    
    # 添加子地点
    sub_locations = [
        {
            "location_id": "P023-01",
            "location_name": "东湖",
            "modern_name": "凤翔东湖",
            "modern_address": "陕西省宝鸡市凤翔区东湖路",
            "province": "陕西省",
            "city": "宝鸡市",
            "district": "凤翔区",
            "coord_quality": "precise",
            "visit_year": 1061,
            "stay_duration": "三年",
            "su_works": ["凤翔八观"],
            "author_note": "苏轼主持修建，原名饮凤池",
            "current_status": "有遗址可参观",
            "has_memorial": True,
            "has_photo_in_book": True,
            "cultural_tags": ["创作地", "名胜"],
            "source": "李常生《苏轼行踪考》第五篇",
            "data_quality": "A"
        },
        {
            "location_id": "P023-02",
            "location_name": "喜雨亭",
            "modern_name": "喜雨亭",
            "modern_address": "陕西省宝鸡市凤翔区东湖内",
            "province": "陕西省",
            "city": "宝鸡市",
            "district": "凤翔区",
            "coord_quality": "precise",
            "visit_year": 1062,
            "su_works": ["喜雨亭记"],
            "author_note": "苏轼建亭并作记",
            "current_status": "有纪念建筑",
            "has_memorial": True,
            "has_photo_in_book": True,
            "cultural_tags": ["创作地", "古迹"],
            "source": "李常生《苏轼行踪考》第五篇",
            "data_quality": "A"
        },
        {
            "location_id": "P023-03",
            "location_name": "凌虚台",
            "modern_name": "凌虚台",
            "modern_address": "陕西省宝鸡市凤翔区东湖内",
            "province": "陕西省",
            "city": "宝鸡市",
            "district": "凤翔区",
            "coord_quality": "precise",
            "visit_year": 1062,
            "su_works": ["凌虚台记"],
            "author_note": "苏轼作《凌虚台记》",
            "current_status": "有纪念建筑",
            "has_memorial": True,
            "has_photo_in_book": True,
            "cultural_tags": ["创作地", "古迹"],
            "source": "李常生《苏轼行踪考》第五篇",
            "data_quality": "A"
        },
        {
            "location_id": "P023-04",
            "location_name": "苏公祠",
            "modern_name": "苏公祠",
            "modern_address": "陕西省宝鸡市凤翔区东湖内",
            "province": "陕西省",
            "city": "宝鸡市",
            "district": "凤翔区",
            "coord_quality": "precise",
            "visit_year": 1061,
            "su_works": [],
            "author_note": "纪念苏轼的祠堂",
            "current_status": "有纪念建筑",
            "has_memorial": True,
            "has_photo_in_book": True,
            "cultural_tags": ["纪念地"],
            "source": "李常生《苏轼行踪考》第五篇",
            "data_quality": "A"
        },
        {
            "location_id": "P023-05",
            "location_name": "大像寺",
            "modern_name": "大像寺",
            "modern_address": "陕西省宝鸡市凤翔区",
            "province": "陕西省",
            "city": "宝鸡市",
            "district": "凤翔区",
            "coord_quality": "district",
            "visit_year": 1062,
            "su_works": [],
            "author_note": "苏轼曾游览",
            "current_status": "有遗址可参观",
            "has_memorial": False,
            "has_photo_in_book": True,
            "cultural_tags": ["游历地"],
            "source": "李常生《苏轼行踪考》第五篇",
            "data_quality": "B"
        },
        {
            "location_id": "P023-06",
            "location_name": "秦穆公墓",
            "modern_name": "秦穆公墓",
            "modern_address": "陕西省宝鸡市凤翔区",
            "province": "陕西省",
            "city": "宝鸡市",
            "district": "凤翔区",
            "coord_quality": "precise",
            "visit_year": 1062,
            "su_works": ["凤翔八观·秦穆公墓"],
            "author_note": "苏轼《凤翔八观》之一",
            "current_status": "有遗址可参观",
            "has_memorial": False,
            "has_photo_in_book": True,
            "cultural_tags": ["游历地", "古迹"],
            "source": "李常生《苏轼行踪考》第五篇",
            "data_quality": "A"
        },
        {
            "location_id": "P023-07",
            "location_name": "九成宫醴泉铭碑",
            "modern_name": "九成宫醴泉铭碑",
            "modern_address": "陕西省宝鸡市麟游县",
            "province": "陕西省",
            "city": "宝鸡市",
            "district": "麟游县",
            "coord_quality": "precise",
            "visit_year": 1062,
            "su_works": ["凤翔八观·九成宫"],
            "author_note": "苏轼《凤翔八观》之一",
            "current_status": "有遗址可参观",
            "has_memorial": False,
            "has_photo_in_book": True,
            "cultural_tags": ["游历地", "古迹"],
            "source": "李常生《苏轼行踪考》第五篇",
            "data_quality": "A"
        },
        {
            "location_id": "P023-08",
            "location_name": "钓鱼台",
            "modern_name": "姜子牙钓鱼台",
            "modern_address": "陕西省宝鸡市陈仓区磻溪镇",
            "province": "陕西省",
            "city": "宝鸡市",
            "district": "陈仓区",
            "coord_quality": "precise",
            "visit_year": 1062,
            "su_works": [],
            "author_note": "苏轼出巡时曾到此",
            "current_status": "有遗址可参观",
            "has_memorial": False,
            "has_photo_in_book": True,
            "cultural_tags": ["游历地"],
            "source": "李常生《苏轼行踪考》第五篇",
            "data_quality": "B"
        }
    ]
    
    # 添加子地点到列表
    locations.extend(sub_locations)
    
    # 保存更新后的凤翔数据
    with open(input_path, 'w', encoding='utf-8') as f:
        json.dump(locations, f, ensure_ascii=False, indent=2)
    
    # 更新 all_locations.json
    with open(all_path, 'r', encoding='utf-8') as f:
        all_locations = json.load(f)
    
    # 移除旧的凤翔数据
    all_locations = [loc for loc in all_locations if loc.get('city') != '凤翔']
    # 添加更新后的凤翔数据
    all_locations.extend(locations)
    
    with open(all_path, 'w', encoding='utf-8') as f:
        json.dump(all_locations, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 凤翔数据更新完成！")
    print(f"   共 {len(locations)} 个地点")
    print("\n📍 更新内容:")
    for loc in locations:
        print(f"   - {loc['location_name']} ({loc['modern_name']}) [{loc['data_quality']}]")

if __name__ == "__main__":
    update_fengxiang_locations()
