#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import random
import os

OUTPUT_DIR = "extracted_locations"

def load_all_locations():
    """加载所有提取的地点数据"""
    locations = []
    all_path = os.path.join(OUTPUT_DIR, "all_locations.json")
    if os.path.exists(all_path):
        with open(all_path, 'r', encoding='utf-8') as f:
            locations = json.load(f)
    return locations

def validate_location(loc):
    """验证单个地点数据"""
    errors = []
    warnings = []
    
    # 必填字段检查
    required_fields = ['location_name', 'modern_name', 'province', 'city', 'coord_quality']
    for field in required_fields:
        if not loc.get(field):
            errors.append(f"缺少必填字段: {field}")
    
    # 坐标质量校验
    if loc.get('coord_quality') not in ['precise', 'district', 'city']:
        errors.append(f"无效的坐标质量值: {loc.get('coord_quality')}")
    
    # 数据质量校验
    if loc.get('data_quality') not in ['A', 'B', 'C']:
        errors.append(f"无效的数据质量值: {loc.get('data_quality')}")
    
    # 访问年份校验
    year = loc.get('visit_year')
    if year and (year < 1037 or year > 1101):
        warnings.append(f"访问年份超出苏轼生卒范围: {year}")
    
    # 地址完整性检查
    address = loc.get('modern_address', '')
    if len(address) < 5:
        warnings.append(f"地址信息不完整: {address}")
    
    # 作品数量检查
    if len(loc.get('su_works', [])) > 10:
        warnings.append("关联作品数量过多，建议复核")
    
    return {
        'location_id': loc.get('location_id'),
        'location_name': loc.get('location_name'),
        'errors': errors,
        'warnings': warnings,
        'is_valid': len(errors) == 0
    }

def generate_sample(locations, sample_rate_a=0.1, sample_rate_b=0.3, sample_rate_c=1.0):
    """根据数据质量分层抽样"""
    samples = []
    
    # 按质量分级
    grade_a = [l for l in locations if l.get('data_quality') == 'A']
    grade_b = [l for l in locations if l.get('data_quality') == 'B']
    grade_c = [l for l in locations if l.get('data_quality') == 'C']
    
    # 分层抽样
    sample_a = random.sample(grade_a, max(1, int(len(grade_a) * sample_rate_a)))
    sample_b = random.sample(grade_b, max(1, int(len(grade_b) * sample_rate_b)))
    sample_c = grade_c  # C级全查
    
    samples.extend(sample_a)
    samples.extend(sample_b)
    samples.extend(sample_c)
    
    return {
        'grade_a_count': len(grade_a),
        'grade_b_count': len(grade_b),
        'grade_c_count': len(grade_c),
        'sample_count': len(samples),
        'samples': samples
    }

def main():
    # 加载数据
    locations = load_all_locations()
    print(f"📊 共加载 {len(locations)} 个地点数据")
    
    # 数据质量分布
    grade_counts = {'A': 0, 'B': 0, 'C': 0}
    for loc in locations:
        grade = loc.get('data_quality', 'C')
        grade_counts[grade] += 1
    
    print(f"\n📈 数据质量分布:")
    for grade, count in grade_counts.items():
        print(f"   {grade}级: {count} 个 ({(count/len(locations))*100:.1f}%)")
    
    # 坐标质量分布
    coord_counts = {}
    for loc in locations:
        coord = loc.get('coord_quality', 'unknown')
        coord_counts[coord] = coord_counts.get(coord, 0) + 1
    
    print(f"\n📍 坐标质量分布:")
    for coord, count in coord_counts.items():
        print(f"   {coord}: {count} 个")
    
    # 验证所有数据
    print("\n🔍 开始数据校验...")
    validation_results = []
    valid_count = 0
    error_count = 0
    
    for loc in locations:
        result = validate_location(loc)
        validation_results.append(result)
        if result['is_valid']:
            valid_count += 1
        else:
            error_count += 1
    
    print(f"✅ 有效数据: {valid_count} 个")
    print(f"❌ 错误数据: {error_count} 个")
    
    # 输出错误详情
    if error_count > 0:
        print("\n⚠️ 错误详情:")
        for result in validation_results:
            if not result['is_valid']:
                print(f"\n   地点: {result['location_name']} ({result['location_id']})")
                for error in result['errors']:
                    print(f"      - {error}")
    
    # 输出警告详情
    print("\n⚡ 警告详情:")
    warning_locations = [r for r in validation_results if r['warnings']]
    for result in warning_locations[:5]:  # 只显示前5个
        print(f"\n   地点: {result['location_name']}")
        for warning in result['warnings']:
            print(f"      - {warning}")
    
    # 生成抽检样本
    print("\n🎲 生成抽检样本...")
    sample_result = generate_sample(locations)
    print(f"   A级 ({sample_result['grade_a_count']}个): 抽取 {len([s for s in sample_result['samples'] if s.get('data_quality') == 'A'])} 个")
    print(f"   B级 ({sample_result['grade_b_count']}个): 抽取 {len([s for s in sample_result['samples'] if s.get('data_quality') == 'B'])} 个")
    print(f"   C级 ({sample_result['grade_c_count']}个): 抽取 {len([s for s in sample_result['samples'] if s.get('data_quality') == 'C'])} 个")
    print(f"   合计抽检: {sample_result['sample_count']} 个 ({(sample_result['sample_count']/len(locations))*100:.1f}%)")
    
    # 保存抽检清单
    sample_output = {
        'total_count': len(locations),
        'grade_distribution': grade_counts,
        'coord_distribution': coord_counts,
        'validation_summary': {
            'valid_count': valid_count,
            'error_count': error_count,
            'warning_count': len(warning_locations)
        },
        'sample_rate': {
            'A': 0.1,
            'B': 0.3,
            'C': 1.0
        },
        'samples': sample_result['samples']
    }
    
    with open(os.path.join(OUTPUT_DIR, 'validation_report.json'), 'w', encoding='utf-8') as f:
        json.dump(sample_output, f, ensure_ascii=False, indent=2)
    
    print("\n📄 复核报告已保存到: extracted_locations/validation_report.json")
    
    # 打印抽检清单
    print("\n📝 抽检清单:")
    for sample in sample_result['samples']:
        print(f"   [{sample['data_quality']}] {sample['location_name']} - {sample['modern_name']}")

if __name__ == "__main__":
    main()
