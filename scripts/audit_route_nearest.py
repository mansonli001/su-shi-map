#!/usr/bin/env python3
"""排查路线中的离群地点：距离路线最近邻地点过远"""
import json, math

def haversine(lat1, lng1, lat2, lng2):
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
    
    place_ids = set()
    for seg in rd.get('track_segments', []):
        for pid in seg.get('place_ids', []):
            place_ids.add(pid)
    for key in ['sight_place_ids', 'around_place_ids']:
        for pid in rd.get(key, []):
            place_ids.add(pid)
    
    if len(place_ids) < 3:
        continue
    
    coords = {}
    for pid in place_ids:
        if pid in place_map:
            p = place_map[pid]
            if p.get('lat') and p.get('lng'):
                coords[pid] = (p['lat'], p['lng'])
    
    if len(coords) < 3:
        continue
    
    # 对每个地点，找路线中最近的另一个地点
    for pid, (lat, lng) in coords.items():
        min_d = float('inf')
        nearest_pid = None
        for pid2, (lat2, lng2) in coords.items():
            if pid2 == pid:
                continue
            d = haversine(lat, lng, lat2, lng2)
            if d < min_d:
                min_d = d
                nearest_pid = pid2
        
        # 距离最近邻超过80km的标记为离群
        if min_d > 80:
            an = place_map[pid].get('ancient_name', '')
            nearest_an = place_map[nearest_pid].get('ancient_name', '') if nearest_pid else ''
            outliers.append({
                'route': rid,
                'route_name': rname,
                'place_id': pid,
                'place_name': an,
                'lat': lat,
                'lng': lng,
                'nearest_id': nearest_pid,
                'nearest_name': nearest_an,
                'nearest_dist_km': round(min_d, 1),
            })

outliers.sort(key=lambda x: x['nearest_dist_km'], reverse=True)

print(f'路线离群地点排查（距最近邻地点>80km）')
print(f'共发现 {len(outliers)} 个离群地点')
print()
for o in outliers:
    print(f"  {o['route']} {o['route_name']}")
    print(f"    {o['place_id']} {o['place_name']}: ({o['lat']}, {o['lng']})")
    print(f"    最近邻: {o['nearest_id']} {o['nearest_name']}, 距离 {o['nearest_dist_km']}km")
    print()
