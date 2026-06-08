#!/usr/bin/env python3
"""
B级地点作品美食补充
依据：苏轼年谱 + 行踪考extracted_locations
"""
import json, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
PLACES_DIR = os.path.join(PROJECT_DIR, 'data-v4', 'places')

# B级地点核心作品和美食数据
B_PLACE_SUPPLEMENT = {
    "P001": {
        "name": "白鹤峰",
        "sub_place_works": {
            "白鹤峰新居": {"works": ["白鹤峰新居欲成夜过西邻翟秀才"]},
        },
        "foods": [{"name": "梅菜扣肉", "description": "惠州名菜", "origin_story": "惠州传统名菜", "tag": "惠州必吃"}]
    },
    "P009": {
        "name": "汴京翰林院",
        "sub_place_works": {},
        "foods": [{"name": "开封灌汤包", "description": "北宋都城传统美食", "origin_story": "汴京为北宋都城", "tag": "汴京必吃"}]
    },
    "P010": {
        "name": "汴京太学",
        "sub_place_works": {},
        "foods": [{"name": "开封灌汤包", "description": "北宋都城传统美食", "origin_story": "汴京为北宋都城", "tag": "汴京必吃"}]
    },
    "P011": {
        "name": "汴京文德殿",
        "sub_place_works": {},
        "foods": [{"name": "开封灌汤包", "description": "北宋都城传统美食", "origin_story": "汴京为北宋都城", "tag": "汴京必吃"}]
    },
    "P012": {
        "name": "汴京御史台",
        "sub_place_works": {
            "御史台": {"works": ["狱中寄子由二首"]},
        },
        "foods": [{"name": "开封灌汤包", "description": "北宋都城传统美食", "origin_story": "汴京为北宋都城", "tag": "汴京必吃"}]
    },
    "P013": {
        "name": "汴京御史台监狱",
        "sub_place_works": {
            "御史台监狱": {"works": ["狱中寄子由二首"]},
        },
        "foods": [{"name": "开封灌汤包", "description": "北宋都城传统美食", "origin_story": "汴京为北宋都城", "tag": "汴京必吃"}]
    },
    "P014": {
        "name": "汴京政事堂",
        "sub_place_works": {},
        "foods": [{"name": "开封灌汤包", "description": "北宋都城传统美食", "origin_story": "汴京为北宋都城", "tag": "汴京必吃"}]
    },
    "P018": {
        "name": "常州终老故居",
        "sub_place_works": {},
        "foods": [{"name": "常州大麻糕", "description": "常州传统糕点", "origin_story": "常州地方传统美食", "tag": "常州必吃"}]
    },
    "P020": {
        "name": "陈州",
        "sub_place_works": {
            "铁墓": {"works": ["记铁墓厄台"]},
        },
        "foods": [{"name": "陈州胡辣汤", "description": "河南传统早餐", "origin_story": "陈州传统美食", "tag": "陈州特色"}]
    },
    "P021": {
        "name": "成都",
        "sub_place_works": {},
        "foods": [{"name": "麻婆豆腐", "description": "成都名菜", "origin_story": "成都传统名菜", "tag": "成都必吃"}, {"name": "担担面", "description": "成都传统面食", "origin_story": "成都传统小吃", "tag": "成都特色"}]
    },
    "P025": {
        "name": "滁州",
        "sub_place_works": {},
        "foods": [{"name": "滁州烧鸡", "description": "滁州传统名吃", "origin_story": "滁州传统美食", "tag": "滁州特色"}]
    },
    "P036": {
        "name": "登州",
        "sub_place_works": {
            "蓬莱阁": {"works": ["海市诗"]},
        },
        "foods": [{"name": "蓬莱小面", "description": "蓬莱传统面食", "origin_story": "登州传统美食", "tag": "登州特色"}, {"name": "鲅鱼水饺", "description": "胶东特色水饺", "origin_story": "山东沿海传统美食", "tag": "登州必吃"}]
    },
    "P044": {
        "name": "凤翔",
        "sub_place_works": {
            "凤翔府衙": {"works": ["凤翔八观诗"]},
            "东湖": {"works": ["凤翔东湖"]},
        },
        "foods": [{"name": "凤翔豆花泡馍", "description": "凤翔传统早餐", "origin_story": "凤翔传统美食", "tag": "凤翔必吃"}, {"name": "西凤酒", "description": "凤翔名酒，中国四大名酒之一", "origin_story": "苏轼在凤翔时常饮西凤酒", "tag": "凤翔必喝"}]
    },
    "P051": {
        "name": "瓜州渡",
        "sub_place_works": {
            "镇江金山寺": {"works": ["游金山寺"]},
        },
        "foods": [{"name": "镇江锅盖面", "description": "镇江传统面食", "origin_story": "镇江传统美食", "tag": "镇江必吃"}, {"name": "镇江肴肉", "description": "镇江名菜，水晶肴蹄", "origin_story": "镇江传统名菜", "tag": "镇江特色"}]
    },
    "P052": {
        "name": "瓜州古渡",
        "sub_place_works": {
            "镇江金山寺": {"works": ["游金山寺"]},
        },
        "foods": [{"name": "镇江锅盖面", "description": "镇江传统面食", "origin_story": "镇江传统美食", "tag": "镇江必吃"}]
    },
    "P054": {
        "name": "广州",
        "sub_place_works": {},
        "foods": [{"name": "广式早茶", "description": "广州传统饮食文化", "origin_story": "广州传统美食", "tag": "广州必吃"}, {"name": "白切鸡", "description": "广州名菜", "origin_story": "粤菜经典", "tag": "广州必吃"}]
    },
    "P058": {
        "name": "杭州",
        "sub_place_works": {},
        "foods": []  # A级已补充
    },
    "P089": {
        "name": "金陵",
        "sub_place_works": {
            "钟山": {"works": []},
            "清凉寺": {"works": []},
        },
        "foods": [{"name": "南京盐水鸭", "description": "南京名菜，皮白肉嫩", "origin_story": "金陵传统名菜", "tag": "金陵必吃"}, {"name": "鸭血粉丝汤", "description": "南京传统小吃", "origin_story": "金陵传统美食", "tag": "金陵特色"}]
    },
    "P090": {
        "name": "金陵秦淮",
        "sub_place_works": {
            "金陵/江宁": {"works": ["泊船瓜洲"]},
        },
        "foods": [{"name": "南京盐水鸭", "description": "南京名菜", "origin_story": "金陵传统名菜", "tag": "金陵必吃"}]
    },
    "P091": {
        "name": "金陵钟山",
        "sub_place_works": {
            "金陵/江宁": {"works": ["泊船瓜洲"]},
        },
        "foods": [{"name": "南京盐水鸭", "description": "南京名菜", "origin_story": "金陵传统名菜", "tag": "金陵必吃"}]
    },
    "P108": {
        "name": "庐山",
        "sub_place_works": {
            "西林寺": {"works": ["题西林壁"]},
        },
        "foods": [{"name": "庐山石鱼", "description": "庐山特色山珍", "origin_story": "庐山传统美食", "tag": "庐山特色"}, {"name": "庐山石耳炖鸡", "description": "庐山名菜", "origin_story": "庐山传统美食", "tag": "庐山特色"}]
    },
    "P109": {
        "name": "庐山全山",
        "sub_place_works": {
            "庐山西林寺": {"works": ["题西林壁"]},
        },
        "foods": [{"name": "庐山石鱼", "description": "庐山特色山珍", "origin_story": "庐山传统美食", "tag": "庐山特色"}]
    },
    "P117": {
        "name": "眉山玻璃江",
        "sub_place_works": {
            "三苏祠": {"works": []},
        },
        "foods": [{"name": "东坡肘子", "description": "眉山名菜，苏轼家乡味", "origin_story": "传为苏家菜谱流传", "tag": "眉山必吃"}, {"name": "眉山泡菜", "description": "眉山传统泡菜", "origin_story": "四川传统美食", "tag": "眉山特色"}]
    },
    "P118": {
        "name": "眉山故居",
        "sub_place_works": {
            "三苏祠": {"works": []},
        },
        "foods": [{"name": "东坡肘子", "description": "眉山名菜", "origin_story": "传为苏家菜谱流传", "tag": "眉山必吃"}, {"name": "眉山泡菜", "description": "眉山传统泡菜", "origin_story": "四川传统美食", "tag": "眉山特色"}]
    },
    "P124": {
        "name": "渑池僧舍",
        "sub_place_works": {
            "渑池": {"works": ["和子由渑池怀旧"]},
        },
        "foods": [{"name": "渑池仰韶酒", "description": "渑池名酒", "origin_story": "仰韶文化发源地", "tag": "渑池特色"}]
    },
    "P146": {
        "name": "润州",
        "sub_place_works": {
            "金山寺": {"works": ["金山梦中作"]},
        },
        "foods": [{"name": "镇江锅盖面", "description": "镇江传统面食", "origin_story": "镇江传统美食", "tag": "镇江必吃"}, {"name": "镇江肴肉", "description": "镇江名菜", "origin_story": "镇江传统名菜", "tag": "镇江特色"}]
    },
    "P147": {
        "name": "三苏祠",
        "sub_place_works": {},
        "foods": [{"name": "东坡肘子", "description": "眉山名菜", "origin_story": "传为苏家菜谱流传", "tag": "眉山必吃"}]
    },
    "P170": {
        "name": "藤州",
        "sub_place_works": {},
        "foods": [{"name": "藤县米粉", "description": "藤州传统小吃", "origin_story": "广西传统美食", "tag": "藤州特色"}]
    },
    "P198": {
        "name": "扬州",
        "sub_place_works": {
            "平山堂": {"works": ["西江月·平山堂"]},
        },
        "foods": [{"name": "扬州炒饭", "description": "扬州名菜，粒粒分明", "origin_story": "扬州传统名菜", "tag": "扬州必吃"}, {"name": "扬州狮子头", "description": "扬州名菜，肥瘦相间", "origin_story": "淮扬菜经典", "tag": "扬州必吃"}, {"name": "扬州干丝", "description": "扬州传统名菜", "origin_story": "淮扬菜经典", "tag": "扬州特色"}]
    },
    "P199": {
        "name": "扬州平山堂",
        "sub_place_works": {
            "平山堂": {"works": ["西江月·平山堂"]},
        },
        "foods": [{"name": "扬州炒饭", "description": "扬州名菜", "origin_story": "扬州传统名菜", "tag": "扬州必吃"}]
    },
    "P200": {
        "name": "扬州瘦西湖旧址",
        "sub_place_works": {},
        "foods": [{"name": "扬州炒饭", "description": "扬州名菜", "origin_story": "扬州传统名菜", "tag": "扬州必吃"}]
    },
    "P227": {
        "name": "镇江金山寺",
        "sub_place_works": {
            "金山寺": {"works": ["游金山寺"]},
        },
        "foods": [{"name": "镇江锅盖面", "description": "镇江传统面食", "origin_story": "镇江传统美食", "tag": "镇江必吃"}]
    },
    "P228": {
        "name": "中和古镇",
        "sub_place_works": {},
        "foods": [{"name": "儋州烤生蚝", "description": "海南特色", "origin_story": "苏轼《食蚝》记载", "tag": "儋州必吃"}]
    },
}


def supplement_b_places():
    updated = 0
    works_added = 0
    foods_added = 0
    
    for place_id, supplement in B_PLACE_SUPPLEMENT.items():
        fp = os.path.join(PLACES_DIR, f'{place_id}.json')
        if not os.path.exists(fp):
            continue
        
        with open(fp, 'r', encoding='utf-8') as f:
            place_data = json.load(f)
        
        # 补充子地点作品
        for sp in place_data.get('sub_places', []):
            sp_name = sp.get('name', '')
            if sp_name in supplement.get('sub_place_works', {}):
                sp_sup = supplement['sub_place_works'][sp_name]
                existing_works = sp.get('works', [])
                new_works = [w for w in sp_sup.get('works', []) if w not in existing_works]
                if new_works:
                    sp['works'] = existing_works + new_works
                    works_added += len(new_works)
        
        # 补充美食
        if supplement.get('foods'):
            existing_foods = place_data.get('foods', [])
            existing_food_names = {f.get('name') if isinstance(f, dict) else f for f in existing_foods}
            for food in supplement['foods']:
                if food['name'] not in existing_food_names:
                    existing_foods.append(food)
                    foods_added += 1
            place_data['foods'] = existing_foods
        
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(place_data, f, ensure_ascii=False, indent=2)
        
        updated += 1
    
    print(f"总计: 更新{updated}个B级地点, 新增{works_added}条作品, 新增{foods_added}条美食")


if __name__ == '__main__':
    supplement_b_places()
