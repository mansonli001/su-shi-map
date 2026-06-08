#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

def merge_v2():
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
    
    # 创建旧数据的唯一键映射（基于location_name + city）
    old_seen = set()
    merged = []
    
    # 先添加所有旧数据（保留A级标记）
    for loc in old_locations:
        key = (loc.get('location_name', ''), loc.get('city', ''))
        if key not in old_seen:
            merged.append(loc)
            old_seen.add(key)
    
    # 添加新数据中的新城市地点（补充覆盖）
    for loc in new_locations:
        key = (loc.get('location_name', ''), loc.get('city', ''))
        if key not in old_seen:
            # 新补充的地点
            merged.append(loc)
            old_seen.add(key)
    
    print(f"\n✅ 合并后: {len(merged)} 个地点")
    
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
    
    # 美食覆盖
    food_count = sum(1 for loc in merged if loc.get('local_foods'))
    print(f"\n🍲 美食覆盖: {food_count}/{len(merged)} ({(food_count/len(merged))*100:.1f}%)")
    
    # 保存最终版本
    final_path = os.path.join(output_dir, "final_locations.json")
    with open(final_path, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 最终数据已保存到: {final_path}")
    
    return merged

if __name__ == "__main__":
    merge_v2()
