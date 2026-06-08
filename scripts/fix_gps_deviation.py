#!/usr/bin/env python3
"""
修正GPS偏差大的地点坐标
策略：对偏差>3km的地点，用modern_visit的POI坐标替换（如果POI更准确）
或者手动修正关键地点坐标
"""
import json, os, math

PLACES_DIR = 'data-v4/places'
PUBLIC_DIR = 'public/data-v4/places'

def dist(lat1, lng1, lat2, lng2):
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2-lat1)
    dl = math.radians(lng2-lng1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))

# 手动修正的关键地点坐标（基于实际景点位置）
# 格式: place_id: (lat, lng, source_note)
MANUAL_CORRECTIONS = {
    # P024 赤壁 → 东坡赤壁公园
    "P024": (30.4544, 114.8730, "东坡赤壁公园实际位置"),
    # P072 黄州 → 黄冈市区（苏轼贬谪居住地）
    "P072": (30.4544, 114.8730, "与东坡赤壁同区域，苏轼实际居住地"),
    # P080 剑门关 → 剑门关景区
    "P080": (32.1485, 105.8949, "剑门关景区实际位置"),
    # P036 登州 → 蓬莱阁
    "P036": (37.4316, 120.7606, "蓬莱阁景区实际位置"),
    # P049 姑苏寒山寺 → 寒山寺
    "P049": (31.3116, 120.5720, "寒山寺实际位置"),
    # P108 庐山 → 庐山景区
    "P108": (29.5630, 115.9868, "庐山景区中心"),
    # P041 飞来峰 → 灵隐寺飞来峰
    "P041": (30.2426, 120.1020, "飞来峰造像实际位置"),
    # P227 镇江金山寺 → 金山寺
    "P227": (32.2192, 119.4145, "金山寺实际位置"),
    # P001 白鹤峰 → 惠州东坡祠
    "P001": (23.0896, 114.4168, "惠州东坡祠实际位置"),
    # P199 扬州平山堂 → 平山堂
    "P199": (32.4158, 119.4210, "平山堂实际位置"),
    # P148 三潭印月 → 三潭印月
    "P148": (30.2380, 120.1420, "三潭印月实际位置"),
    # P182 西湖苏堤 → 苏堤
    "P182": (30.2400, 120.1380, "苏堤实际位置"),
    # P008 汴京 → 开封府
    "P008": (34.7972, 114.3496, "开封府实际位置"),
    # P119 密州 → 诸城超然台
    "P119": (35.9965, 119.4085, "诸城超然台实际位置"),
    # P038 定州 → 定州开元寺塔
    "P038": (38.3792, 114.9902, "定州开元寺塔实际位置"),
    # P017 常州 → 常州苏轼终老地
    "P017": (31.7744, 119.9740, "常州苏轼终老地"),
    # P034 儋州 → 儋州东坡书院
    "P034": (19.5215, 109.4768, "儋州东坡书院实际位置"),
    # P051 瓜州渡 → 瓜洲古渡
    "P051": (32.2082, 119.4278, "瓜洲古渡实际位置"),
}

# 修正POI匹配错误的地点
POI_CORRECTIONS = {
    # P024 赤壁的POI匹配到了赤壁市的家具店，需要修正
    "P024": {
        "amap_poi_id": "B019C0KMNP",
        "amap_name": "东坡赤壁",
        "location": "114.873,30.4544",
        "cityname": "黄冈市",
        "adname": "黄州区",
        "type": "风景名胜;风景名胜;国家级景点",
        "typecode": "110202",
    },
}

updated = 0
for pid, (lat, lng, note) in MANUAL_CORRECTIONS.items():
    pf = os.path.join(PLACES_DIR, f'{pid}.json')
    if not os.path.exists(pf):
        continue
    
    with open(pf, encoding='utf-8') as f:
        pd = json.load(f)
    
    old_lat, old_lng = pd.get('lat', 0), pd.get('lng', 0)
    old_dist = dist(old_lat, old_lng, lat, lng) if old_lat and old_lng else 0
    
    if old_dist < 100:  # 偏差<100米不需要修正
        continue
    
    pd['lat'] = lat
    pd['lng'] = lng
    pd['coordinate_source'] = 'manual_corrected'
    
    # 修正POI数据
    if pid in POI_CORRECTIONS:
        if 'modern_visit' not in pd:
            pd['modern_visit'] = {}
        pd['modern_visit'].update(POI_CORRECTIONS[pid])
    
    with open(pf, 'w', encoding='utf-8') as f:
        json.dump(pd, f, ensure_ascii=False, indent=2)
    pub_pf = os.path.join(PUBLIC_DIR, f'{pid}.json')
    if os.path.exists(pub_pf):
        with open(pub_pf, 'w', encoding='utf-8') as f:
            json.dump(pd, f, ensure_ascii=False, indent=2)
    
    updated += 1
    an = pd.get('ancient_name', '')
    print(f"  OK {pid} {an}: ({old_lat:.4f},{old_lng:.4f}) → ({lat},{lng}) 偏差{old_dist:.0f}m [{note}]")

print(f"\n共修正 {updated} 个地点坐标")
