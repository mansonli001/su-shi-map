#!/usr/bin/env python3
"""修正坐标与名称不匹配的地点"""
import json, os

PLACES_DIR = 'data-v4/places'
PUBLIC_DIR = 'public/data-v4/places'

CORRECTIONS = {
    # P016 常山 - 浙江衢州常山县
    "P016": {
        "lat": 28.9030,
        "lng": 118.5020,
        "reason": "常山县在浙江衢州，原坐标(35.89,119.41)在山东日照"
    },
    # P047 赣江古道 - 江西赣州段
    "P047": {
        "lat": 25.8500,
        "lng": 114.9300,
        "reason": "赣江在江西，原坐标(29.17,121.05)在浙江宁波"
    },
    # P066 湖州西塞山 - 浙江湖州
    "P066": {
        "lat": 30.8700,
        "lng": 120.0900,
        "reason": "西塞山在浙江湖州，原坐标(30.21,115.17)在安徽安庆"
    },
    # P137 秦岭古驿 - 陕西秦岭
    "P137": {
        "lat": 33.7500,
        "lng": 107.8000,
        "reason": "秦岭在陕西，原坐标(30.39,103.58)在四川成都附近"
    },
    # P204 宜宾锁江楼 - 四川宜宾
    "P204": {
        "lat": 28.7690,
        "lng": 104.6230,
        "reason": "宜宾在四川，原坐标(29.74,116.01)在江西九江"
    },
}

# P024 赤壁 - 修正background描述
BACKGROUND_FIXES = {
    "P024": "赤壁（赤鼻矶），黄州城外长江北岸。苏轼谪居黄州时，常游赤壁，在此写下前后《赤壁赋》与《念奴娇·赤壁怀古》等千古名篇。",
    "P072": "黄州（今湖北黄冈），苏轼因乌台诗案被贬至此。谪居五年间，他躬耕东坡、自号东坡居士，创作了《赤壁赋》《念奴娇·赤壁怀古》《定风波》等名篇。",
}

updated = 0
for pid, fix in CORRECTIONS.items():
    pf = os.path.join(PLACES_DIR, f'{pid}.json')
    if not os.path.exists(pf):
        continue
    with open(pf, encoding='utf-8') as f:
        pd = json.load(f)
    
    old_lat, old_lng = pd.get('lat', 0), pd.get('lng', 0)
    pd['lat'] = fix['lat']
    pd['lng'] = fix['lng']
    
    with open(pf, 'w', encoding='utf-8') as f:
        json.dump(pd, f, ensure_ascii=False, indent=2)
    pub_pf = os.path.join(PUBLIC_DIR, f'{pid}.json')
    with open(pub_pf, 'w', encoding='utf-8') as f:
        json.dump(pd, f, ensure_ascii=False, indent=2)
    
    updated += 1
    print(f"  OK {pid} {pd.get('ancient_name','')}: ({old_lat},{old_lng}) → ({fix['lat']},{fix['lng']}) - {fix['reason']}")

# 修正background
for pid, bg in BACKGROUND_FIXES.items():
    pf = os.path.join(PLACES_DIR, f'{pid}.json')
    if not os.path.exists(pf):
        continue
    with open(pf, encoding='utf-8') as f:
        pd = json.load(f)
    
    pd['background'] = bg
    
    with open(pf, 'w', encoding='utf-8') as f:
        json.dump(pd, f, ensure_ascii=False, indent=2)
    pub_pf = os.path.join(PUBLIC_DIR, f'{pid}.json')
    with open(pub_pf, 'w', encoding='utf-8') as f:
        json.dump(pd, f, ensure_ascii=False, indent=2)
    
    print(f"  OK {pid} {pd.get('ancient_name','')}: background已修正")

print(f"\n共修正 {updated} 个坐标 + {len(BACKGROUND_FIXES)} 个背景描述")
