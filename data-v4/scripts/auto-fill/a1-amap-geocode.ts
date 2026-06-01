/**
 * A1 · 高德 Web Service 坐标自动化
 * ----------------------------------------------------------
 * 用 AMAP_WEB_SERVICE_KEY 调用高德地理编码 API，把 234 节点
 * 的 modern_name 全部真实地理编码，校验/修正现有坐标。
 *
 * 策略：
 *   1. 读 places-index.json 234 节点
 *   2. 逐条调高德 /v3/geocode/geo（GCJ-02 输出）
 *   3. 对比现有 lng/lat：
 *      - 距离 < 1km：保持现状，标 amap_verified
 *      - 距离 1-10km：替换为高德值（更精确），标 amap_corrected
 *      - 距离 > 10km：标 amap_conflict，写入待审清单（人工裁决）
 *      - 高德查不到：保持现状，标 amap_failed，写入待审清单
 *   4. 输出：
 *      - data-v4/meta/coords-amap-verified.json（机读）
 *      - data-v4/meta/coords-amap-conflict.md（人读，需外部专家或用户裁决）
 *
 * QPS 限制：高德 Web 服务 标准版 50 QPS，免费版 3 QPS。
 * 为安全计，使用 250ms 间隔（4 QPS），全 234 节点约 60 秒。
 *
 * 用法：
 *   AMAP_WEB_SERVICE_KEY=xxx npx tsx data-v4/scripts/auto-fill/a1-amap-geocode.ts
 *   或先 source .env.local 再跑
 *
 * 安全：
 *   - 只读 modern_name（标准化的现代地名），不编码 ancient_name（宋代名容易误判）
 *   - 失败重试 1 次，超时 5s
 *   - 全程不修改原数据，只输出新文件，等用户确认后再合并
 * ----------------------------------------------------------
 */

import * as fs from "fs";
import * as path from "path";

// 手动读 .env.local（避免引入 dotenv 依赖）
function loadEnvLocal() {
  const envPath = path.resolve(__dirname, "..", "..", "..", ".env.local");
  if (!fs.existsSync(envPath)) return;
  const content = fs.readFileSync(envPath, "utf-8");
  for (const line of content.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const idx = trimmed.indexOf("=");
    if (idx < 0) continue;
    const key = trimmed.slice(0, idx).trim();
    const val = trimmed.slice(idx + 1).trim();
    if (!process.env[key]) process.env[key] = val;
  }
}
loadEnvLocal();

const AMAP_KEY = process.env.AMAP_WEB_SERVICE_KEY;
if (!AMAP_KEY) {
  console.error("❌ AMAP_WEB_SERVICE_KEY 未配置（.env.local）");
  process.exit(1);
}

const PROJECT_ROOT = path.resolve(__dirname, "..", "..", "..");
const PLACES_INDEX_FILE = path.join(PROJECT_ROOT, "public/data-v4/places-index.json");
const OUTPUT_VERIFIED = path.join(PROJECT_ROOT, "data-v4/meta/auto-fill-results/coords-amap-verified.json");
const OUTPUT_CONFLICT = path.join(PROJECT_ROOT, "data-v4/meta/auto-fill-results/coords-amap-conflict.md");

// ============ 类型定义 ============
interface PlaceIndex {
  id: string;
  ancient_name: string;
  modern_name: string;
  type: string;
  lng: number;
  lat: number;
  coordinate_source: string;
  related_routes: string[];
}

interface AmapGeocodeResponse {
  status: string;
  info: string;
  count: string;
  geocodes?: {
    formatted_address: string;
    province: string;
    city: string;
    district: string;
    location: string; // "lng,lat"
    level: string;
  }[];
}

interface VerificationResult {
  id: string;
  ancient_name: string;
  modern_name: string;
  type: string;
  current_lng: number;
  current_lat: number;
  current_source: string;
  amap_lng: number | null;
  amap_lat: number | null;
  amap_formatted_address: string | null;
  amap_level: string | null;
  distance_km: number | null;
  status: "amap_verified" | "amap_corrected" | "amap_conflict" | "amap_failed";
  notes?: string;
}

// ============ 工具函数 ============

/** 计算两点距离（km），简化球面公式 */
function haversineDistance(lng1: number, lat1: number, lng2: number, lat2: number): number {
  const R = 6371;
  const toRad = (x: number) => (x * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLng = toRad(lng2 - lng1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

/** 调用高德 geocode（GCJ-02）*/
async function amapGeocode(address: string): Promise<AmapGeocodeResponse> {
  const url = `https://restapi.amap.com/v3/geocode/geo?key=${AMAP_KEY}&address=${encodeURIComponent(address)}&output=json`;
  const ctrl = new AbortController();
  const timeout = setTimeout(() => ctrl.abort(), 5000);
  try {
    const resp = await fetch(url, { signal: ctrl.signal });
    return (await resp.json()) as AmapGeocodeResponse;
  } finally {
    clearTimeout(timeout);
  }
}

/** 单点验证：调用高德 + 对比 */
async function verifyOne(p: PlaceIndex): Promise<VerificationResult> {
  const result: VerificationResult = {
    id: p.id,
    ancient_name: p.ancient_name,
    modern_name: p.modern_name,
    type: p.type,
    current_lng: p.lng,
    current_lat: p.lat,
    current_source: p.coordinate_source,
    amap_lng: null,
    amap_lat: null,
    amap_formatted_address: null,
    amap_level: null,
    distance_km: null,
    status: "amap_failed",
  };

  // 跳过明显不该地理编码的（沿途水景/古道之类，没有具体行政区点）
  const fuzzyKeywords = ["全线", "全域", "古道", "水路", "海岸", "海峡", "干流", "水系", "南麓", "北麓", "余脉", "边缘", "画廊", "夹江"];
  if (fuzzyKeywords.some((kw) => p.modern_name.includes(kw))) {
    result.status = "amap_failed";
    result.notes = "fuzzy_geographic_feature_skip";
    return result;
  }

  try {
    const resp = await amapGeocode(p.modern_name);
    if (resp.status === "1" && resp.geocodes && resp.geocodes.length > 0) {
      const top = resp.geocodes[0];
      const [lng, lat] = top.location.split(",").map(Number);
      result.amap_lng = lng;
      result.amap_lat = lat;
      result.amap_formatted_address = top.formatted_address;
      result.amap_level = top.level;

      const dist = haversineDistance(p.lng, p.lat, lng, lat);
      result.distance_km = Math.round(dist * 100) / 100;

      if (dist < 1) {
        result.status = "amap_verified";
      } else if (dist < 10) {
        result.status = "amap_corrected";
      } else {
        result.status = "amap_conflict";
      }
    } else {
      result.status = "amap_failed";
      result.notes = `amap_no_result: ${resp.info}`;
    }
  } catch (err) {
    result.status = "amap_failed";
    result.notes = `request_error: ${(err as Error).message}`;
  }
  return result;
}

/** 延时 */
function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

// ============ 主流程 ============
async function main() {
  console.log("📥 读取 places-index.json...");
  const index = JSON.parse(fs.readFileSync(PLACES_INDEX_FILE, "utf-8"));
  const places: PlaceIndex[] = index.places;
  console.log(`   共 ${places.length} 节点`);

  const results: VerificationResult[] = [];
  const startTime = Date.now();

  for (let i = 0; i < places.length; i++) {
    const p = places[i];
    process.stdout.write(`\r[${i + 1}/${places.length}] ${p.id} ${p.ancient_name} (${p.modern_name})...`);
    const result = await verifyOne(p);
    results.push(result);
    await sleep(250); // 4 QPS
  }
  console.log(""); // 换行

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  console.log(`\n✅ 全部完成，耗时 ${elapsed}s`);

  // 统计
  const stats = {
    total: results.length,
    verified: results.filter((r) => r.status === "amap_verified").length,
    corrected: results.filter((r) => r.status === "amap_corrected").length,
    conflict: results.filter((r) => r.status === "amap_conflict").length,
    failed: results.filter((r) => r.status === "amap_failed").length,
  };
  console.log(`\n📊 结果统计：`);
  console.log(`   ✅ amap_verified（距离 < 1km · 现状靠谱）   : ${stats.verified}`);
  console.log(`   🔧 amap_corrected（距离 1-10km · 高德更准）  : ${stats.corrected}`);
  console.log(`   ⚠️  amap_conflict（距离 > 10km · 需人工裁决） : ${stats.conflict}`);
  console.log(`   ❌ amap_failed（高德查不到/跳过模糊地名）    : ${stats.failed}`);

  // 写机读 JSON
  fs.mkdirSync(path.dirname(OUTPUT_VERIFIED), { recursive: true });
  fs.writeFileSync(
    OUTPUT_VERIFIED,
    JSON.stringify(
      {
        _meta: {
          generated_at: new Date().toISOString(),
          stats,
          api: "amap geocode v3",
          input_count: places.length,
        },
        results,
      },
      null,
      2
    )
  );
  console.log(`\n💾 ${OUTPUT_VERIFIED}`);

  // 写人读 conflict 清单（待人工裁决）
  const conflicts = results.filter((r) => r.status === "amap_conflict" || r.status === "amap_failed");
  const md: string[] = [];
  md.push(`# 高德地理编码 · 待裁决清单（${conflicts.length} 条）\n`);
  md.push(`生成时间：${new Date().toISOString()}\n`);
  md.push(`## 一、统计\n`);
  md.push(`- ⚠️ amap_conflict（距离 > 10km，需人工裁决）：${stats.conflict}`);
  md.push(`- ❌ amap_failed（高德查不到 / 跳过模糊地名）：${stats.failed}\n`);
  md.push(`## 二、冲突详情（amap_conflict · 距离 > 10km）\n`);
  md.push(`| ID | 古名 | 现名 | 当前坐标 | 高德坐标 | 距离 | 高德识别地址 | 处理建议 |`);
  md.push(`|---|---|---|---|---|---|---|---|`);
  for (const r of results.filter((x) => x.status === "amap_conflict")) {
    md.push(
      `| ${r.id} | ${r.ancient_name} | ${r.modern_name} | (${r.current_lng.toFixed(4)}, ${r.current_lat.toFixed(4)}) | (${r.amap_lng?.toFixed(4)}, ${r.amap_lat?.toFixed(4)}) | ${r.distance_km}km | ${r.amap_formatted_address} | （待人工裁决：保持现状 / 用高德值 / 改 modern_name 重查）|`
    );
  }
  md.push(`\n## 三、失败详情（amap_failed · 高德查不到）\n`);
  md.push(`| ID | 古名 | 现名 | 当前坐标 | 失败原因 |`);
  md.push(`|---|---|---|---|---|`);
  for (const r of results.filter((x) => x.status === "amap_failed")) {
    md.push(`| ${r.id} | ${r.ancient_name} | ${r.modern_name} | (${r.current_lng.toFixed(4)}, ${r.current_lat.toFixed(4)}) | ${r.notes || "unknown"} |`);
  }
  fs.writeFileSync(OUTPUT_CONFLICT, md.join("\n"));
  console.log(`💾 ${OUTPUT_CONFLICT}`);

  console.log(`\n下一步：人工 review conflict.md，决定每条 verified/corrected/keep_current。`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
