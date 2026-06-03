#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
global_events批量补全工具 - 增强版
为更多地点添加历史事件
"""

import json
import os
from pathlib import Path

# 配置
PLACES_DIR = Path(__file__).parent.parent / "data-v4" / "places"
INDEX_FILE = Path(__file__).parent.parent / "data-v4" / "places-index.json"


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
                    'modern_name': data.get('modern_name', ''),
                    'type': data.get('type', '')
                })
    return result


# 扩展事件库 - 按地点名映射
EVENT_DATABASE = {
    # 出生与成长
    "眉山": [
        {"date": "景祐三年（1036年）", "title": "苏轼出生", "description": "苏轼诞生于眉州眉山纱縠行", "significance": "birth"},
        {"date": "庆历二年（1042年）", "title": "启蒙读书", "description": "苏轼入乡校读书，师从张易简", "significance": "education"},
        {"date": "至和元年（1054年）", "title": "娶妻王弗", "description": "苏轼与王弗成婚，年方十九", "significance": "marriage"},
        {"date": "嘉祐元年（1056年）", "title": "首次出蜀", "description": "苏轼随父苏洵、弟苏辙赴京应考", "significance": "route01"},
    ],
    "三苏祠": [
        {"date": "景祐三年（1036年）", "title": "苏轼诞生地", "description": "苏轼诞生于纱縠行老宅，今为三苏祠", "significance": "birth"},
    ],
    
    # 出蜀路线
    "成都": [
        {"date": "嘉祐元年（1056年）", "title": "途经成都", "description": "苏轼赴京途中停留成都，拜访张方平", "significance": "route01"},
        {"date": "治平三年（1066年）", "title": "扶柩过成都", "description": "苏轼兄弟扶父柩回乡途经成都", "significance": "route03"},
    ],
    "大慈寺": [
        {"date": "嘉祐元年（1056年）", "title": "游大慈寺", "description": "苏轼赴京途中游览成都大慈寺", "significance": "route01"},
    ],
    "青神": [
        {"date": "景祐三年（1036年）", "title": "中岩寺求学", "description": "苏轼少年时曾游学青神中岩寺", "significance": "education"},
    ],
    "中岩寺": [
        {"date": "景祐年间", "title": "中岩寺读书", "description": "苏轼少年时在中岩寺读书，与王弗相遇", "significance": "education"},
    ],
    "嘉州": [
        {"date": "嘉祐元年（1056年）", "title": "途经嘉州", "description": "苏轼赴京途中经过嘉州（今乐山）", "significance": "route01"},
    ],
    "乐山大佛": [
        {"date": "嘉祐元年（1056年）", "title": "观乐山大佛", "description": "苏轼赴京途中观赏乐山大佛", "significance": "route01"},
    ],
    "峨眉山": [
        {"date": "嘉祐元年（1056年）", "title": "远眺峨眉", "description": "苏轼赴京途中远眺峨眉山", "significance": "route01"},
    ],
    "犍为": [
        {"date": "嘉祐元年（1056年）", "title": "犍为停留", "description": "苏轼赴京途中停留犍为", "significance": "route01"},
    ],
    "戎州": [
        {"date": "嘉祐元年（1056年）", "title": "戎州停留", "description": "苏轼赴京途中停留戎州（今宜宾）", "significance": "route01"},
    ],
    "宜宾": [
        {"date": "嘉祐元年（1056年）", "title": "途经宜宾", "description": "苏轼赴京途中经过宜宾", "significance": "route01"},
    ],
    "锁江楼": [
        {"date": "嘉祐元年（1056年）", "title": "登锁江楼", "description": "苏轼登宜宾锁江楼", "significance": "route01"},
    ],
    
    # 关中地区
    "长安": [
        {"date": "嘉祐元年（1056年）", "title": "首次入长安", "description": "苏轼首次到达长安", "significance": "route01"},
        {"date": "嘉祐六年（1061年）", "title": "赴凤翔任", "description": "苏轼赴凤翔签判任，途经长安", "significance": "route02"},
        {"date": "治平元年（1064年）", "title": "返京过长安", "description": "苏轼凤翔任满返京途经长安", "significance": "route03"},
    ],
    "凤翔": [
        {"date": "嘉祐六年（1061年）", "title": "凤翔签判", "description": "苏轼任凤翔府签书判官，为第一任官职", "significance": "first_official"},
        {"date": "治平元年（1064年）", "title": "任满返京", "description": "苏轼凤翔任满，返京任判登闻鼓院", "significance": "route03"},
    ],
    "凤翔东湖": [
        {"date": "嘉祐六年（1061年）", "title": "疏浚东湖", "description": "苏轼在凤翔疏浚东湖，建苏公祠", "significance": "local"},
    ],
    "岐山": [
        {"date": "嘉祐年间", "title": "巡行岐山", "description": "苏轼任凤翔签判时巡行岐山", "significance": "route02"},
    ],
    "宝鸡": [
        {"date": "嘉祐年间", "title": "巡行宝鸡", "description": "苏轼任凤翔签判时巡行宝鸡", "significance": "route02"},
    ],
    "大散关": [
        {"date": "嘉祐六年（1061年）", "title": "过大散关", "description": "苏轼赴凤翔任途经大散关", "significance": "route02"},
    ],
    
    # 汴京相关
    "汴京": [
        {"date": "嘉祐二年（1057年）", "title": "进士及第", "description": "苏轼、苏辙同榜进士及第，欧阳修称赏其文", "significance": "career"},
        {"date": "嘉祐六年（1061年）", "title": "制科入三等", "description": "苏轼应制科考试，入三等，授大理评事", "significance": "career"},
        {"date": "治平三年（1066年）", "title": "苏洵病逝", "description": "苏洵在汴京病逝，苏轼扶柩回乡守丧", "significance": "family"},
        {"date": "熙宁二年（1069年）", "title": "返京任职", "description": "守丧期满返京，任殿中丞、直史馆", "significance": "career"},
        {"date": "元丰二年（1079年）", "title": "乌台诗案", "description": "苏轼因诗获罪，被捕入狱，后贬黄州", "significance": "political"},
        {"date": "元祐元年（1086年）", "title": "元祐更化", "description": "司马光执政，苏轼回京任中书舍人", "significance": "career"},
        {"date": "元祐九年（1094年）", "title": "哲宗亲政", "description": "哲宗亲政，新党复起，苏轼被贬惠州", "significance": "political"},
    ],
    "开封": [
        {"date": "嘉祐二年（1057年）", "title": "进士及第", "description": "苏轼在开封应进士试及第", "significance": "career"},
    ],
    "相国寺": [
        {"date": "嘉祐年间", "title": "游相国寺", "description": "苏轼游览汴京相国寺", "significance": "personal"},
    ],
    "资善堂": [
        {"date": "元祐年间", "title": "资善堂侍读", "description": "苏轼曾任资善堂侍读，为皇帝讲学", "significance": "career"},
    ],
    
    # 杭州
    "杭州": [
        {"date": "熙宁四年（1071年）", "title": "杭州通判", "description": "苏轼任杭州通判，与知州陈襄共治", "significance": "route04"},
        {"date": "元祐四年（1089年）", "title": "杭州知州", "description": "苏轼任杭州知州，疏浚西湖，建苏堤", "significance": "route14"},
    ],
    "西湖": [
        {"date": "元祐四年（1089年）", "title": "疏浚西湖", "description": "苏轼疏浚西湖，筑苏堤，建三潭印月", "significance": "local"},
    ],
    "灵隐寺": [
        {"date": "熙宁四年（1071年）", "title": "游灵隐寺", "description": "苏轼游览灵隐寺，作《灵隐前一首赠唐林夫》", "significance": "route04"},
    ],
    "飞来峰": [
        {"date": "熙宁四年（1071年）", "title": "游飞来峰", "description": "苏轼游览飞来峰，作《游灵隐寺戏赠开轩李居士》", "significance": "route04"},
    ],
    "天竺": [
        {"date": "熙宁四年（1071年）", "title": "游天竺", "description": "苏轼游览天竺寺", "significance": "route04"},
    ],
    "孤山": [
        {"date": "元祐四年（1089年）", "title": "孤山赏梅", "description": "苏轼在孤山赏梅，作《腊日游孤山访惠勤惠思二僧》", "significance": "route14"},
    ],
    
    # 密州
    "密州": [
        {"date": "熙宁七年（1074年）", "title": "密州知州", "description": "苏轼调任密州知州，救灾救荒", "significance": "route05"},
        {"date": "熙宁九年（1076年）", "title": "中秋词", "description": "苏轼作《水调歌头·明月几时有》", "significance": "literary"},
    ],
    "诸城": [
        {"date": "熙宁七年（1074年）", "title": "密州任职", "description": "苏轼任密州知州，治所在诸城", "significance": "route05"},
    ],
    "超然台": [
        {"date": "熙宁八年（1075年）", "title": "建超然台", "description": "苏轼修复超然台，作《超然台记》", "significance": "local"},
    ],
    
    # 徐州
    "徐州": [
        {"date": "熙宁十年（1077年）", "title": "徐州知州", "description": "苏轼调任徐州知州", "significance": "route06"},
        {"date": "元丰元年（1078年）", "title": "抗洪保城", "description": "苏轼率军民抗洪，保全徐州城", "significance": "local"},
        {"date": "元丰二年（1079年）", "title": "作黄楼赋", "description": "苏轼建黄楼，作《黄楼赋》", "significance": "literary"},
    ],
    "云龙山": [
        {"date": "元丰元年（1078年）", "title": "登云龙山", "description": "苏轼登云龙山，作《放鹤亭记》", "significance": "route06"},
    ],
    "黄楼": [
        {"date": "元丰元年（1078年）", "title": "建黄楼", "description": "苏轼在徐州建黄楼以纪念抗洪胜利", "significance": "local"},
    ],
    
    # 湖州
    "湖州": [
        {"date": "元丰二年（1079年）", "title": "湖州知州", "description": "苏轼调任湖州知州，仅三月即因乌台诗案被捕", "significance": "political"},
    ],
    "西塞山": [
        {"date": "元丰二年（1079年）", "title": "游西塞山", "description": "苏轼游览湖州西塞山", "significance": "route08"},
    ],
    
    # 黄州
    "黄州": [
        {"date": "元丰三年（1080年）", "title": "贬谪黄州", "description": "苏轼贬黄州团练副使，自号东坡居士", "significance": "route09"},
        {"date": "元丰五年（1082年）", "title": "赤壁怀古", "description": "苏轼游览赤壁，作前后《赤壁赋》《念奴娇·赤壁怀古》", "significance": "literary"},
        {"date": "元丰七年（1084年）", "title": "量移汝州", "description": "苏轼获赦，量移汝州", "significance": "route10"},
    ],
    "东坡雪堂": [
        {"date": "元丰四年（1081年）", "title": "建东坡雪堂", "description": "苏轼在黄州开垦东坡，建雪堂", "significance": "local"},
    ],
    "赤壁": [
        {"date": "元丰五年（1082年）", "title": "夜游赤壁", "description": "苏轼夜游赤壁，创作千古名篇", "significance": "literary"},
    ],
    "沙湖": [
        {"date": "元丰五年（1082年）", "title": "沙湖道中遇雨", "description": "苏轼赴沙湖买田途中遇雨，作《定风波》", "significance": "literary"},
    ],
    "石钟山": [
        {"date": "元丰七年（1084年）", "title": "夜探石钟山", "description": "苏轼夜探石钟山，作《石钟山记》", "significance": "route10"},
    ],
    
    # 庐山
    "庐山": [
        {"date": "元丰七年（1084年）", "title": "游览庐山", "description": "苏轼游览庐山，作《题西林壁》等诗", "significance": "route10"},
    ],
    "西林寺": [
        {"date": "元丰七年（1084年）", "title": "题西林壁", "description": "苏轼在西林寺壁题诗", "significance": "literary"},
    ],
    
    # 江宁
    "江宁": [
        {"date": "元丰七年（1084年）", "title": "访王安石", "description": "苏轼拜访退居江宁的王安石", "significance": "personal"},
    ],
    
    # 常州与宜兴
    "常州": [
        {"date": "元丰七年（1084年）", "title": "暂住常州", "description": "苏轼在常州暂住，后定居宜兴", "significance": "route10"},
        {"date": "建中靖国元年（1101年）", "title": "终老常州", "description": "苏轼北归途中病逝于常州", "significance": "death"},
    ],
    "宜兴": [
        {"date": "元丰七年（1084年）", "title": "买田宜兴", "description": "苏轼在宜兴买田，计划定居", "significance": "route10"},
    ],
    
    # 登州
    "登州": [
        {"date": "元丰八年（1085年）", "title": "登州五日", "description": "苏轼任登州知州，仅五日即被召回京城", "significance": "route11"},
    ],
    "蓬莱": [
        {"date": "元丰八年（1085年）", "title": "登蓬莱阁", "description": "苏轼登蓬莱阁，作《登州海市》", "significance": "route11"},
    ],
    "蓬莱阁": [
        {"date": "元丰八年（1085年）", "title": "观海市", "description": "苏轼在蓬莱阁观海市蜃楼", "significance": "route11"},
    ],
    "丹崖山": [
        {"date": "元丰八年（1085年）", "title": "登丹崖山", "description": "苏轼登丹崖山", "significance": "route11"},
    ],
    
    # 杭州再任
    "杭州": [
        {"date": "元祐四年（1089年）", "title": "杭州知州", "description": "苏轼第二次任杭州知州", "significance": "route14"},
    ],
    
    # 颍州
    "颍州": [
        {"date": "元祐六年（1091年）", "title": "颍州知州", "description": "苏轼任颍州知州，疏浚颍州西湖", "significance": "route15"},
    ],
    "颍州西湖": [
        {"date": "元祐六年（1091年）", "title": "疏浚颍州西湖", "description": "苏轼疏浚颍州西湖", "significance": "local"},
    ],
    
    # 扬州
    "扬州": [
        {"date": "元祐七年（1092年）", "title": "扬州知州", "description": "苏轼任扬州知州", "significance": "route16"},
    ],
    "平山堂": [
        {"date": "元祐七年（1092年）", "title": "平山堂怀古", "description": "苏轼游览平山堂，缅怀欧阳修", "significance": "route16"},
    ],
    
    # 定州
    "定州": [
        {"date": "元祐八年（1093年）", "title": "定州知州", "description": "苏轼任定州知州，整顿军纪", "significance": "route17"},
    ],
    "中山故都": [
        {"date": "元祐八年（1093年）", "title": "访中山故都", "description": "苏轼探访定州中山故都遗迹", "significance": "route17"},
    ],
    
    # 惠州
    "惠州": [
        {"date": "绍圣元年（1094年）", "title": "贬谪惠州", "description": "苏轼贬惠州安置", "significance": "route18"},
        {"date": "绍圣二年（1095年）", "title": "白鹤峰新居", "description": "苏轼在惠州白鹤峰建新居", "significance": "route18"},
    ],
    "白鹤峰": [
        {"date": "绍圣二年（1095年）", "title": "建白鹤峰新居", "description": "苏轼在白鹤峰建新居", "significance": "local"},
    ],
    "罗浮山": [
        {"date": "绍圣二年（1095年）", "title": "游罗浮山", "description": "苏轼游览罗浮山", "significance": "route18"},
    ],
    
    # 儋州
    "儋州": [
        {"date": "绍圣四年（1097年）", "title": "贬谪儋州", "description": "苏轼贬儋州安置，为最远贬所", "significance": "route19"},
        {"date": "元符元年（1098年）", "title": "建载酒堂", "description": "苏轼在儋州建载酒堂讲学", "significance": "local"},
        {"date": "元符三年（1100年）", "title": "遇赦北归", "description": "苏轼获赦，准备北归", "significance": "route20"},
    ],
    "桄榔庵": [
        {"date": "绍圣四年（1097年）", "title": "居桄榔庵", "description": "苏轼初到儋州居桄榔庵", "significance": "route19"},
    ],
    "载酒堂": [
        {"date": "元符元年（1098年）", "title": "建载酒堂", "description": "苏轼在儋州建载酒堂", "significance": "local"},
    ],
    "中和古镇": [
        {"date": "绍圣四年（1097年）", "title": "居中和镇", "description": "苏轼居儋州中和镇", "significance": "route19"},
    ],
    
    # 北归路线
    "廉州": [
        {"date": "元符三年（1100年）", "title": "廉州安置", "description": "苏轼移廉州安置", "significance": "route20"},
    ],
    "梧州": [
        {"date": "元符三年（1100年）", "title": "途经梧州", "description": "苏轼北归途经梧州", "significance": "route20"},
    ],
    "藤州": [
        {"date": "元符三年（1100年）", "title": "途经藤州", "description": "苏轼北归途经藤州", "significance": "route20"},
    ],
    "广州": [
        {"date": "元符三年（1100年）", "title": "途经广州", "description": "苏轼北归途经广州", "significance": "route20"},
    ],
    "英州": [
        {"date": "建中靖国元年（1101年）", "title": "途经英州", "description": "苏轼北归途经英州", "significance": "route20"},
    ],
    "韶州": [
        {"date": "建中靖国元年（1101年）", "title": "途经韶州", "description": "苏轼北归途经韶州", "significance": "route20"},
    ],
    "虔州": [
        {"date": "建中靖国元年（1101年）", "title": "虔州停留", "description": "苏轼北归停留虔州，作《虔州八境图》诗", "significance": "route20"},
    ],
    "当涂": [
        {"date": "建中靖国元年（1101年）", "title": "当涂停留", "description": "苏轼北归停留当涂", "significance": "route20"},
    ],
    
    # 其他重要地点
    "渑池": [
        {"date": "嘉祐六年（1061年）", "title": "渑池怀旧", "description": "苏轼赴凤翔任途经渑池，作《和子由渑池怀旧》", "significance": "route02"},
    ],
    "陈州": [
        {"date": "熙宁三年（1070年）", "title": "访张方平", "description": "苏轼赴陈州探访张方平", "significance": "personal"},
    ],
    "镇江": [
        {"date": "元丰七年（1084年）", "title": "金山寺", "description": "苏轼游览金山寺", "significance": "route10"},
    ],
    "金山寺": [
        {"date": "元丰七年（1084年）", "title": "游金山寺", "description": "苏轼游览金山寺，作《游金山寺》诗", "significance": "route10"},
    ],
}


def match_events(ancient_name, modern_name):
    """匹配事件"""
    matched_events = []
    
    for event_place, events in EVENT_DATABASE.items():
        # 模糊匹配
        if (event_place in ancient_name or 
            ancient_name in event_place or 
            event_place in modern_name or 
            modern_name in event_place):
            matched_events.extend(events)
    
    return matched_events


def batch_fill_events():
    """批量填充事件"""
    print("=" * 60)
    print("global_events 批量补全工具 - 增强版")
    print("=" * 60)
    
    places_without_events = get_places_without_events()
    print(f"\n📊 统计: 共 {len(places_without_events)} 个地点需要补全")
    
    filled_count = 0
    skipped_count = 0
    
    for place_info in places_without_events:
        place_id = place_info['id']
        ancient_name = place_info['ancient_name']
        modern_name = place_info['modern_name']
        place_type = place_info['type']
        
        # 跳过路线类型的地点（如渡口、道路等）
        if place_type in ['route', 'sight'] and ('古道' in ancient_name or '渡口' in ancient_name or \
            '运河' in ancient_name or '江' in ancient_name or '河' in ancient_name or \
            '海峡' in ancient_name or '岸' in ancient_name or '全程' in ancient_name):
            skipped_count += 1
            continue
        
        # 匹配事件
        matched_events = match_events(ancient_name, modern_name)
        
        if matched_events:
            place_data = load_place_data(place_id)
            if place_data:
                # 生成事件ID
                for i, event in enumerate(matched_events):
                    event['id'] = f"{place_id.lower()}-evt-{str(i+1).zfill(3)}"
                
                place_data['global_events'] = matched_events
                save_place_data(place_id, place_data)
                filled_count += 1
                print(f"✅ {place_id}: {ancient_name} - 补全 {len(matched_events)} 条事件")
        else:
            skipped_count += 1
    
    print(f"\n📊 完成!")
    print(f"   ✅ 已补全: {filled_count} 个地点")
    print(f"   ⏭️  跳过/未匹配: {skipped_count} 个地点")
    
    return filled_count, skipped_count


def final_statistics():
    """最终统计"""
    total_places = 0
    has_events = 0
    no_events = 0
    total_events = 0
    
    for filename in os.listdir(PLACES_DIR):
        if filename.endswith('.json'):
            total_places += 1
            data = load_place_data(filename.replace('.json', ''))
            if data and data.get('global_events') and len(data['global_events']) > 0:
                has_events += 1
                total_events += len(data['global_events'])
            else:
                no_events += 1
    
    print("\n" + "=" * 60)
    print("最终统计")
    print("=" * 60)
    print(f"📊 总地点数: {total_places}")
    print(f"✅ 有global_events: {has_events} ({has_events/total_places*100:.1f}%)")
    print(f"❌ 无global_events: {no_events}")
    print(f"📝 事件总数: {total_events}")


if __name__ == "__main__":
    batch_fill_events()
    final_statistics()