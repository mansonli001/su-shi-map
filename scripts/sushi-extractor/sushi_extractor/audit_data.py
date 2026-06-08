#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

def audit_locations():
    output_dir = "extracted_locations"
    all_path = os.path.join(output_dir, "all_locations.json")
    
    # 读取所有地点数据
    with open(all_path, 'r', encoding='utf-8') as f:
        locations = json.load(f)
    
    print("📊 数据完整性审计报告")
    print("="*60)
    
    # 统计各字段的完整性
    field_stats = {
        'location_name': {'missing': 0, 'total': 0},
        'modern_name': {'missing': 0, 'total': 0},
        'modern_address': {'missing': 0, 'short': 0, 'total': 0},
        'province': {'missing': 0, 'total': 0},
        'city': {'missing': 0, 'total': 0},
        'coord_quality': {'missing': 0, 'invalid': 0, 'total': 0},
        'data_quality': {'missing': 0, 'invalid': 0, 'total': 0},
        'su_works': {'empty': 0, 'total': 0},
        'local_foods': {'empty': 0, 'total': 0},
        'su_foods': {'empty': 0, 'total': 0},
        'cultural_tags': {'empty': 0, 'total': 0},
        'has_photo_in_book': {'missing': 0, 'total': 0},
        'author_note': {'missing': 0, 'short': 0, 'total': 0},
    }
    
    # 按城市分组统计
    city_stats = {}
    
    for loc in locations:
        city = loc.get('city', '未知')
        if city not in city_stats:
            city_stats[city] = {'count': 0, 'A级': 0, 'B级': 0, 'C级': 0}
        city_stats[city]['count'] += 1
        city_stats[city][loc.get('data_quality', 'C') + '级'] += 1
        
        # 检查各个字段
        for field in ['location_name', 'modern_name', 'province', 'city']:
            field_stats[field]['total'] += 1
            if not loc.get(field):
                field_stats[field]['missing'] += 1
        
        # 地址检查
        field_stats['modern_address']['total'] += 1
        addr = loc.get('modern_address', '')
        if not addr:
            field_stats['modern_address']['missing'] += 1
        elif len(addr) < 10:
            field_stats['modern_address']['short'] += 1
        
        # 坐标质量
        field_stats['coord_quality']['total'] += 1
        cq = loc.get('coord_quality')
        if not cq:
            field_stats['coord_quality']['missing'] += 1
        elif cq not in ['precise', 'district', 'city']:
            field_stats['coord_quality']['invalid'] += 1
        
        # 数据质量
        field_stats['data_quality']['total'] += 1
        dq = loc.get('data_quality')
        if not dq:
            field_stats['data_quality']['missing'] += 1
        elif dq not in ['A', 'B', 'C']:
            field_stats['data_quality']['invalid'] += 1
        
        # 作品
        field_stats['su_works']['total'] += 1
        if not loc.get('su_works') or len(loc['su_works']) == 0:
            field_stats['su_works']['empty'] += 1
        
        # 美食
        field_stats['local_foods']['total'] += 1
        if not loc.get('local_foods') or len(loc['local_foods']) == 0:
            field_stats['local_foods']['empty'] += 1
        
        field_stats['su_foods']['total'] += 1
        if not loc.get('su_foods') or len(loc['su_foods']) == 0:
            field_stats['su_foods']['empty'] += 1
        
        # 标签
        field_stats['cultural_tags']['total'] += 1
        if not loc.get('cultural_tags') or len(loc['cultural_tags']) == 0:
            field_stats['cultural_tags']['empty'] += 1
        
        # 照片标记
        field_stats['has_photo_in_book']['total'] += 1
        if 'has_photo_in_book' not in loc:
            field_stats['has_photo_in_book']['missing'] += 1
        
        # 作者笔记
        field_stats['author_note']['total'] += 1
        note = loc.get('author_note', '')
        if not note:
            field_stats['author_note']['missing'] += 1
        elif len(note) < 10:
            field_stats['author_note']['short'] += 1
    
    # 输出城市统计
    print("\n🏙️  城市地点分布:")
    print("-" * 40)
    for city, stats in sorted(city_stats.items(), key=lambda x: -x[1]['count']):
        print(f"  {city}: {stats['count']}个 (A:{stats['A级']}, B:{stats['B级']}, C:{stats['C级']})")
    
    # 输出字段完整性统计
    print("\n📋 字段完整性统计:")
    print("-" * 60)
    print(f"{'字段':<20} {'总数':>6} {'缺失':>6} {'异常':>6} {'完整率':>8}")
    print("-" * 60)
    
    for field, stats in field_stats.items():
        missing = stats.get('missing', 0) + stats.get('empty', 0) + stats.get('short', 0) + stats.get('invalid', 0)
        rate = ((stats['total'] - missing) / stats['total']) * 100
        print(f"{field:<20} {stats['total']:>6} {missing:>6} {stats.get('invalid', 0):>6} {rate:>7.1f}%")
    
    # 找出信息不完整的地点
    print("\n⚠️  需要补充信息的地点:")
    print("-" * 60)
    for loc in locations:
        issues = []
        if not loc.get('modern_address') or len(loc['modern_address']) < 10:
            issues.append("地址不完整")
        if not loc.get('su_works') or len(loc['su_works']) == 0:
            issues.append("无关联作品")
        if not loc.get('local_foods') or len(loc['local_foods']) == 0:
            issues.append("无当地美食")
        if not loc.get('author_note') or len(loc['author_note']) < 10:
            issues.append("无作者笔记")
        
        if issues:
            print(f"📍 {loc.get('location_name')} ({loc.get('city')})")
            print(f"   问题: {', '.join(issues)}")
    
    # 统计各城市的作品数量
    print("\n📝 各城市苏轼作品统计:")
    print("-" * 40)
    city_works = {}
    for loc in locations:
        city = loc.get('city', '未知')
        if city not in city_works:
            city_works[city] = []
        city_works[city].extend(loc.get('su_works', []))
    
    for city, works in city_works.items():
        unique_works = list(set(works))
        print(f"  {city}: {len(unique_works)} 部作品")
        if unique_works:
            print(f"    {', '.join(unique_works[:5])}{'...' if len(unique_works) > 5 else ''}")
    
    # 统计美食覆盖
    print("\n🍲 各城市美食统计:")
    print("-" * 40)
    city_foods = {}
    for loc in locations:
        city = loc.get('city', '未知')
        if city not in city_foods:
            city_foods[city] = {'local': [], 'su': []}
        city_foods[city]['local'].extend(loc.get('local_foods', []))
        city_foods[city]['su'].extend(loc.get('su_foods', []))
    
    for city, foods in city_foods.items():
        local = list(set(foods['local']))
        su = list(set(foods['su']))
        print(f"  {city}:")
        if local:
            print(f"    当地美食: {', '.join(local)}")
        if su:
            print(f"    苏轼相关: {', '.join(su)}")
    
    print("\n✅ 审计完成")

if __name__ == "__main__":
    audit_locations()
