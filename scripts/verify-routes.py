#!/usr/bin/env python3
"""验证路线数据的完整性"""

import json
from pathlib import Path


def main():
    """主函数"""
    data_dir = Path("/Users/mansonlee/CodeBuddy/Vibe coding/su-shi-map/data")
    
    # 加载数据
    with open(data_dir / "places-detailed-v3.json", "r", encoding="utf-8") as f:
        places_data = json.load(f)
    places = places_data["places"]
    
    with open(data_dir / "routes-v3.json", "r", encoding="utf-8") as f:
        routes_data = json.load(f)
    routes = routes_data["routes"]
    
    print("=== 路线数据完整性验证 ===\n")
    
    # 检查每条路线
    missing_places = {}
    for route_id, route in sorted(routes.items()):
        print(f"{route_id}: {route.get('route_name', '')}")
        print(f"  途经点数量: {len(route.get('place_ids', []))}")
        
        route_missing = []
        for place_id in route.get("place_ids", []):
            if place_id not in places:
                route_missing.append(place_id)
        
        if route_missing:
            print(f"  ⚠️  缺失地点: {route_missing}")
            missing_places[route_id] = route_missing
        else:
            print(f"  ✅ 所有地点都存在")
        
        # 检查时间
        if not route.get("start_date"):
            print(f"  ⚠️  缺少 start_date")
        if not route.get("end_date"):
            print(f"  ⚠️  缺少 end_date")
        if not route.get("description"):
            print(f"  ⚠️  缺少 description")
        
        print()
    
    # 统计
    print("=== 总结 ===")
    if missing_places:
        print(f"❌ 有 {len(missing_places)} 条路线包含缺失地点")
        for route_id, place_ids in missing_places.items():
            print(f"  {route_id}: {place_ids}")
    else:
        print("✅ 所有路线的地点都存在")
    
    # 检查地点的route_events
    print("\n=== 地点route_events完整性检查 ===\n")
    incomplete_places = []
    for place_id, place in places.items():
        route_orders = place.get("route_order", {})
        route_events = place.get("route_events", {})
        
        missing_events = []
        for route_id in route_orders:
            if route_id not in route_events:
                missing_events.append(route_id)
        
        if missing_events:
            incomplete_places.append({
                "place_id": place_id,
                "name": place.get("name_song", ""),
                "missing_routes": missing_events
            })
            print(f"{place_id} ({place.get('name_song', '')}):")
            print(f"  ⚠️  以下路线缺少事件: {missing_events}")
        # else:
        #     print(f"{place_id}: ✅ 所有路线都有事件")
    
    if incomplete_places:
        print(f"\n❌ 有 {len(incomplete_places)} 个地点缺少route_events")
    else:
        print("\n✅ 所有地点的route_events都完整")
    
    # 检查地点的基本字段
    print("\n=== 地点基本字段检查 ===\n")
    invalid_places = []
    for place_id, place in places.items():
        issues = []
        if not place.get("name_song"):
            issues.append("缺少name_song")
        if not place.get("name_modern"):
            issues.append("缺少name_modern")
        if not place.get("latitude") or place.get("latitude") == 0:
            issues.append("缺少latitude")
        if not place.get("longitude") or place.get("longitude") == 0:
            issues.append("缺少longitude")
        if not place.get("place_type"):
            issues.append("缺少place_type")
        
        if issues:
            invalid_places.append({
                "place_id": place_id,
                "issues": issues
            })
            print(f"{place_id}: ⚠️  {', '.join(issues)}")
    
    if invalid_places:
        print(f"\n❌ 有 {len(invalid_places)} 个地点缺少基本字段")
    else:
        print("\n✅ 所有地点的基本字段都完整")
    
    print("\n=== 验证完成 ===")


if __name__ == "__main__":
    main()
