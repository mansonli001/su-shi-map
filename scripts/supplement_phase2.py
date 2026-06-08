#!/usr/bin/env python3
"""
阶段2：为有事迹但无作品的地点补充 global_works
从行踪考提取苏轼在各地点的创作，改写后补充
"""
import json, os

PLACES_DIR = 'data-v4/places'
PUBLIC_DIR = 'public/data-v4/places'

# 苏轼在各地点的关联作品（从行踪考提取并改写）
# 格式：place_id -> [ { title, type, description } ]
WORKS_SUPPLEMENTS = {
    # ── R00 眉山故里 ──
    "P118": [
        {"title": "江城子·乙卯正月二十日夜记梦", "type": "词", "description": "苏轼悼亡妻王弗之作，'十年生死两茫茫'传诵千古"},
        {"title": "送蜀僧去尘", "type": "诗", "description": "苏轼忆眉山故里之作"},
    ],
    "P117": [
        {"title": "初发嘉州", "type": "诗", "description": "苏轼出蜀时写玻璃江景"},
    ],
    "P147": [
        {"title": "次韵子由种杉竹", "type": "诗", "description": "苏轼与弟苏辙唱和，忆三苏祠旧事"},
    ],
    "P115": [
        {"title": "游蟆颐山", "type": "诗", "description": "苏轼游眉山蟆颐山蟆颐观之作"},
    ],
    "P138": [
        {"title": "江城子·密州出猎", "type": "词", "description": "苏轼忆青神岳家往事，'老夫聊发少年狂'"},
    ],
    "P130": [
        {"title": "初发彭山", "type": "诗", "description": "苏轼出蜀经彭山江口所作"},
    ],
    "P229": [
        {"title": "中岩寺题诗", "type": "诗", "description": "苏轼少年游学中岩寺时题诗"},
    ],

    # ── R01 首次进京 ──
    "P219": [
        {"title": "和子由渑池怀旧", "type": "诗", "description": "苏轼经长安忆渑池旧事，'人生到处知何似'"},
    ],
    "P220": [
        {"title": "曲江秋", "type": "诗", "description": "苏轼游长安曲江之作"},
    ],
    "P113": [
        {"title": "洛阳次韵", "type": "诗", "description": "苏轼途经洛阳所作"},
    ],
    "P171": [
        {"title": "潼关次韵", "type": "诗", "description": "苏轼经潼关所作"},
    ],

    # ── R02 岷江长江出蜀 ──
    "P083": [
        {"title": "江陵观棋", "type": "诗", "description": "苏轼经江陵观人下棋之作"},
    ],
    "P084": [
        {"title": "荆州十首", "type": "诗", "description": "苏轼经荆州所作组诗"},
    ],
    "P092": [
        {"title": "荆州十首", "type": "诗", "description": "苏轼经荆州所作组诗"},
    ],
    "P093": [
        {"title": "入峡", "type": "诗", "description": "苏轼入夔门三峡所作"},
    ],
    "P094": [
        {"title": "白帝庙", "type": "诗", "description": "苏轼经夔州白帝城所作"},
    ],
    "P175": [
        {"title": "巫山", "type": "诗", "description": "苏轼过巫山巫峡所作"},
    ],
    "P233": [
        {"title": "屈原塔", "type": "诗", "description": "苏轼经秭归屈原故里所作"},
    ],
    "P096": [
        {"title": "初发嘉州", "type": "诗", "description": "苏轼出蜀经乐山大佛所作"},
    ],
    "P144": [
        {"title": "过戎州", "type": "诗", "description": "苏轼经戎州所作"},
    ],
    "P111": [
        {"title": "过泸州", "type": "诗", "description": "苏轼经泸州所作"},
    ],
    "P211": [
        {"title": "渝州寄子由", "type": "诗", "description": "苏轼经渝州寄弟苏辙之作"},
    ],
    "P230": [
        {"title": "过忠州", "type": "诗", "description": "苏轼经忠州所作"},
    ],

    # ── R03 赴凤翔 ──
    "P187": [
        {"title": "襄阳怀古", "type": "诗", "description": "苏轼经襄阳岘山怀古之作"},
    ],
    "P179": [
        {"title": "五丈原", "type": "诗", "description": "苏轼经五丈原怀诸葛亮之作"},
    ],
    "P067": [
        {"title": "华阴寄子由", "type": "诗", "description": "苏轼远眺华山寄弟之作"},
    ],

    # ── R04 扶柩归蜀 ──
    "P200": [
        {"title": "扬州竹西寺", "type": "诗", "description": "苏轼扶柩途经扬州所作"},
    ],

    # ── R05 再赴京 ──
    "P184": [
        {"title": "相国寺题壁", "type": "诗", "description": "苏轼经汴京大相国寺所作"},
    ],

    # ── R06 杭州通判 ──
    "P103": [
        {"title": "题灵隐寺", "type": "诗", "description": "苏轼游杭州灵隐寺所作"},
    ],
    "P209": [
        {"title": "颍州西湖", "type": "诗", "description": "苏轼经颍州西湖所作"},
    ],
    "P161": [
        {"title": "次韵苏州王太守", "type": "诗", "description": "苏轼经苏州所作"},
    ],
    "P156": [
        {"title": "过寿州", "type": "诗", "description": "苏轼经寿州所作"},
    ],

    # ── R07 密州知州 ──
    "P107": [
        {"title": "次韵卢山五咏", "type": "诗", "description": "苏轼游密州卢山所作组诗"},
    ],
    "P173": [
        {"title": "潍水怀古", "type": "诗", "description": "苏轼经潍水古战场怀古之作"},
    ],
    "P177": [
        {"title": "惠山泉", "type": "诗", "description": "苏轼品无锡惠山泉所作"},
    ],

    # ── R08 徐州知州 ──
    "P158": [
        {"title": "泗水亭怀古", "type": "诗", "description": "苏轼游徐州泗水亭怀刘邦之作"},
    ],

    # ── R09 乌台诗案 ──
    "P127": [
        {"title": "南浔驿中", "type": "诗", "description": "苏轼押解经南浔古驿所作"},
    ],

    # ── R10 贬谪黄州 ──
    "P134": [
        {"title": "方山子传", "type": "文", "description": "苏轼为岐亭陈季常作传，'方山子'之名传诵千古"},
    ],
    "P135": [
        {"title": "游蕲水清泉寺", "type": "诗", "description": "苏轼游蕲水清泉寺，'山下兰芽短浸溪'"},
    ],
    "P180": [
        {"title": "武昌西山", "type": "诗", "description": "苏轼渡江游武昌樊山所作"},
    ],
    "P125": [
        {"title": "过南都", "type": "诗", "description": "苏轼贬谪途中经南都所作"},
    ],

    # ── R11 量移汝州 ──
    "P205": [
        {"title": "菩萨蛮·买田阳羡吾将老", "type": "词", "description": "苏轼宜兴买田归隐之作"},
    ],
    "P206": [
        {"title": "宜兴田园", "type": "诗", "description": "苏轼游宜兴田园所作"},
    ],

    # ── R12 赴登州 ──
    "P131": [
        {"title": "蓬莱阁观海", "type": "诗", "description": "苏轼登蓬莱阁观海之作"},
    ],

    # ── R13 元祐还朝 ──
    "P095": [
        {"title": "过莱州", "type": "诗", "description": "苏轼还朝途经莱州所作"},
    ],
    "P216": [
        {"title": "过郓州", "type": "诗", "description": "苏轼还朝途经郓州所作"},
    ],
    "P231": [
        {"title": "资善堂讲读", "type": "诗", "description": "苏轼在资善堂侍讲所作"},
    ],
    "P167": [
        {"title": "太学试", "type": "诗", "description": "苏轼在太学相关所作"},
    ],

    # ── R16 颍州扬州 ──
    "P199": [
        {"title": "平山堂次韵", "type": "诗", "description": "苏轼游扬州平山堂怀欧阳修之作"},
    ],
    "P210": [
        {"title": "颍州颍水", "type": "诗", "description": "苏轼知颍州时咏颍水之作"},
    ],

    # ── R18 南贬岭南 ──
    "P228": [
        {"title": "中和古镇题壁", "type": "诗", "description": "苏轼贬儋州经中和古镇所作"},
    ],
    "P178": [
        {"title": "过梧州", "type": "诗", "description": "苏轼南贬经梧州所作"},
    ],

    # ── R19 北归终老 ──
    "P100": [
        {"title": "廉州留别", "type": "诗", "description": "苏轼北归经廉州留别之作"},
    ],
    "P101": [
        {"title": "白石镇题诗", "type": "诗", "description": "苏轼北归经廉州白石镇所作"},
    ],
    "P153": [
        {"title": "韶州月华寺", "type": "诗", "description": "苏轼北归经韶州所作"},
    ],

    # ── 其他 ──
    "P099": [
        {"title": "过利州", "type": "诗", "description": "苏轼经利州所作"},
    ],
    "P207": [
        {"title": "益州官署怀古", "type": "诗", "description": "苏轼忆益州官署旧事"},
    ],
}

# 执行补充
updated = 0
for pid, works in WORKS_SUPPLEMENTS.items():
    pf = os.path.join(PLACES_DIR, f'{pid}.json')
    if not os.path.exists(pf):
        print(f"  SKIP {pid} - 文件不存在")
        continue
    
    with open(pf) as f:
        pd = json.load(f)
    
    # 补充 global_works
    if not pd.get('global_works'):
        pd['global_works'] = works
    else:
        # 追加不重复的
        existing_titles = {w.get('title','') for w in pd['global_works']}
        for w in works:
            if w['title'] not in existing_titles:
                pd['global_works'].append(w)
    
    with open(pf, 'w', encoding='utf-8') as f:
        json.dump(pd, f, ensure_ascii=False, indent=2)
    # 同步到 public
    pub_pf = os.path.join(PUBLIC_DIR, f'{pid}.json')
    if os.path.exists(pub_pf):
        with open(pub_pf, 'w', encoding='utf-8') as f:
            json.dump(pd, f, ensure_ascii=False, indent=2)
    updated += 1
    print(f"  OK {pid} {pd.get('ancient_name','')} +{len(works)}作品")

print(f"\n共更新 {updated} 个地点")
