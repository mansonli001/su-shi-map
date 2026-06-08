#!/usr/bin/env python3
"""排查路线中的离群地点：距离路线中心过远的地点"""
import json, math

def haversine(lat1, lng1, lat2, lng2):
    """两点间距离(km)"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.asin(a**0.5)

with open('data-v4/places-index.json') as f:
    pi = json.load(f)
place_map = {p['id']: p for p in pi['places']}

with open('data-v4/routes-index.json') as f:
    ri = json.load(f)

outliers = []

for route in ri['routes']:
    rid = route['id']
    rname = route.get('name', '')
    
    with open(f'data-v4/routes/{rid}.json') as f:
        rd = json.load(f)
    
    # 收集路线中所有地点
    place_ids = set()
    for seg in rd.get('track_segments', []):
        for pid in seg.get('place_ids', []):
            place_ids.add(pid)
    for key in ['sight_place_ids', 'around_place_ids']:
        for pid in rd.get(key, []):
            place_ids.add(pid)
    
    if len(place_ids) < 3:
        continue
    
    # 计算每个地点的坐标
    coords = {}
    for pid in place_ids:
        if pid in place_map:
            p = place_map[pid]
            if p.get('lat') and p.get('lng'):
                coords[pid] = (p['lat'], p['lng'])
    
    if len(coords) < 3:
        continue
    
    # 计算路线中心点
    lats = [c[0] for c in coords.values()]
    lngs = [c[1] for c in coords.values()]
    center_lat = sum(lats) / len(lats)
    center_lng = sum(lngs) / len(lngs)
    
    # 计算每个地点到中心的距离
    distances = []
    for pid, (lat, lng) in coords.items():
        d = haversine(lat, lng, center_lat, center_lng)
        distances.append((d, pid, lat, lng))
    
    distances.sort(reverse=True)
    
    # 计算中位距离
    median_d = distances[len(distances)//2][0]
    
    # 距离超过中位距离3倍或超过200km的标记为离群
    for d, pid, lat, lng in distances:
        an = place_map[pid].get('ancient_name', '')
        threshold = max(median_d * 3, 150)
        if d > threshold:
            outliers.append({
                'route': rid,
                'route_name': rname,
                'place_id': pid,
                'place_name': an,
                'lat': lat,
                'lng': lng,
                'distance_km': round(d, 1),
                'median_km': round(median_d, 1),
                'threshold_km': round(threshold, 1),
            })

outliers.sort(key=lambda x: x['distance_km'], reverse=True)

print(f'路线离群地点排查（距离路线中心>150km或>3倍中位距离）')
print(f'共发现 {len(outliers)} 个离群地点')
print()
for o in outliers:
    print(f"  {o['route']} {o['route_name']}")
    print(f"    {o['place_id']} {o['place_name']}: ({o['lat']}, {o['lng']})")
    print(f"    距路线中心 {o['distance_km']}km（中位距离{o['median_km']}km，阈值{o['threshold_km']}km）")
    print()
