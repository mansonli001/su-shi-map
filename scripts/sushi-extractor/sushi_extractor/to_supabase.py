"""
提取结果 → Supabase upsert 格式转换 + 高德坐标自动补全
用法:
  python to_supabase.py \
    --input output/locations.json \
    --amap-key YOUR_AMAP_KEY \
    --supabase-url YOUR_URL \
    --supabase-key YOUR_KEY
"""

import json, os, time, argparse, requests
from pathlib import Path

AMAP_GEO_URL = "https://restapi.amap.com/v3/geocode/geo"
AMAP_POI_URL = "https://restapi.amap.com/v3/place/text"

# 苏轼相关 POI 搜索关键词（按命中率排序）
SU_KEYWORDS = [
    "东坡", "苏东坡", "苏轼", "东坡纪念馆", "东坡赤壁",
    "雪堂", "定惠院", "临皋亭", "东坡书院"
]


def geocode_address(address: str, city: str, amap_key: str) -> dict | None:
    """用高德地理编码把地址转坐标"""
    if not address:
        return None
    try:
        r = requests.get(AMAP_GEO_URL, params={
            "address": address, "city": city or "", "key": amap_key
        }, timeout=8)
        data = r.json()
        if data.get("status") == "1" and data.get("geocodes"):
            loc = data["geocodes"][0]["location"]  # "lng,lat"
            lng, lat = map(float, loc.split(","))
            return {"lat": lat, "lng": lng, "quality": "precise"}
    except Exception as e:
        print(f"  [地理编码失败] {address}: {e}")
    return None


def search_su_poi(city: str, amap_key: str) -> dict | None:
    """在城市内搜苏轼相关 POI，取第一个结果"""
    for kw in SU_KEYWORDS:
        try:
            r = requests.get(AMAP_POI_URL, params={
                "keywords": kw, "city": city,
                "types": "110000|120000",  # 风景名胜 + 历史古迹
                "key": amap_key, "output": "json"
            }, timeout=8)
            data = r.json()
            if data.get("status") == "1" and data.get("pois"):
                poi = data["pois"][0]
                lng, lat = map(float, poi["location"].split(","))
                return {
                    "lat": lat, "lng": lng,
                    "quality": "precise",
                    "poi_name": poi["name"],
                    "poi_id":   poi["id"]
                }
        except Exception:
            pass
        time.sleep(0.2)
    return None


def record_to_supabase_row(rec: dict, amap_key: str | None) -> dict:
    """把书中提取记录转换为 Supabase locations 表的行格式"""
    lat, lng = None, None
    coord_quality = rec.get("coord_quality_estimate", "city")
    poi_name, poi_id = None, None

    if amap_key:
        city = rec.get("city") or rec.get("province") or ""

        # 优先用详细地址地理编码
        if rec.get("modern_address"):
            geo = geocode_address(rec["modern_address"], city, amap_key)
            if geo:
                lat, lng = geo["lat"], geo["lng"]
                coord_quality = "precise"

        # 其次搜苏轼相关 POI
        if not lat and city:
            poi = search_su_poi(city, amap_key)
            if poi:
                lat, lng      = poi["lat"], poi["lng"]
                coord_quality = "precise"
                poi_name      = poi.get("poi_name")
                poi_id        = poi.get("poi_id")

        # 最后用城市名做兜底编码
        if not lat and city:
            geo = geocode_address(city, "", amap_key)
            if geo:
                lat, lng      = geo["lat"], geo["lng"]
                coord_quality = "city"

        time.sleep(0.3)  # 限速

    return {
        # ── 基础信息 ────────────────────────────────────────
        "name":              rec.get("location_name"),
        "modern_name":       rec.get("modern_name"),
        "modern_address":    rec.get("modern_address"),
        "province":          rec.get("province"),
        "city":              rec.get("city"),
        "district":          rec.get("district"),
        # ── 坐标 ────────────────────────────────────────────
        "lat":               lat,
        "lng":               lng,
        "coord_quality":     coord_quality,
        "verified_lat":      None,   # 留给人工核验填写
        "verified_lng":      None,
        "su_poi_name":       poi_name,
        "su_poi_id":         poi_id,
        # ── 苏轼行程 ────────────────────────────────────────
        "visit_year":        rec.get("visit_year"),
        "visit_period":      rec.get("visit_period"),
        "su_works":          rec.get("su_works") or [],
        "su_quote":          rec.get("su_quote"),
        # ── 内容 ────────────────────────────────────────────
        "author_note":       rec.get("author_note"),   # 改写后用，不原文展示
        "current_status":    rec.get("current_status"),
        "has_memorial":      rec.get("has_memorial", False),
        "tags":              rec.get("tags") or [],
        # ── 元数据 ──────────────────────────────────────────
        "source":            "李常生《苏轼行踪考》",
        "data_quality":      "A",   # 来自实地考察，质量最高
        "search_radius":     500 if coord_quality == "precise" else (
                             2000 if coord_quality == "district" else 5000),
    }


def push_to_supabase(rows: list[dict], url: str, key: str, table: str = "locations"):
    """批量 upsert 到 Supabase（冲突时按 name 更新）"""
    from supabase import create_client
    sb = create_client(url, key)

    BATCH = 50
    success, failed = 0, 0
    for i in range(0, len(rows), BATCH):
        batch = rows[i:i+BATCH]
        try:
            sb.table(table).upsert(batch, on_conflict="name").execute()
            success += len(batch)
            print(f"  [Supabase] upsert {i+len(batch)}/{len(rows)}")
        except Exception as e:
            print(f"  [错误] batch {i}: {e}")
            failed += len(batch)

    print(f"\n✅ Supabase upsert 完成: 成功 {success} | 失败 {failed}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",         required=True, help="locations.json 路径")
    parser.add_argument("--output",        default="output/supabase_rows.json")
    parser.add_argument("--amap-key",      default=None,  help="高德 API Key（可选，用于自动坐标）")
    parser.add_argument("--supabase-url",  default=None)
    parser.add_argument("--supabase-key",  default=None)
    parser.add_argument("--no-push",       action="store_true", help="只生成 JSON，不推送 Supabase")
    args = parser.parse_args()

    amap_key = args.amap_key or os.environ.get("AMAP_KEY")

    with open(args.input, encoding="utf-8") as f:
        records = json.load(f)

    print(f"📥 读入 {len(records)} 条记录，开始转换...\n")

    rows = []
    for i, rec in enumerate(records):
        name = rec.get("location_name", f"未命名_{i}")
        print(f"  [{i+1}/{len(records)}] {name}")
        row = record_to_supabase_row(rec, amap_key)
        rows.append(row)

    # 输出 JSON
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"\n💾 已保存: {args.output}")

    # 统计坐标质量
    quality_count = {}
    for r in rows:
        q = r.get("coord_quality", "unknown")
        quality_count[q] = quality_count.get(q, 0) + 1
    print(f"\n📍 坐标质量分布: {quality_count}")
    print(f"   （precise=精确POI / district=区级 / city=城市级）")

    # 推送 Supabase
    if not args.no_push:
        if args.supabase_url and args.supabase_key:
            push_to_supabase(rows, args.supabase_url, args.supabase_key)
        else:
            print("\n[提示] 未提供 Supabase 参数，跳过推送。")
            print("       手动推送: 用 supabase_rows.json 在 Supabase Dashboard 导入")


if __name__ == "__main__":
    main()
