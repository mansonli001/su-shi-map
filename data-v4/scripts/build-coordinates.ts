/**
 * data-v4 Phase 1 / Step 4
 * ----------------------------------------------------------
 * 把 234 个节点全部补上 GCJ-02 坐标
 *
 * 三层匹配策略：
 *  1. 白名单命中（古名直接 / 古名作为 key 的前缀） → core_curated（精度 ★★★★+）
 *  2. 子串模糊匹配（节点古名 contains 白名单 key 或反向） → inferred（精度 ★★★）
 *  3. 路线区域中位 → approximate（精度 ★★，标注 chgis_pending）
 *
 * 输出：data-v4/meta/places-with-coords.json
 * ----------------------------------------------------------
 */

import * as fs from "fs";
import * as path from "path";

interface RawNode {
  ancient_name: string;
  modern_name: string;
  routes: { route_id: string; layer: "main" | "sight" | "around"; order_in_route: number }[];
  occurrences: number;
}

interface Whitelist {
  [key: string]: { lng: number; lat: number; modern: string; type?: string };
}

interface CoordedNode extends RawNode {
  lng: number;
  lat: number;
  coordinate_source:
    | "core_curated"
    | "inferred"
    | "approximate"
    | "chgis_pending";
  trustworthy: boolean;
  match_strategy: "exact" | "alias" | "substring" | "route_centroid";
  matched_key?: string; // 命中白名单的 key
  inferred_type?: string;
}

const projectRoot = path.resolve(__dirname, "..", "..");

// ======================================================
// 路线区域中心兜底（基于订正版主线节点经纬度大致质心）
// ======================================================
const ROUTE_CENTROIDS: Record<string, { lng: number; lat: number }> = {
  R00: { lng: 103.86, lat: 30.05 }, // 眉山-成都
  R01: { lng: 109.5, lat: 33.0 }, // 蜀-京全程
  R02: { lng: 108.5, lat: 30.0 }, // 出蜀南行长江
  R03: { lng: 110.5, lat: 33.5 }, // 荆州-凤翔
  R04: { lng: 113.0, lat: 32.0 }, // 凤翔-京-扶柩归蜀
  R05: { lng: 109.0, lat: 33.5 }, // 眉山-京 1069
  R06: { lng: 117.5, lat: 32.0 }, // 京-杭州通判
  R07: { lng: 119.0, lat: 33.0 }, // 杭州-密州
  R08: { lng: 118.0, lat: 34.5 }, // 密州-徐州
  R09: { lng: 118.5, lat: 33.0 }, // 徐州-湖州-押京
  R10: { lng: 115.5, lat: 32.5 }, // 京-黄州
  R11: { lng: 117.0, lat: 30.5 }, // 黄州-庐山-金陵-常州
  R12: { lng: 119.5, lat: 35.0 }, // 宜兴-登州
  R13: { lng: 117.5, lat: 36.5 }, // 登州-还朝
  R14: { lng: 117.0, lat: 32.5 }, // 京-杭再任
  R15: { lng: 118.5, lat: 32.5 }, // 杭州-京 1091
  R16: { lng: 116.5, lat: 33.0 }, // 京-颍州-扬州
  R17: { lng: 115.5, lat: 36.0 }, // 扬州-京-定州
  R18: { lng: 113.0, lat: 23.0 }, // 定州-惠州-儋州
  R19: { lng: 113.5, lat: 25.5 }, // 北归终老常州
};

// ======================================================
// 匹配函数
// ======================================================
function matchNode(
  node: RawNode,
  whitelist: Whitelist
):
  | (Pick<CoordedNode, "lng" | "lat" | "coordinate_source" | "trustworthy" | "match_strategy" | "matched_key" | "inferred_type">)
  | null {
  const ancient = node.ancient_name;

  // 1. 精确命中
  if (whitelist[ancient]) {
    const w = whitelist[ancient];
    return {
      lng: w.lng,
      lat: w.lat,
      coordinate_source: "core_curated",
      trustworthy: true,
      match_strategy: "exact",
      matched_key: ancient,
      inferred_type: w.type,
    };
  }

  // 2. 子串匹配（白名单 key 是节点的子串，或反之）
  // 优先匹配较长的 key（更具体）
  const keysSorted = Object.keys(whitelist).sort((a, b) => b.length - a.length);
  for (const key of keysSorted) {
    if (key.length < 2) continue;
    if (ancient.includes(key) || key.includes(ancient)) {
      // 排除常见误伤：单字"州"、"山"等不算
      if (key.length === 1) continue;
      const w = whitelist[key];
      return {
        lng: w.lng,
        lat: w.lat,
        coordinate_source: "inferred",
        trustworthy: false,
        match_strategy: "substring",
        matched_key: key,
        inferred_type: w.type,
      };
    }
  }

  // 3. 现代名匹配（节点已带 modern_name，回查白名单 modern 字段）
  if (node.modern_name) {
    for (const [key, w] of Object.entries(whitelist)) {
      if (w.modern && (w.modern.includes(node.modern_name) || node.modern_name.includes(w.modern.replace(/^[^市县区州]+/, "")))) {
        return {
          lng: w.lng,
          lat: w.lat,
          coordinate_source: "inferred",
          trustworthy: false,
          match_strategy: "alias",
          matched_key: key,
          inferred_type: w.type,
        };
      }
    }
  }

  // 4. 路线中心兜底
  const primaryRoute = node.routes[0]?.route_id;
  if (primaryRoute && ROUTE_CENTROIDS[primaryRoute]) {
    const c = ROUTE_CENTROIDS[primaryRoute];
    // 加一个小扰动避免完全堆叠（基于古名 hash）
    const hash = Array.from(node.ancient_name).reduce((s, ch) => s + ch.charCodeAt(0), 0);
    const dx = ((hash % 100) - 50) / 1000; // ±0.05 度 ≈ ±5km
    const dy = ((hash * 7 % 100) - 50) / 1000;
    return {
      lng: +(c.lng + dx).toFixed(4),
      lat: +(c.lat + dy).toFixed(4),
      coordinate_source: "approximate",
      trustworthy: false,
      match_strategy: "route_centroid",
    };
  }

  return null;
}

// ======================================================
// 入口
// ======================================================
function main() {
  const masterPath = path.join(projectRoot, "data-v4", "meta", "places-master-raw.json");
  const whitelistPath = path.join(projectRoot, "data-v4", "meta", "coordinate-whitelist.json");

  const master = JSON.parse(fs.readFileSync(masterPath, "utf-8"));
  const whitelistRaw = JSON.parse(fs.readFileSync(whitelistPath, "utf-8"));
  const { _meta: _, ...whitelist } = whitelistRaw as Whitelist & { _meta: unknown };

  const nodes: RawNode[] = master.nodes;

  const stats = { core_curated: 0, inferred: 0, approximate: 0, missing: 0 };
  const coorded: CoordedNode[] = [];
  const missing: string[] = [];

  for (const n of nodes) {
    const m = matchNode(n, whitelist as Whitelist);
    if (!m) {
      missing.push(n.ancient_name);
      stats.missing++;
      continue;
    }
    coorded.push({
      ...n,
      ...m,
      // 若节点没有 modern_name，且白名单 hit 提供了 modern，回填
      modern_name:
        n.modern_name ||
        (m.matched_key && (whitelist as Whitelist)[m.matched_key]?.modern) ||
        "",
    });
    stats[m.coordinate_source]++;
  }

  console.log(`[match] 总节点 ${nodes.length}：`);
  console.log(`  ★★★★+ core_curated   ${stats.core_curated}（精确白名单命中）`);
  console.log(`  ★★★   inferred       ${stats.inferred}（子串/别名匹配）`);
  console.log(`  ★★    approximate    ${stats.approximate}（路线区域中位兜底）`);
  console.log(`  ❌    missing         ${stats.missing}`);

  if (missing.length > 0) {
    console.log(`\n[missing] 未匹配节点（请补白名单或视为 approximate）：`);
    missing.forEach((m) => console.log(`  - ${m}`));
  }

  // 输出
  const outPath = path.join(projectRoot, "data-v4", "meta", "places-with-coords.json");
  fs.writeFileSync(
    outPath,
    JSON.stringify(
      {
        _meta: {
          generated_at: new Date().toISOString(),
          total: nodes.length,
          stats,
          missing,
        },
        nodes: coorded,
      },
      null,
      2
    ),
    "utf-8"
  );

  console.log(`\n[write] data-v4/meta/places-with-coords.json`);
  console.log(`\n✅ Step 4 完成。下一步：Step 5 生成 places-index.json + routes/R*.json`);
}

main();
