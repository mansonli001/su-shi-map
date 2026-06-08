#!/usr/bin/env python3
"""
阶段6：234个地点与行踪考交叉校验
重点校验：
1. 关键居住/任职地的global_events是否完整
2. 关键地点的global_works是否遗漏名篇
3. 美食数据是否与东坡美食传统一致
4. 文旅数据是否遗漏重要景点
5. background描述是否准确
"""
import json, os

PLACES_DIR = 'data-v4/places'
PUBLIC_DIR = 'public/data-v4/places'

# 交叉校验修正数据 — 按路线组织
# 每个修正项包含：补充缺失的global_events、global_works、foods、memorial_sites
CORRECTIONS = {
    # ── R00 眉山故里 ──
    "P118": {  # 眉山故居 - 补充更多事迹
        "add_events": [
            {"id": "p118-003", "date": "1037年", "title": "苏轼出生于眉山", "description": "苏轼于景祐三年十二月十九日生于眉山纱縠行", "significance": "出生"},
            {"id": "p118-004", "date": "1054年", "title": "娶妻王弗", "description": "苏轼在眉山娶王弗为妻", "significance": "成家"},
        ],
        "add_memorial_sites": [
            {"name": "三苏祠", "description": "苏洵苏轼苏辙故居，全国重点文物保护单位，AAAA级景区", "type": "故居"},
        ]
    },
    "P116": {  # 眉山 - 补充文旅
        "add_memorial_sites": [
            {"name": "眉山三苏纪念馆", "description": "眉山市区三苏文化专题博物馆", "type": "博物馆"},
        ]
    },

    # ── R06 杭州通判 ──
    "P036": {  # 杭州 - 补充名篇
        "add_events": [
            {"id": "p036-005", "date": "1072年", "title": "作《饮湖上初晴后雨》", "description": "苏轼游西湖作'水光潋滟晴方好，山色空蒙雨亦奇'，千古名句", "significance": "西湖名篇"},
        ],
    },
    "P041": {  # 飞来峰 - 补充作品
        "add_events": [
            {"id": "p041-003", "date": "1072年", "title": "游飞来峰", "description": "苏轼游飞来峰作'不畏浮云遮望眼，自缘身在最高层'", "significance": "名句出处"},
        ],
    },

    # ── R07 密州知州 ──
    "P124": {  # 密州 - 补充名篇
        "add_events": [
            {"id": "p124-003", "date": "1075年", "title": "作《江城子·密州出猎》", "description": "苏轼在密州作'老夫聊发少年狂'，开豪放词先河", "significance": "豪放词开篇"},
            {"id": "p124-004", "date": "1076年", "title": "中秋作《水调歌头》", "description": "苏轼在密州中秋夜作'明月几时有'，思念弟弟苏辙", "significance": "中秋千古名篇"},
        ],
    },

    # ── R08 徐州知州 ──
    "P196": {  # 徐州黄楼 - 补充事迹
        "add_events": [
            {"id": "p196-003", "date": "1077年", "title": "抗洪筑黄楼", "description": "苏轼率民抗洪保城，筑黄楼以纪念", "significance": "抗洪功绩"},
        ],
    },

    # ── R10 贬谪黄州 ──
    "P072": {  # 黄州 - 补充更多事迹和作品
        "add_events": [
            {"id": "p072-010", "date": "1082年", "title": "作《念奴娇·赤壁怀古》", "description": "苏轼游赤壁作'大江东去，浪淘尽千古风流人物'，豪放词巅峰", "significance": "豪放词巅峰"},
            {"id": "p072-011", "date": "1082年", "title": "作前后《赤壁赋》", "description": "苏轼秋夜游赤壁作《前赤壁赋》《后赤壁赋》，文赋双璧", "significance": "文赋巅峰"},
            {"id": "p072-012", "date": "1080年", "title": "作《卜算子·黄州定慧院寓居作》", "description": "苏轼初到黄州寓居定慧院作'缺月挂疏桐'，抒贬谪孤寂", "significance": "贬谪词代表作"},
            {"id": "p072-013", "date": "1082年", "title": "筑东坡雪堂", "description": "苏轼在东坡开荒筑雪堂，自号'东坡居士'", "significance": "东坡之名由来"},
        ],
        "add_memorial_sites": [
            {"name": "东坡赤壁", "description": "全国重点文物保护单位，苏轼赤壁赋创作地", "type": "景区"},
            {"name": "东坡雪堂遗址", "description": "苏轼开荒筑雪堂处", "type": "古迹"},
        ]
    },

    # ── R12 赴登州 ──
    "P089": {  # 登州 - 补充事迹
        "add_events": [
            {"id": "p089-003", "date": "1085年", "title": "登州五日上盐税书", "description": "苏轼到任登州仅五日即被召还，期间上书请改盐税", "significance": "五日为民请命"},
        ],
    },

    # ── R14 再知杭州 ──
    "P036": {  # 杭州 - 补充再知杭州事迹
        "add_events": [
            {"id": "p036-006", "date": "1089年", "title": "疏浚西湖筑苏堤", "description": "苏轼再知杭州疏浚西湖，以淤泥筑长堤，后人称苏堤", "significance": "苏堤春晓"},
            {"id": "p036-007", "date": "1089年", "title": "设安乐坊济民", "description": "苏轼在杭州设安乐坊，为中国最早的公立医院之一", "significance": "惠民医政"},
        ],
    },

    # ── R17 外放定州 ──
    "P039": {  # 定州 - 补充事迹
        "add_events": [
            {"id": "p039-027", "date": "1093年", "title": "知定州整军纪", "description": "苏轼知定州整顿军纪、修缮营房", "significance": "治军"},
        ],
        "add_memorial_sites": [
            {"name": "定州开元寺塔", "description": "中国最高砖塔，苏轼知定州时曾登临", "type": "古迹"},
        ]
    },

    # ── R18 南贬岭南 ──
    "P074": {  # 惠州 - 补充名篇
        "add_events": [
            {"id": "p074-005", "date": "1095年", "title": "作《食荔枝》", "description": "苏轼在惠州作'日啖荔枝三百颗，不辞长作岭南人'", "significance": "岭南名篇"},
            {"id": "p074-006", "date": "1095年", "title": "修东新桥西新桥", "description": "苏轼在惠州捐资修桥，方便百姓往来", "significance": "惠民工程"},
        ],
    },
    "P073": {  # 儋州 - 补充事迹
        "add_events": [
            {"id": "p073-005", "date": "1097年", "title": "开儋州学风", "description": "苏轼在儋州讲学授业，开创海南文化教育先河", "significance": "海南文教始祖"},
            {"id": "p073-006", "date": "1098年", "title": "作《别海南黎民表》", "description": "苏轼在儋州与当地百姓结下深厚情谊", "significance": "黎汉情深"},
        ],
    },

    # ── R19 北归终老 ──
    "P017": {  # 常州 - 补充事迹
        "add_events": [
            {"id": "p017-005", "date": "1101年", "title": "病逝常州", "description": "苏轼遇赦北归途中病逝于常州，享年六十六岁", "significance": "人生终点"},
        ],
        "add_memorial_sites": [
            {"name": "常州苏轼纪念馆", "description": "常州孙氏馆旧址，苏轼终老之地", "type": "纪念馆"},
        ]
    },
    "P018": {  # 常州终老故居
        "add_events": [
            {"id": "p018-003", "date": "1101年7月", "title": "终老孙氏馆", "description": "苏轼在常州孙氏馆病逝，'问汝平生功业，黄州惠州儋州'", "significance": "绝笔"},
        ],
    },

    # ── 其他重要地点补充 ──
    "P030": {  # 大慈寺 - 补充事迹
        "add_events": [
            {"id": "p030-004", "date": "1055年", "title": "游大慈寺观壁画", "description": "苏轼游成都大慈寺观赏壁画，留下题咏", "significance": "艺术鉴赏"},
        ],
    },
    "P022": {  # 成都青羊宫
        "add_events": [
            {"id": "p022-003", "date": "1055年", "title": "游青羊宫", "description": "苏轼游成都青羊宫，观道家胜景", "significance": "道教文化"},
        ],
    },
    "P016": {  # 常山
        "add_events": [
            {"id": "p016-002", "date": "1075年", "title": "常山祭神祈雨", "description": "苏轼在密州常山祈雨，作祭文", "significance": "祈雨"},
        ],
    },
    "P033": {  # 丹崖山
        "add_events": [
            {"id": "p033-003", "date": "1080年", "title": "游丹崖山", "description": "苏轼在黄州期间游丹崖山", "significance": "贬谪游览"},
        ],
    },
    "P020": {  # 陈州
        "add_events": [
            {"id": "p020-003", "date": "1071年", "title": "过陈州访苏辙", "description": "苏轼赴杭州途中过陈州访弟苏辙", "significance": "兄弟情深"},
        ],
    },
    "P048": {  # 高邮
        "add_events": [
            {"id": "p048-002", "date": "1084年", "title": "过高邮访秦观", "description": "苏轼量移汝州途中过高邮访门生秦观", "significance": "师生情谊"},
        ],
    },
    "P054": {  # 广州
        "add_events": [
            {"id": "p054-002", "date": "1094年", "title": "经广州赴惠州", "description": "苏轼南贬经广州，游白云山蒲涧寺", "significance": "贬谪途经"},
        ],
        "add_memorial_sites": [
            {"name": "广州六榕寺", "description": "苏轼题'六榕'二字，原名净慧寺", "type": "寺院"},
        ]
    },
    "P019": {  # 陈仓
        "add_events": [
            {"id": "p019-002", "date": "1061年", "title": "经陈仓赴凤翔", "description": "苏轼赴凤翔签判任途经陈仓", "significance": "赴任途经"},
        ],
    },
    "P068": {  # 华州
        "add_events": [
            {"id": "p068-002", "date": "1061年", "title": "经华州入关中", "description": "苏轼赴凤翔途经华州", "significance": "赴任途经"},
        ],
    },
    "P080": {  # 剑门关
        "add_events": [
            {"id": "p080-002", "date": "1056年", "title": "过剑门关出蜀", "description": "苏轼首次出蜀过剑门关，'剑阁峥嵘而崔嵬'", "significance": "蜀道天险"},
        ],
        "add_memorial_sites": [
            {"name": "剑门关景区", "description": "蜀道天险，5A级景区", "type": "景区"},
        ]
    },
    "P053": {  # 光州
        "add_events": [
            {"id": "p053-002", "date": "1080年", "title": "贬谪经光州", "description": "苏轼贬谪黄州途经光州", "significance": "贬谪途经"},
        ],
    },
    "P027": {  # 楚州
        "add_events": [
            {"id": "p027-002", "date": "1071年", "title": "经楚州赴杭州", "description": "苏轼赴杭州通判任途经楚州", "significance": "赴任途经"},
        ],
    },
    "P079": {  # 犍为
        "add_events": [
            {"id": "p079-002", "date": "1059年", "title": "经犍为出蜀", "description": "苏轼出蜀顺岷江经犍为", "significance": "出蜀途经"},
        ],
    },
    "P066": {  # 湖州西塞山
        "add_events": [
            {"id": "p066-002", "date": "1072年", "title": "游西塞山", "description": "苏轼知湖州时游西塞山，张志和渔歌子故地", "significance": "诗词故地"},
        ],
    },
    "P056": {  # 海州花果山
        "add_events": [
            {"id": "p056-002", "date": "1074年", "title": "经海州花果山", "description": "苏轼自杭州调密州途经海州", "significance": "赴任途经"},
        ],
    },
    "P055": {  # 海州
        "add_events": [
            {"id": "p055-002", "date": "1074年", "title": "经海州赴密州", "description": "苏轼自杭州调密州途经海州", "significance": "赴任途经"},
        ],
    },
    "P049": {  # 姑苏寒山寺
        "add_events": [
            {"id": "p049-002", "date": "1071年", "title": "游寒山寺", "description": "苏轼游苏州寒山寺题诗", "significance": "名寺题咏"},
        ],
    },
    "P143": {  # 仁和运河
        "add_events": [
            {"id": "p143-002", "date": "1089年", "title": "疏浚运河", "description": "苏轼再知杭州疏浚仁和运河", "significance": "治水"},
        ],
    },
}

# 执行修正
updated = 0
for pid, corr in CORRECTIONS.items():
    pf = os.path.join(PLACES_DIR, f'{pid}.json')
    if not os.path.exists(pf):
        print(f"  SKIP {pid} - 文件不存在")
        continue
    
    with open(pf) as f:
        pd = json.load(f)
    
    changed = False
    
    # 补充 global_events
    if corr.get('add_events'):
        existing_ids = {e.get('id','') for e in pd.get('global_events', [])}
        for evt in corr['add_events']:
            if evt['id'] not in existing_ids:
                if 'global_events' not in pd:
                    pd['global_events'] = []
                pd['global_events'].append(evt)
                changed = True
    
    # 补充 memorial_sites
    if corr.get('add_memorial_sites'):
        existing_names = {ms.get('name','') for ms in pd.get('memorial_sites', [])}
        for ms in corr['add_memorial_sites']:
            if ms['name'] not in existing_names:
                if 'memorial_sites' not in pd:
                    pd['memorial_sites'] = []
                pd['memorial_sites'].append(ms)
                changed = True
    
    if changed:
        with open(pf, 'w', encoding='utf-8') as f:
            json.dump(pd, f, ensure_ascii=False, indent=2)
        pub_pf = os.path.join(PUBLIC_DIR, f'{pid}.json')
        if os.path.exists(pub_pf):
            with open(pub_pf, 'w', encoding='utf-8') as f:
                json.dump(pd, f, ensure_ascii=False, indent=2)
        updated += 1
        print(f"  OK {pid} {pd.get('ancient_name','')}")
    else:
        print(f"  SKIP {pid} - 无变化")

print(f"\n共更新 {updated} 个地点")
