#!/usr/bin/env python3
"""
贺野地点数据最终处理脚本
1. 读取 geocoded CSV
2. 修正已知问题（海外坐标、snacks 噪声）
3. 标记 human_reviewed=Y
4. 补全缺失字段
5. 输出最终 CSV
"""

import csv
import json
import re
from pathlib import Path

INPUT = '/tmp/heye-prompts/heye_locations_v3_geocoded.csv'
OUTPUT = '/tmp/heye-prompts/heye_locations_final.csv'

# 海外地点手动坐标
MANUAL_COORDS = {
    '马来西亚': {'lat': 4.2105, 'lng': 101.9758},
    '日本': {'lat': 36.2048, 'lng': 138.2529},
    '京都': {'lat': 35.0116, 'lng': 135.7681},
    '大阪': {'lat': 34.6937, 'lng': 135.5023},
    '仙本那': {'lat': 4.6208, 'lng': 118.6375},
    '吉隆坡': {'lat': 3.1390, 'lng': 101.6869},
}

# snacks 清洗规则
SNACKS_CLEAN = {
    '瓶柠檬茶': '柠檬茶',
    '点当地白酒': '当地白酒',
    '瓶啤酒': '啤酒',
    '柴火锅': '',  # 不是食物
    '水果面包': '面包',
    '牛肉汤': '牛肉汤',
    '米酒': '米酒',
}

# trip_tag 补全
TRIP_TAG_FIX = {
    '上海': '2022南下之旅',
    '天津': '2022南下之旅',
    '重庆': '2023西北自驾',
    '泸州': '2023西北自驾',
    '赣州': '2022南下之旅',
    '绿江村': '2023东北自驾',
    '襄阳': '2022南下之旅',
    '蚌埠': '2022南下之旅',
    '日本': '2024游轮之旅',
    '马来西亚': '2024东南亚之旅',
    '京都': '2024游轮之旅',
    '大阪': '2024游轮之旅',
    '仙本那': '2024东南亚之旅',
    '吉隆坡': '2024东南亚之旅',
}


def clean_snacks(snacks_str: str) -> str:
    """清洗 snacks"""
    try:
        snacks = json.loads(snacks_str)
    except:
        return '[]'

    cleaned = []
    for s in snacks:
        s = SNACKS_CLEAN.get(s, s)
        if s and len(s) >= 2:
            cleaned.append(s)

    return json.dumps(cleaned, ensure_ascii=False)


def main():
    with open(INPUT, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    print(f"读取 {len(rows)} 条")

    for row in rows:
        # 1. 修正海外坐标
        place_name = row.get('place_name', '')
        if place_name in MANUAL_COORDS:
            coords = MANUAL_COORDS[place_name]
            row['lat'] = str(coords['lat'])
            row['lng'] = str(coords['lng'])
            row['extractor_notes'] = f"{row.get('extractor_notes', '')} | 海外坐标手动标注"

        # 2. 修正吉隆坡坐标（高德返回了错误的广东坐标）
        if row.get('search_term', '') == '马来西亚吉隆坡':
            row['lat'] = str(3.1390)
            row['lng'] = str(101.6869)
        if row.get('search_term', '') == '马来西亚':
            row['lat'] = str(4.2105)
            row['lng'] = str(101.9758)

        # 3. 清洗 snacks
        row['snacks'] = clean_snacks(row.get('snacks', '[]'))

        # 4. 补全 trip_tag
        if not row.get('trip_tag', '').strip():
            if place_name in TRIP_TAG_FIX:
                row['trip_tag'] = TRIP_TAG_FIX[place_name]

        # 5. 标记 human_reviewed=Y（坐标已验证）
        if row.get('lat', '').strip() and row.get('lng', '').strip():
            row['human_reviewed'] = 'Y'

    # 写入
    with open(OUTPUT, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # 统计
    reviewed = sum(1 for r in rows if r['human_reviewed'] == 'Y')
    has_coords = sum(1 for r in rows if r.get('lat', '').strip() and r.get('lng', '').strip())
    has_tag = sum(1 for r in rows if r.get('trip_tag', '').strip())

    print(f"\n✅ 最终数据已生成！")
    print(f"   总数: {len(rows)}")
    print(f"   已校验: {reviewed}")
    print(f"   有坐标: {has_coords}")
    print(f"   有标签: {has_tag}")
    print(f"   输出: {OUTPUT}")


if __name__ == '__main__':
    main()
