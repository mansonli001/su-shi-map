#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

# 更新常州数据，添加子地点
def update_changzhou_locations():
    output_dir = "extracted_locations"
    input_path = os.path.join(output_dir, "常州_locations.json")
    all_path = os.path.join(output_dir, "all_locations.json")
    
    # 读取现有数据
    with open(input_path, 'r', encoding='utf-8') as f:
        locations = json.load(f)
    
    # 常州主地点信息增强
    if locations:
        locations[0].update({
            "location_name": "常州",
            "modern_name": "常州东坡文化景区",
            "modern_address": "江苏省常州市天宁区",
            "coord_quality": "precise",
            "visit_year": 1101,
            "visit_period": "晚年",
            "stay_duration": "约2个月",
            "su_works": [],
            "su_quote": "",
            "author_note": "苏轼终老之地，病逝于常州孙氏公馆（藤花旧馆）",
            "current_status": "有纪念建筑",
            "has_memorial": True,
            "has_photo_in_book": True,
            "photo_count": 2,
            "photo_captions": ["藤花旧馆", "舣舟亭"],
            "local_foods": ["大麻糕", "银丝面", "加蟹小笼包", "天目湖砂锅鱼头"],
            "su_foods": [],
            "cultural_tags": ["终老地", "逝世地"],
            "nearby_sites": ["藤花旧馆", "舣舟亭", "东坡公园", "奔牛镇"],
            "data_quality": "A"
        })
    
    # 添加子地点
    sub_locations = [
        {
            "location_id": "P076-01",
            "location_name": "藤花旧馆",
            "modern_name": "藤花旧馆（苏轼终老处）",
            "modern_address": "江苏省常州市天宁区青果巷",
            "province": "江苏省",
            "city": "常州市",
            "district": "天宁区",
            "coord_quality": "precise",
            "visit_year": 1101,
            "stay_duration": "约1个月",
            "su_works": [],
            "su_quote": "",
            "author_note": "苏轼病逝于此，时年六十六岁",
            "current_status": "有纪念建筑",
            "has_memorial": True,
            "has_photo_in_book": True,
            "cultural_tags": ["终老地", "纪念地"],
            "source": "李常生《苏轼行踪考》第二十二篇",
            "data_quality": "A"
        },
        {
            "location_id": "P076-02",
            "location_name": "舣舟亭",
            "modern_name": "舣舟亭",
            "modern_address": "江苏省常州市天宁区东坡公园内",
            "province": "江苏省",
            "city": "常州市",
            "district": "天宁区",
            "coord_quality": "precise",
            "visit_year": 1101,
            "su_works": [],
            "current_status": "有遗址可参观",
            "has_memorial": True,
            "has_photo_in_book": True,
            "cultural_tags": ["纪念地", "古迹"],
            "source": "李常生《苏轼行踪考》第二十二篇",
            "data_quality": "A"
        },
        {
            "location_id": "P076-03",
            "location_name": "东坡公园",
            "modern_name": "东坡公园",
            "modern_address": "江苏省常州市天宁区延陵中路",
            "province": "江苏省",
            "city": "常州市",
            "district": "天宁区",
            "coord_quality": "precise",
            "visit_year": 1101,
            "su_works": [],
            "current_status": "有纪念建筑",
            "has_memorial": True,
            "has_photo_in_book": True,
            "cultural_tags": ["纪念地", "公园"],
            "source": "李常生《苏轼行踪考》第二十二篇",
            "data_quality": "A"
        },
        {
            "location_id": "P076-04",
            "location_name": "奔牛镇",
            "modern_name": "奔牛古镇",
            "modern_address": "江苏省常州市新北区奔牛镇",
            "province": "江苏省",
            "city": "常州市",
            "district": "新北区",
            "coord_quality": "district",
            "visit_year": 1101,
            "su_works": [],
            "current_status": "历史古镇",
            "has_memorial": False,
            "has_photo_in_book": True,
            "cultural_tags": ["途经地"],
            "source": "李常生《苏轼行踪考》第二十二篇",
            "data_quality": "B"
        }
    ]
    
    # 添加子地点到列表
    locations.extend(sub_locations)
    
    # 保存更新后的常州数据
    with open(input_path, 'w', encoding='utf-8') as f:
        json.dump(locations, f, ensure_ascii=False, indent=2)
    
    # 更新 all_locations.json
    with open(all_path, 'r', encoding='utf-8') as f:
        all_locations = json.load(f)
    
    # 移除旧的常州数据
    all_locations = [loc for loc in all_locations if loc.get('city') != '常州']
    # 添加更新后的常州数据
    all_locations.extend(locations)
    
    with open(all_path, 'w', encoding='utf-8') as f:
        json.dump(all_locations, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 常州数据更新完成！")
    print(f"   共 {len(locations)} 个地点")
    print("\n📍 更新内容:")
    for loc in locations:
        print(f"   - {loc['location_name']} ({loc['modern_name']}) [{loc['data_quality']}]")

if __name__ == "__main__":
    update_changzhou_locations()
