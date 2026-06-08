#!/usr/bin/env python3
"""
分析所有v4地点的数据丰富度，为批量处理制定策略
"""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(SCRIPT_DIR, '..', '..', '..')
PLACES_DIR = os.path.join(PROJECT_DIR, 'data-v4', 'places')

def analyze_places():
    results = []
    
    for filename in sorted(os.listdir(PLACES_DIR)):
        if not filename.endswith('.json'):
            continue
        
        filepath = os.path.join(PLACES_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        place_id = data.get('id', '')
        ancient_name = data.get('ancient_name', '')
        modern_name = data.get('modern_name', '')
        
        # 计算数据丰富度
        global_events = data.get('global_events', [])
        global_works = data.get('global_works', [])
        memorial_sites = data.get('memorial_sites', [])
        route_events = data.get('route_events', {})
        sub_places = data.get('sub_places', [])
        foods = data.get('foods', [])
        
        # 提取居住地关键词
        residence_keywords = ['寓居', '居住', '移居', '迁居', '住', '居', '贬', '谪', '安置']
        residence_found = []
        for event in global_events:
            desc = event.get('description', '')
            title = event.get('title', '')
            for kw in residence_keywords:
                if kw in desc or kw in title:
                    residence_found.append({
                        'event_id': event.get('id', ''),
                        'title': title,
                        'desc_snippet': desc[:50]
                    })
                    break
        
        # 提取创作地点
        work_locations = set()
        for work in global_works:
            loc = work.get('location', '')
            if loc:
                # 去掉城市名前缀
                loc_clean = loc.replace(ancient_name, '').strip()
                if loc_clean:
                    work_locations.add(loc_clean)
        
        # 提取路线事件中的居住信息
        route_residences = []
        for route_id, route_val in route_events.items():
            # route_events值可能是dict或list
            if isinstance(route_val, dict):
                story = route_val.get('su_shi_story', '')
                for kw in residence_keywords:
                    if kw in story:
                        route_residences.append({
                            'route_id': route_id,
                            'story_snippet': story[:80]
                        })
                        break
            elif isinstance(route_val, list):
                for item in route_val:
                    if isinstance(item, dict):
                        story = item.get('su_shi_story', '')
                        for kw in residence_keywords:
                            if kw in story:
                                route_residences.append({
                                    'route_id': route_id,
                                    'story_snippet': story[:80]
                                })
                                break
        
        # 计算丰富度分数
        score = 0
        score += len(global_events) * 2
        score += len(global_works) * 1
        score += len(memorial_sites) * 3
        score += len(work_locations) * 2
        score += len(residence_found) * 3
        score += len(route_residences) * 2
        score += len(foods) * 1
        
        # 分级
        if score >= 20:
            grade = 'A'
        elif score >= 10:
            grade = 'B'
        elif score >= 5:
            grade = 'C'
        else:
            grade = 'D'
        
        results.append({
            'place_id': place_id,
            'ancient_name': ancient_name,
            'modern_name': modern_name,
            'grade': grade,
            'score': score,
            'global_events_count': len(global_events),
            'global_works_count': len(global_works),
            'memorial_sites_count': len(memorial_sites),
            'work_locations': list(work_locations),
            'residence_found': residence_found,
            'route_residences': route_residences,
            'has_sub_places': len(sub_places) > 0,
            'has_coords': data.get('lat') is not None and data.get('lng') is not None,
            'coordinate_source': data.get('coordinate_source', ''),
            'type': data.get('type', '')
        })
    
    # 统计
    grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
    for r in results:
        grade_counts[r['grade']] += 1
    
    print("=" * 70)
    print("📊 234个地点数据丰富度分析")
    print("=" * 70)
    print(f"\n分级标准：")
    print(f"  A级 (≥20分): 数据丰富，可自动提取子地点 → {grade_counts['A']}个")
    print(f"  B级 (10-19分): 数据中等，需半自动补充 → {grade_counts['B']}个")
    print(f"  C级 (5-9分): 数据较少，需手动补充 → {grade_counts['C']}个")
    print(f"  D级 (<5分): 数据稀少，需从行踪考提取 → {grade_counts['D']}个")
    
    # 按级别输出
    for grade in ['A', 'B', 'C', 'D']:
        grade_results = [r for r in results if r['grade'] == grade]
        if not grade_results:
            continue
        
        print(f"\n{'='*70}")
        print(f"{'A' if grade == 'A' else 'B' if grade == 'B' else 'C' if grade == 'C' else 'D'}级地点 ({len(grade_results)}个)")
        print(f"{'='*70}")
        
        for r in sorted(grade_results, key=lambda x: -x['score']):
            residence_info = ''
            if r['residence_found']:
                residence_info = f" | 居住: {len(r['residence_found'])}"
            
            work_loc_info = ''
            if r['work_locations']:
                work_loc_info = f" | 创作地: {', '.join(r['work_locations'][:3])}"
            
            coords_info = '✅' if r['has_coords'] else '❌'
            sub_info = '📦' if r['has_sub_places'] else '⬜'
            
            print(f"  {r['place_id']} {r['ancient_name']}({r['modern_name']}) "
                  f"[{r['score']}分] 事件:{r['global_events_count']} 作品:{r['global_works_count']} "
                  f"景点:{r['memorial_sites_count']}{residence_info}{work_loc_info} "
                  f"坐标:{coords_info} 子地点:{sub_info}")
    
    # 保存详细结果
    output_file = os.path.join(SCRIPT_DIR, 'reports', 'place_richness_analysis.json')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细分析已保存: {output_file}")
    
    # 输出可自动处理的地点列表
    auto_processable = [r for r in results if r['grade'] in ('A', 'B') and not r['has_sub_places']]
    print(f"\n🚀 可自动/半自动处理的地点: {len(auto_processable)}个")
    print(f"   A级: {len([r for r in auto_processable if r['grade'] == 'A'])}个")
    print(f"   B级: {len([r for r in auto_processable if r['grade'] == 'B'])}个")

if __name__ == '__main__':
    analyze_places()
