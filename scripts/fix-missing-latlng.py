"""
一次性脚本：给 data-v4/places 中缺 lat/lng 的 42 个 place 补坐标。

策略：
1. 线性/区域地物（河流/运河/古道/湖泊）：用预设代表点（人工指定，最贴近文中具体足迹）
2. 城市/具体地点：modern_name → 高德 geocode
3. 同时回写 public/ 和 data-v4-source/（双源同步，遵守 INVENTORY-BASELINE）

执行：python3 scripts/fix-missing-latlng.py
"""
import json, os, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public" / "data-v4" / "places"
SRC = ROOT / "data-v4-source" / "places"

# 读 .env.local 拿 key（不进 git）
def load_env():
    env = ROOT / ".env.local"
    if not env.exists(): return {}
    out = {}
    for line in env.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out

ENV = load_env()
KEY = ENV.get("AMAP_WEB_SERVICE_KEY")
if not KEY:
    print("ERROR: AMAP_WEB_SERVICE_KEY 缺失"); sys.exit(1)

# 线性/区域地物的人工代表点（lng, lat）
# 选苏轼实际经过/记录的关键节点，不是地物中心
PRESET = {
    "P004": (108.65, 21.65),   # 北部湾海岸 → 钦州港湾
    "P005": (113.59, 23.05),   # 北江 → 广州三水汇流处
    "P006": (114.34, 34.79),   # 汴河 → 开封城内段
    "P007": (114.34, 34.79),   # 汴河漕运 → 开封
    "P060": (115.95, 37.70),   # 河北平原驿道 → 衡水代表点
    "P061": (118.78, 33.26),   # 洪泽湖 → 湖中心
    "P062": (118.55, 33.30),   # 洪泽湖古渡口 → 老子山渡
    "P069": (117.34, 32.67),   # 淮河南岸驿道 → 蚌埠段
    "P071": (115.43, 32.63),   # 淮河中游 → 信阳淮滨段
    "P086": (120.07, 31.55),   # 江南运河 → 苏州段
    "P105": (113.13, 23.07),   # 西江水路 → 肇庆段
    "P132": (116.31, 29.13),   # 鄱阳湖 → 都昌湖心
    "P133": (118.10, 35.38),   # 齐鲁古道 → 临沂段
    "P150": (115.27, 30.45),   # 浠水沙湖 → 沙湖镇
    "P164": (120.10, 31.30),   # 太湖西岸 → 宜兴段
    "P165": (120.22, 31.20),   # 太湖 → 湖心
    "P166": (114.50, 38.05),   # 太行山东麓 → 石家庄段
    "P168": (117.13, 36.20),   # 泰山余脉 → 泰安南
    "P215": (116.40, 35.40),   # 京杭大运河 → 济宁段
    "P222": (114.30, 30.60),   # 长江中游 → 武汉段
    "P223": (114.88, 30.45),   # 黄冈长江渡口 → 黄州渡
    "P224": (118.78, 32.05),   # 长江下游 → 南京段
}

# geocode 城市/具体地点
def geocode(addr):
    qs = urllib.parse.urlencode({"key": KEY, "address": addr, "output": "JSON"})
    url = f"https://restapi.amap.com/v3/geocode/geo?{qs}"
    req = urllib.request.Request(url, headers={"User-Agent": "su-shi-map-fix/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        d = json.loads(resp.read().decode("utf-8"))
    if d.get("status") != "1" or not d.get("geocodes"):
        return None
    loc = d["geocodes"][0].get("location", "")
    if "," not in loc: return None
    lng, lat = loc.split(",")
    return float(lng), float(lat)

def patch(pid, lng, lat, source):
    n = 0
    for base in (PUB, SRC):
        fp = base / f"{pid}.json"
        if not fp.exists(): continue
        d = json.loads(fp.read_text(encoding="utf-8"))
        d["lat"] = lat
        d["lng"] = lng
        d["_latlng_source"] = source  # 标记来源，方便后续核查
        fp.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
        n += 1
    return n

def main():
    missing = []
    for fp in sorted(PUB.glob("*.json")):
        d = json.loads(fp.read_text(encoding="utf-8"))
        if not d.get("lat") or not d.get("lng"):
            missing.append((fp.stem, d.get("modern_name"), d.get("ancient_name")))

    print(f"待补 {len(missing)} 个")
    ok = fail = 0
    for pid, modern, ancient in missing:
        if pid in PRESET:
            lng, lat = PRESET[pid]
            n = patch(pid, lng, lat, "preset")
            print(f"  ✓ {pid} {modern}  → ({lng},{lat}) [preset, {n}files]")
            ok += 1
            continue
        # geocode by modern_name
        try:
            r = geocode(modern)
            if not r:
                # 退回用 ancient_name
                r = geocode(ancient) if ancient else None
            if not r:
                print(f"  ✗ {pid} {modern} / {ancient}  geocode 全失败")
                fail += 1
                continue
            lng, lat = r
            n = patch(pid, lng, lat, "geocode")
            print(f"  ✓ {pid} {modern}  → ({lng},{lat}) [geocode, {n}files]")
            ok += 1
            time.sleep(0.15)  # 限速
        except Exception as e:
            print(f"  ✗ {pid} {modern}  err: {e}")
            fail += 1

    print(f"\n完成：成功 {ok}，失败 {fail}")

if __name__ == "__main__":
    main()
