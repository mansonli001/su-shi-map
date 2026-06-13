#!/usr/bin/env python3
"""
CSV → 静态 JSON 转换脚本
读取 heye_extractor.py 产出的 CSV（20 字段），
过滤 human_reviewed=='Y'，剥离流程字段，派生展示层字段，
产出：
  - public/data-heye/locations.json    全量地点索引
  - public/data-heye/province-stats.json  省份统计（着色用）
  - public/data-heye/meta.json         首页统计 + 全局元信息

用法：
    python scripts/csv_to_heye_json.py --csv heye_locations.csv --out-dir public/data-heye
    python scripts/csv_to_heye_json.py --csv heye_locations.csv --out-dir public/data-heye --validate
"""

import csv
import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

# ─────────────────────────────────────────────
# 省名归一映射表（数据省名 → GeoJSON 省名）
# ─────────────────────────────────────────────
PROVINCE_NAME_MAP = {
    '内蒙古': '内蒙古自治区',
    '广西':   '广西壮族自治区',
    '西藏':   '西藏自治区',
    '宁夏':   '宁夏回族自治区',
    '新疆':   '新疆维吾尔自治区',
    '北京':   '北京市',
    '上海':   '上海市',
    '天津':   '天津市',
    '重庆':   '重庆市',
}

# 反向映射（GeoJSON → 数据省名）
GEOJSON_TO_DATA_MAP = {v: k for k, v in PROVINCE_NAME_MAP.items()}


def normalize_province(province: str) -> str:
    """数据省名 → GeoJSON 省名（用于着色匹配）"""
    return PROVINCE_NAME_MAP.get(province, province)


def parse_visit_year(visit_date: str | None) -> int | None:
    """从 visit_date 抽取年份，如 '2022年12月' → 2022"""
    if not visit_date:
        return None
    m = re.search(r'(\d{4})', visit_date)
    return int(m.group(1)) if m else None


def parse_snacks(snacks_str: str) -> list[str]:
    """解析 snacks JSON 字符串为数组"""
    if not snacks_str or snacks_str.strip() == '[]':
        return []
    try:
        result = json.loads(snacks_str)
        return result if isinstance(result, list) else []
    except json.JSONDecodeError:
        return []


def determine_coordinate_source(row: dict) -> str:
    """推断坐标来源标记"""
    lat = row.get('lat', '').strip()
    lng = row.get('lng', '').strip()
    search_term = row.get('search_term', '').strip()
    notes = row.get('extractor_notes', '').strip()

    if not lat or not lng:
        return 'amap_search'  # 默认，实际不应进入展示层

    if '推断' in notes or '估算' in notes:
        return 'inferred'
    if search_term:
        return 'amap_search'
    return 'manual'


def density_tier(count: int) -> int:
    """计算着色档：0=无 / 1=1-2 / 2=3-5 / 3=6+"""
    if count == 0:
        return 0
    elif count <= 2:
        return 1
    elif count <= 5:
        return 2
    else:
        return 3


def read_csv(csv_path: str) -> list[dict]:
    """读取 CSV 文件，返回行列表"""
    rows = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def validate_csv(rows: list[dict]) -> list[str]:
    """校验 human_reviewed=Y 的行，返回告警列表"""
    warnings = []
    for i, row in enumerate(rows):
        if row.get('human_reviewed', '').upper() != 'Y':
            continue
        line_num = i + 2  # CSV 行号（含表头）
        lat = row.get('lat', '').strip()
        lng = row.get('lng', '').strip()
        province = row.get('province', '').strip()
        place_name = row.get('place_name', '').strip()
        excerpt = row.get('excerpt', '').strip()

        if not lat or not lng:
            warnings.append(f"行{line_num} [{row.get('id','?')}] {place_name}: lat/lng 为空")
        else:
            try:
                lat_f = float(lat)
                lng_f = float(lng)
                # 海外地点允许超出中国范围
                overseas_provinces = {'马来西亚', '日本'}
                is_overseas = province in overseas_provinces
                if not is_overseas and not (18 <= lat_f <= 54 and 73 <= lng_f <= 135):
                    warnings.append(f"行{line_num} [{row.get('id','?')}] {place_name}: 坐标超出中国范围 ({lat_f}, {lng_f})")
            except ValueError:
                warnings.append(f"行{line_num} [{row.get('id','?')}] {place_name}: lat/lng 非数字")

        if not province:
            warnings.append(f"行{line_num} [{row.get('id','?')}] {place_name}: province 为空")
        if not place_name:
            warnings.append(f"行{line_num} [{row.get('id','?')}]: place_name 为空")
        if not excerpt:
            warnings.append(f"行{line_num} [{row.get('id','?')}] {place_name}: excerpt 为空")

    return warnings


def transform_row(row: dict) -> dict | None:
    """CSV 行 → 展示层 HeyeLocation（snake_case JSON）"""
    if row.get('human_reviewed', '').upper() != 'Y':
        return None

    lat_str = row.get('lat', '').strip()
    lng_str = row.get('lng', '').strip()

    if not lat_str or not lng_str:
        return None

    try:
        lat = float(lat_str)
        lng = float(lng_str)
    except ValueError:
        return None

    visit_date = row.get('visit_date', '').strip() or None
    trip_tag = row.get('trip_tag', '').strip() or None
    snacks = parse_snacks(row.get('snacks', '[]'))
    featured = row.get('featured', 'false').lower() == 'true'

    return {
        'id': row['id'],
        'province': row.get('province', ''),
        'city': row.get('city', ''),
        'place_name': row.get('place_name', ''),
        'full_name': row.get('full_name', ''),
        'region': row.get('region', ''),
        'lat': lat,
        'lng': lng,
        'coordinate_source': determine_coordinate_source(row),
        'visit_date': visit_date,
        'visit_year': parse_visit_year(visit_date),
        'trip_tag': trip_tag,
        'excerpt': row.get('excerpt', ''),
        'snacks': snacks,
        'image_url': row.get('image_url', ''),
        'article_url': row.get('article_url', ''),
        'source_title': row.get('source_title', ''),
        'featured': featured,
        'visit_count': int(row.get('visit_count', '1') or '1'),
        'visit_history': row.get('visit_history', ''),
    }


def build_province_stats(locations: list[dict]) -> dict:
    """构建省份统计（着色用）"""
    province_data: dict[str, dict] = defaultdict(lambda: {
        'place_ids': [],
        'cities': set(),
    })

    for loc in locations:
        prov = loc['province']
        province_data[prov]['place_ids'].append(loc['id'])
        province_data[prov]['cities'].add(loc['city'])

    provinces = {}
    for prov, data in province_data.items():
        count = len(data['place_ids'])
        provinces[prov] = {
            'place_count': count,
            'city_count': len(data['cities']),
            'place_ids': data['place_ids'],
            'density_tier': density_tier(count),
        }

    return provinces


def build_meta(locations: list[dict], province_stats: dict) -> dict:
    """构建首页统计 + 全局元信息"""
    provinces = set()
    cities = set()
    all_snacks = set()
    articles = set()
    trip_tags = set()
    featured_count = 0

    for loc in locations:
        provinces.add(loc['province'])
        cities.add(loc['city'])
        all_snacks.update(loc['snacks'])
        if loc['source_title']:
            articles.add(loc['source_title'])
        if loc['trip_tag']:
            trip_tags.add(loc['trip_tag'])
        if loc['featured']:
            featured_count += 1

    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')

    return {
        'schema_version': 'heye-v1.0',
        'generated_at': now,
        'data_source': '公众号「有生余年」· 贺野原创',
        'disclaimer': '地点坐标经人工校验，excerpt 为原文原话引用，版权归原作者所有。',
        'stats': {
            'total_places': len(locations),
            'province_count': len(provinces),
            'city_count': len(cities),
            'snack_variety': len(all_snacks),
            'article_count': len(articles),
            'trip_count': len(trip_tags),
            'featured_count': featured_count,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="CSV → 静态 JSON 转换")
    parser.add_argument('--csv', required=True, help='输入 CSV 路径')
    parser.add_argument('--out-dir', default='public/data-heye', help='输出目录')
    parser.add_argument('--validate', action='store_true', help='校验模式：只校验不输出')
    args = parser.parse_args()

    # 读取 CSV
    rows = read_csv(args.csv)
    print(f"读取 {len(rows)} 行 CSV")

    # 校验
    warnings = validate_csv(rows)
    if warnings:
        print(f"\n⚠️  校验发现 {len(warnings)} 个问题：")
        for w in warnings:
            print(f"  {w}")
        if args.validate:
            sys.exit(1)
    else:
        print("✅ 校验通过，无问题")

    if args.validate:
        sys.exit(0)

    # 转换：只保留 human_reviewed=Y 且有坐标的行
    locations = []
    skipped = 0
    for row in rows:
        loc = transform_row(row)
        if loc:
            locations.append(loc)
        else:
            skipped += 1

    print(f"转换完成：{len(locations)} 条有效地点，{skipped} 条跳过（未校验/无坐标）")

    if not locations:
        print("❌ 无有效地点，退出")
        sys.exit(1)

    # 构建省份统计
    province_stats = build_province_stats(locations)

    # 检查省名归一
    for prov in province_stats:
        geojson_name = normalize_province(prov)
        if geojson_name != prov:
            print(f"  省名归一：{prov} → {geojson_name}")

    # 构建元信息
    meta = build_meta(locations, province_stats)

    # 输出
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # locations.json
    locations_json = {
        '_meta': {
            'schema_version': 'heye-v1.0',
            'data_source': '公众号「有生余年」· 贺野原创',
            'disclaimer': '地点坐标经人工校验，excerpt 为原文原话引用，版权归原作者所有。',
            'generated_at': meta['generated_at'],
            'total_locations': len(locations),
        },
        'locations': locations,
    }
    with open(out_dir / 'locations.json', 'w', encoding='utf-8') as f:
        json.dump(locations_json, f, ensure_ascii=False, indent=2)
    print(f"✅ {out_dir / 'locations.json'} ({len(locations)} 条)")

    # province-stats.json
    stats_json = {
        '_meta': {
            'generated_at': meta['generated_at'],
            'schema_version': 'heye-v1.0',
        },
        'provinces': province_stats,
    }
    with open(out_dir / 'province-stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats_json, f, ensure_ascii=False, indent=2)
    print(f"✅ {out_dir / 'province-stats.json'} ({len(province_stats)} 省)")

    # meta.json
    with open(out_dir / 'meta.json', 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"✅ {out_dir / 'meta.json'}")

    # 统计摘要
    stats = meta['stats']
    print(f"\n📊 统计摘要：")
    print(f"   地点: {stats['total_places']}")
    print(f"   省份: {stats['province_count']}")
    print(f"   城市: {stats['city_count']}")
    print(f"   小吃: {stats['snack_variety']} 种")
    print(f"   文章: {stats['article_count']} 篇")
    print(f"   出行: {stats['trip_count']} 次")
    print(f"   精选: {stats['featured_count']} 条")


if __name__ == '__main__':
    main()
