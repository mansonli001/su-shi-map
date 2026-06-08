#!/usr/bin/env python3
"""
A级地点作品美食补充脚本
依据：
1. v4已有的global_works
2. 行踪考extracted_locations中的su_works和local_foods
3. 苏轼年谱核心作品
"""
import json, os, copy

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
PLACES_DIR = os.path.join(PROJECT_DIR, 'data-v4', 'places')
EXTRACTED_DIR = os.path.join(SCRIPT_DIR, 'extracted_locations')

# A级地点核心作品和美食数据（依据苏轼年谱+行踪考）
A_PLACE_SUPPLEMENT = {
    "P008": {
        "name": "汴京",
        "sub_place_works": {
            "兴国寺浴室院": {
                "works": ["兴国寺浴室院六祖画赞"],
                "works_detail": [
                    {"title": "兴国寺浴室院六祖画赞", "type": "文", "date": "嘉祐元年（1056年）", "note": "三苏初到汴京寓居兴国寺浴室院时所作"}
                ]
            },
            "文德殿": {
                "works": [],
                "works_detail": []
            },
            "御史台": {
                "works": ["狱中寄子由二首"],
                "works_detail": [
                    {"title": "狱中寄子由二首", "type": "诗", "date": "元丰二年（1079年）", "note": "乌台诗案狱中绝笔，'圣主如天万物春，小臣愚暗自亡身'"}
                ]
            }
        },
        "foods": [
            {"name": "开封灌汤包", "description": "北宋都城传统美食，皮薄馅大汤汁鲜美", "origin_story": "汴京为北宋都城，苏轼在朝期间品尝京城美食", "tag": "汴京必吃"},
            {"name": "桶子鸡", "description": "开封传统名菜，色泽金黄肥而不腻", "origin_story": "北宋宫廷菜流传民间", "tag": "汴京特色"},
            {"name": "鲤鱼焙面", "description": "开封名菜，糖醋鲤鱼配细如发丝的焙面", "origin_story": "北宋名菜，苏轼在汴京时或有所品", "tag": "汴京名菜"}
        ]
    },
    "P017": {
        "name": "常州",
        "sub_place_works": {
            "孙氏馆": {
                "works": ["答径山琳长老"],
                "works_detail": [
                    {"title": "答径山琳长老", "type": "诗", "date": "建中靖国元年（1101年）", "note": "苏轼临终前在常州所作，'与君皆丙子，各已三万日'"}
                ]
            }
        },
        "foods": [
            {"name": "常州大麻糕", "description": "常州传统糕点，酥香松脆", "origin_story": "常州地方传统美食", "tag": "常州必吃"},
            {"name": "银丝面", "description": "常州特色面食，面条细如银丝", "origin_story": "常州传统早餐", "tag": "常州特色"},
            {"name": "加蟹小笼包", "description": "常州名点，皮薄汁多蟹香浓郁", "origin_story": "常州传统点心", "tag": "常州名点"}
        ]
    },
    "P024": {
        "name": "赤壁",
        "sub_place_works": {
            "东坡赤壁": {
                "works": ["念奴娇·赤壁怀古", "前赤壁赋", "后赤壁赋"],
                "works_detail": [
                    {"title": "念奴娇·赤壁怀古", "type": "词", "date": "元丰五年（1082年）", "note": "大江东去，浪淘尽，千古风流人物"},
                    {"title": "前赤壁赋", "type": "文", "date": "元丰五年七月（1082年）", "note": "壬戌之秋，七月既望，苏子与客泛舟赤壁之下"},
                    {"title": "后赤壁赋", "type": "文", "date": "元丰五年十月（1082年）", "note": "是岁十月之望，步自雪堂，将归于临皋"}
                ]
            }
        },
        "foods": [
            {"name": "东坡肉", "description": "黄州东坡肉，慢著火少著水，火候足时它自美", "origin_story": "苏轼在黄州发明，'净洗铛，少著水，柴头罨烟焰不起'", "tag": "黄州必吃"},
            {"name": "东坡羹", "description": "苏轼发明的菜羹，以蔓菁芦菔等煮成", "origin_story": "苏轼在黄州作《东坡羹颂》", "tag": "东坡发明"},
            {"name": "东坡饼", "description": "黄州传统面点，酥脆香甜", "origin_story": "传为苏轼在黄州时所创", "tag": "黄州特色"}
        ]
    },
    "P034": {
        "name": "儋州",
        "sub_place_works": {
            "桄榔庵": {
                "works": ["桄榔庵铭"],
                "works_detail": [
                    {"title": "桄榔庵铭", "type": "文", "date": "绍圣四年（1097年）", "note": "苏轼初到儋州居桄榔庵时所作"}
                ]
            },
            "载酒堂": {
                "works": ["载酒堂记"],
                "works_detail": [
                    {"title": "载酒堂记（或相关诗作）", "type": "文", "date": "绍圣年间", "note": "儋州讲学之所"}
                ]
            },
            "东坡书院": {
                "works": [],
                "works_detail": []
            }
        },
        "foods": [
            {"name": "儋州烤生蚝", "description": "海南特色，海蚝炭烤鲜嫩多汁", "origin_story": "苏轼《食蚝》：'无令中朝士大夫知，恐争谋南徙，以分此味'", "tag": "儋州必吃"},
            {"name": "儋州米烂", "description": "儋州传统小吃，米粉配多种佐料", "origin_story": "儋州地方传统美食", "tag": "儋州特色"},
            {"name": "椰子鸡", "description": "海南名菜，椰汁炖鸡清甜鲜美", "origin_story": "海南传统美食", "tag": "海南名菜"}
        ]
    },
    "P035": {
        "name": "儋州桄榔庵",
        "sub_place_works": {
            "桄榔庵": {
                "works": ["桄榔庵铭"],
                "works_detail": [
                    {"title": "桄榔庵铭", "type": "文", "date": "绍圣四年（1097年）", "note": "苏轼初到儋州居桄榔庵时所作"}
                ]
            }
        },
        "foods": [
            {"name": "儋州烤生蚝", "description": "海南特色，海蚝炭烤鲜嫩多汁", "origin_story": "苏轼《食蚝》记载", "tag": "儋州必吃"}
        ]
    },
    "P039": {
        "name": "定州中山故都",
        "sub_place_works": {
            "定州州衙": {
                "works": [],
                "works_detail": []
            },
            "中山故都": {
                "works": [],
                "works_detail": []
            }
        },
        "foods": [
            {"name": "定州焖子", "description": "定州传统名吃，淀粉肉冻切片拌蒜汁", "origin_story": "定州地方传统美食", "tag": "定州必吃"},
            {"name": "驴肉火烧", "description": "河北名吃，酥脆火烧夹卤驴肉", "origin_story": "河北传统美食", "tag": "定州特色"}
        ]
    },
    "P058": {
        "name": "杭州",
        "sub_place_works": {
            "凤凰山州衙": {
                "works": [],
                "works_detail": []
            },
            "西湖": {
                "works": ["饮湖上初晴后雨"],
                "works_detail": [
                    {"title": "饮湖上初晴后雨二首", "type": "诗", "date": "熙宁六年（1073年）", "note": "水光潋滟晴方好，山色空蒙雨亦奇。欲把西湖比西子，淡妆浓抹总相宜。"}
                ]
            },
            "苏堤": {
                "works": [],
                "works_detail": []
            },
            "孤山": {
                "works": [],
                "works_detail": []
            },
            "灵隐寺": {
                "works": [],
                "works_detail": []
            },
            "望湖楼": {
                "works": ["六月二十七日望湖楼醉书"],
                "works_detail": [
                    {"title": "六月二十七日望湖楼醉书", "type": "诗", "date": "熙宁五年（1072年）", "note": "黑云翻墨未遮山，白雨跳珠乱入船"}
                ]
            }
        },
        "foods": [
            {"name": "西湖醋鱼", "description": "杭州名菜，草鱼糖醋烹制酸甜适口", "origin_story": "杭州传统名菜，苏轼治湖后流传", "tag": "杭州必吃"},
            {"name": "东坡肉", "description": "杭州东坡肉，酥烂不碎油而不腻", "origin_story": "传为苏轼疏浚西湖时慰民所创", "tag": "杭州必吃"},
            {"name": "龙井虾仁", "description": "杭州名菜，龙井茶香配鲜虾仁", "origin_story": "杭州传统名菜", "tag": "杭州名菜"},
            {"name": "叫化鸡", "description": "杭州传统名菜，泥裹烤鸡酥烂鲜香", "origin_story": "杭州传统美食", "tag": "杭州特色"},
            {"name": "片儿川", "description": "杭州传统面食，笋片雪菜肉丝面", "origin_story": "杭州传统早餐", "tag": "杭州特色"}
        ]
    },
    "P072": {
        "name": "黄州",
        "sub_place_works": {
            "定慧院": {
                "works": ["卜算子·黄州定慧院寓居作"],
                "works_detail": [
                    {"title": "卜算子·黄州定慧院寓居作", "type": "词", "date": "元丰三年（1080年）", "note": "缺月挂疏桐，漏断人初静。谁见幽人独往来，缥缈孤鸿影。"}
                ]
            },
            "临皋亭": {
                "works": ["临皋闲题", "与范子丰书"],
                "works_detail": [
                    {"title": "临皋闲题", "type": "文", "date": "元丰年间", "note": "临皋亭下八十数步，便是大江"},
                    {"title": "与范子丰书", "type": "文", "date": "元丰年间", "note": "临皋亭中所作书信"}
                ]
            },
            "东坡雪堂": {
                "works": ["雪堂记"],
                "works_detail": [
                    {"title": "雪堂记", "type": "文", "date": "元丰五年（1082年）", "note": "苏轼筑雪堂后所作"}
                ]
            },
            "东坡赤壁": {
                "works": ["念奴娇·赤壁怀古", "前赤壁赋", "后赤壁赋"],
                "works_detail": [
                    {"title": "念奴娇·赤壁怀古", "type": "词", "date": "元丰五年（1082年）", "note": "大江东去，浪淘尽，千古风流人物"},
                    {"title": "前赤壁赋", "type": "文", "date": "元丰五年七月（1082年）", "note": "壬戌之秋，七月既望"},
                    {"title": "后赤壁赋", "type": "文", "date": "元丰五年十月（1082年）", "note": "步自雪堂，将归于临皋"}
                ]
            },
            "安国寺": {
                "works": ["安国寺浴"],
                "works_detail": [
                    {"title": "安国寺浴", "type": "诗", "date": "元丰三年（1080年）", "note": "苏轼在黄州常往安国寺沐浴"}
                ]
            },
            "承天寺": {
                "works": ["记承天寺夜游"],
                "works_detail": [
                    {"title": "记承天寺夜游", "type": "文", "date": "元丰六年（1083年）", "note": "庭下如积水空明，水中藻荇交横，盖竹柏影也"}
                ]
            },
            "沙湖道中": {
                "works": ["定风波·莫听穿林打叶声"],
                "works_detail": [
                    {"title": "定风波·莫听穿林打叶声", "type": "词", "date": "元丰五年三月（1082年）", "note": "竹杖芒鞋轻胜马，谁怕？一蓑烟雨任平生"}
                ]
            },
            "东坡纪念馆": {
                "works": [],
                "works_detail": []
            }
        },
        "foods": [
            {"name": "东坡肉", "description": "黄州东坡肉，慢著火少著水，火候足时它自美", "origin_story": "苏轼在黄州发明，'净洗铛，少著水，柴头罨烟焰不起'", "tag": "黄州必吃"},
            {"name": "东坡羹", "description": "苏轼发明的菜羹，以蔓菁芦菔等煮成", "origin_story": "苏轼作《东坡羹颂》", "tag": "东坡发明"},
            {"name": "东坡饼", "description": "黄州传统面点，酥脆香甜", "origin_story": "传为苏轼在黄州时所创", "tag": "黄州特色"}
        ]
    },
    "P073": {
        "name": "黄州东坡雪堂",
        "sub_place_works": {
            "东坡雪堂": {
                "works": ["雪堂记"],
                "works_detail": [
                    {"title": "雪堂记", "type": "文", "date": "元丰五年（1082年）", "note": "苏轼筑雪堂后所作"}
                ]
            }
        },
        "foods": [
            {"name": "东坡肉", "description": "黄州东坡肉", "origin_story": "苏轼在黄州发明", "tag": "黄州必吃"}
        ]
    },
    "P075": {
        "name": "惠州合江楼",
        "sub_place_works": {
            "合江楼": {
                "works": ["寓居合江楼"],
                "works_detail": [
                    {"title": "寓居合江楼", "type": "诗", "date": "绍圣元年（1094年）", "note": "苏轼初到惠州寓居合江楼时所作"}
                ]
            },
            "白鹤峰新居": {
                "works": ["白鹤峰新居欲成夜过西邻翟秀才"],
                "works_detail": [
                    {"title": "白鹤峰新居欲成夜过西邻翟秀才", "type": "诗", "date": "绍圣三年（1096年）", "note": "苏轼在惠州营建白鹤峰新居"}
                ]
            },
            "西湖": {
                "works": [],
                "works_detail": []
            },
            "罗浮山": {
                "works": ["食荔枝"],
                "works_detail": [
                    {"title": "食荔枝二首", "type": "诗", "date": "绍圣二年（1095年）", "note": "日啖荔枝三百颗，不辞长作岭南人"}
                ]
            }
        },
        "foods": [
            {"name": "梅菜扣肉", "description": "惠州名菜，梅菜与五花肉层层相叠蒸制", "origin_story": "惠州传统名菜", "tag": "惠州必吃"},
            {"name": "酿豆腐", "description": "客家名菜，豆腐中酿入肉馅煎制", "origin_story": "惠州客家传统美食", "tag": "惠州特色"},
            {"name": "荔枝", "description": "岭南佳果，苏轼最爱", "origin_story": "苏轼'日啖荔枝三百颗，不辞长作岭南人'", "tag": "惠州必吃"},
            {"name": "盐焗鸡", "description": "客家名菜，盐焗鸡皮脆肉嫩", "origin_story": "惠州客家传统美食", "tag": "惠州特色"}
        ]
    },
    "P119": {
        "name": "密州",
        "sub_place_works": {
            "密州州衙": {
                "works": [],
                "works_detail": []
            },
            "超然台": {
                "works": ["水调歌头·明月几时有", "超然台记"],
                "works_detail": [
                    {"title": "水调歌头·明月几时有", "type": "词", "date": "熙宁九年中秋（1076年）", "note": "明月几时有，把酒问青天。但愿人长久，千里共婵娟。"},
                    {"title": "超然台记", "type": "文", "date": "熙宁八年（1075年）", "note": "苏轼修葺超然台后所作"}
                ]
            },
            "常山": {
                "works": ["江城子·密州出猎"],
                "works_detail": [
                    {"title": "江城子·密州出猎", "type": "词", "date": "熙宁八年（1075年）", "note": "老夫聊发少年狂，左牵黄，右擎苍。会挽雕弓如满月，西北望，射天狼。"}
                ]
            }
        },
        "foods": [
            {"name": "德州扒鸡", "description": "山东名吃，骨酥肉烂香味浓郁", "origin_story": "山东传统名吃", "tag": "山东必吃"},
            {"name": "保店驴肉", "description": "山东名吃，驴肉鲜嫩醇香", "origin_story": "山东传统美食", "tag": "山东特色"}
        ]
    },
    "P195": {
        "name": "徐州",
        "sub_place_works": {
            "徐州州衙": {
                "works": [],
                "works_detail": []
            },
            "黄楼": {
                "works": ["黄楼赋"],
                "works_detail": [
                    {"title": "黄楼赋", "type": "赋", "date": "元丰元年（1078年）", "note": "苏轼在徐州抗洪后建黄楼，作黄楼赋"}
                ]
            },
            "云龙山": {
                "works": ["放鹤亭记"],
                "works_detail": [
                    {"title": "放鹤亭记", "type": "文", "date": "元丰元年（1078年）", "note": "苏轼为云龙山人张天骥所作"}
                ]
            },
            "放鹤亭": {
                "works": ["放鹤亭记"],
                "works_detail": [
                    {"title": "放鹤亭记", "type": "文", "date": "元丰元年（1078年）", "note": "苏轼为云龙山人张天骥所作"}
                ]
            },
            "燕子楼": {
                "works": ["永遇乐·彭城夜宿燕子楼"],
                "works_detail": [
                    {"title": "永遇乐·彭城夜宿燕子楼", "type": "词", "date": "元丰元年（1078年）", "note": "明月如霜，好风如水，清景无限"}
                ]
            }
        },
        "foods": [
            {"name": "地锅鸡", "description": "徐州名菜，铁锅炖鸡贴饼子", "origin_story": "徐州传统名菜", "tag": "徐州必吃"},
            {"name": "羊汤", "description": "徐州特色，白汤羊肉鲜而不膻", "origin_story": "徐州传统美食", "tag": "徐州特色"},
            {"name": "烙馍", "description": "徐州传统面食，薄如纸韧如皮", "origin_story": "徐州传统主食", "tag": "徐州特色"}
        ]
    },
    "P217": {
        "name": "载酒堂",
        "sub_place_works": {
            "载酒堂": {
                "works": [],
                "works_detail": []
            }
        },
        "foods": [
            {"name": "儋州烤生蚝", "description": "海南特色，海蚝炭烤鲜嫩多汁", "origin_story": "苏轼《食蚝》记载", "tag": "儋州必吃"}
        ]
    }
}


def supplement_a_places():
    updated = 0
    works_added = 0
    foods_added = 0
    
    for place_id, supplement in A_PLACE_SUPPLEMENT.items():
        fp = os.path.join(PLACES_DIR, f'{place_id}.json')
        with open(fp, 'r', encoding='utf-8') as f:
            place_data = json.load(f)
        
        # 补充子地点作品
        for sp in place_data.get('sub_places', []):
            sp_name = sp.get('name', '')
            if sp_name in supplement.get('sub_place_works', {}):
                sp_sup = supplement['sub_place_works'][sp_name]
                # 补充works（标题列表）
                existing_works = sp.get('works', [])
                new_works = [w for w in sp_sup['works'] if w not in existing_works]
                if new_works:
                    sp['works'] = existing_works + new_works
                    works_added += len(new_works)
                # 补充works_detail
                if sp_sup.get('works_detail'):
                    existing_detail = sp.get('works_detail', [])
                    existing_titles = {d.get('title') for d in existing_detail}
                    for wd in sp_sup['works_detail']:
                        if wd['title'] not in existing_titles:
                            existing_detail.append(wd)
                    sp['works_detail'] = existing_detail
        
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
        print(f"✅ {place_id} {supplement['name']}: 子地点作品补充, 美食={len(supplement.get('foods', []))}个")
    
    print(f"\n总计: 更新{updated}个地点, 新增{works_added}条作品, 新增{foods_added}条美食")


if __name__ == '__main__':
    supplement_a_places()
