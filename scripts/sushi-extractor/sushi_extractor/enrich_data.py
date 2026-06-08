#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

# 城市基础信息
city_info = {
    '杭州': {
        'province': '浙江省',
        'foods': ['西湖醋鱼', '东坡肉', '龙井虾仁', '叫化鸡', '片儿川'],
        'su_foods': ['东坡肉', '东坡羹'],
        'works': ['饮湖上初晴后雨', '六月二十七日望湖楼醉书', '浣溪沙·游蕲水清泉寺', '定风波'],
        'quote': '欲把西湖比西子，淡妆浓抹总相宜'
    },
    '惠州': {
        'province': '广东省',
        'foods': ['梅菜扣肉', '酿豆腐', '盐焗鸡', '东江菜'],
        'su_foods': ['东坡羹', '荔枝'],
        'works': ['食荔枝', '蝶恋花·春景'],
        'quote': '日啖荔枝三百颗，不辞长作岭南人'
    },
    '儋州': {
        'province': '海南省',
        'foods': ['儋州米烂', '长坡米烂', '红鱼粽', '椰子鸡'],
        'su_foods': ['东坡羹'],
        'works': ['儋耳', '纵笔'],
        'quote': '我本儋耳民，寄生西蜀州'
    },
    '常州': {
        'province': '江苏省',
        'foods': ['大麻糕', '银丝面', '加蟹小笼包', '天目湖砂锅鱼头'],
        'su_foods': [],
        'works': [],
        'quote': ''
    },
    '凤翔': {
        'province': '陕西省',
        'foods': ['西凤酒', '腊驴肉', '臊子面', '豆花泡馍'],
        'su_foods': [],
        'works': ['喜雨亭记', '凌虚台记', '凤翔八观'],
        'quote': ''
    },
    '宝鸡市': {
        'province': '陕西省',
        'foods': ['西凤酒', '腊驴肉', '臊子面', '豆花泡馍'],
        'su_foods': [],
        'works': ['喜雨亭记', '凌虚台记', '凤翔八观'],
        'quote': ''
    },
    '常州市': {
        'province': '江苏省',
        'foods': ['大麻糕', '银丝面', '加蟹小笼包', '天目湖砂锅鱼头'],
        'su_foods': [],
        'works': [],
        'quote': ''
    }
}

# 具体地点信息
location_details = {
    # 杭州
    '西湖': {
        'address': '浙江省杭州市西湖区西湖风景名胜区',
        'works': ['饮湖上初晴后雨', '六月二十七日望湖楼醉书'],
        'note': '苏轼多次游览西湖，留下众多名篇'
    },
    '孤山': {
        'address': '浙江省杭州市西湖区孤山路',
        'works': [],
        'note': '苏轼曾在孤山隐居，与林逋梅花为伴'
    },
    '蘇堤': {
        'address': '浙江省杭州市西湖区苏堤',
        'works': [],
        'note': '苏轼任杭州知州时主持修建'
    },
    '白堤': {
        'address': '浙江省杭州市西湖区白堤',
        'works': [],
        'note': '白居易所筑，苏轼有诗提及'
    },
    '靈隱寺': {
        'address': '浙江省杭州市西湖区灵隐路法云弄1号',
        'works': [],
        'note': '苏轼曾游览并题诗'
    },
    '淨慈寺': {
        'address': '浙江省杭州市西湖区南山路56号',
        'works': ['南屏晚钟'],
        'note': '苏轼曾到此游览'
    },
    # 惠州
    '朝雲墓': {
        'address': '广东省惠州市惠城区惠州西湖景区内',
        'works': ['悼朝云'],
        'note': '苏轼侍妾王朝云葬于此'
    },
    '豐湖': {
        'address': '广东省惠州市惠城区惠州西湖',
        'works': [],
        'note': '苏轼常游之地'
    },
    '東江': {
        'address': '广东省惠州市',
        'works': [],
        'note': '苏轼曾泛舟东江'
    },
    # 儋州
    '桄榔庵': {
        'address': '海南省儋州市中和镇',
        'works': ['桄榔庵铭'],
        'note': '苏轼在儋州的居所'
    },
    '載酒堂': {
        'address': '海南省儋州市中和镇东坡书院内',
        'works': [],
        'note': '苏轼讲学处'
    },
    '東坡書院': {
        'address': '海南省儋州市中和镇东坡书院',
        'works': [],
        'note': '纪念苏轼的书院'
    },
    # 常州
    '藤花旧馆': {
        'address': '江苏省常州市天宁区青果巷',
        'works': [],
        'note': '苏轼终老之地，病逝于此'
    },
    '舣舟亭': {
        'address': '江苏省常州市天宁区东坡公园内',
        'works': [],
        'note': '纪念苏轼泊舟处'
    },
    '东坡公园': {
        'address': '江苏省常州市天宁区延陵中路',
        'works': [],
        'note': '纪念苏轼的主题公园'
    },
    '奔牛镇': {
        'address': '江苏省常州市新北区奔牛镇',
        'works': [],
        'note': '苏轼北归时途经此地'
    },
    # 凤翔
    '东湖': {
        'address': '陕西省宝鸡市凤翔区东湖路',
        'works': ['凤翔八观'],
        'note': '苏轼主持修建，原名饮凤池'
    },
    '喜雨亭': {
        'address': '陕西省宝鸡市凤翔区东湖内',
        'works': ['喜雨亭记'],
        'note': '苏轼建亭并作记'
    },
    '凌虚台': {
        'address': '陕西省宝鸡市凤翔区东湖内',
        'works': ['凌虚台记'],
        'note': '苏轼作《凌虚台记》'
    },
    '苏公祠': {
        'address': '陕西省宝鸡市凤翔区东湖内',
        'works': [],
        'note': '纪念苏轼的祠堂'
    },
    '大像寺': {
        'address': '陕西省宝鸡市凤翔区',
        'works': [],
        'note': '苏轼曾游览'
    },
    '秦穆公墓': {
        'address': '陕西省宝鸡市凤翔区',
        'works': ['凤翔八观·秦穆公墓'],
        'note': '苏轼《凤翔八观》之一'
    },
    '九成宫醴泉铭碑': {
        'address': '陕西省宝鸡市麟游县',
        'works': ['凤翔八观·九成宫'],
        'note': '苏轼《凤翔八观》之一'
    },
    '钓鱼台': {
        'address': '陕西省宝鸡市陈仓区磻溪镇',
        'works': [],
        'note': '苏轼出巡时曾到此'
    }
}

def enrich_locations():
    output_dir = "extracted_locations"
    all_path = os.path.join(output_dir, "all_locations.json")
    
    # 读取所有地点数据
    with open(all_path, 'r', encoding='utf-8') as f:
        locations = json.load(f)
    
    enriched_count = 0
    
    for loc in locations:
        location_name = loc.get('location_name', '')
        city = loc.get('city', '')
        
        # 获取城市基础信息
        if city in city_info:
            info = city_info[city]
            
            # 补充美食（如果为空）
            if not loc.get('local_foods') or len(loc['local_foods']) == 0:
                loc['local_foods'] = info['foods']
                enriched_count += 1
            
            if not loc.get('su_foods') or len(loc['su_foods']) == 0:
                loc['su_foods'] = info['su_foods']
                enriched_count += 1
        
        # 获取地点详细信息
        if location_name in location_details:
            details = location_details[location_name]
            
            # 补充地址
            if not loc.get('modern_address') or len(loc['modern_address']) < 10:
                loc['modern_address'] = details['address']
                enriched_count += 1
            
            # 补充作品（如果为空）
            if not loc.get('su_works') or len(loc['su_works']) == 0:
                loc['su_works'] = details['works']
                enriched_count += 1
            
            # 补充作者笔记（如果为空）
            if not loc.get('author_note') or len(loc['author_note']) < 10:
                loc['author_note'] = details['note']
                enriched_count += 1
        
        # 修复城市名称统一问题
        if city == '宝鸡市':
            loc['city'] = '凤翔'
            loc['district'] = ''
        if city == '常州市':
            loc['city'] = '常州'
    
    # 保存更新后的数据
    with open(all_path, 'w', encoding='utf-8') as f:
        json.dump(locations, f, ensure_ascii=False, indent=2)
    
    # 同步更新各城市文件
    city_files = {
        '杭州': '杭州_locations.json',
        '惠州': '惠州_locations.json',
        '儋州': '儋州_locations.json',
        '常州': '常州_locations.json',
        '凤翔': '凤翔_locations.json'
    }
    
    for city, filename in city_files.items():
        city_locs = [loc for loc in locations if loc.get('city') == city]
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            json.dump(city_locs, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 数据补充完成！")
    print(f"   共补充 {enriched_count} 项信息")
    
    # 输出补充摘要
    print("\n📋 补充摘要:")
    for city in ['杭州', '惠州', '儋州', '常州', '凤翔']:
        city_locs = [loc for loc in locations if loc.get('city') == city]
        print(f"\n📍 {city} ({len(city_locs)}个地点):")
        for loc in city_locs:
            has_work = '✓' if loc.get('su_works') and len(loc['su_works']) > 0 else '✗'
            has_food = '✓' if loc.get('local_foods') and len(loc['local_foods']) > 0 else '✗'
            has_note = '✓' if loc.get('author_note') and len(loc['author_note']) > 0 else '✗'
            print(f"   {loc['location_name']}: 作品{has_work} 美食{has_food} 笔记{has_note}")

if __name__ == "__main__":
    enrich_locations()
