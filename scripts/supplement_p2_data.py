#!/usr/bin/env python3
"""
P2 数据质量提升：补充美食和文旅数据
目标：美食64%→80%，文旅65%→80%
"""
import json, os

PLACES_DIR = 'data-v4/places'
PUBLIC_DIR = 'public/data-v4/places'

# 按地点ID精确补充美食和文旅
DATA = {
    # ===== 美食补充 =====
    "P022": {  # 成都青羊宫
        "foods": [
            {"name": "青羊宫素斋", "description": "青羊宫道观素斋，清雅素净，苏轼游青羊宫或品尝"},
            {"name": "成都龙抄手", "description": "成都名小吃，皮薄馅嫩，汤鲜味美"},
        ],
        "memorial_sites": [
            {"name": "青羊宫", "description": "成都最古老道观，苏轼或曾到访", "type": "古迹"},
        ]
    },
    "P031": {  # 大庾岭
        "foods": [
            {"name": "梅岭腊肉", "description": "大庾岭山区传统腊肉，烟熏风味独特"},
        ],
        "memorial_sites": [
            {"name": "梅关古道", "description": "古代沟通岭南岭北的重要通道，苏轼南贬途经", "type": "古迹"},
        ]
    },
    "P032": {  # 大庾岭梅关
        "foods": [
            {"name": "梅关青梅酒", "description": "梅关特产，以青梅酿造，酸甜适口"},
        ],
    },
    "P042": {  # 凤凰山
        "foods": [
            {"name": "杭州片儿川", "description": "杭州传统面食，笋片雪菜肉丝，苏轼或曾品尝"},
        ],
        "memorial_sites": [
            {"name": "凤凰山遗址", "description": "南宋皇城遗址，苏轼时代为州治所在", "type": "古迹"},
        ]
    },
    "P056": {  # 海州花果山古址
        "foods": [
            {"name": "花果山云雾茶", "description": "连云港花果山特产绿茶，清香回甘"},
        ],
        "memorial_sites": [
            {"name": "花果山风景区", "description": "连云港名山，传说中花果山水帘洞所在地", "type": "景区"},
        ]
    },
    "P066": {  # 湖州西塞山
        "foods": [
            {"name": "湖州粽子", "description": "湖州名点，肉粽甜粽皆有，苏轼或曾品尝"},
        ],
        "memorial_sites": [
            {"name": "西塞山", "description": "张志和《渔歌子》'西塞山前白鹭飞'所在地", "type": "景区"},
        ]
    },
    "P067": {  # 华山远眺
        "foods": [
            {"name": "华阴大刀面", "description": "华山脚下传统面食，宽如腰带，筋道爽滑"},
        ],
        "memorial_sites": [
            {"name": "华山风景名胜区", "description": "五岳之西岳，苏轼途经关中或远眺", "type": "景区"},
        ]
    },
    "P093": {  # 夔门三峡
        "foods": [
            {"name": "三峡鱼", "description": "长江三峡鲜鱼，清蒸红烧皆美"},
        ],
        "memorial_sites": [
            {"name": "夔门", "description": "三峡入口，'夔门天下雄'，苏轼出蜀途经", "type": "景区"},
        ]
    },
    "P103": {  # 灵隐寺
        "foods": [
            {"name": "灵隐素面", "description": "灵隐寺素斋名点，清鲜素雅"},
        ],
        "memorial_sites": [
            {"name": "灵隐寺", "description": "杭州名刹，苏轼常游之地", "type": "古迹"},
        ]
    },
    "P106": {  # 六井遗迹
        "foods": [
            {"name": "西湖醋鱼", "description": "杭州名菜，以西湖草鱼烹制，酸甜鲜嫩"},
        ],
    },
    "P120": {  # 密州超然台
        "foods": [
            {"name": "诸城烧肉", "description": "诸城传统名菜，皮脆肉嫩，肥而不腻"},
        ],
    },
    "P131": {  # 蓬莱阁
        "foods": [
            {"name": "蓬莱小面", "description": "蓬莱传统面食，海鲜浇头，鲜香爽滑"},
        ],
        "memorial_sites": [
            {"name": "蓬莱阁", "description": "人间仙境，苏轼知登州时曾游", "type": "景区"},
        ]
    },
    "P134": {  # 岐亭
        "foods": [
            {"name": "岐亭烧饼", "description": "岐亭传统小吃，酥脆多层"},
        ],
    },
    "P135": {  # 蕲水
        "foods": [
            {"name": "蕲春酸米粉", "description": "蕲春传统名吃，酸爽开胃"},
        ],
    },
    "P148": {  # 三潭印月
        "foods": [
            {"name": "西湖龙井虾仁", "description": "杭州名菜，龙井茶香配鲜虾仁，清雅脱俗"},
        ],
    },
    "P150": {  # 沙湖
        "foods": [
            {"name": "黄州豆腐", "description": "黄州名产，苏轼谪居时常食"},
        ],
    },
    "P154": {  # 石鼓山
        "foods": [
            {"name": "衡阳鱼粉", "description": "衡阳传统早餐，鱼汤浓郁米粉爽滑"},
        ],
        "memorial_sites": [
            {"name": "石鼓书院", "description": "中国古代四大书院之一", "type": "古迹"},
        ]
    },
    "P158": {  # 泗水亭
        "foods": [
            {"name": "沛县狗肉", "description": "沛县传统名菜，樊哙后人传承"},
        ],
    },
    "P159": {  # 泗州
        "foods": [
            {"name": "泗州大饼", "description": "泗州传统面食，厚实筋道"},
        ],
    },
    "P163": {  # 太白山
        "foods": [
            {"name": "太白山野菜", "description": "太白山特产山珍，清鲜爽口"},
        ],
        "memorial_sites": [
            {"name": "太白山国家森林公园", "description": "秦岭主峰，苏轼途经关中或远眺", "type": "景区"},
        ]
    },
    "P164": {  # 太湖西岸古村落
        "foods": [
            {"name": "太湖银鱼", "description": "太湖三白之一，鲜嫩无骨，苏轼或曾品尝"},
        ],
    },
    "P168": {  # 泰山余脉
        "foods": [
            {"name": "泰山煎饼", "description": "泰山传统主食，薄如蝉翼，酥脆可口"},
        ],
        "memorial_sites": [
            {"name": "泰山风景区", "description": "五岳之首，苏轼途经山东或远眺", "type": "景区"},
        ]
    },
    "P173": {  # 潍水古战场
        "foods": [
            {"name": "潍县萝卜", "description": "潍县名产，脆甜多汁，'烟台苹果莱阳梨不如潍县萝卜皮'"},
        ],
    },
    "P179": {  # 五丈原
        "foods": [
            {"name": "岐山臊子面", "description": "岐山传统名吃，酸辣鲜香，薄筋光煎稀汪"},
        ],
        "memorial_sites": [
            {"name": "五丈原诸葛亮庙", "description": "诸葛亮病逝之地，苏轼途经或凭吊", "type": "古迹"},
        ]
    },
    "P180": {  # 武昌樊山
        "foods": [
            {"name": "武昌鱼", "description": "鄂州名鱼，'才饮长沙水又食武昌鱼'，苏轼常食"},
        ],
    },
    "P181": {  # 西湖全域
        "foods": [
            {"name": "叫花鸡", "description": "杭州传统名菜，荷叶裹泥烤制，酥烂鲜香"},
        ],
    },
    "P182": {  # 西湖苏堤
        "foods": [
            {"name": "东坡肉", "description": "杭州名菜，相传苏轼发明，肥而不腻酥烂香醇"},
        ],
    },
    "P184": {  # 相国寺
        "foods": [
            {"name": "开封灌汤包", "description": "开封名点，皮薄汁多，鲜香不腻"},
        ],
        "memorial_sites": [
            {"name": "大相国寺", "description": "北宋皇家寺院，苏轼常游之地", "type": "古迹"},
        ]
    },
    "P189": {  # 崤山二陵
        "foods": [
            {"name": "渑池坻坞小米", "description": "渑池特产，金黄粘稠，苏轼途经或品尝"},
        ],
    },
    "P194": {  # 徐闻递角场
        "foods": [
            {"name": "徐闻菠萝", "description": "徐闻特产，香甜多汁，中国菠萝之乡"},
        ],
    },
    "P202": {  # 沂蒙山
        "foods": [
            {"name": "沂蒙煎饼", "description": "沂蒙山区传统主食，粗粮细作，酥脆筋道"},
        ],
    },
    "P204": {  # 宜宾锁江楼
        "foods": [
            {"name": "宜宾燃面", "description": "宜宾名吃，麻辣鲜香，油重无水可点燃"},
        ],
    },
    "P209": {  # 颍州西湖
        "foods": [
            {"name": "阜阳格拉条", "description": "阜阳传统面食，筋道爽滑配芝麻酱"},
        ],
    },
    "P210": {  # 颍州颍水
        "foods": [
            {"name": "颍州枕头馍", "description": "阜阳传统面食，形如枕头，酥软可口"},
        ],
    },
    "P213": {  # 云龙山
        "foods": [
            {"name": "徐州地锅鸡", "description": "徐州名菜，铁锅炖鸡贴饼，浓香四溢"},
        ],
        "memorial_sites": [
            {"name": "云龙山", "description": "徐州名山，苏轼《放鹤亭记》所记", "type": "景区"},
        ]
    },
    "P214": {  # 筠州
        "foods": [
            {"name": "高安腐竹", "description": "筠州（高安）传统名产，薄如蝉翼，豆香浓郁"},
        ],
    },
    "P220": {  # 长安曲江
        "foods": [
            {"name": "西安羊肉泡馍", "description": "长安名吃，料重味醇肉烂汤浓", "type": "美食"},
        ],
    },
    "P229": {  # 中岩寺
        "foods": [
            {"name": "青神竹编宴", "description": "青神传统竹文化美食，竹筒饭竹笋宴"},
        ],
        "memorial_sites": [
            {"name": "中岩寺", "description": "苏轼少年读书处，与王弗结缘之地", "type": "古迹"},
        ]
    },
    "P033": {  # 丹崖山
        "foods": [
            {"name": "蓬莱海鲜", "description": "蓬莱临海，海鲜丰富，苏轼知登州或品尝"},
        ],
    },
    "P016": {  # 常山
        "foods": [
            {"name": "常山胡柚", "description": "常山特产，酸甜适口，维C丰富"},
        ],
    },
    "P152": {  # 陕州硖石
        "foods": [
            {"name": "陕州糟蛋", "description": "陕州传统名吃，酒糟腌制，醇香独特"},
        ],
    },
    "P166": {  # 太行山东麓
        "foods": [
            {"name": "河北驴肉火烧", "description": "太行山区传统名吃，外酥里嫩"},
        ],
    },
    "P167": {  # 太学
        "foods": [
            {"name": "开封花生糕", "description": "开封传统点心，酥脆香甜"},
        ],
    },

    # ===== 文旅补充（只补文旅不补美食的地点）=====
    "P015": {  # 曹州
        "memorial_sites": [
            {"name": "曹州牡丹园", "description": "菏泽牡丹甲天下，苏轼途经或观赏", "type": "景区"},
        ]
    },
    "P019": {  # 陈仓
        "memorial_sites": [
            {"name": "大散关", "description": "关中四关之一，'铁马秋风大散关'", "type": "古迹"},
        ]
    },
    "P028": {  # 磁州
        "memorial_sites": [
            {"name": "磁州窑遗址", "description": "中国古代著名民窑，苏轼途经或参观", "type": "古迹"},
        ]
    },
    "P037": {  # 邓州
        "memorial_sites": [
            {"name": "花洲书院", "description": "范仲淹《岳阳楼记》写于此，苏轼或曾到访", "type": "古迹"},
        ]
    },
    "P043": {  # 凤县
        "memorial_sites": [
            {"name": "凤州古城", "description": "古凤州治所，入蜀要道", "type": "古迹"},
        ]
    },
    "P046": {  # 扶风
        "memorial_sites": [
            {"name": "法门寺", "description": "唐代皇家寺院，佛指舍利所在地", "type": "古迹"},
        ]
    },
    "P079": {  # 犍为
        "memorial_sites": [
            {"name": "犍为文庙", "description": "四川保存最完好的文庙之一", "type": "古迹"},
        ]
    },
    "P102": {  # 临沂
        "memorial_sites": [
            {"name": "王羲之故居", "description": "书圣王羲之故里，苏轼或曾凭吊", "type": "古迹"},
        ]
    },
    "P104": {  # 灵隐天竺
        "memorial_sites": [
            {"name": "三天竺法镜寺", "description": "天竺三寺之一，苏轼常游", "type": "古迹"},
        ]
    },
    "P107": {  # 卢山
        "memorial_sites": [
            {"name": "卢山", "description": "密州名山，苏轼常游之地", "type": "景区"},
        ]
    },
    "P110": {  # 庐州
        "memorial_sites": [
            {"name": "包公祠", "description": "纪念包拯的祠堂，合肥名胜", "type": "古迹"},
        ]
    },
    "P111": {  # 泸州
        "memorial_sites": [
            {"name": "泸州老窖窖池", "description": "明代古窖池群，全国重点文保", "type": "古迹"},
        ]
    },
    "P114": {  # 洛阳龙门
        "memorial_sites": [
            {"name": "龙门石窟", "description": "世界文化遗产，苏轼途经洛阳或曾游览", "type": "景区"},
        ]
    },
    "P128": {  # 宁强
        "memorial_sites": [
            {"name": "青木川古镇", "description": "陕甘川交界古镇，入蜀古道驿站", "type": "古迹"},
        ]
    },
    "P129": {  # 彭山
        "memorial_sites": [
            {"name": "彭祖山", "description": "彭祖故里，长寿文化发源地", "type": "景区"},
        ]
    },
    "P130": {  # 彭山江口
        "memorial_sites": [
            {"name": "江口沉银遗址", "description": "张献忠沉银地，岷江重要渡口", "type": "古迹"},
        ]
    },
    "P139": {  # 青神平羌江
        "memorial_sites": [
            {"name": "平羌小三峡", "description": "岷江平羌峡，苏轼少年游玩地", "type": "景区"},
        ]
    },
    "P144": {  # 戎州
        "memorial_sites": [
            {"name": "宜宾大观楼", "description": "宜宾地标，登楼可览三江汇流", "type": "古迹"},
        ]
    },
    "P162": {  # 宿州
        "memorial_sites": [
            {"name": "皇藏峪", "description": "宿州名胜，传说刘邦避难处", "type": "景区"},
        ]
    },
    "P169": {  # 唐州
        "memorial_sites": [
            {"name": "泌阳白云山", "description": "唐州名山，风景秀丽", "type": "景区"},
        ]
    },
    "P174": {  # 尉氏
        "memorial_sites": [
            {"name": "阮籍啸台", "description": "竹林七贤阮籍遗迹，尉氏名胜", "type": "古迹"},
        ]
    },
    "P176": {  # 巫山神女峰
        "memorial_sites": [
            {"name": "巫山神女峰", "description": "巫山十二峰之一，'巫山神女'传说所在地", "type": "景区"},
        ]
    },
    "P186": {  # 襄城
        "memorial_sites": [
            {"name": "紫云山", "description": "襄城名胜，苏轼途经或游览", "type": "景区"},
        ]
    },
    "P188": {  # 襄阳古隆中
        "memorial_sites": [
            {"name": "古隆中", "description": "诸葛亮隐居地，三顾茅庐发生地", "type": "古迹"},
        ]
    },
    "P191": {  # 邢州
        "memorial_sites": [
            {"name": "开元寺", "description": "邢州古刹，唐代名寺", "type": "古迹"},
        ]
    },
    "P192": {  # 兴廉村净行院
        "memorial_sites": [
            {"name": "净行院遗址", "description": "苏轼南贬途中借宿的寺院", "type": "古迹"},
        ]
    },
    "P193": {  # 兴元
        "memorial_sites": [
            {"name": "古汉台", "description": "汉中刘邦发祥地，兴元府治所", "type": "古迹"},
        ]
    },
    "P201": {  # 叶县
        "memorial_sites": [
            {"name": "叶县县衙", "description": "中国现存最完整的明代县衙", "type": "古迹"},
        ]
    },
    "P212": {  # 郁林
        "memorial_sites": [
            {"name": "真武阁", "description": "容县古建筑，四大名阁之一", "type": "古迹"},
        ]
    },
    "P230": {  # 忠州
        "memorial_sites": [
            {"name": "石宝寨", "description": "长江边孤峰古寨，'江上明珠'", "type": "景区"},
        ]
    },
    "P231": {  # 资善堂
        "memorial_sites": [
            {"name": "资善堂遗址", "description": "北宋皇子读书处，汴京宫城内", "type": "古迹"},
        ]
    },
    "P232": {  # 淄州
        "memorial_sites": [
            {"name": "蒲松龄故居", "description": "淄川名胜，聊斋文化发源地", "type": "古迹"},
        ]
    },
}

updated = 0
for pid, data in DATA.items():
    pf = os.path.join(PLACES_DIR, f'{pid}.json')
    if not os.path.exists(pf):
        continue
    with open(pf, encoding='utf-8') as f:
        pd = json.load(f)
    
    changed = False
    
    # 补充美食
    if data.get('foods') and not pd.get('foods'):
        pd['foods'] = data['foods']
        changed = True
    elif data.get('foods') and pd.get('foods'):
        # 追加不重复的
        existing_names = {f['name'] for f in pd['foods']}
        for food in data['foods']:
            if food['name'] not in existing_names:
                pd['foods'].append(food)
                changed = True
    
    # 补充文旅
    if data.get('memorial_sites') and not pd.get('memorial_sites'):
        pd['memorial_sites'] = data['memorial_sites']
        changed = True
    elif data.get('memorial_sites') and pd.get('memorial_sites'):
        existing_names = {s['name'] for s in pd['memorial_sites']}
        for site in data['memorial_sites']:
            if site['name'] not in existing_names:
                pd['memorial_sites'].append(site)
                changed = True
    
    if not changed:
        continue
    
    with open(pf, 'w', encoding='utf-8') as f:
        json.dump(pd, f, ensure_ascii=False, indent=2)
    pub_pf = os.path.join(PUBLIC_DIR, f'{pid}.json')
    with open(pub_pf, 'w', encoding='utf-8') as f:
        json.dump(pd, f, ensure_ascii=False, indent=2)
    
    updated += 1
    an = pd.get('ancient_name', '')
    fc = len(pd.get('foods', []))
    mc = len(pd.get('memorial_sites', []))
    print(f"  OK {pid} {an}: 美食={fc} 文旅={mc}")

print(f"\n共更新 {updated} 个地点")
