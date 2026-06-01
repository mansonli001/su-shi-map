import json

with open('data/routes-v3.json', 'r', encoding='utf-8') as f:
    routes_data = json.load(f)

with open('data/places-detailed-v3.json', 'r', encoding='utf-8') as f:
    places_data = json.load(f)

place_names = {}
for place_id, place in places_data['places'].items():
    place_names[place_id] = place['name_song']

print('# 苏轼行踪路线19条完整清单（V4数据）')
print()
print('| 序号 | route_id | 路线名称 | 时间 | 起点→终点 | 途经点数 | 途经点顺序 |')
print('|------|----------|---------|------|----------|---------|-----------|')

for i, (route_id, route) in enumerate(routes_data['routes'].items(), 1):
    route_name = route['route_name']
    start_date = route['start_date']
    end_date = route['end_date']
    place_ids = route['place_ids']
    
    start_place = place_names.get(place_ids[0], place_ids[0])
    end_place = place_names.get(place_ids[-1], place_ids[-1])
    
    places_order = []
    for j, pid in enumerate(place_ids, 1):
        name = place_names.get(pid, pid)
        places_order.append(f'{j}.{name}')
    
    places_str = ' → '.join(places_order)
    
    print(f'| {i} | {route_id} | {route_name} | {start_date}→{end_date} | {start_place}→{end_place} | {len(place_ids)}个 | {places_str} |')