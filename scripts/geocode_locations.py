#!/usr/bin/env python3
"""
贺野地点坐标补全脚本
使用高德地图 Web Service API 批量查询经纬度
"""

import ssl
import csv
import json
import os
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

# 跳过 SSL 验证（开发环境）
ssl._create_default_https_context = ssl._create_unverified_context

# 高德 API Key
AMAP_KEY = os.environ.get('AMAP_WEB_SERVICE_KEY', '')
if not AMAP_KEY:
    # 尝试从 .env.local 读取
    env_path = Path(__file__).parent.parent / '.env.local'
    if env_path.exists():
        for line in open(env_path):
            if line.startswith('AMAP_WEB_SERVICE_KEY='):
                AMAP_KEY = line.strip().split('=', 1)[1]
                break

if not AMAP_KEY:
    print("[!] AMAP_WEB_SERVICE_KEY 未配置")
    sys.exit(1)

GEOCODE_URL = 'https://restapi.amap.com/v3/geocode/geo'


def geocode(search_term: str) -> dict:
    """调用高德地理编码 API"""
    params = {
        'key': AMAP_KEY,
        'address': search_term,
        'output': 'json',
    }
    url = f"{GEOCODE_URL}?{urllib.parse.urlencode(params)}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        if data.get('status') == '1' and data.get('geocodes'):
            geo = data['geocodes'][0]
            location = geo.get('location', '')  # "lng,lat"
            if location:
                lng, lat = location.split(',')
                return {
                    'lat': lat,
                    'lng': lng,
                    'formatted_address': geo.get('formatted_address', ''),
                    'level': geo.get('level', ''),
                }
    except Exception as e:
        print(f"  [!] 请求失败: {e}")

    return {}


def main():
    input_csv = sys.argv[1] if len(sys.argv) > 1 else '/tmp/heye-prompts/heye_locations_v3.csv'
    output_csv = input_csv.replace('.csv', '_geocoded.csv')

    # 读取 CSV
    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"读取 {len(rows)} 条地点")

    # 查询坐标
    success = 0
    fail = 0

    for i, row in enumerate(rows):
        if row.get('lat') and row.get('lng'):
            success += 1
            continue

        search_term = row.get('search_term', '')
        if not search_term:
            fail += 1
            continue

        print(f"  [{i+1}/{len(rows)}] {row['place_name']} → {search_term}", end=' ')

        result = geocode(search_term)
        if result:
            row['lat'] = result['lat']
            row['lng'] = result['lng']
            row['extractor_notes'] = f"{row.get('extractor_notes', '')} | 坐标: {result.get('formatted_address', '')} ({result.get('level', '')})"
            print(f"✅ {result['lat'][:8]}, {result['lng'][:9]} ({result.get('level', '')})")
            success += 1
        else:
            print("❌ 未找到")
            fail += 1

        # 限流：每秒不超过5次
        time.sleep(0.25)

    # 写入 CSV
    with open(output_csv, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ 坐标补全完成！")
    print(f"   成功: {success}")
    print(f"   失败: {fail}")
    print(f"   输出: {output_csv}")


if __name__ == '__main__':
    main()
