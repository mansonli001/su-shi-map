#!/usr/bin/env python3
"""全面审查GPS精细化结果"""
import json, os, glob, subprocess

places_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'data-v4', 'places')
places_dir = os.path.normpath(places_dir)
project_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')
project_dir = os.path.normpath(project_dir)

print("=" * 70)
print("Q1: 主地点GPS更新审查")
print("=" * 70)

coord_changed = []
coord_added = []
coord_unchanged = []
no_coord = []

for i in range(1, 235):
    pid = f'P{i:03d}'
    f = os.path.join(places_dir, f'{pid}.json')
    with open(f) as fh:
        p = json.load(fh)
    
    new_lat = p.get('lat')
    new_lng = p.get('lng')
    new_src = p.get('coordinate_source', 'none')
    ancient = p.get('ancient_name', '')
    ptype = p.get('type', '')
    
    result = subprocess.run(['git', 'show', f'HEAD:data-v4/places/{pid}.json'], 
                          capture_output=True, text=True, cwd=project_dir)
    if result.returncode != 0:
        continue
    
    old = json.loads(result.stdout)
    old_lat = old.get('lat')
    old_lng = old.get('lng')
    old_src = old.get('coordinate_source', 'none')
    
    if new_lat is None:
        no_coord.append((pid, ancient, ptype))
    elif old_lat is None:
        coord_added.append((pid, ancient, ptype, new_src))
    elif old_lat != new_lat or old_lng != new_lng:
        coord_changed.append((pid, ancient, ptype, old_src, new_src, 
                            f'{old_lat},{old_lng}', f'{new_lat},{new_lng}'))
    else:
        coord_unchanged.append((pid, ancient, ptype, old_src))

print(f"总地点: 234")
print(f"坐标未变: {len(coord_unchanged)}")
print(f"坐标被替换: {len(coord_changed)}")
print(f"新增坐标: {len(coord_added)}")
print(f"仍无坐标: {len(no_coord)}")

# 坐标被替换的详情
print(f"\n--- 坐标被替换的地点（{len(coord_changed)}个）---")
for pid, name, ptype, old_src, new_src, old_c, new_c in coord_changed[:30]:
    print(f"  {pid} {name}({ptype}): {old_src}→{new_src}")
if len(coord_changed) > 30:
    print(f"  ... 还有{len(coord_changed)-30}个")

# 新增坐标的详情
print(f"\n--- 新增坐标的地点（{len(coord_added)}个）---")
for pid, name, ptype, src in coord_added[:20]:
    print(f"  {pid} {name}({ptype}): {src}")
if len(coord_added) > 20:
    print(f"  ... 还有{len(coord_added)-20}个")

# 仍无坐标
print(f"\n--- 仍无坐标的地点（{len(no_coord)}个）---")
for pid, name, ptype in no_coord:
    print(f"  {pid} {name}({ptype})")

# Q1.2: 坐标替换来源分析 - 是否有自己编纂的
print(f"\n--- 坐标来源分析 ---")
all_sources = {}
for pid, name, ptype, old_src, new_src, old_c, new_c in coord_changed:
    all_sources[new_src] = all_sources.get(new_src, 0) + 1
for pid, name, ptype, src in coord_added:
    all_sources[src] = all_sources.get(src, 0) + 1
for k, v in sorted(all_sources.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# Q1.3: type分布
print(f"\n--- 地点type分布 ---")
type_dist = {}
for pid, name, ptype, *rest in coord_changed + coord_added + [(n[0],n[1],n[2]) for n in no_coord] + coord_unchanged:
    type_dist[ptype] = type_dist.get(ptype, 0) + 1
for k, v in sorted(type_dist.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# Q2: 子地点是否列入文旅
print("\n" + "=" * 70)
print("Q2: 子地点文旅适用性审查")
print("=" * 70)

sub_for_tourism = 0
sub_no_coords = 0
sub_types = {}
sub_with_works = 0
sub_total = 0

for i in range(1, 235):
    pid = f'P{i:03d}'
    f = os.path.join(places_dir, f'{pid}.json')
    with open(f) as fh:
        p = json.load(fh)
    
    for sp in p.get('sub_places', []):
        sub_total += 1
        t = sp.get('type', 'unknown')
        sub_types[t] = sub_types.get(t, 0) + 1
        if sp.get('lat') is not None:
            sub_for_tourism += 1
        else:
            sub_no_coords += 1
        if sp.get('works') and len(sp.get('works', [])) > 0:
            sub_with_works += 1

print(f"子地点总数: {sub_total}")
print(f"有坐标（可用于文旅）: {sub_for_tourism} ({sub_for_tourism/sub_total*100:.1f}%)")
print(f"无坐标: {sub_no_coords} ({sub_no_coords/sub_total*100:.1f}%)")
print(f"有关联作品: {sub_with_works} ({sub_with_works/sub_total*100:.1f}%)")

# Q3: 三峡全程等特殊地点
print("\n" + "=" * 70)
print("Q3: 特殊地点处理情况")
print("=" * 70)

special_keywords = ['三峡', '全程', '途中', '路上', '运河', '长江', '黄河', '水路', '陆路']
for i in range(1, 235):
    pid = f'P{i:03d}'
    f = os.path.join(places_dir, f'{pid}.json')
    with open(f) as fh:
        p = json.load(fh)
    
    name = p.get('ancient_name', '')
    bg = p.get('background', '')
    ptype = p.get('type', '')
    sub = p.get('sub_places', [])
    
    for kw in special_keywords:
        if kw in name or kw in bg:
            print(f"  {pid} {name} (type={ptype})")
            print(f"    sub_places: {len(sub)}个")
            if sub:
                for s in sub[:3]:
                    print(f"      - {s.get('name','')} ({s.get('type','')}) lat={s.get('lat','N/A')}")
            break

# Q4: 作品和美食情况
print("\n" + "=" * 70)
print("Q4: 作品与美食数据现状")
print("=" * 70)

places_with_works = 0
places_with_foods = 0
total_works = 0
total_foods = 0
sub_with_works_list = []

for i in range(1, 235):
    pid = f'P{i:03d}'
    f = os.path.join(places_dir, f'{pid}.json')
    with open(f) as fh:
        p = json.load(fh)
    
    # 主地点作品
    works = p.get('works', [])
    if works:
        places_with_works += 1
        total_works += len(works)
    
    # 主地点美食
    foods = p.get('foods', [])
    if foods:
        places_with_foods += 1
        total_foods += len(foods)
    
    # 子地点作品
    for sp in p.get('sub_places', []):
        sp_works = sp.get('works', [])
        if sp_works:
            sub_with_works_list.append((pid, p.get('ancient_name',''), sp.get('name',''), sp_works))

print(f"主地点有作品: {places_with_works}/234")
print(f"主地点作品总数: {total_works}")
print(f"主地点有美食: {places_with_foods}/234")
print(f"主地点美食总数: {total_foods}")
print(f"子地点有作品: {len(sub_with_works_list)}")
if sub_with_works_list:
    print("子地点作品示例:")
    for pid, pname, sname, works in sub_with_works_list[:10]:
        print(f"  {pid} {pname} → {sname}: {works}")
