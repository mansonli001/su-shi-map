#!/usr/bin/env python3
"""查找缺美食和文旅的地点"""
import json, os

with open('data-v4/places-index.json') as f:
    pi = json.load(f)

no_food = []
no_memorial = []
skip_kw = ['古道','驿道','水路','渡口','运河','全程','全线','沿岸','风光','栈道','古驿']

for p in pi['places']:
    pid = p['id']
    pf = f'data-v4/places/{pid}.json'
    if not os.path.exists(pf): continue
    with open(pf) as f:
        pd = json.load(f)
    an = pd.get('ancient_name','')
    t = pd.get('type','')
    is_transit = any(k in an for k in skip_kw)

    if not pd.get('foods') and not is_transit:
        no_food.append((pid, an, t))
    if not pd.get('memorial_sites') and not is_transit:
        no_memorial.append((pid, an, t))

print(f'缺美食的非transit地点: {len(no_food)}')
for pid, an, t in no_food:
    print(f'  {pid} {an} ({t})')

print(f'\n缺文旅的非transit地点: {len(no_memorial)}')
for pid, an, t in no_memorial:
    print(f'  {pid} {an} ({t})')
