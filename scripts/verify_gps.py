#!/usr/bin/env python3
"""
验证关键地点的主坐标是否正确
检查所有manual_corrected地点的坐标是否合理
"""
import json, os, math

PLACES_DIR = 'data-v4/places'

# 关键地点的验证坐标（基于历史地理和现代地图确认）
VERIFY = {
    "P024": {"name": "赤壁", "expect_lat": 30.45, "expect_lng": 114.87, "tolerance": 2000},
    "P072": {"name": "黄州", "expect_lat": 30.45, "expect_lng": 114.87, "tolerance": 2000},
    "P034": {"name": "儋州", "expect_lat": 19.52, "expect_lng": 109.48, "tolerance": 5000},
    "P036": {"name": "登州", "expect_lat": 37.43, "expect_lng": 120.76, "tolerance": 3000},
    "P038": {"name": "定州", "expect_lat": 38.38, "expect_lng": 114.99, "tolerance": 3000},
    "P049": {"name": "寒山寺", "expect_lat": 31.31, "expect_lng": 120.57, "tolerance": 1000},
    "P080": {"name": "剑门关", "expect_lat": 32.15, "expect_lng": 105.89, "tolerance": 3000},
    "P089": {"name": "金陵", "expect_lat": 32.06, "expect_lng": 118.80, "tolerance": 5000},
    "P108": {"name": "庐山", "expect_lat": 29.56, "expect_lng": 115.99, "tolerance": 3000},
    "P116": {"name": "眉山", "expect_lat": 30.08, "expect_lng": 103.83, "tolerance": 5000},
    "P008": {"name": "汴京", "expect_lat": 34.80, "expect_lng": 114.35, "tolerance": 3000},
    "P058": {"name": "杭州", "expect_lat": 30.25, "expect_lng": 120.15, "tolerance": 5000},
    "P161": {"name": "苏州", "expect_lat": 31.30, "expect_lng": 120.59, "tolerance": 5000},
    "P021": {"name": "成都", "expect_lat": 30.66, "expect_lng": 104.06, "tolerance": 5000},
    "P219": {"name": "长安", "expect_lat": 34.26, "expect_lng": 108.94, "tolerance": 5000},
}

def dist(lat1, lng1, lat2, lng2):
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2-lat1)
    dl = math.radians(lng2-lng1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))

ok = 0
bad = 0
for pid, v in VERIFY.items():
    pf = os.path.join(PLACES_DIR, f'{pid}.json')
    with open(pf, encoding='utf-8') as f:
        pd = json.load(f)
    
    actual_lat = pd.get('lat', 0)
    actual_lng = pd.get('lng', 0)
    d = dist(actual_lat, actual_lng, v['expect_lat'], v['expect_lng'])
    
    status = "OK" if d <= v['tolerance'] else "BAD"
    if status == "OK":
        ok += 1
    else:
        bad += 1
    print(f"  {status} {pid} {v['name']}: 偏差{d:.0f}m (容忍{v['tolerance']}m) 坐标({actual_lat},{actual_lng})")

print(f"\n验证结果: {ok}个正确, {bad}个异常")
