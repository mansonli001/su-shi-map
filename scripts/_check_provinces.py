#!/usr/bin/env python3
import json

with open('data/places-core.json') as f:
    places = json.load(f)

PROVINCES = ['四川','陕西','河南','江苏','浙江','湖北','湖南','江西','安徽','山东','河北','广东','海南','福建','甘肃','北京','天津','上海','重庆','广西','云南','贵州','辽宁','山西']

provinces = {}
for p in places:
    mn = p.get('modernName','')
    found = False
    for prov in PROVINCES:
        if mn.startswith(prov):
            provinces.setdefault(prov,[]).append(p['id'])
            found = True
            break
    if not found:
        provinces.setdefault('其他',[]).append(p['id'])

for prov, ids in sorted(provinces.items(), key=lambda x: -len(x[1])):
    print(f'{prov}: {len(ids)}')
print(f'total: {len(places)}')

# 关键城市
for city in ['眉山','凤翔','黄州','惠州','儋州','开封']:
    ids = [p['id'] for p in places if city in p.get('modernName','') or city in p.get('songName','')]
    print(f'{city}: {ids}')

# 汴京
bj = [p['id'] for p in places if '开封' in p.get('modernName','') or '汴京' in p.get('songName','') or '汴梁' in p.get('songName','')]
print(f'汴京/开封: {bj}')
