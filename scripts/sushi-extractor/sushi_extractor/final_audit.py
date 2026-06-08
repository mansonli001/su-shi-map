#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

def final_audit():
    output_dir = "extracted_locations"
    final_path = os.path.join(output_dir, "final_locations.json")
    
    with open(final_path, 'r', encoding='utf-8') as f:
        locations = json.load(f)
    
    print("="*60)
    print("📊 《苏轼行踪考》数据提取最终报告")
    print("="*60)
    
    # 城市分布
    city_count = {}
    for loc in locations:
        city = loc.get('city', '未知')
        city_count[city] = city_count.get(city, 0) + 1
    
    print(f"\n🏙️  城市分布 ({len(city_count)} 个城市):")
    print("-"*50)
    for city, count in sorted(city_count.items(), key=lambda x: -x[1]):
        print(f"   {city}: {count}个")
    
    # 质量分布
    grade_count = {'A': 0, 'B': 0, 'C': 0}
    for loc in locations:
        grade = loc.get('data_quality', 'C')
        grade_count[grade] += 1
    
    print(f"\n📈 质量分布:")
    print("-"*50)
    for grade, count in grade_count.items():
        print(f"   {grade}级: {count}个 ({(count/len(locations))*100:.1f}%)")
    
    # 坐标质量
    coord_count = {'precise': 0, 'district': 0, 'city': 0}
    for loc in locations:
        coord = loc.get('coord_quality', 'city')
        coord_count[coord] = coord_count.get(coord, 0) + 1
    
    print(f"\n📍 坐标质量:")
    print("-"*50)
    for coord, count in coord_count.items():
        print(f"   {coord}: {count}个")
    
    # 字段完整性
    fields = ['local_foods', 'su_foods', 'su_works', 'author_note', 'cultural_tags']
    print(f"\n📋 字段完整性:")
    print("-"*50)
    for field in fields:
        complete = sum(1 for loc in locations if loc.get(field))
        print(f"   {field}: {complete}/{len(locations)} ({(complete/len(locations))*100:.1f}%)")
    
    # 作品统计
    all_works = []
    for loc in locations:
        all_works.extend(loc.get('su_works', []))
    unique_works = list(set(all_works))
    print(f"\n📝 苏轼作品统计: {len(unique_works)} 部")
    if unique_works:
        print(f"   {', '.join(unique_works[:10])}{'...' if len(unique_works) > 10 else ''}")
    
    # 美食统计
    all_foods = []
    for loc in locations:
        all_foods.extend(loc.get('local_foods', []))
    unique_foods = list(set(all_foods))
    print(f"\n🍲 当地美食统计: {len(unique_foods)} 种")
    if unique_foods:
        print(f"   {', '.join(unique_foods[:10])}{'...' if len(unique_foods) > 10 else ''}")
    
    # 有纪念地的地点
    memorial_count = sum(1 for loc in locations if loc.get('has_memorial'))
    print(f"\n🏛️ 纪念地: {memorial_count} 个")
    
    print("\n" + "="*60)
    print("✅ 数据提取完成！")
    print("="*60)

if __name__ == "__main__":
    final_audit()
