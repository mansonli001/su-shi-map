#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

def merge_locations():
    output_dir = "extracted_locations"
    
    # 读取之前手工提取的详细数据
    old_path = os.path.join(output_dir, "all_locations.json")
    # 读取新批量提取的数据
    new_path = os.path.join(output_dir, "all_locations_full.json")
    
    with open(old_path, 'r', encoding='utf-8') as f:
        old_locations = json.load(f)
    
    with open(new_path, 'r', encoding='utf-8') as f:
        new_locations = json.load(f)
    
    print(f"📊 数据合并分析")
    print("="*60)
    print(f"旧数据（手工详细提取）: {len(old_locations)} 个")
    print(f"新数据（批量提取）: {len(new_locations)} 个")
    
    # 合并策略：保留旧数据的详细字段，用新数据补充缺失字段
    merged = []
    old_by_city = {loc.get('city', ''): loc for loc in old_locations}
    new_by_city = {}
    for loc in new_locations:
        city = loc.get('city', '')
        if city not in new_by_city:
            new_by_city[city] = []
        new_by_city[city].append(loc)
    
    # 优先使用旧数据的详细地点，补充新数据中的地点
    all_cities = set(old_by_city.keys()) | set(new_by_city.keys())
    
    for city in all_cities:
        # 使用旧数据的详细地点
        if city in old_by_city:
            merged.append(old_by_city[city])
        
        # 补充新数据中旧数据没有的城市（排除重复）
        if city in new_by_city and city not in old_by_city:
            for loc in new_by_city[city]:
                loc['data_quality'] = 'B'  # 批量提取的数据降为B级
                merged.append(loc)
        elif city in new_by_city and city in old_by_city:
            # 同一城市有多个新地点（如杭州通判+知州）
            for loc in new_by_city[city]:
                if loc.get('location_name') != old_by_city[city].get('location_name'):
                    loc['data_quality'] = 'B'
                    merged.append(loc)
    
    print(f"\n✅ 合并后: {len(merged)} 个地点")
    
    # 保存合并后的数据
    with open(os.path.join(output_dir, "all_locations_merged.json"), 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    
    # 按城市统计
    city_count = {}
    for loc in merged:
        city = loc.get('city', '未知')
        city_count[city] = city_count.get(city, 0) + 1
    
    print(f"\n📊 合并后城市分布:")
    for city, count in sorted(city_count.items(), key=lambda x: -x[1]):
        print(f"   {city}: {count}个")
    
    # 质量分布
    grade_count = {'A': 0, 'B': 0, 'C': 0}
    for loc in merged:
        grade = loc.get('data_quality', 'C')
        grade_count[grade] += 1
    
    print(f"\n📈 质量分布:")
    for grade, count in grade_count.items():
        print(f"   {grade}级: {count}个 ({(count/len(merged))*100:.1f}%)")
    
    # 保存最终版本
    final_path = os.path.join(output_dir, "final_locations.json")
    with open(final_path, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 最终数据已保存到: {final_path}")
    
    return merged

if __name__ == "__main__":
    merge_locations()
