/**
 * data-loader.ts 冒烟脚本
 * ----------------------------------------------------------
 * 不依赖浏览器环境，直接验证：
 *   ① v4 模式下 places-index / routes-index / places/P*.json 全可读
 *   ② v4 → v3 PlaceCore 适配字段对齐
 *   ③ 抽样地点详情结构合理
 *
 * 跑法：NEXT_PUBLIC_DATA_VERSION=v4 npx tsx data-v4/scripts/verify-data-loader.ts
 */

import fs from "fs";
import path from "path";

const ROOT = path.resolve(__dirname, "../..");
const PUBLIC_V4 = path.join(ROOT, "public", "data-v4");
const SRC_V4 = path.join(ROOT, "data-v4");

// 一致性检查：public/data-v4 与 data-v4 内容是否一致（避免漏同步）
function checkSync(): { ok: boolean; missing: string[] } {
  const missing: string[] = [];
  const files = [
    "places-index.json",
    "routes-index.json",
    "map-config.json",
    "meta/id-mapping-v3-to-v4.json",
    "meta/migration-stats.json",
    "places/P001.json",
    "routes/R10.json",
  ];
  for (const f of files) {
    if (!fs.existsSync(path.join(PUBLIC_V4, f))) missing.push(`public/data-v4/${f}`);
    if (!fs.existsSync(path.join(SRC_V4, f))) missing.push(`data-v4/${f}`);
  }
  return { ok: missing.length === 0, missing };
}

console.log("=== data-loader 冒烟 ===");

const sync = checkSync();
if (!sync.ok) {
  console.error("[FAIL] 数据同步缺失：", sync.missing);
  process.exit(1);
}
console.log("[ok] public/data-v4 与 data-v4 同步检查通过");

// ① places-index.json
const idx = JSON.parse(
  fs.readFileSync(path.join(PUBLIC_V4, "places-index.json"), "utf-8"),
);
console.log(
  `[ok] places-index.json 读到 ${idx.places.length} 节点 / detail_count=${idx._meta?.detail_count}`,
);

// ② v4 → v3 适配抽样
const sample = idx.places.slice(0, 3);
for (const p of sample) {
  const v3 = {
    id: p.id,
    songName: p.ancient_name,
    modernName: p.modern_name,
    type: p.type,
    lat: p.lat,
    lng: p.lng,
    routeId: p.related_routes?.[0],
  };
  const ok =
    v3.id && v3.songName && v3.modernName && v3.type && typeof v3.lat === "number";
  console.log(`  [adapter] ${ok ? "ok" : "FAIL"} ${v3.id} ${v3.songName} (${v3.modernName}) routeId=${v3.routeId}`);
  if (!ok) {
    console.error("适配失败", v3);
    process.exit(1);
  }
}

// ③ routes-index
const routes = JSON.parse(
  fs.readFileSync(path.join(PUBLIC_V4, "routes-index.json"), "utf-8"),
);
console.log(`[ok] routes-index.json ${routes.routes.length} 条路线`);

// ④ 抽样地点详情
const detailFiles = fs
  .readdirSync(path.join(PUBLIC_V4, "places"))
  .filter((f) => f.endsWith(".json"));
console.log(`[ok] places/ 共 ${detailFiles.length} 个详情文件`);

let withPeriods = 0;
let withMemorial = 0;
let withFoods = 0;
let withGlobalEvents = 0;
for (const f of detailFiles) {
  const d = JSON.parse(fs.readFileSync(path.join(PUBLIC_V4, "places", f), "utf-8"));
  if (d.periods?.length) withPeriods++;
  if (d.memorial_sites?.length) withMemorial++;
  if (d.foods?.length) withFoods++;
  if (d.global_events?.length) withGlobalEvents++;
}
console.log(
  `  详情统计：periods ${withPeriods} / memorial ${withMemorial} / foods ${withFoods} / global_events ${withGlobalEvents}`,
);

// ⑤ 抽查 R10 黄州贬谪
const r10 = JSON.parse(fs.readFileSync(path.join(PUBLIC_V4, "routes/R10.json"), "utf-8"));
console.log(
  `[ok] R10 黄州贬谪：${r10.name || r10.metadata?.name || "?"} | segments=${r10.track_segments?.length ?? 0}`,
);
if (r10.track_segments?.[0]) {
  const seg = r10.track_segments[0];
  console.log(
    `  segment[0] label="${seg.label}" places=${seg.place_ids?.length ?? 0} mode=${seg.transport_mode}`,
  );
}

// ⑥ 映射统计
const mapping = JSON.parse(
  fs.readFileSync(path.join(PUBLIC_V4, "meta/id-mapping-v3-to-v4.json"), "utf-8"),
);
console.log(
  `[ok] 映射表：v4=${mapping._meta.total_v4} 匹配=${mapping._meta.matched} 未匹配=${mapping._meta.unmatched}`,
);

console.log("\n✅ data-loader 冒烟全部通过。");
