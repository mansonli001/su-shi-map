#!/usr/bin/env python3
"""
区分GPS偏离类型：
1. 主坐标本身不准（需要修正主坐标）
2. POI匹配错误（需要修正POI或清除错误POI）
3. 主坐标正确但POI是城市级（如"广州市"），偏差正常
"""
import json, os, math

with open('data-v4/places-index.json') as f:
    pi = json.load(f)

def dist(lat1, lng1, lat2, lng2):
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2-lat1)
    dl = math.radians(lng2-lng1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))

# 分类统计
poi_wrong = []  # POI匹配错误（匹配到不相关地点）
poi_city = []   # POI是城市级（如"广州市"，偏差正常）
poi_ok = []     # 主坐标可能不准

for p in pi['places']:
    pid = p['id']
    pf = f'data-v4/places/{pid}.json'
    if not os.path.exists(pf): continue
    with open(pf) as f:
        pd = json.load(f)
    
    mv = pd.get('modern_visit', {})
    if not mv or not mv.get('location'): continue
    
    try:
        parts = mv['location'].split(',')
        mv_lng, mv_lat = float(parts[0]), float(parts[1])
    except:
        continue
    
    place_lat = pd.get('lat', 0)
    place_lng = pd.get('lng', 0)
    if not place_lat or not place_lng: continue
    
    d = dist(place_lat, place_lng, mv_lat, mv_lng)
    if d <= 500: continue  # 只看偏差>500m的
    
    poi_name = mv.get('amap_name', '')
    poi_type = mv.get('type', '')
    coord_src = pd.get('coordinate_source', '')
    an = pd.get('ancient_name', '')
    
    # 判断POI是否匹配错误
    is_wrong_poi = False
    wrong_keywords = ['中学', '小学', '学校', '家具', '床垫', '超市', '酒店', '宾馆',
                      '收费站', '加油站', '银行', '医院', '诊所', '快递', '物流',
                      '停车场', '4S店', '汽修', '装修', '建材', '农贸市场']
    for kw in wrong_keywords:
        if kw in poi_name:
            is_wrong_poi = True
            break
    
    # 判断是否城市级POI
    is_city_poi = False
    city_keywords = ['市', '区', '县']
    if poi_name and sum(1 for k in city_keywords if k in poi_name) >= 1 and len(poi_name) <= 4:
        is_city_poi = True
    
    entry = {
        'id': pid, 'name': an, 'type': pd.get('type',''),
        'dist': d, 'poi_name': poi_name, 'poi_type': poi_type,
        'coord_src': coord_src,
    }
    
    if is_wrong_poi:
        poi_wrong.append(entry)
    elif is_city_poi:
        poi_city.append(entry)
    else:
        poi_ok.append(entry)

print(f"=== POI匹配错误（{len(poi_wrong)}个）===")
print("这些地点的POI匹配到了不相关的商家/机构，需要重新匹配")
for e in sorted(poi_wrong, key=lambda x: -x['dist'])[:20]:
    print(f"  {e['id']} {e['name']}: 偏差{e['dist']:.0f}m, POI={e['poi_name']}")

print(f"\n=== 城市级POI（{len(poi_city)}个）===")
print("POI匹配到城市级行政区划，偏差正常（城市中心≠具体景点）")
for e in sorted(poi_city, key=lambda x: -x['dist'])[:10]:
    print(f"  {e['id']} {e['name']}: 偏差{e['dist']:.0f}m, POI={e['poi_name']}")

print(f"\n=== 需要进一步核查（{len(poi_ok)}个）===")
print("主坐标和POI都可能需要调整")
for e in sorted(poi_ok, key=lambda x: -x['dist'])[:20]:
    print(f"  {e['id']} {e['name']}: 偏差{e['dist']:.0f}m, POI={e['poi_name']}, 来源={e['coord_src']}")
