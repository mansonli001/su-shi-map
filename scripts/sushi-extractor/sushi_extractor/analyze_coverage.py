#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

def analyze_coverage():
    # 读取现有地点
    existing_path = '/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/public/data/places-core.json'
    with open(existing_path, 'r', encoding='utf-8') as f:
        existing_places = json.load(f)

    # 读取从书中提取的数据
    book_path = 'extracted_locations/final_locations.json'
    with open(book_path, 'r', encoding='utf-8') as f:
        book_places = json.load(f)

    print("="*60)
    print("📊 数据对比分析")
    print("="*60)
    print(f"现有地点数: {len(existing_places)}")
    print(f"书中提取数据: {len(book_places)}")

    # 分析现有地点的stage分布
    stage_dist = {}
    for p in existing_places:
        stage = p.get('stage', '未知')
        stage_dist[stage] = stage_dist.get(stage, 0) + 1

    print(f"\n现有地点人生阶段分布:")
    for stage, count in sorted(stage_dist.items(), key=lambda x: -x[1]):
        print(f"  {stage}: {count}个")

    # 分析书中数据的城市分布
    book_city = {}
    for p in book_places:
        city = p.get('city', '未知')
        book_city[city] = book_city.get(city, 0) + 1

    print(f"\n书中数据城市分布:")
    for city, count in sorted(book_city.items(), key=lambda x: -x[1]):
        print(f"  {city}: {count}个")

    # 匹配分析
    matched = []
    unmatched = []
    for ep in existing_places:
        song_name = ep.get('songName', '')
        matched_book = None
        for bp in book_places:
            book_name = bp.get('location_name', '')
            # 简单匹配：名称包含关系
            if song_name in book_name or book_name in song_name:
                matched_book = bp
                break
        if matched_book:
            matched.append((ep, matched_book))
        else:
            unmatched.append(ep)

    print(f"\n🔗 匹配结果:")
    print(f"  已匹配: {len(matched)} 个")
    print(f"  未匹配: {len(unmatched)} 个")

    # 显示部分未匹配的地点
    if unmatched:
        print(f"\n未匹配地点示例 (前15):")
        for p in unmatched[:15]:
            print(f"  - {p.get('songName')} ({p.get('modernName')})")

    return {
        'existing': existing_places,
        'book': book_places,
        'matched': matched,
        'unmatched': unmatched
    }

if __name__ == "__main__":
    analyze_coverage()
