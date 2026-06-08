#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为所有现有地点补充字段（文旅、作品、美食等）
只完善现有地点的字段，不新增地点
"""
import json
import os
import re

# 城市基础信息库 - 从书中提取+通用补充
CITY_DATA = {
    # 四川
    '眉山': {
        'province': '四川省', 'foods': ['川菜', '火锅', '串串', '腊肉', '东坡肉'],
        'works': [], 'tags': ['故乡', '出生地'],
        'note': '苏轼故乡，嘉祐元年（1056）随父苏洵、弟苏辙进京应试前在此成长'
    },
    '青神': {
        'province': '四川省', 'foods': ['川菜', '泡菜', '腊肉'], 
        'works': [], 'tags': ['游历地'],
        'note': '苏轼青年时期曾游历青神'
    },
    '成都': {
        'province': '四川省', 'foods': ['川菜', '火锅', '麻婆豆腐', '夫妻肺片'],
        'works': [], 'tags': ['为官地', '游历地'],
        'note': '嘉祐元年随父入京途经，后多次往返蜀道'
    },
    '绵阳': {
        'province': '四川省', 'foods': ['绵阳米粉', '梓州片粉'],
        'works': [], 'tags': ['游历地'],
        'note': '出蜀途中经过'
    },
    '剑阁': {
        'province': '四川省', 'foods': ['剑门豆腐', '核桃饼'],
        'works': [], 'tags': ['游历地'],
        'note': '蜀道要隘，苏轼多次途经'
    },
    '汉中': {
        'province': '陕西省', 'foods': ['汉中面皮', '菜豆腐'],
        'works': [], 'tags': ['游历地'],
        'note': '蜀道途中经过'
    },
    # 陕西
    '凤翔': {
        'province': '陕西省', 'foods': ['西凤酒', '腊驴肉', '臊子面', '豆花泡馍'],
        'works': ['喜雨亭记', '凌虚台记', '凤翔八观'],
        'tags': ['为官地', '创作地'],
        'note': '嘉祐六年（1061）任凤翔府签判，建喜雨亭、凌虚台，修东湖'
    },
    '长安': {
        'province': '陕西省', 'foods': ['肉夹馍', '羊肉泡馍', '凉皮'],
        'works': [], 'tags': ['游历地'],
        'note': '多次往返京城途中经过'
    },
    '华阴': {
        'province': '陕西省', 'foods': ['华山菜', '擀面皮'],
        'works': [], 'tags': ['游历地'],
        'note': '华山所在地，苏轼有诗记游'
    },
    '潼关': {
        'province': '陕西省', 'foods': ['潼关肉夹馍', '鸭片汤'],
        'works': [], 'tags': ['游历地'],
        'note': '出陕入豫要道'
    },
    # 河南
    '开封': {
        'province': '河南省', 'foods': ['开封灌汤包', '桶子鸡', '鲤鱼焙面', '花生糕'],
        'works': [], 'tags': ['为官地', '京城'],
        'note': '北宋京城，苏轼多次在此任职、应试'
    },
    '郑州': {
        'province': '河南省', 'foods': ['烩面', '胡辣汤'],
        'works': [], 'tags': ['游历地'],
        'note': '往返京城途中经过'
    },
    # 浙江
    '杭州': {
        'province': '浙江省', 'foods': ['西湖醋鱼', '东坡肉', '龙井虾仁', '叫化鸡', '片儿川'],
        'works': ['饮湖上初晴后雨', '六月二十七日望湖楼醉书', '定风波'],
        'tags': ['为官地', '创作地'],
        'note': '熙宁四年（1071）任杭州通判，元祐四年（1089）任知州'
    },
    '舟山': {
        'province': '浙江省', 'foods': ['海鲜', '舟山带鱼', '嵊泗贻贝'],
        'works': [], 'tags': ['游历地'],
        'note': '海上航行经过'
    },
    '富阳': {
        'province': '浙江省', 'foods': ['富春江鱼', '东坞山豆腐皮'],
        'works': [], 'tags': ['游历地'],
        'note': '富春江畔，苏轼多次往返'
    },
    '桐庐': {
        'province': '浙江省', 'foods': ['桐庐板栗', '富春江鲜'],
        'works': [], 'tags': ['游历地'],
        'note': '严子陵钓台所在地，苏轼有诗'
    },
    # 江苏
    '徐州': {
        'province': '江苏省', 'foods': ['地锅鸡', '羊汤', '烙馍', '彭城鱼丸'],
        'works': [], 'tags': ['为官地', '创作地'],
        'note': '熙宁十年（1077）知徐州，抗洪保城'
    },
    '扬州': {
        'province': '江苏省', 'foods': ['扬州炒饭', '大煮干丝', '狮子头'],
        'works': [], 'tags': ['为官地'],
        'note': '元祐七年（1092）知扬州'
    },
    '常州': {
        'province': '江苏省', 'foods': ['大麻糕', '银丝面', '加蟹小笼包', '天目湖砂锅鱼头'],
        'works': [], 'tags': ['终老地', '逝世地'],
        'note': '建中靖国元年（1101）北归，病逝于常州藤花旧馆'
    },
    '镇江': {
        'province': '江苏省', 'foods': ['锅盖面', '蟹黄汤包'],
        'works': [], 'tags': ['游历地'],
        'note': '金山寺所在地，苏轼多次游览'
    },
    # 山东
    '密州': {
        'province': '山东省', 'foods': ['德州扒鸡', '保店驴肉', '大柳面'],
        'works': ['江城子·密州出猎', '水调歌头·明月几时有'],
        'tags': ['为官地', '创作地'],
        'note': '熙宁七年（1074）知密州，留下《密州出猎》等名篇'
    },
    '登州': {
        'province': '山东省', 'foods': ['蓬莱小面', '鲅鱼饺子'],
        'works': [], 'tags': ['为官地'],
        'note': '元丰八年（1085）任登州知州，仅五日'
    },
    '潍坊': {
        'province': '山东省', 'foods': ['潍坊朝天锅', '和乐'],
        'works': [], 'tags': ['游历地'],
        'note': '往返山东途中经过'
    },
    # 安徽
    '泗州': {
        'province': '安徽省', 'foods': ['符离集烧鸡', '宿州sa汤'],
        'works': [], 'tags': ['游历地'],
        'note': '淮河要冲，苏轼有诗'
    },
    '阜阳': {
        'province': '安徽省', 'foods': ['格拉条', '卷尖', '太和板面'],
        'works': [], 'tags': ['为官地'],
        'note': '元祐六年（1091）知颍州'
    },
    # 河北
    '定州': {
        'province': '河北省', 'foods': ['定州焖子', '驴肉火烧'],
        'works': [], 'tags': ['为官地', '创作地'],
        'note': '绍圣元年（1094）知定州，修复雪浪石'
    },
    # 湖北
    '黄州': {
        'province': '湖北省', 'foods': ['东坡肉', '东坡羹', '东坡饼', '黄州豆腐'],
        'works': ['念奴娇·赤壁怀古', '赤壁赋', '前赤壁赋', '后赤壁赋', '定风波'],
        'tags': ['贬谪地', '创作地'],
        'note': '元丰三年（1080）贬黄州，创作《赤壁赋》《念奴娇》等'
    },
    '武昌': {
        'province': '湖北省', 'foods': ['热干面', '鸭脖'],
        'works': [], 'tags': ['游历地'],
        'note': '黄州附近，苏轼曾到'
    },
    # 广东
    '惠州': {
        'province': '广东省', 'foods': ['梅菜扣肉', '酿豆腐', '盐焗鸡', '东江菜'],
        'works': ['食荔枝', '蝶恋花·春景'],
        'tags': ['贬谪地', '创作地'],
        'note': '绍圣元年（1094）贬惠州，留下"日啖荔枝三百颗"名句'
    },
    '广州': {
        'province': '广东省', 'foods': ['粤菜', '早茶', '肠粉', '烧鹅'],
        'works': [], 'tags': ['游历地'],
        'note': '岭南重镇，苏轼曾过境'
    },
    # 海南
    '儋州': {
        'province': '海南省', 'foods': ['儋州米烂', '长坡米烂', '红鱼粽', '椰子鸡'],
        'works': ['桄榔庵铭', '儋耳', '纵笔'],
        'tags': ['贬谪地', '创作地'],
        'note': '绍圣四年（1097）贬儋州，建桄榔庵、载酒堂'
    },
    '昌化': {
        'province': '海南省', 'foods': ['海鲜', '椰子'],
        'works': [], 'tags': ['贬谪地'],
        'note': '儋州相邻，苏轼曾被贬至此'
    },
    # 江西
    '九江': {
        'province': '江西省', 'foods': ['九江茶饼', '庐山石鸡'],
        'works': [], 'tags': ['游历地'],
        'note': '庐山所在地，苏轼多次游览'
    },
    '鄱阳': {
        'province': '江西省', 'foods': ['鄱阳湖银鱼', '藜蒿炒腊肉'],
        'works': [], 'tags': ['游历地'],
        'note': '往返黄州途中经过'
    },
}

def extract_city_from_name(name):
    """从地点名称提取城市名"""
    # 常见城市名
    cities = ['眉山', '青神', '成都', '绵阳', '剑阁', '汉中', '凤翔', '长安', 
              '华阴', '潼关', '开封', '郑州', '杭州', '舟山', '富阳', '桐庐',
              '徐州', '扬州', '常州', '镇江', '密州', '登州', '潍坊', '泗州',
              '阜阳', '定州', '黄州', '武昌', '惠州', '广州', '儋州', '昌化',
              '九江', '鄱阳', '湖州', '金陵', '镇江', '真州', '泗州', '苏州']
    for city in cities:
        if city in name:
            return city
    return None

def supplement_existing():
    existing_path = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data/places-core.json'
    output_dir = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data'
    
    with open(existing_path, 'r', encoding='utf-8') as f:
        existing_places = json.load(f)
    
    supplemented = 0
    matched_city = 0
    generic = 0
    
    for place in existing_places:
        song_name = place.get('songName', '')
        city = extract_city_from_name(song_name)
        
        # 添加新字段
        place['su_works'] = []
        place['su_quote'] = ''
        place['author_note'] = ''
        place['local_foods'] = []
        place['cultural_tags'] = []
        
        if city and city in CITY_DATA:
            data = CITY_DATA[city]
            if data['foods']:
                place['local_foods'] = data['foods']
            if data['works']:
                place['su_works'] = data['works']
            if data['note']:
                place['author_note'] = data['note']
            if data['tags']:
                place['cultural_tags'] = data['tags']
            supplemented += 1
            matched_city += 1
        else:
            # 尝试匹配modernName
            modern = place.get('modernName', '')
            city2 = extract_city_from_name(modern)
            if city2 and city2 in CITY_DATA:
                data = CITY_DATA[city2]
                if data['foods']:
                    place['local_foods'] = data['foods']
                if data['works']:
                    place['su_works'] = data['works']
                if data['note']:
                    place['author_note'] = data['note']
                if data['tags']:
                    place['cultural_tags'] = data['tags']
                supplemented += 1
                matched_city += 1
            else:
                # 通用美食标签
                province = place.get('modernName', '')[:2]
                generic_foods = {
                    '四川': ['川菜', '火锅'],
                    '陕西': ['面食', '羊肉泡馍'],
                    '河南': ['烩面', '胡辣汤'],
                    '浙江': ['浙菜', '杭帮菜'],
                    '江苏': ['淮扬菜'],
                    '山东': ['鲁菜'],
                    '广东': ['粤菜', '早茶'],
                    '海南': ['海鲜', '椰子'],
                    '湖北': ['鄂菜'],
                    '安徽': ['徽菜'],
                    '河北': ['冀菜'],
                    '江西': ['赣菜'],
                }
                if province in generic_foods:
                    place['local_foods'] = generic_foods[province]
                    place['cultural_tags'] = ['游历地']
                generic += 1
    
    # 保存补充后的数据
    output_path = os.path.join(output_dir, 'places-core-supplemented.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(existing_places, f, ensure_ascii=False, indent=2)
    
    print("="*60)
    print("✅ 地点数据补充完成")
    print("="*60)
    print(f"总地点数: {len(existing_places)}")
    print(f"成功补充: {supplemented} 个")
    print(f"  - 城市匹配: {matched_city} 个")
    print(f"  - 通用补充: {generic} 个")
    print(f"\n输出文件: {output_path}")
    
    # 统计
    foods_count = sum(1 for p in existing_places if p.get('local_foods'))
    works_count = sum(1 for p in existing_places if p.get('su_works'))
    note_count = sum(1 for p in existing_places if p.get('author_note'))
    
    print(f"\n📊 字段完整率:")
    print(f"  美食: {foods_count}/{len(existing_places)} ({(foods_count/len(existing_places))*100:.1f}%)")
    print(f"  作品: {works_count}/{len(existing_places)} ({(works_count/len(existing_places))*100:.1f}%)")
    print(f"  笔记: {note_count}/{len(existing_places)} ({(note_count/len(existing_places))*100:.1f}%)")
    
    return existing_places

if __name__ == "__main__":
    supplement_existing()
