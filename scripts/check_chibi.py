#!/usr/bin/env python3
import json, math

def dist(lat1, lng1, lat2, lng2):
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2-lat1)
    dl = math.radians(lng2-lng1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))

# P024 赤壁
with open('data-v4/places/P024.json') as f:
    pd = json.load(f)
print('P024 赤壁:')
print(f'  主坐标: {pd.get("lat")}, {pd.get("lng")}')
mv = pd.get('modern_visit', {})
if mv and mv.get('location'):
    parts = mv['location'].split(',')
    mv_lng, mv_lat = float(parts[0]), float(parts[1])
    print(f'  POI坐标: {mv_lat}, {mv_lng}')
    print(f'  POI名称: {mv.get("amap_name")}')
    d = dist(pd['lat'], pd['lng'], mv_lat, mv_lng)
    print(f'  偏差: {d:.0f}米')
else:
    print('  无modern_visit数据')
print(f'  坐标来源: {pd.get("coordinate_source")}')

# P072 黄州
with open('data-v4/places/P072.json') as f:
    pd2 = json.load(f)
print('\nP072 黄州:')
print(f'  主坐标: {pd2.get("lat")}, {pd2.get("lng")}')
mv2 = pd2.get('modern_visit', {})
if mv2 and mv2.get('location'):
    parts = mv2['location'].split(',')
    mv2_lng, mv2_lat = float(parts[0]), float(parts[1])
    print(f'  POI坐标: {mv2_lat}, {mv2_lng}')
    print(f'  POI名称: {mv2.get("amap_name")}')
    d = dist(pd2['lat'], pd2['lng'], mv2_lat, mv2_lng)
    print(f'  偏差: {d:.0f}米')

# 东坡赤壁真实坐标（黄冈市赤壁公园）
real_lat, real_lng = 30.4544, 114.8730
print(f'\n东坡赤壁真实位置: {real_lat}, {real_lng}')
d1 = dist(pd['lat'], pd['lng'], real_lat, real_lng)
print(f'  P024赤壁距东坡赤壁: {d1:.0f}米')
d2 = dist(pd2['lat'], pd2['lng'], real_lat, real_lng)
print(f'  P072黄州距东坡赤壁: {d2:.0f}米')
