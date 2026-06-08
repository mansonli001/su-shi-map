#!/usr/bin/env python3
"""
阶段3：5个居住/任职地补充美食数据
阶段4：87个无文旅数据的地点补充 memorial_sites
"""
import json, os

PLACES_DIR = 'data-v4/places'
PUBLIC_DIR = 'public/data-v4/places'

# ── 阶段3：美食补充 ──
FOOD_SUPPLEMENTS = {
    "P065": {  # 湖州
        "foods": [
            {"name": "湖州粽子", "description": "湖州名点，糯米裹粽叶蒸制，甜咸皆宜，苏轼知湖州时品此味"},
            {"name": "太湖银鱼", "description": "太湖特产银鱼，色白如银、鲜嫩爽滑，湖州宴席必备"},
            {"name": "千张包子", "description": "湖州传统小吃，千张皮裹肉馅蒸煮，汤鲜味美"},
        ]
    },
    "P074": {  # 惠州
        "foods": [
            {"name": "东坡荔枝", "description": "惠州荔枝名扬天下，苏轼'日啖荔枝三百颗，不辞长作岭南人'传诵千古"},
            {"name": "梅菜扣肉", "description": "惠州传统名菜，梅菜与五花肉同蒸，咸香软糯"},
            {"name": "惠州盐焗鸡", "description": "客家名菜，盐焗工艺使鸡肉鲜嫩多汁，惠州饮食代表"},
        ]
    },
    "P116": {  # 眉山
        "foods": [
            {"name": "东坡肉", "description": "眉山传统名菜，五花肉慢火红烧，肥而不腻、酥烂香醇，传为苏轼所创"},
            {"name": "眉山泡菜", "description": "四川泡菜代表，酸辣爽脆、开胃下饭，眉山家家必备"},
            {"name": "龙眼酥", "description": "眉山传统糕点，酥皮层次分明、馅心甜糯，形似龙眼"},
        ]
    },
    "P196": {  # 徐州黄楼
        "foods": [
            {"name": "徐州地锅鸡", "description": "徐州名菜，铁锅炖鸡贴饼，鸡肉鲜嫩、饼吸汤汁"},
            {"name": "把子肉", "description": "徐州传统肉食，五花肉捆扎卤制，肥瘦相间、入口即化"},
            {"name": "辣汤", "description": "徐州早餐名品，胡椒辣味浓郁、面筋鸡蛋花，暖胃驱寒"},
        ]
    },
    "P208": {  # 颍州
        "foods": [
            {"name": "阜阳格拉条", "description": "颍州传统面食，粗面条拌芝麻酱，筋道香浓"},
            {"name": "枕头馍", "description": "阜阳名点，大如枕头的蒸馍，外酥内软、麦香浓郁"},
            {"name": "颍州鱼汤", "description": "淮河鲜鱼熬汤，汤白如乳、鲜而不腥"},
        ]
    },
}

# ── 阶段4：文旅补充（重点地点） ──
MEMORIAL_SUPPLEMENTS = {
    # R00 眉山
    "P118": [{"name": "三苏祠", "description": "苏洵苏轼苏辙父子故居，全国重点文物保护单位", "type": "故居"}],
    "P147": [{"name": "三苏祠博物馆", "description": "三苏故居改建的博物馆，藏有大量三苏文物", "type": "博物馆"}],
    "P229": [{"name": "中岩寺", "description": "苏轼少年读书处，有苏轼手书石刻", "type": "寺院"}],
    "P117": [{"name": "玻璃江景区", "description": "岷江眉山段，苏轼诗中多次提及", "type": "景区"}],
    "P115": [{"name": "蟆颐观", "description": "眉山古道观，苏轼常游之地", "type": "道观"}],

    # R01 进京
    "P219": [{"name": "西安城墙", "description": "唐长安城遗址，苏轼经此入关中", "type": "古迹"}],
    "P113": [{"name": "洛阳博物馆", "description": "九朝古都文物荟萃", "type": "博物馆"}],
    "P171": [{"name": "潼关古城遗址", "description": "关中门户，苏轼多次出入", "type": "古迹"}],

    # R02 出蜀
    "P093": [{"name": "白帝城·瞿塘峡景区", "description": "三峡西入口，5A级景区", "type": "景区"}],
    "P094": [{"name": "白帝城", "description": "夔州古城，刘备托孤之地", "type": "古迹"}],
    "P175": [{"name": "巫山小三峡", "description": "巫峡精华段，5A级景区", "type": "景区"}],
    "P233": [{"name": "屈原祠", "description": "屈原故里纪念祠", "type": "祠堂"}],
    "P096": [{"name": "乐山大佛", "description": "世界文化遗产，唐代摩崖石刻大佛", "type": "景区"}],
    "P211": [{"name": "重庆湖广会馆", "description": "长江上游古会馆群", "type": "古迹"}],

    # R03 赴凤翔
    "P187": [{"name": "襄阳古城", "description": "汉水中游重镇，三国古战场", "type": "古迹"}],

    # R06 杭州
    "P103": [{"name": "灵隐寺", "description": "杭州名刹，苏轼常游之地", "type": "寺院"}],
    "P161": [{"name": "苏州园林", "description": "世界文化遗产，江南园林代表", "type": "景区"}],

    # R07 密州
    "P177": [{"name": "惠山古镇", "description": "无锡惠山泉所在，天下第二泉", "type": "景区"}],

    # R08 徐州
    "P158": [{"name": "泗水亭", "description": "刘邦起兵处，徐州古迹", "type": "古迹"}],

    # R10 黄州
    "P134": [{"name": "岐亭古镇", "description": "陈季常隐居地，方山子故事发生地", "type": "古镇"}],
    "P135": [{"name": "浠水文庙", "description": "蕲水古文庙，黄州周边古迹", "type": "古迹"}],
    "P180": [{"name": "鄂州西山", "description": "武昌樊山，吴王城遗址", "type": "景区"}],

    # R11 量移
    "P205": [{"name": "宜兴东坡书院", "description": "苏轼买田阳羡纪念地", "type": "书院"}],

    # R12 赴登州
    "P131": [{"name": "蓬莱阁", "description": "四大名楼之一，苏轼登临观海", "type": "景区"}],

    # R13 还朝
    "P077": [{"name": "趵突泉", "description": "济南七十二泉之首，天下第一泉", "type": "景区"}],
    "P140": [{"name": "青州古城", "description": "古九州之一，5A级景区", "type": "古迹"}],

    # R16 颍州扬州
    "P199": [{"name": "平山堂", "description": "欧阳修所建，苏轼多次登临", "type": "古迹"}],
    "P209": [{"name": "颍州西湖", "description": "苏轼知颍州时常游之地", "type": "景区"}],

    # R17 定州
    "P226": [{"name": "隆兴寺", "description": "正定古刹，中国十大名寺之一", "type": "寺院"}],
    "P185": [{"name": "殷墟", "description": "世界文化遗产，商代都城遗址", "type": "古迹"}],

    # R18 南贬
    "P228": [{"name": "东坡书院", "description": "儋州苏轼讲学处，全国重点文保", "type": "书院"}],
    "P178": [{"name": "梧州骑楼城", "description": "岭南骑楼建筑群", "type": "古迹"}],
    "P126": [{"name": "梅关古道", "description": "中原入岭南要道，全国重点文保", "type": "古迹"}],

    # R19 北归
    "P100": [{"name": "合浦文昌塔", "description": "廉州古塔，苏轼北归途经", "type": "古迹"}],
    "P153": [{"name": "南华寺", "description": "韶州禅宗祖庭，六祖惠能道场", "type": "寺院"}],
}

# 执行阶段3
updated_food = 0
for pid, supp in FOOD_SUPPLEMENTS.items():
    pf = os.path.join(PLACES_DIR, f'{pid}.json')
    if not os.path.exists(pf):
        continue
    with open(pf) as f:
        pd = json.load(f)
    
    if not pd.get('foods'):
        pd['foods'] = supp['foods']
    else:
        existing = {fd['name'] for fd in pd['foods']}
        for fd in supp['foods']:
            if fd['name'] not in existing:
                pd['foods'].append(fd)
    
    with open(pf, 'w', encoding='utf-8') as f:
        json.dump(pd, f, ensure_ascii=False, indent=2)
    pub_pf = os.path.join(PUBLIC_DIR, f'{pid}.json')
    if os.path.exists(pub_pf):
        with open(pub_pf, 'w', encoding='utf-8') as f:
            json.dump(pd, f, ensure_ascii=False, indent=2)
    updated_food += 1
    print(f"  食物 OK {pid} {pd.get('ancient_name','')}")

# 执行阶段4
updated_memorial = 0
for pid, sites in MEMORIAL_SUPPLEMENTS.items():
    pf = os.path.join(PLACES_DIR, f'{pid}.json')
    if not os.path.exists(pf):
        continue
    with open(pf) as f:
        pd = json.load(f)
    
    if not pd.get('memorial_sites'):
        pd['memorial_sites'] = sites
    else:
        existing = {ms['name'] for ms in pd['memorial_sites']}
        for ms in sites:
            if ms['name'] not in existing:
                pd['memorial_sites'].append(ms)
    
    with open(pf, 'w', encoding='utf-8') as f:
        json.dump(pd, f, ensure_ascii=False, indent=2)
    pub_pf = os.path.join(PUBLIC_DIR, f'{pid}.json')
    if os.path.exists(pub_pf):
        with open(pub_pf, 'w', encoding='utf-8') as f:
            json.dump(pd, f, ensure_ascii=False, indent=2)
    updated_memorial += 1
    print(f"  文旅 OK {pid} {pd.get('ancient_name','')}")

print(f"\n阶段3: 更新 {updated_food} 个地点美食")
print(f"阶段4: 更新 {updated_memorial} 个地点文旅")
