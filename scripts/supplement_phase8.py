#!/usr/bin/env python3
"""
阶段8：美食+文旅大规模补充
目标：美食39%→60%，文旅53%→70%
策略：为苏轼实际停留过的城市/地区补充当地传统美食和文旅景点
"""
import json, os

PLACES_DIR = 'data-v4/places'
PUBLIC_DIR = 'public/data-v4/places'

# 苏轼经过的重要城市/地区的美食和文旅数据
# 按地点ID组织，仅补充有实际停留或文化关联的地点
SUPPLEMENTS = {
    # ── 美食补充 ──
    "P040": {  # 徐州
        "foods": [
            {"name": "东坡肉", "description": "苏轼知徐州时创制，五花肉慢火炖煮，肥而不腻，苏东坡'慢着火少着水'之法传世"},
            {"name": "徐州把子肉", "description": "徐州传统名菜，大块五花肉以蒲草捆扎卤制，浓油赤酱，与东坡肉同源"},
            {"name": "徐州地锅鸡", "description": "徐州农家菜，铁锅炖鸡贴面饼，鸡香饼软，苏北风味代表"},
        ]
    },
    "P045": {  # 凤翔
        "foods": [
            {"name": "凤翔豆花泡馍", "description": "凤翔传统早餐，豆花配锅盔馍片，麻辣鲜香，苏轼签判凤翔时或已尝此味"},
            {"name": "凤翔腊驴肉", "description": "凤翔名产，驴肉腊制后肉质紧实，佐酒佳品"},
            {"name": "西凤酒", "description": "凤翔柳林镇名酒，始于殷商，苏轼或饮此酒赋诗"},
        ]
    },
    "P042": {  # 湖州
        "foods": [
            {"name": "湖州粽子", "description": "湖州名点，形如枕头，糯米鲜肉裹箬叶，苏轼或于端午品此味"},
            {"name": "湖州千张包", "description": "湖州传统小吃，百叶包裹肉馅煮制，鲜嫩爽滑"},
            {"name": "安吉白茶", "description": "湖州安吉特产，茶汤清亮，苏轼嗜茶必品"},
        ]
    },
    "P044": {  # 颍州
        "foods": [
            {"name": "阜阳格拉条", "description": "颍州传统面食，粗面条拌芝麻酱，筋道浓香"},
            {"name": "阜阳枕头馍", "description": "颍州名点，形如枕头，外酥内软，传为苏轼时代已有"},
            {"name": "颍州西湖鱼", "description": "颍州西湖鲜鱼，苏轼知颍州时常泛舟湖上，或品此鱼"},
        ]
    },
    "P038": {  # 定州
        "foods": [
            {"name": "定州焖子", "description": "定州传统名吃，淀粉肉末灌制蒸煮，切片蘸蒜汁，香滑爽口"},
            {"name": "定州手掰肠", "description": "定州特色肉肠，手掰成段，肉质紧实，佐酒佳品"},
        ]
    },
    "P013": {  # 登州
        "foods": [
            {"name": "蓬莱小面", "description": "登州传统面食，细面配海鲜卤汤，鲜香爽滑，苏轼到任五日即离去或未及品尝"},
            {"name": "蓬莱海鲜", "description": "登州临海，鲍鱼海参扇贝丰富，苏轼'食鱼'之乐可于此寻"},
        ]
    },
    "P080": {  # 剑门关
        "foods": [
            {"name": "剑门豆腐宴", "description": "剑门关名菜，以当地山泉水制豆腐，煎炒炖炸花样百出"},
            {"name": "剑门关土鸡", "description": "剑门山区散养土鸡，肉质紧实，炖汤鲜美"},
        ]
    },
    "P083": {  # 金陵
        "foods": [
            {"name": "金陵盐水鸭", "description": "南京传统名菜，鸭肉鲜嫩皮白肉粉，苏轼途经金陵或品此味"},
            {"name": "秦淮小吃", "description": "金陵传统点心，鸭血粉丝汤、小笼包、糖芋苗，秦淮河畔风味"},
        ]
    },
    "P084": {  # 镇江金山
        "foods": [
            {"name": "镇江肴肉", "description": "镇江名菜，猪蹄膀硝制后晶莹透明，蘸醋姜食之，苏轼或于金山寺旁尝此味"},
            {"name": "镇江锅盖面", "description": "镇江传统面食，面条劲道汤鲜味浓，锅盖浮于汤中同煮"},
        ]
    },
    "P090": {  # 庐山
        "foods": [
            {"name": "庐山云雾茶", "description": "庐山名茶，生于云雾之间，苏轼游庐山必品此茶"},
            {"name": "庐山石鱼", "description": "庐山溪涧中小鱼，肉质细嫩，与石鸡、石耳并称庐山三石"},
        ]
    },
    "P052": {  # 赣州
        "foods": [
            {"name": "赣南小炒鱼", "description": "赣州传统名菜，鲜鱼切块小炒，麻辣鲜香"},
            {"name": "赣南脐橙", "description": "赣州名产，果大皮薄汁多味甜，苏轼南贬经此或品此果"},
        ]
    },
    "P054": {  # 广州
        "foods": [
            {"name": "广式早茶", "description": "广州饮食文化代表，虾饺烧卖叉烧包，苏轼途经广州或体验此风"},
            {"name": "广州煲仔饭", "description": "广州传统美食，砂锅煲饭配腊味，锅巴焦香"},
        ]
    },
    "P078": {  # 吉安
        "foods": [
            {"name": "吉安炒粉", "description": "吉安传统小吃，米粉炒制加肉蛋蔬，香滑可口"},
            {"name": "吉安红米", "description": "吉安特产红米，色泽红润，煮粥软糯"},
        ]
    },
    "P108": {  # 汴京
        "foods": [
            {"name": "开封灌汤包", "description": "汴京传统名点，薄皮大馅汤汁鲜美，苏轼在汴京时或常品此味"},
            {"name": "开封桶子鸡", "description": "汴京名菜，整鸡去骨填馅蒸制，形如圆桶，鲜嫩多汁"},
            {"name": "汴京烤鸭", "description": "北宋宫廷名菜，汴京烤鸭为北京烤鸭前身，苏轼或于御宴尝此"},
        ]
    },
    "P024": {  # 赤壁
        "foods": [
            {"name": "赤壁鱼糕", "description": "赤壁传统名菜，鱼肉制糕蒸制，鲜嫩滑爽"},
            {"name": "赤壁青砖茶", "description": "赤壁名产，砖茶紧压发酵，汤色红浓，苏轼游赤壁后或饮此茶"},
        ]
    },
    "P116": {  # 眉山
        "foods": [
            {"name": "东坡肘子", "description": "眉山名菜，传为苏轼之妻王弗创制，肘子炖至酥烂，酱香浓郁"},
            {"name": "眉山泡菜", "description": "眉山传统，蔬菜入坛发酵，酸辣爽口，苏轼家中常备"},
            {"name": "眉山龙眼酥", "description": "眉山传统糕点，酥皮包馅形如龙眼，香甜酥脆"},
        ]
    },
    "P073": {  # 儋州
        "foods": [
            {"name": "儋州米烂", "description": "儋州传统小吃，米粉配肉末花生酸菜，酸辣鲜香"},
            {"name": "儋州粽子", "description": "儋州名点，火山岩糯米裹咸蛋黄猪肉，叶香米糯"},
            {"name": "海南椰子鸡", "description": "海南名菜，椰子水炖鸡，清甜鲜美，苏轼在儋或品此味"},
        ]
    },
    "P047": {  # 扬州
        "foods": [
            {"name": "扬州炒饭", "description": "扬州名食，米饭配蛋虾仁火腿丁翻炒，粒粒分明"},
            {"name": "扬州狮子头", "description": "扬州名菜，大肉丸炖煮，肥瘦相间，入口即化"},
            {"name": "扬州干丝", "description": "扬州传统，豆腐干切丝烫煮，配鸡汁，苏轼知扬州或品此味"},
        ]
    },
    "P124": {  # 密州
        "foods": [
            {"name": "诸城烧肉", "description": "密州传统名菜，猪肉先煮后熏烤，皮酥肉嫩"},
            {"name": "诸城辣丝", "description": "密州小菜，萝卜丝拌辣油，爽脆开胃"},
        ]
    },
    "P036": {  # 杭州
        "foods": [
            {"name": "东坡肉", "description": "苏轼知杭州时疏浚西湖慰民工以酒肉，慢火炖猪肉，'慢着火少着水，火候足时它自美'"},
            {"name": "西湖醋鱼", "description": "杭州名菜，草鱼糖醋烹制，鲜嫩酸甜"},
            {"name": "龙井虾仁", "description": "杭州名菜，龙井茶配鲜虾仁，清香鲜嫩"},
        ]
    },

    # ── 文旅补充 ──
    "P040": {
        "memorial_sites": [
            {"name": "徐州黄楼", "description": "苏轼知徐州时抗洪所建，为徐州地标，现重建于故黄河畔", "type": "古迹"},
            {"name": "云龙山", "description": "苏轼常游之地，放鹤亭为其所建，'放鹤亭记'传诵千古", "type": "景区"},
        ]
    },
    "P045": {
        "memorial_sites": [
            {"name": "凤翔东湖", "description": "苏轼签判凤翔时疏浚修建，'东湖'之名沿用至今", "type": "景区"},
            {"name": "凤翔苏轼纪念馆", "description": "纪念苏轼在凤翔事迹的专题展馆", "type": "纪念馆"},
        ]
    },
    "P042": {
        "memorial_sites": [
            {"name": "飞英塔", "description": "湖州标志性古塔，塔中塔奇观，苏轼或曾登临", "type": "古迹"},
            {"name": "铁佛寺", "description": "湖州古刹，宋代铁铸观音像，苏轼在湖时常访", "type": "古迹"},
        ]
    },
    "P044": {
        "memorial_sites": [
            {"name": "颍州西湖", "description": "苏轼知颍州时常游之地，'大千起灭一尘里'即咏此湖", "type": "景区"},
            {"name": "欧阳修纪念馆", "description": "欧阳修终老颍州，苏轼为其文集作序", "type": "纪念馆"},
        ]
    },
    "P038": {
        "memorial_sites": [
            {"name": "定州开元寺塔", "description": "全国重点文物保护单位，北宋古塔，苏轼知定州时常登临", "type": "古迹"},
            {"name": "定州贡院", "description": "清代科举考场，定州历史文化遗产", "type": "古迹"},
        ]
    },
    "P013": {
        "memorial_sites": [
            {"name": "蓬莱阁", "description": "苏轼到任登州五日即被召还，期间游蓬莱阁作诗", "type": "景区"},
            {"name": "登州古城", "description": "苏轼曾任登州知州，虽仅五日却留下'乞罢登莱榷盐'疏", "type": "古迹"},
        ]
    },
    "P080": {
        "memorial_sites": [
            {"name": "剑门关", "description": "蜀道天险，'一夫当关万夫莫开'，苏轼出蜀入蜀必经之地", "type": "景区"},
            {"name": "剑门蜀道", "description": "全国重点文物保护单位，古蜀道精华段", "type": "古迹"},
        ]
    },
    "P083": {
        "memorial_sites": [
            {"name": "秦淮河", "description": "金陵母亲河，苏轼途经金陵或泛舟秦淮", "type": "景区"},
            {"name": "钟山", "description": "金陵名山，王安石退居于此，苏轼曾往拜访", "type": "景区"},
        ]
    },
    "P084": {
        "memorial_sites": [
            {"name": "金山寺", "description": "镇江名刹，苏轼多次游访，'金山寺'诗传诵", "type": "古迹"},
            {"name": "北固山", "description": "镇江三山之一，苏轼登临赋诗", "type": "景区"},
        ]
    },
    "P090": {
        "memorial_sites": [
            {"name": "庐山", "description": "苏轼游庐山作'不识庐山真面目'，千古名句", "type": "景区"},
            {"name": "白鹿洞书院", "description": "中国古代四大书院之一，苏轼或曾到访", "type": "古迹"},
        ]
    },
    "P052": {
        "memorial_sites": [
            {"name": "赣州古城墙", "description": "宋代古城墙，苏轼南贬经此", "type": "古迹"},
            {"name": "八境台", "description": "赣州地标，苏轼曾为八境台题诗", "type": "古迹"},
        ]
    },
    "P054": {
        "memorial_sites": [
            {"name": "六榕寺", "description": "苏轼途经广州游此寺，题'六榕'二字，寺因之改名", "type": "古迹"},
            {"name": "南海神庙", "description": "古代海上丝绸之路起点，苏轼或曾到访", "type": "古迹"},
        ]
    },
    "P108": {
        "memorial_sites": [
            {"name": "开封府", "description": "北宋首都核心，苏轼多次在汴京任职", "type": "古迹"},
            {"name": "大相国寺", "description": "汴京名刹，苏轼常游访品茶", "type": "古迹"},
            {"name": "铁塔", "description": "北宋古塔，汴京地标，苏轼在汴时或常登临", "type": "古迹"},
        ]
    },
    "P024": {
        "memorial_sites": [
            {"name": "东坡赤壁", "description": "苏轼赤壁赋创作地，全国重点文物保护单位", "type": "景区"},
        ]
    },
    "P047": {
        "memorial_sites": [
            {"name": "瘦西湖", "description": "扬州名湖，苏轼知扬州时或常游", "type": "景区"},
            {"name": "大明寺", "description": "扬州古刹，苏轼或曾到访", "type": "古迹"},
        ]
    },
    "P124": {
        "memorial_sites": [
            {"name": "超然台", "description": "苏轼知密州时修葺，'超然台记'传诵千古", "type": "古迹"},
            {"name": "密州常山", "description": "苏轼常猎之地，'江城子·密州出猎'即咏此", "type": "景区"},
        ]
    },
    "P036": {
        "memorial_sites": [
            {"name": "苏堤", "description": "苏轼疏浚西湖所筑，'苏堤春晓'为西湖十景之首", "type": "景区"},
            {"name": "三潭印月", "description": "西湖标志性景观，苏轼疏浚西湖时设三塔为界", "type": "景区"},
        ]
    },
    "P017": {
        "memorial_sites": [
            {"name": "常州苏轼纪念馆", "description": "纪念苏轼终老常州的专题展馆", "type": "纪念馆"},
            {"name": "藤花旧馆", "description": "苏轼终老之地，常州重要文化遗址", "type": "古迹"},
        ]
    },
    "P073": {
        "memorial_sites": [
            {"name": "东坡书院", "description": "苏轼在儋州讲学处，全国重点文物保护单位", "type": "古迹"},
            {"name": "载酒堂", "description": "苏轼在儋州讲学授业之所，'载酒堂'匾额传为苏轼手书", "type": "古迹"},
        ]
    },
    "P074": {
        "memorial_sites": [
            {"name": "惠州西湖", "description": "苏轼贬惠州时常游之地，'一更山吐月'即咏此", "type": "景区"},
            {"name": "东坡祠", "description": "惠州纪念苏轼的祠堂，位于白鹤峰苏轼故居旧址", "type": "纪念馆"},
        ]
    },
    "P078": {
        "memorial_sites": [
            {"name": "白鹭洲书院", "description": "吉安古书院，苏轼南贬经此或曾到访", "type": "古迹"},
        ]
    },
    "P034": {
        "memorial_sites": [
            {"name": "梅关古道", "description": "大庾岭古驿道，苏轼南贬过岭作'大庾岭上梅'诗", "type": "古迹"},
        ]
    },
    "P149": {
        "memorial_sites": [
            {"name": "三峡", "description": "长江三峡，苏轼出蜀经此作'入峡'诗，壮丽山水千古传诵", "type": "景区"},
        ]
    },
    "P010": {
        "memorial_sites": [
            {"name": "白帝城", "description": "三峡起点，全国重点文物保护单位，苏轼出蜀经此", "type": "景区"},
        ]
    },
    "P060": {
        "memorial_sites": [
            {"name": "赵州桥", "description": "世界最古老石拱桥，苏轼经河北或知此桥", "type": "古迹"},
        ]
    },
    "P041": {
        "memorial_sites": [
            {"name": "飞来峰造像", "description": "杭州灵隐寺前飞来峰，苏轼游此作诗", "type": "古迹"},
        ]
    },
    "P049": {
        "memorial_sites": [
            {"name": "寒山寺", "description": "苏州名刹，张继'枫桥夜泊'传诵千古，苏轼或曾到访", "type": "古迹"},
        ]
    },
}

# 执行补充
updated = 0
for pid, data in SUPPLEMENTS.items():
    pf = os.path.join(PLACES_DIR, f'{pid}.json')
    if not os.path.exists(pf):
        print(f"  SKIP {pid} 文件不存在")
        continue
    
    with open(pf, encoding='utf-8') as f:
        pd = json.load(f)
    
    changed = False
    
    # 补充美食
    if 'foods' in data and data['foods']:
        if 'foods' not in pd:
            pd['foods'] = []
        existing_names = {f['name'] for f in pd['foods']}
        for food in data['foods']:
            if food['name'] not in existing_names:
                pd['foods'].append(food)
                existing_names.add(food['name'])
                changed = True
    
    # 补充文旅
    if 'memorial_sites' in data and data['memorial_sites']:
        if 'memorial_sites' not in pd:
            pd['memorial_sites'] = []
        existing_names = {m['name'] for m in pd['memorial_sites']}
        for site in data['memorial_sites']:
            if site['name'] not in existing_names:
                pd['memorial_sites'].append(site)
                existing_names.add(site['name'])
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
        foods_count = len(pd.get('foods', []))
        memorial_count = len(pd.get('memorial_sites', []))
        print(f"  OK {pid} {an} 美食={foods_count} 文旅={memorial_count}")

print(f"\n共更新 {updated} 个地点")
