#!/usr/bin/env python3
"""
分析地点GPS坐标与现代景点POI的偏离
找出有modern_visit数据的地点，计算坐标偏差
"""
import json, os, math

with open('data-v4/places-index.json') as f:
    pi = json.load(f)

def haversine(lat1, lng1, lat2, lng2):
    """计算两点间距离（米）"""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

deviations = []
for p in pi['places']:
    pid = p['id']
    pf = f'data-v4/places/{pid}.json'
    if not os.path.exists(pf): continue
    with open(pf) as f:
        pd = json.load(f)
    
    mv = pd.get('modern_visit', {})
    if not mv or not mv.get('location'): continue
    
    # 解析modern_visit的坐标
    try:
        parts = mv['location'].split(',')
        mv_lng = float(parts[0])
        mv_lat = float(parts[1])
    except:
        continue
    
    # 地点的主坐标
    place_lat = pd.get('lat', 0)
    place_lng = pd.get('lng', 0)
    
    if not place_lat or not place_lng: continue
    
    dist = haversine(place_lat, place_lng, mv_lat, mv_lng)
    
    if dist > 500:  # 只显示偏差>500米的
        deviations.append({
            'id': pid,
            'name': pd.get('ancient_name', ''),
            'type': pd.get('type', ''),
            'place_lat': place_lat,
            'place_lng': place_lng,
            'poi_lat': mv_lat,
            'poi_lng': mv_lng,
            'distance': dist,
            'poi_name': mv.get('amap_name', ''),
            'poi_type': mv.get('type', ''),
            'coord_source': pd.get('coordinate_source', ''),
        })

deviations.sort(key=lambda x: -x['distance'])

print(f"GPS偏差>500米的地点: {len(deviations)}个")
print()
print(f"{'ID':6s} {'名称':12s} {'类型':8s} {'偏差(m)':8s} {'坐标来源':20s} {'POI名称'}")
print("-" * 100)
for d in deviations:
    print(f"{d['id']:6s} {d['name']:12s} {d['type']:8s} {d['distance']:8.0f} {d['coord_source']:20s} {d['poi_name']}")
