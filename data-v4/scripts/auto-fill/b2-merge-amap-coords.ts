/**
 * B2 · 合并高德 amap_corrected 坐标
 * ----------------------------------------------------------
 * 把 A1 跑出来的 86 个 amap_corrected（距离 1-10km）坐标
 * 真实写回 places-index.json + places/P*.json。
 *
 * 不动：amap_verified（已经准的）/ amap_conflict（需人工裁决）/ amap_failed
 *
 * 输出：
 *   - 修改 places-index.json 中的 lng/lat + coordinate_source = "amap_corrected"
 *   - 修改 places/P*.json 中的 lng/lat + coordinate_source = "amap_corrected"
 *   - data-v4/meta/auto-fill-results/coords-merge-report.md
 *
 * 用法：
 *   npx tsx data-v4/scripts/auto-fill/b2-merge-amap-coords.ts
 * ----------------------------------------------------------
 */

import * as fs from "fs";
import * as path from "path";

const PROJECT_ROOT = path.resolve(__dirname, "..", "..", "..");
const VERIFIED_FILE = path.join(PROJECT_ROOT, "data-v4/meta/auto-fill-results/coords-amap-verified.json");
const PLACES_INDEX = path.join(PROJECT_ROOT, "public/data-v4/places-index.json");
const PLACES_DIR = path.join(PROJECT_ROOT, "public/data-v4/places");
const REPORT_FILE = path.join(PROJECT_ROOT, "data-v4/meta/auto-fill-results/coords-merge-report.md");

interface VerificationResult {
  id: string;
  ancient_name: string;
  modern_name: string;
  current_lng: number;
  current_lat: number;
  current_source: string;
  amap_lng: number | null;
  amap_lat: number | null;
  amap_formatted_address: string | null;
  amap_level: string | null;
  distance_km: number | null;
  status: string;
}

async function main() {
  console.log("📥 读取 A1 验证结果...");
  const verifiedData = JSON.parse(fs.readFileSync(VERIFIED_FILE, "utf-8"));
  const results: VerificationResult[] = verifiedData.results;

  // 仅取 amap_corrected
  const corrected = results.filter((r) => r.status === "amap_corrected");
  console.log(`   待合并 amap_corrected: ${corrected.length} 条`);

  console.log("\n📥 读取 places-index.json...");
  const indexJson = JSON.parse(fs.readFileSync(PLACES_INDEX, "utf-8"));

  let mergedCount = 0;
  const mergeLog: { id: string; name: string; from: [number, number]; to: [number, number]; dist: number }[] = [];

  // ----- 1. 更新 places-index.json -----
  for (const cor of corrected) {
    const idx = indexJson.places.findIndex((p: any) => p.id === cor.id);
    if (idx < 0) continue;
    const oldLng = indexJson.places[idx].lng;
    const oldLat = indexJson.places[idx].lat;
    indexJson.places[idx].lng = cor.amap_lng;
    indexJson.places[idx].lat = cor.amap_lat;
    indexJson.places[idx].coordinate_source = "amap_corrected";
    indexJson.places[idx].amap_address = cor.amap_formatted_address;
    indexJson.places[idx].coords_updated_at = new Date().toISOString();
    mergedCount++;
    mergeLog.push({
      id: cor.id,
      name: cor.ancient_name,
      from: [oldLng, oldLat],
      to: [cor.amap_lng!, cor.amap_lat!],
      dist: cor.distance_km!,
    });

    // ----- 2. 同步更新 places/P*.json -----
    const placeFile = path.join(PLACES_DIR, `${cor.id}.json`);
    if (fs.existsSync(placeFile)) {
      const pd = JSON.parse(fs.readFileSync(placeFile, "utf-8"));
      pd.lng = cor.amap_lng;
      pd.lat = cor.amap_lat;
      pd.coordinate_source = "amap_corrected";
      pd.amap_address = cor.amap_formatted_address;
      pd.coords_updated_at = new Date().toISOString();
      fs.writeFileSync(placeFile, JSON.stringify(pd, null, 2));
    }
  }

  // 更新 _meta
  if (indexJson._meta) {
    indexJson._meta.coords_amap_merged_at = new Date().toISOString();
    indexJson._meta.coords_amap_corrected_count = mergedCount;
    if (!indexJson._meta.coordinate_source_dist) indexJson._meta.coordinate_source_dist = {};
    indexJson._meta.coordinate_source_dist.amap_corrected = mergedCount;
  }

  fs.writeFileSync(PLACES_INDEX, JSON.stringify(indexJson, null, 2));

  // 输出报告
  fs.mkdirSync(path.dirname(REPORT_FILE), { recursive: true });
  const md: string[] = [
    `# B2 高德坐标合并报告`,
    ``,
    `生成时间：${new Date().toISOString()}`,
    ``,
    `## 统计`,
    `- 合并 amap_corrected 坐标：**${mergedCount}** 条`,
    `- places-index.json 已更新`,
    `- places/P*.json 已同步更新`,
    ``,
    `## 详细变更（按距离降序）`,
    ``,
    `| ID | 古名 | 原坐标 | 高德坐标 | 距离(km) |`,
    `|---|---|---|---|---|`,
  ];
  mergeLog.sort((a, b) => b.dist - a.dist);
  for (const m of mergeLog) {
    md.push(
      `| ${m.id} | ${m.name} | (${m.from[0].toFixed(4)}, ${m.from[1].toFixed(4)}) | (${m.to[0].toFixed(4)}, ${m.to[1].toFixed(4)}) | ${m.dist} |`
    );
  }

  fs.writeFileSync(REPORT_FILE, md.join("\n"));
  console.log(`\n✅ 完成：${mergedCount} 条坐标合并到 places-index.json + places/*.json`);
  console.log(`💾 ${REPORT_FILE}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
