#!/usr/bin/env python3
"""
阶段8批量补充：美食+文旅（第二轮）
覆盖剩余的主要州府城市和景点
"""
import json, os

PLACES_DIR = 'data-v4/places'
PUBLIC_DIR = 'public/data-v4/places'

# 按地点ancient_name关键词匹配补充
# 格式: 关键词: {foods: [...], memorial_sites: [...]}
DATA = {
    # ── 州府城市美食+文旅 ──
    "洛阳": {
        "foods": [
            {"name": "洛阳水席", "description": "洛阳传统名宴，24道汤菜，始于唐代，苏轼途经洛阳或赴此宴"},
            {"name": "洛阳牡丹饼", "description": "洛阳名点，以牡丹花瓣入馅，酥香清雅"},
        ],
        "memorial_sites": [
            {"name": "龙门石窟", "description": "世界文化遗产，苏轼途经洛阳或曾游览", "type": "景区"},
            {"name": "白马寺", "description": "中国第一古刹，苏轼或曾到访", "type": "古迹"},
        ]
    },
    "襄阳": {
        "foods": [
            {"name": "襄阳牛肉面", "description": "襄阳传统早餐，碱面配牛肉牛杂，麻辣鲜香"},
            {"name": "襄阳黄酒", "description": "襄阳传统米酒，微甜爽口，苏轼或饮此酒"},
        ],
        "memorial_sites": [
            {"name": "襄阳古城", "description": "千年古城，苏轼途经襄阳或登城远眺", "type": "古迹"},
            {"name": "古隆中", "description": "诸葛亮隐居地，苏轼或曾凭吊", "type": "景区"},
        ]
    },
    "长安": {
        "foods": [
            {"name": "长安羊肉泡馍", "description": "长安传统名食，掰馍泡羊汤，浓香暖胃"},
            {"name": "长安肉夹馍", "description": "长安名小吃，白吉馍夹腊汁肉，酥香满口"},
        ],
        "memorial_sites": [
            {"name": "大雁塔", "description": "唐代名塔，苏轼途经长安或曾登临", "type": "古迹"},
            {"name": "曲江池", "description": "唐代名园，苏轼游长安或访此迹", "type": "景区"},
        ]
    },
    "济南": {
        "foods": [
            {"name": "济南把子肉", "description": "济南传统名菜，五花肉蒲草捆扎卤制，浓香软糯"},
            {"name": "济南甜沫", "description": "济南传统早餐，小米粥加花生豆腐丝，咸甜适口"},
        ],
        "memorial_sites": [
            {"name": "趵突泉", "description": "济南七十二名泉之首，苏轼或曾品泉", "type": "景区"},
            {"name": "大明湖", "description": "济南名湖，苏轼途经或曾游览", "type": "景区"},
        ]
    },
    "青州": {
        "foods": [
            {"name": "青州蜜桃", "description": "青州名产，桃肉细腻汁多味甜"},
            {"name": "青州煎包", "description": "青州传统小吃，皮薄馅足底焦香"},
        ],
        "memorial_sites": [
            {"name": "青州古城", "description": "古九州之一，保存完好的明清古城", "type": "古迹"},
        ]
    },
    "汝州": {
        "foods": [
            {"name": "汝州粉皮", "description": "汝州传统名吃，绿豆粉皮凉拌，爽滑筋道"},
        ],
        "memorial_sites": [
            {"name": "风穴寺", "description": "汝州古刹，苏轼量移汝州或曾到访", "type": "古迹"},
        ]
    },
    "许州": {
        "foods": [
            {"name": "许昌腐竹", "description": "许州传统名产，豆香浓郁，口感筋道"},
        ],
        "memorial_sites": [
            {"name": "春秋楼", "description": "许州古建筑，关羽夜读春秋处", "type": "古迹"},
        ]
    },
    "陕州": {
        "foods": [
            {"name": "陕州糟蛋", "description": "陕州传统名吃，鸡蛋酒糟腌制，风味独特"},
        ],
        "memorial_sites": [
            {"name": "陕州地坑院", "description": "独特地下民居，全国重点文物保护单位", "type": "古迹"},
        ]
    },
    "宿州": {
        "foods": [
            {"name": "宿州sa汤", "description": "宿州传统早餐，麦仁鸡汤熬制，浓香暖胃"},
            {"name": "符离集烧鸡", "description": "宿州名菜，卤制烧鸡色香味俱佳"},
        ],
    },
    "庐州": {
        "foods": [
            {"name": "合肥李鸿章大杂烩", "description": "庐州传统名菜，多种食材烩制，鲜香浓郁"},
            {"name": "合肥四大名点", "description": "庐州传统糕点：麻饼、烘糕、寸金、白切"},
        ],
    },
    "高邮": {
        "foods": [
            {"name": "高邮咸鸭蛋", "description": "高邮名产，蛋黄流油，苏轼途经或品此味"},
            {"name": "高邮蒲包肉", "description": "高邮传统小吃，蒲叶包肉蒸制，鲜嫩清香"},
        ],
    },
    "濠州": {
        "foods": [
            {"name": "凤阳豆腐", "description": "濠州传统名菜，豆腐烹制花样繁多"},
        ],
        "memorial_sites": [
            {"name": "明皇陵", "description": "凤阳明皇陵，朱元璋父母陵墓", "type": "古迹"},
        ]
    },
    "洪州": {
        "foods": [
            {"name": "南昌拌粉", "description": "洪州传统早餐，米粉拌酱料花生，香辣爽口"},
            {"name": "南昌瓦罐汤", "description": "洪州传统名食，瓦罐煨汤，鲜香滋补"},
        ],
        "memorial_sites": [
            {"name": "滕王阁", "description": "洪州名楼，王勃'滕王阁序'传诵千古，苏轼或曾登临", "type": "古迹"},
        ]
    },
    "江州": {
        "foods": [
            {"name": "九江茶饼", "description": "江州传统名点，酥脆香甜，佐茶佳品"},
            {"name": "九江萝卜饼", "description": "江州传统小吃，外酥内嫩，萝卜鲜香"},
        ],
        "memorial_sites": [
            {"name": "浔阳楼", "description": "江州名楼，苏轼途经或曾登临", "type": "古迹"},
        ]
    },
    "楚州": {
        "foods": [
            {"name": "淮安茶馓", "description": "楚州传统名点，油炸面食，酥脆金黄"},
            {"name": "淮安软兜", "description": "楚州传统名菜，鳝鱼烹制，鲜嫩滑爽"},
        ],
    },
    "曹州": {
        "foods": [
            {"name": "菏泽牡丹宴", "description": "曹州传统名宴，以牡丹入菜，风雅别致"},
        ],
    },
    "邓州": {
        "foods": [
            {"name": "邓州糊辣汤", "description": "邓州传统早餐，浓稠麻辣，暖胃醒神"},
        ],
    },
    "光州": {
        "foods": [
            {"name": "潢川贡面", "description": "光州传统名产，细如发丝的面条，爽滑筋道"},
        ],
    },
    "唐州": {
        "foods": [
            {"name": "唐河凉粉", "description": "唐州传统小吃，豌豆凉粉凉拌，爽滑解暑"},
        ],
    },
    "襄城": {
        "foods": [
            {"name": "襄城焖面", "description": "襄城传统面食，面条与菜肉同焖，浓香入味"},
        ],
    },
    "相州": {
        "foods": [
            {"name": "安阳三熏", "description": "相州传统名菜，熏鸡熏肉熏蛋，烟香浓郁"},
        ],
    },
    "邢州": {
        "foods": [
            {"name": "邢台道口烧鸡", "description": "邢州传统名吃，卤制烧鸡，皮酥肉嫩"},
        ],
    },
    "磁州": {
        "foods": [
            {"name": "磁州焖子", "description": "磁州传统名吃，淀粉肉末蒸制，切片蘸汁"},
        ],
    },
    "真定": {
        "foods": [
            {"name": "正定八大碗", "description": "真定传统宴席，八碗荤素搭配，实惠丰盛"},
        ],
    },
    "淄州": {
        "foods": [
            {"name": "淄博周村烧饼", "description": "淄州传统名点，薄脆芝麻饼，酥香可口"},
        ],
    },
    "临沂": {
        "foods": [
            {"name": "临沂糁汤", "description": "临沂传统早餐，麦仁肉汤熬制，浓香暖胃"},
            {"name": "临沂煎饼", "description": "沂蒙传统主食，薄如纸的杂粮煎饼"},
        ],
    },
    "海州": {
        "foods": [
            {"name": "连云港海鲜", "description": "海州临海，鱼虾贝蟹丰富，苏轼或品此鲜"},
        ],
    },
    "绵州": {
        "foods": [
            {"name": "绵阳米粉", "description": "绵州传统早餐，细米粉配红油汤底，麻辣鲜香"},
        ],
        "memorial_sites": [
            {"name": "越王楼", "description": "绵州名楼，苏轼出蜀途经或曾登临", "type": "古迹"},
        ]
    },
    "泸州": {
        "foods": [
            {"name": "泸州老窖", "description": "泸州名酒，浓香型白酒代表，苏轼出蜀或饮此酒"},
            {"name": "泸州黄粑", "description": "泸州传统名点，糯米红糖蒸制，软糯香甜"},
        ],
    },
    "戎州": {
        "foods": [
            {"name": "宜宾燃面", "description": "戎州传统名吃，干拌面条红油花生，麻辣鲜香"},
            {"name": "五粮液", "description": "戎州名酒，苏轼出蜀途经或饮此酒"},
        ],
    },
    "犍为": {
        "foods": [
            {"name": "犍为薄饼", "description": "犍为传统小吃，薄饼裹萝卜丝，蘸甜醋食用"},
        ],
    },
    "渝州": {
        "foods": [
            {"name": "重庆火锅", "description": "渝州名食，麻辣锅底涮毛肚鸭肠，鲜辣过瘾"},
            {"name": "重庆小面", "description": "渝州传统早餐，麻辣素面，筋道爽口"},
        ],
    },
    "忠州": {
        "foods": [
            {"name": "忠州豆腐乳", "description": "忠州传统名产，腐乳醇香，佐餐佳品"},
        ],
    },
    "夔州": {
        "foods": [
            {"name": "奉节脐橙", "description": "夔州名产，果大汁多味甜，苏轼出蜀或品此果"},
        ],
    },
    "巫山": {
        "foods": [
            {"name": "巫山烤鱼", "description": "巫山传统名菜，鲜鱼炭烤配蔬菜，麻辣鲜香"},
        ],
    },
    "秭归": {
        "foods": [
            {"name": "秭归脐橙", "description": "秭归名产，屈原故里特产，汁多味甜"},
        ],
        "memorial_sites": [
            {"name": "屈原祠", "description": "屈原故里纪念祠，苏轼出蜀途经或曾凭吊", "type": "古迹"},
        ]
    },
    "梓潼": {
        "foods": [
            {"name": "梓潼酥饼", "description": "梓潼传统名点，酥脆层多，芝麻香浓"},
        ],
        "memorial_sites": [
            {"name": "七曲山大庙", "description": "梓潼文昌帝君祖庭，苏轼出蜀途经或曾拜谒", "type": "古迹"},
        ]
    },
    "勉县": {
        "foods": [
            {"name": "勉县热米皮", "description": "勉县传统早餐，米皮蒸制切条，配辣油豆芽"},
        ],
        "memorial_sites": [
            {"name": "武侯墓", "description": "诸葛亮墓，苏轼途经或曾凭吊", "type": "古迹"},
        ]
    },
    "宁强": {
        "foods": [
            {"name": "宁强核桃馍", "description": "宁强传统名点，核桃仁碎入馍，酥香可口"},
        ],
    },
    "兴元": {
        "foods": [
            {"name": "汉中面皮", "description": "兴元传统名吃，米皮配辣油，爽滑麻辣"},
            {"name": "汉中菜豆腐", "description": "兴元传统小吃，豆浆点豆腐配酸菜，清淡爽口"},
        ],
    },
    "陈仓": {
        "foods": [
            {"name": "宝鸡擀面皮", "description": "陈仓传统名吃，面皮筋道配辣油，酸辣爽口"},
        ],
    },
    "华州": {
        "foods": [
            {"name": "华州面花", "description": "华州传统面食艺术，面团捏花蒸制，美观可口"},
        ],
    },
    "潼关": {
        "foods": [
            {"name": "潼关肉夹馍", "description": "潼关名吃，千层酥馍夹腊汁肉，酥脆鲜香"},
        ],
        "memorial_sites": [
            {"name": "潼关古城", "description": "关中门户，苏轼进京出蜀必经", "type": "古迹"},
        ]
    },
    "韶州": {
        "foods": [
            {"name": "韶关铜勺饼", "description": "韶州传统小吃，米浆铜勺炸制，酥脆可口"},
        ],
    },
    "南雄": {
        "foods": [
            {"name": "南雄酸笋鸭", "description": "南雄传统名菜，酸笋配鸭肉，酸辣鲜香"},
            {"name": "南雄板鸭", "description": "南雄名产，腊制板鸭，肉质紧实"},
        ],
    },
    "梧州": {
        "foods": [
            {"name": "梧州龟苓膏", "description": "梧州传统名吃，龟板土茯苓熬制，清凉解暑"},
            {"name": "梧州纸包鸡", "description": "梧州传统名菜，鸡肉纸包油炸，鲜嫩多汁"},
        ],
    },
    "郁林": {
        "foods": [
            {"name": "玉林牛巴", "description": "郁林传统名吃，牛肉腌制烘干，香韧耐嚼"},
        ],
    },
    "无锡": {
        "foods": [
            {"name": "无锡酱排骨", "description": "无锡传统名菜，排骨浓酱炖煮，甜香酥烂"},
            {"name": "无锡小笼包", "description": "无锡名点，皮薄汁多馅鲜，微甜口味"},
        ],
    },
    "彭山": {
        "foods": [
            {"name": "彭山甜皮鸭", "description": "彭山传统名菜，鸭皮刷糖色，甜香酥脆"},
        ],
    },
    "青神": {
        "foods": [
            {"name": "青神竹编", "description": "青神传统工艺，竹编精细，苏轼妻王弗家乡"},
            {"name": "青神江团鱼", "description": "青神岷江名鱼，肉质细嫩，苏轼少年或品此味"},
        ],
        "memorial_sites": [
            {"name": "中岩寺", "description": "苏轼与王弗结缘之地，'唤鱼池'传为佳话", "type": "古迹"},
        ]
    },
    "渑池": {
        "foods": [
            {"name": "渑池仰韶酒", "description": "渑池传统名酒，仰韶文化发源地，苏轼或饮此酒"},
        ],
        "memorial_sites": [
            {"name": "渑池会盟台", "description": "秦赵会盟之地，苏轼途经渑池作'和子由渑池怀旧'", "type": "古迹"},
        ]
    },
    "沂州": {
        "foods": [
            {"name": "沂州糁汤", "description": "沂州传统早餐，麦仁肉汤浓稠，暖胃解乏"},
        ],
    },
    "扶风": {
        "foods": [
            {"name": "扶风鹿糕馍", "description": "扶风传统名点，馍面印鹿纹，酥香可口"},
        ],
    },
    "凤县": {
        "foods": [
            {"name": "凤县花椒", "description": "凤县名产，大红袍花椒麻香浓郁"},
        ],
    },
    "尉氏": {
        "foods": [
            {"name": "尉氏烩面", "description": "尉氏传统面食，宽面条配羊肉汤，浓香暖胃"},
        ],
    },
    "叶县": {
        "foods": [
            {"name": "叶县烩面", "description": "叶县传统面食，面条配羊汤，鲜香暖胃"},
        ],
    },

    # ── 景点文旅补充 ──
    "灵隐": {
        "memorial_sites": [
            {"name": "灵隐寺", "description": "杭州名刹，苏轼常游访，'灵隐前唐额'诗传诵", "type": "古迹"},
        ]
    },
    "西湖": {
        "memorial_sites": [
            {"name": "西湖", "description": "苏轼疏浚西湖筑苏堤，'欲把西湖比西子'传诵千古", "type": "景区"},
        ]
    },
    "罗浮": {
        "memorial_sites": [
            {"name": "罗浮山", "description": "岭南名山，苏轼贬惠州游此，'罗浮山下四时春'", "type": "景区"},
        ]
    },
    "鄱阳": {
        "memorial_sites": [
            {"name": "鄱阳湖", "description": "中国最大淡水湖，苏轼南贬途经", "type": "景区"},
        ]
    },
    "石钟": {
        "memorial_sites": [
            {"name": "石钟山", "description": "苏轼作'石钟山记'，千古名篇", "type": "景区"},
        ]
    },
    "云龙": {
        "memorial_sites": [
            {"name": "云龙山", "description": "苏轼知徐州时常游，放鹤亭为其所建", "type": "景区"},
        ]
    },
    "超然": {
        "memorial_sites": [
            {"name": "超然台", "description": "苏轼知密州修葺，'超然台记'传诵千古", "type": "古迹"},
        ]
    },
    "大慈": {
        "memorial_sites": [
            {"name": "大慈寺", "description": "成都名刹，苏轼少年时常游", "type": "古迹"},
        ]
    },
    "澄迈": {
        "memorial_sites": [
            {"name": "澄迈老城", "description": "苏轼贬儋州途经澄迈，'澄迈驿通潮阁'诗传诵", "type": "古迹"},
        ]
    },
    "沙湖": {
        "memorial_sites": [
            {"name": "沙湖", "description": "黄州附近湖泊，苏轼游此遇雨作'定风波'", "type": "景区"},
        ]
    },
    "岐亭": {
        "memorial_sites": [
            {"name": "岐亭", "description": "苏轼贬黄州途中访陈季常处，'方山子传'即写此人", "type": "古迹"},
        ]
    },
    "蕲水": {
        "memorial_sites": [
            {"name": "清泉寺", "description": "蕲水名刹，苏轼游此作'山下兰芽短浸溪'", "type": "古迹"},
        ]
    },
    "武昌": {
        "memorial_sites": [
            {"name": "武昌西山", "description": "苏轼贬黄州时常游，'武昌西山'诗传诵", "type": "景区"},
        ]
    },
    "蓬莱": {
        "memorial_sites": [
            {"name": "蓬莱阁", "description": "苏轼到任登州五日即被召还，游蓬莱阁作诗", "type": "景区"},
        ]
    },
    "太白": {
        "memorial_sites": [
            {"name": "太白山", "description": "秦岭主峰，苏轼赴凤翔途经，'太白山下早行'诗传诵", "type": "景区"},
        ]
    },
    "五丈": {
        "memorial_sites": [
            {"name": "五丈原", "description": "诸葛亮病逝之地，苏轼途经或曾凭吊", "type": "古迹"},
        ]
    },
    "宜兴": {
        "memorial_sites": [
            {"name": "宜兴东坡书院", "description": "苏轼买田宜兴处，后建书院纪念", "type": "古迹"},
        ]
    },
}

# 加载地点索引
with open('data-v4/places-index.json') as f:
    pi = json.load(f)

# 建立名称→ID映射
name_to_id = {}
for p in pi['places']:
    an = p.get('ancient_name', '')
    mn = p.get('modern_name', '')
    name_to_id[an] = p['id']
    name_to_id[mn] = p['id']

def find_id(keyword):
    for name, pid in name_to_id.items():
        if keyword in name or name in keyword:
            return pid
    return None

# 执行补充
updated = 0
food_added = 0
memorial_added = 0

for keyword, data in DATA.items():
    pid = find_id(keyword)
    if not pid:
        print(f"  SKIP 未找到: {keyword}")
        continue

    pf = os.path.join(PLACES_DIR, f'{pid}.json')
    if not os.path.exists(pf):
        continue

    with open(pf, encoding='utf-8') as f:
        pd = json.load(f)

    changed = False

    # 补充美食
    for food in data.get('foods', []):
        if 'foods' not in pd:
            pd['foods'] = []
        existing = {f['name'] for f in pd['foods']}
        if food['name'] not in existing:
            pd['foods'].append(food)
            food_added += 1
            changed = True

    # 补充文旅
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
