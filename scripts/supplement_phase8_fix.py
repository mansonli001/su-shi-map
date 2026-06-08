#!/usr/bin/env python3
"""
修复P149误匹配 + 精确补充被跳过的城市数据
"""
import json, os

PLACES_DIR = 'data-v4/places'
PUBLIC_DIR = 'public/data-v4/places'

with open('data-v4/places-index.json') as f:
    pi = json.load(f)

# 精确ID映射（不再用模糊匹配）
EXACT_DATA = {
    # 被P149误吞的城市，需要精确分配
    "P175": {  # 巫山
        "foods": [{"name": "巫山烤鱼", "description": "巫山传统名菜，鲜鱼炭烤配蔬菜，麻辣鲜香"}],
        "memorial_sites": [{"name": "巫山神女峰", "description": "巫山名景，'巫山神女'传说所在地", "type": "景区"}]
    },
    "P233": {  # 秭归
        "foods": [{"name": "秭归脐橙", "description": "秭归名产，屈原故里特产，汁多味甜"}],
        "memorial_sites": [{"name": "屈原祠", "description": "屈原故里纪念祠，苏轼出蜀途经或曾凭吊", "type": "古迹"}]
    },
    "P230": {  # 忠州
        "foods": [{"name": "忠州豆腐乳", "description": "忠州传统名产，腐乳醇香，佐餐佳品"}],
    },
    "P211": {  # 渝州
        "foods": [
            {"name": "重庆火锅", "description": "渝州名食，麻辣锅底涮毛肚鸭肠，鲜辣过瘾"},
            {"name": "重庆小面", "description": "渝州传统早餐，麻辣素面，筋道爽口"},
        ],
    },
    "P162": {  # 宿州
        "foods": [
            {"name": "宿州sa汤", "description": "宿州传统早餐，麦仁鸡汤熬制，浓香暖胃"},
            {"name": "符离集烧鸡", "description": "宿州名菜，卤制烧鸡色香味俱佳"},
        ],
    },
    "P186": {  # 襄城
        "foods": [{"name": "襄城焖面", "description": "襄城传统面食，面条与菜肉同焖，浓香入味"}],
    },
    "P185": {  # 相州
        "foods": [{"name": "安阳三熏", "description": "相州传统名菜，熏鸡熏肉熏蛋，烟香浓郁"}],
    },
    "P191": {  # 邢州
        "foods": [{"name": "邢台道口烧鸡", "description": "邢州传统名吃，卤制烧鸡，皮酥肉嫩"}],
    },
    "P226": {  # 真定
        "foods": [{"name": "正定八大碗", "description": "真定传统宴席，八碗荤素搭配，实惠丰盛"}],
    },
    "P232": {  # 淄州
        "foods": [{"name": "淄博周村烧饼", "description": "淄州传统名点，薄脆芝麻饼，酥香可口"}],
    },
    "P203": {  # 沂州
        "foods": [{"name": "沂州糁汤", "description": "沂州传统早餐，麦仁肉汤浓稠，暖胃解乏"}],
    },
    "P174": {  # 尉氏
        "foods": [{"name": "尉氏烩面", "description": "尉氏传统面食，宽面条配羊肉汤，浓香暖胃"}],
    },
    "P201": {  # 叶县
        "foods": [{"name": "叶县烩面", "description": "叶县传统面食，面条配羊汤，鲜香暖胃"}],
    },
    "P197": {  # 许州
        "foods": [{"name": "许昌腐竹", "description": "许州传统名产，豆香浓郁，口感筋道"}],
        "memorial_sites": [{"name": "春秋楼", "description": "许州古建筑，关羽夜读春秋处", "type": "古迹"}],
    },
    "P151": {  # 陕州
        "foods": [{"name": "陕州糟蛋", "description": "陕州传统名吃，鸡蛋酒糟腌制，风味独特"}],
        "memorial_sites": [{"name": "陕州地坑院", "description": "独特地下民居，全国重点文物保护单位", "type": "古迹"}],
    },
    "P169": {  # 唐州
        "foods": [{"name": "唐河凉粉", "description": "唐州传统小吃，豌豆凉粉凉拌，爽滑解暑"}],
    },
    "P193": {  # 兴元
        "foods": [
            {"name": "汉中面皮", "description": "兴元传统名吃，米皮配辣油，爽滑麻辣"},
            {"name": "汉中菜豆腐", "description": "兴元传统小吃，豆浆点豆腐配酸菜，清淡爽口"},
        ],
    },
    "P171": {  # 潼关
        "foods": [{"name": "潼关肉夹馍", "description": "潼关名吃，千层酥馍夹腊汁肉，酥脆鲜香"}],
        "memorial_sites": [{"name": "潼关古城", "description": "关中门户，苏轼进京出蜀必经", "type": "古迹"}],
    },
    "P153": {  # 韶州
        "foods": [{"name": "韶关铜勺饼", "description": "韶州传统小吃，米浆铜勺炸制，酥脆可口"}],
    },
    "P178": {  # 梧州
        "foods": [
            {"name": "梧州龟苓膏", "description": "梧州传统名吃，龟板土茯苓熬制，清凉解暑"},
            {"name": "梧州纸包鸡", "description": "梧州传统名菜，鸡肉纸包油炸，鲜嫩多汁"},
        ],
    },
    "P212": {  # 郁林
        "foods": [{"name": "玉林牛巴", "description": "郁林传统名吃，牛肉腌制烘干，香韧耐嚼"}],
    },
    "P177": {  # 无锡
        "foods": [
            {"name": "无锡酱排骨", "description": "无锡传统名菜，排骨浓酱炖煮，甜香酥烂"},
            {"name": "无锡小笼包", "description": "无锡名点，皮薄汁多馅鲜，微甜口味"},
        ],
    },
    "P219": {  # 长安
        "foods": [
            {"name": "长安羊肉泡馍", "description": "长安传统名食，掰馍泡羊汤，浓香暖胃"},
            {"name": "长安肉夹馍", "description": "长安名小吃，白吉馍夹腊汁肉，酥香满口"},
        ],
        "memorial_sites": [
            {"name": "大雁塔", "description": "唐代名塔，苏轼途经长安或曾登临", "type": "古迹"},
            {"name": "曲江池", "description": "唐代名园，苏轼游长安或访此迹", "type": "景区"},
        ]
    },
    "P187": {  # 襄阳
        "foods": [
            {"name": "襄阳牛肉面", "description": "襄阳传统早餐，碱面配牛肉牛杂，麻辣鲜香"},
            {"name": "襄阳黄酒", "description": "襄阳传统米酒，微甜爽口"},
        ],
        "memorial_sites": [
            {"name": "襄阳古城", "description": "千年古城，苏轼途经襄阳或登城远眺", "type": "古迹"},
        ]
    },
    "P234": {  # 梓潼
        "foods": [{"name": "梓潼酥饼", "description": "梓潼传统名点，酥脆层多，芝麻香浓"}],
        "memorial_sites": [{"name": "七曲山大庙", "description": "梓潼文昌帝君祖庭，苏轼出蜀途经或曾拜谒", "type": "古迹"}],
    },
    "P152": {  # 陕州硖石
        "memorial_sites": [{"name": "硖石古驿", "description": "陕州硖石古驿站，苏轼途经作诗", "type": "古迹"}],
    },
    "P206": {  # 宜兴田园
        "memorial_sites": [{"name": "宜兴东坡书院", "description": "苏轼买田宜兴处，后建书院纪念", "type": "古迹"}],
    },
    "P179": {  # 五丈原
        "memorial_sites": [{"name": "五丈原诸葛亮庙", "description": "诸葛亮病逝之地，苏轼途经或曾凭吊", "type": "古迹"}],
    },
    "P155": {  # 石钟山
        "memorial_sites": [{"name": "石钟山", "description": "苏轼作'石钟山记'，千古名篇", "type": "景区"}],
    },
    "P150": {  # 沙湖
        "memorial_sites": [{"name": "沙湖", "description": "黄州附近湖泊，苏轼游此遇雨作'定风波'", "type": "景区"}],
    },
}

updated = 0
food_added = 0
memorial_added = 0

for pid, data in EXACT_DATA.items():
    pf = os.path.join(PLACES_DIR, f'{pid}.json')
    if not os.path.exists(pf):
        print(f"  SKIP {pid} 文件不存在")
        continue

    with open(pf, encoding='utf-8') as f:
        pd = json.load(f)

    changed = False

    for food in data.get('foods', []):
        if 'foods' not in pd:
            pd['foods'] = []
        existing = {f['name'] for f in pd['foods']}
        if food['name'] not in existing:
            pd['foods'].append(food)
            food_added += 1
            changed = True

    for site in data.get('memorial_sites', []):
        if 'memorial_sites' not in pd:
            pd['memorial_sites'] = []
        existing = {m['name'] for m in pd['memorial_sites']}
        if site['name'] not in existing:
            pd['memorial_sites'].append(site)
            memorial_added += 1
            changed = True

    if changed:
        with open(pf, 'w', encoding='utf-8') as f:
            json.dump(pd, f, ensure_ascii=False, indent=2)
        pub_pf = os.path.join(PUBLIC_DIR, f'{pid}.json')
        if os.path.exists(pub_pf):
            with open(pub_pf, 'w', encoding='utf-8') as f:
                json.dump(pd, f, ensure_ascii=False, indent=2)
        updated += 1
        an = pd.get('ancient_name', '')
        fc = len(pd.get('foods', []))
        mc = len(pd.get('memorial_sites', []))
        print(f"  OK {pid} {an} 美食={fc} 文旅={mc}")

print(f"\n共更新 {updated} 个地点，补充 {food_added} 个美食 + {memorial_added} 个文旅")
