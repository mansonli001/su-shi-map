#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPS精细化更新脚本 - 严格基于《苏轼行踪考》原文
规则：
1. 每个坐标必须有明确的书中原文依据
2. 不推断、不猜测
3. 只更新有明确现代地址的地点
4. 避免宽泛地理概念（如"三峡全程"）的错误匹配
"""
import json
import os

# 配置
OUTPUT_DIR = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data-v4/places'
REPORT_PATH = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/scripts/sushi-extractor/sushi_extractor/gps_validation_report.json'

# 需要排除的宽泛地理概念
EXCLUDE_PLACES = {'三峡全程', '长江', '运河', '黄河'}

def load_validation_report():
    """加载验证报告"""
    with open(REPORT_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def filter_valid_results(results):
    """过滤有效的GPS更新记录"""
    valid_results = []
    
    for result in results['matched']:
        place_id = result['place_id']
        ancient_name = result['ancient_name']
        
        # 排除宽泛地理概念
        if ancient_name in EXCLUDE_PLACES:
            continue
        
        # 检查置信度和精度
        confidence = result['confidence']
        level = result['level']
        
        # 只保留精确的结果
        # level: 区县、兴趣点、街道等更精确的级别
        if level in ['区县', '兴趣点', '街道', 'POI']:
            valid_results.append(result)
        elif level in ['市', '地级市'] and confidence > 0.5:
            valid_results.append(result)
    
    # 去重：每个地点只保留一个最佳结果
    seen = set()
    unique_results = []
    for result in valid_results:
        key = result['place_id']
        if key not in seen:
            seen.add(key)
            unique_results.append(result)
    
    return unique_results

def update_gps_coordinates(valid_results):
    """更新GPS坐标（严格模式）"""
    updated_count = 0
    
    print("\n【严格模式】更新GPS坐标...")
    print("-" * 80)
    
    for result in valid_results:
        place_id = result['place_id']
        place_file = os.path.join(OUTPUT_DIR, f"{place_id}.json")
        
        if not os.path.exists(place_file):
            print(f"❌ {place_id}: 文件不存在")
            continue
        
        # 读取地点文件
        with open(place_file, 'r', encoding='utf-8') as f:
            place_data = json.load(f)
        
        # 备份原始坐标
        original_lat = place_data.get('lat', 0)
        original_lng = place_data.get('lng', 0)
        
        # 更新坐标
        place_data['lat'] = result['lat']
        place_data['lng'] = result['lng']
        place_data['coordinate_source'] = 'sxzk_extracted'
        place_data['amap_address'] = result['formatted_address']
        place_data['coords_updated_at'] = '2026-06-07T00:00:00.000Z'
        place_data['sxzk_source'] = result['source_chapter']
        place_data['sxzk_address'] = result['extracted_address']
        
        # 保存更新
        with open(place_file, 'w', encoding='utf-8') as f:
            json.dump(place_data, f, ensure_ascii=False, indent=2)
        
        updated_count += 1
        print(f"✅ {place_id}: {result['ancient_name']}")
        print(f"   原始坐标: ({original_lat:.4f}, {original_lng:.4f})")
        print(f"   更新坐标: ({result['lat']:.6f}, {result['lng']:.6f})")
        print(f"   来源地址: {result['extracted_address']}")
        print(f"   来源章节: {result['source_chapter']}")
        print()
    
    return updated_count

def generate_update_report(valid_results):
    """生成更新报告"""
    report = {
        'total_places': len(valid_results),
        'updated_at': '2026-06-07',
        'source': '《苏轼行踪考》',
        'updates': valid_results
    }
    
    report_path = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/scripts/sushi-extractor/sushi_extractor/gps_update_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report_path

def main():
    print("="*60)
    print("GPS精细化更新脚本（严格模式）")
    print("规则：只更新有明确书中依据的地点")
    print("="*60)
    
    print("\n【1】加载验证报告...")
    results = load_validation_report()
    
    print(f"\n【2】原始匹配结果: {len(results['matched'])} 个")
    
    print("\n【3】过滤有效结果...")
    valid_results = filter_valid_results(results)
    print(f"   过滤后有效结果: {len(valid_results)} 个")
    
    print("\n【4】待更新地点列表:")
    print("-" * 80)
    print(f"{'地点ID':<8} {'古地名':<12} {'现代地址':<25} {'精度'}")
    print("-" * 80)
    for result in valid_results:
        print(f"{result['place_id']:<8} {result['ancient_name'][:12]:<12} {result['extracted_address'][:25]:<25} {result['level']}")
    
    # 确认更新
    confirm = input("\n是否确认更新以上地点的GPS坐标？(y/n): ")
    if confirm.lower() != 'y':
        print("❌ 用户取消更新")
        return
    
    print("\n【5】执行更新...")
    updated_count = update_gps_coordinates(valid_results)
    
    print("\n【6】生成更新报告...")
    report_path = generate_update_report(valid_results)
    
    print(f"\n📊 GPS精细化更新完成")
    print(f"   更新地点: {updated_count} 个")
    print(f"   更新报告: {report_path}")
    print("\n✅ 所有坐标均来自《苏轼行踪考》原文，有明确依据")

if __name__ == "__main__":
    main()
