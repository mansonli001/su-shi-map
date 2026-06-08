#!/usr/bin/env python3
"""
P1 POI数据清洗
1. 识别错误POI（匹配到不相关商家/机构）
2. 清除错误POI
3. 对城市级POI更新为更精确的景点POI
"""
import json, os

PLACES_DIR = 'data-v4/places'
PUBLIC_DIR = 'public/data-v4/places'

# 错误POI关键词
WRONG_KW = ['中学', '小学', '学校', '家具', '床垫', '超市', '酒店', '宾馆',
            '收费站', '加油站', '银行', '医院', '诊所', '快递', '物流',
            '停车场', '4S店', '汽修', '装修', '建材', '农贸市场', '馄饨',
            '小栈', '餐厅', '火锅', '烧烤', '奶茶', '蛋糕', '糕点']

# 精确POI替换表（为关键地点提供正确的POI）
POI_FIXES = {
    "P024": {  # 赤壁
        "amap_poi_id": "B019C0KMNP",
        "amap_name": "东坡赤壁",
        "address": "赤壁大道68号",
        "location": "114.873,30.4544",
        "cityname": "黄冈市",
        "adname": "黄州区",
        "type": "风景名胜;风景名胜;国家级景点",
        "typecode": "110202",
    },
    "P072": {  # 黄州 - 已修正
        "amap_poi_id": "B019C0KMNP",
        "amap_name": "东坡赤壁",
        "address": "赤壁大道68号",
        "location": "114.873,30.4544",
        "cityname": "黄冈市",
        "adname": "黄州区",
        "type": "风景名胜;风景名胜;国家级景点",
        "typecode": "110202",
    },
    "P009": {  # 汴京翰林院
        "amap_name": "开封府",
        "address": "包公湖湖北路",
        "location": "114.3496,34.7972",
        "cityname": "开封市",
        "adname": "龙亭区",
        "type": "风景名胜;风景名胜;历史建筑",
        "typecode": "110201",
    },
    "P031": {  # 大庾岭
        "amap_name": "梅关古道景区",
        "address": "梅岭镇",
        "location": "114.031,25.258",
        "cityname": "赣州市",
        "adname": "大余县",
        "type": "风景名胜;风景名胜;国家级景点",
        "typecode": "110202",
    },
    "P032": {  # 大庾岭梅关
        "amap_name": "梅关",
        "address": "梅关古道",
        "location": "114.035,25.26",
        "cityname": "赣州市",
        "adname": "大余县",
        "type": "风景名胜;风景名胜;关隘",
        "typecode": "110201",
    },
    "P034": {  # 儋州
        "amap_name": "东坡书院",
        "address": "中和镇",
        "location": "109.4768,19.5215",
        "cityname": "儋州市",
        "adname": "中和镇",
        "type": "风景名胜;风景名胜;书院",
        "typecode": "110201",
    },
    "P036": {  # 登州
        "amap_name": "蓬莱阁景区",
        "address": "蓬莱阁",
        "location": "120.7606,37.4316",
        "cityname": "烟台市",
        "adname": "蓬莱区",
        "type": "风景名胜;风景名胜;国家级景点",
        "typecode": "110202",
    },
    "P038": {  # 定州
        "amap_name": "定州开元寺塔",
        "address": "中兴东路",
        "location": "114.9902,38.3792",
        "cityname": "定州市",
        "adname": "定州市",
        "type": "风景名胜;风景名胜;古塔",
        "typecode": "110201",
    },
    "P049": {  # 寒山寺
        "amap_name": "寒山寺",
        "address": "枫桥路",
        "location": "120.572,31.3116",
        "cityname": "苏州市",
        "adname": "姑苏区",
        "type": "风景名胜;风景名胜;寺庙",
        "typecode": "110201",
    },
    "P050": {  # 孤山
        "amap_name": "孤山公园",
        "address": "孤山路",
        "location": "120.142,30.241",
        "cityname": "杭州市",
        "adname": "西湖区",
        "type": "风景名胜;风景名胜;公园",
        "typecode": "110101",
    },
    "P068": {  # 华州
        "amap_name": "少华山国家森林公园",
        "address": "莲花寺镇",
        "location": "109.773,34.516",
        "cityname": "渭南市",
        "adname": "华州区",
        "type": "风景名胜;风景名胜;国家级景点",
        "typecode": "110202",
    },
    "P080": {  # 剑门关
        "amap_name": "剑门关景区",
        "address": "剑门关镇",
        "location": "105.8949,32.1485",
        "cityname": "广元市",
        "adname": "剑阁县",
        "type": "风景名胜;风景名胜;国家级景点",
        "typecode": "110202",
    },
    "P081": {  # 剑门关古驿
        "amap_name": "剑门关古道",
        "address": "剑门关镇",
        "location": "105.8949,32.1485",
        "cityname": "广元市",
        "adname": "剑阁县",
        "type": "风景名胜;风景名胜;古道",
        "typecode": "110201",
    },
    "P089": {  # 金陵
        "amap_name": "南京夫子庙-秦淮风光带",
        "address": "贡院街",
        "location": "118.797,32.06",
        "cityname": "南京市",
        "adname": "秦淮区",
        "type": "风景名胜;风景名胜;5A景区",
        "typecode": "110202",
    },
    "P098": {  # 雷州伏波庙
        "amap_name": "雷州伏波祠",
        "address": "雷城镇",
        "location": "110.098,20.897",
        "cityname": "雷州市",
        "adname": "雷城镇",
        "type": "风景名胜;风景名胜;祠堂",
        "typecode": "110201",
    },
    "P104": {  # 灵隐天竺
        "amap_name": "灵隐寺",
        "address": "灵隐路",
        "location": "120.102,30.2405",
        "cityname": "杭州市",
        "adname": "西湖区",
        "type": "风景名胜;风景名胜;寺庙",
        "typecode": "110201",
    },
    "P108": {  # 庐山
        "amap_name": "庐山风景名胜区",
        "address": "牯岭镇",
        "location": "115.9868,29.563",
        "cityname": "九江市",
        "adname": "庐山市",
        "type": "风景名胜;风景名胜;5A景区",
        "typecode": "110202",
    },
    "P109": {  # 庐山全山
        "amap_name": "庐山风景名胜区",
        "address": "牯岭镇",
        "location": "115.9868,29.563",
        "cityname": "九江市",
        "adname": "庐山市",
        "type": "风景名胜;风景名胜;5A景区",
        "typecode": "110202",
    },
    "P112": {  # 罗浮山
        "amap_name": "罗浮山风景名胜区",
        "address": "长宁镇",
        "location": "114.0,23.283",
        "cityname": "惠州市",
        "adname": "博罗县",
        "type": "风景名胜;风景名胜;5A景区",
        "typecode": "110202",
    },
    "P116": {  # 眉山
        "amap_name": "三苏祠",
        "address": "纱縠行南段",
        "location": "103.8315,30.0755",
        "cityname": "眉山市",
        "adname": "东坡区",
        "type": "风景名胜;风景名胜;祠堂",
        "typecode": "110201",
    },
    "P117": {  # 眉山玻璃江
        "amap_name": "岷江眉山段",
        "address": "岷江",
        "location": "103.83,30.05",
        "cityname": "眉山市",
        "adname": "东坡区",
        "type": "自然风光;河流;江河",
        "typecode": "140101",
    },
    "P119": {  # 密州
        "amap_name": "超然台",
        "address": "超然台路",
        "location": "119.4085,35.9965",
        "cityname": "诸城市",
        "adname": "诸城市",
        "type": "风景名胜;风景名胜;古迹",
        "typecode": "110201",
    },
    "P148": {  # 三潭印月
        "amap_name": "三潭印月",
        "address": "西湖",
        "location": "120.142,30.238",
        "cityname": "杭州市",
        "adname": "西湖区",
        "type": "风景名胜;风景名胜;5A景区",
        "typecode": "110202",
    },
    "P156": {  # 寿州
        "amap_name": "寿县古城墙",
        "address": "寿春镇",
        "location": "116.782,32.573",
        "cityname": "淮南市",
        "adname": "寿县",
        "type": "风景名胜;风景名胜;古城",
        "typecode": "110201",
    },
    "P158": {  # 泗水亭
        "amap_name": "泗水亭公园",
        "address": "沛县",
        "location": "117.19,34.261",
        "cityname": "徐州市",
        "adname": "沛县",
        "type": "风景名胜;风景名胜;公园",
        "typecode": "110101",
    },
    "P182": {  # 西湖苏堤
        "amap_name": "苏堤春晓",
        "address": "西湖苏堤",
        "location": "120.138,30.24",
        "cityname": "杭州市",
        "adname": "西湖区",
        "type": "风景名胜;风景名胜;5A景区",
        "typecode": "110202",
    },
    "P194": {  # 徐闻递角场
        "amap_name": "大汉三墩旅游区",
        "address": "南山镇",
        "location": "110.152,20.326",
        "cityname": "湛江市",
        "adname": "徐闻县",
        "type": "风景名胜;风景名胜;古迹",
        "typecode": "110201",
    },
    "P199": {  # 扬州平山堂
        "amap_name": "平山堂",
        "address": "大明寺内",
        "location": "119.421,32.4158",
        "cityname": "扬州市",
        "adname": "邗江区",
        "type": "风景名胜;风景名胜;古迹",
        "typecode": "110201",
    },
    "P205": {  # 宜兴
        "amap_name": "东坡书院(宜兴)",
        "address": "丁蜀镇",
        "location": "119.823,31.358",
        "cityname": "宜兴市",
        "adname": "丁蜀镇",
        "type": "风景名胜;风景名胜;书院",
        "typecode": "110201",
    },
    "P216": {  # 郓州
        "amap_name": "东平湖风景区",
        "address": "东平湖",
        "location": "116.588,35.908",
        "cityname": "泰安市",
        "adname": "东平县",
        "type": "风景名胜;风景名胜;湖泊",
        "typecode": "110201",
    },
    "P217": {  # 载酒堂
        "amap_name": "东坡书院(儋州)",
        "address": "中和镇",
        "location": "109.4768,19.5215",
        "cityname": "儋州市",
        "adname": "中和镇",
        "type": "风景名胜;风景名胜;书院",
        "typecode": "110201",
    },
    "P220": {  # 长安曲江
        "amap_name": "曲江池遗址公园",
        "address": "曲江池东路",
        "location": "108.964,34.198",
        "cityname": "西安市",
        "adname": "曲江新区",
        "type": "风景名胜;风景名胜;遗址公园",
        "typecode": "110201",
    },
    "P227": {  # 镇江金山寺
        "amap_name": "金山寺",
        "address": "金山路",
        "location": "119.4145,32.2192",
        "cityname": "镇江市",
        "adname": "润州区",
        "type": "风景名胜;风景名胜;寺庙",
        "typecode": "110201",
    },
    "P228": {  # 中和古镇
        "amap_name": "中和古镇",
        "address": "中和镇",
        "location": "109.4768,19.5215",
        "cityname": "儋州市",
        "adname": "中和镇",
        "type": "风景名胜;风景名胜;古镇",
        "typecode": "110201",
    },
}

# 第一步：清除错误POI
with open('data-v4/places-index.json') as f:
    pi = json.load(f)

wrong_poi_count = 0
cleared_count = 0
for p in pi['places']:
    pid = p['id']
    pf = os.path.join(PLACES_DIR, f'{pid}.json')
    if not os.path.exists(pf): continue
    with open(pf, encoding='utf-8') as f:
        pd = json.load(f)
    
    mv = pd.get('modern_visit', {})
    if not mv or not mv.get('amap_name'): continue
    
    poi_name = mv.get('amap_name', '')
    is_wrong = any(kw in poi_name for kw in WRONG_KW)
    
    if is_wrong:
        wrong_poi_count += 1
        if pid in POI_FIXES:
            # 有精确替换，直接替换
            pd['modern_visit'] = {**mv, **POI_FIXES[pid]}
            print(f"  FIX {pid} {pd.get('ancient_name','')}: {poi_name} → {POI_FIXES[pid]['amap_name']}")
        else:
            # 清除错误POI
            pd['modern_visit'] = {}
            cleared_count += 1
            print(f"  DEL {pid} {pd.get('ancient_name','')}: 清除错误POI [{poi_name}]")
        
        with open(pf, 'w', encoding='utf-8') as f:
            json.dump(pd, f, ensure_ascii=False, indent=2)
        pub_pf = os.path.join(PUBLIC_DIR, f'{pid}.json')
        with open(pub_pf, 'w', encoding='utf-8') as f:
            json.dump(pd, f, ensure_ascii=False, indent=2)

# 第二步：为有精确POI但没有modern_visit的地点添加
added_count = 0
for pid, poi_data in POI_FIXES.items():
    pf = os.path.join(PLACES_DIR, f'{pid}.json')
    if not os.path.exists(pf): continue
    with open(pf, encoding='utf-8') as f:
        pd = json.load(f)
    
    mv = pd.get('modern_visit', {})
    if mv and mv.get('amap_name') == poi_data.get('amap_name'):
        continue  # 已经是正确的
    
    pd['modern_visit'] = {**mv, **poi_data}
    with open(pf, 'w', encoding='utf-8') as f:
        json.dump(pd, f, ensure_ascii=False, indent=2)
    pub_pf = os.path.join(PUBLIC_DIR, f'{pid}.json')
    with open(pub_pf, 'w', encoding='utf-8') as f:
        json.dump(pd, f, ensure_ascii=False, indent=2)
    added_count += 1

print(f"\n=== POI清洗结果 ===")
print(f"错误POI总数: {wrong_poi_count}")
print(f"精确替换: {wrong_poi_count - cleared_count}")
print(f"清除无替换: {cleared_count}")
print(f"新增精确POI: {added_count}")
