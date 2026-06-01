/**
 * Phase 2.1 + 2.2 合并脚本
 * - 2.1：根据古名/现代名/坐标三重匹配，生成 v3 → v4 ID 映射
 *   - v3 源 1：data/places-core.json（SS001-160 扁平索引）
 *   - v3 源 2：data/places-detailed-v3.json（77 个拼音 key 详情）
 *   - v3 源 3：data/places/SS*.json（120 个 SS 文件，含 periods 章节）
 * - 2.2：把匹配上的 v3 详情灌进 data-v4/places/P*.json
 *
 * 输出：
 *   data-v4/meta/id-mapping-v3-to-v4.json
 *   data-v4/meta/id-mapping-unmatched.json
 *   data-v4/places/P*.json （仅匹配上的）
 *   data-v4/meta/migration-stats.json
 */

import fs from "fs";
import path from "path";

// ----- 路径常量 -----
const ROOT = path.resolve(__dirname, "../..");
const V3_CORE = path.join(ROOT, "data/places-core.json");
const V3_DETAIL = path.join(ROOT, "data/places-detailed-v3.json");
const V3_SS_DIR = path.join(ROOT, "data/places");

const V4_INDEX = path.join(ROOT, "data-v4/places-index.json");
const V4_PLACES_DIR = path.join(ROOT, "data-v4/places");
const V4_META_DIR = path.join(ROOT, "data-v4/meta");

// ----- 类型 -----
interface V3CoreItem {
  id: string;
  lat: number;
  lng: number;
  type: string;
  stage?: string;
  importance?: number;
  songName: string;
  modernName: string;
  routeId?: string;
  routeOrder?: number;
}

interface V3DetailItem {
  place_id: string;
  name_song: string;
  name_modern: string;
  name_pinyin?: string;
  latitude: number;
  longitude: number;
  place_type?: string;
  tags?: string[];
  summary?: string;
  background?: string;
  global_events?: any[];
  global_works?: any[];
  route_events?: Record<string, any[]>;
  route_works?: Record<string, any[]>;
  memorial_sites?: any[];
  foods?: any[];
  transport?: Record<string, string>;
  sub_places?: any[];
}

interface V3SSPeriod {
  id: string;
  periods: Array<{ period: string; title: string; description: string }>;
}

interface V4Place {
  id: string;
  ancient_name: string;
  modern_name: string;
  type: string;
  lat: number;
  lng: number;
  related_routes: string[];
  legacy?: any;
  has_detail: boolean;
}

// ----- 工具 -----
function distDeg(a: { lat: number; lng: number }, b: { lat: number; lng: number }): number {
  return Math.sqrt(Math.pow(a.lat - b.lat, 2) + Math.pow(a.lng - b.lng, 2));
}

function normalize(s: string): string {
  if (!s) return "";
  return s
    .replace(/[\s（）()，,。．·、\/]/g, "")
    .toLowerCase();
}

// 拆分古名变体：眉州/眉山 → ["眉州", "眉山"]
function splitAncientVariants(name: string): string[] {
  if (!name) return [];
  return name
    .split(/[\/／]/g)
    .map((s) => s.trim())
    .filter(Boolean);
}

// ----- 加载 -----
console.log("[load] 读取 v3 数据...");
const v3Core: V3CoreItem[] = JSON.parse(fs.readFileSync(V3_CORE, "utf-8"));
const v3DetailRaw = JSON.parse(fs.readFileSync(V3_DETAIL, "utf-8")) as {
  places: Record<string, V3DetailItem>;
};
const v3Detail: V3DetailItem[] = Object.values(v3DetailRaw.places);

const ssFiles = fs
  .readdirSync(V3_SS_DIR)
  .filter((f) => /^SS\d+\.json$/.test(f));
const v3SS: Map<string, V3SSPeriod> = new Map();
for (const f of ssFiles) {
  const data = JSON.parse(fs.readFileSync(path.join(V3_SS_DIR, f), "utf-8"));
  v3SS.set(data.id, data);
}

const v4IndexRaw = JSON.parse(fs.readFileSync(V4_INDEX, "utf-8")) as {
  places: V4Place[];
};
const v4Places = v4IndexRaw.places;

console.log(
  `[load] v3-core ${v3Core.length} | v3-detail ${v3Detail.length} | v3-SS ${v3SS.size} | v4 ${v4Places.length}`,
);

// ----- 2.1 匹配 -----
interface MatchResult {
  v4_id: string;
  v4_ancient: string;
  v4_modern: string;
  v4_lat: number;
  v4_lng: number;
  ss_id: string | null;
  ss_distance: number | null;
  pinyin_id: string | null;
  pinyin_distance: number | null;
  match_strategy: string;
  confidence: number; // 0-1
  notes: string[];
}

function matchOne(p: V4Place): MatchResult {
  const result: MatchResult = {
    v4_id: p.id,
    v4_ancient: p.ancient_name,
    v4_modern: p.modern_name,
    v4_lat: p.lat,
    v4_lng: p.lng,
    ss_id: null,
    ss_distance: null,
    pinyin_id: null,
    pinyin_distance: null,
    match_strategy: "none",
    confidence: 0,
    notes: [],
  };

  const v4AncientVariants = splitAncientVariants(p.ancient_name);
  const v4AncientNorm = v4AncientVariants.map(normalize);
  const v4ModernNorm = normalize(p.modern_name);

  // ---- 匹配 v3 SS（places-core） ----
  // 候选：古名精确/子串/坐标≤0.5度 三选一
  let bestSS: { item: V3CoreItem; d: number; strat: string; conf: number } | null = null;
  for (const ss of v3Core) {
    const ssAncientNorm = normalize(ss.songName);
    const ssModernNorm = normalize(ss.modernName);
    const d = distDeg({ lat: p.lat, lng: p.lng }, { lat: ss.lat, lng: ss.lng });

    let strat = "";
    let conf = 0;

    // 精确古名命中
    if (v4AncientNorm.some((v) => v && v === ssAncientNorm)) {
      strat = "ancient_exact";
      conf = d <= 0.5 ? 0.95 : 0.7;
    }
    // 古名互相子串（眉山纱縠行 包含 眉山）
    else if (
      v4AncientNorm.some((v) => v && (ssAncientNorm.includes(v) || v.includes(ssAncientNorm)))
    ) {
      strat = "ancient_substr";
      conf = d <= 0.3 ? 0.85 : 0.55;
    }
    // 现代名相同 + 距离近
    else if (v4ModernNorm && ssModernNorm && v4ModernNorm === ssModernNorm && d <= 0.3) {
      strat = "modern_exact";
      conf = 0.8;
    }
    // 现代名子串 + 距离近
    else if (
      v4ModernNorm &&
      ssModernNorm &&
      (v4ModernNorm.includes(ssModernNorm) || ssModernNorm.includes(v4ModernNorm)) &&
      d <= 0.3
    ) {
      strat = "modern_substr";
      conf = 0.65;
    }
    // 仅坐标极近（≤ 0.05 度，约 5km）
    else if (d <= 0.05) {
      strat = "coord_near";
      conf = 0.5;
    }

    if (conf > 0 && (!bestSS || conf > bestSS.conf || (conf === bestSS.conf && d < bestSS.d))) {
      bestSS = { item: ss, d, strat, conf };
    }
  }

  if (bestSS) {
    result.ss_id = bestSS.item.id;
    result.ss_distance = +bestSS.d.toFixed(4);
    result.match_strategy = `ss:${bestSS.strat}`;
    result.confidence = bestSS.conf;
  }

  // ---- 匹配 v3 详情（拼音 key） ----
  let bestPY: { item: V3DetailItem; d: number; strat: string; conf: number } | null = null;
  for (const dt of v3Detail) {
    const dtAncientVariants = splitAncientVariants(dt.name_song);
    const dtAncientNorm = dtAncientVariants.map(normalize);
    const dtModernNorm = normalize(dt.name_modern);
    const d = distDeg(
      { lat: p.lat, lng: p.lng },
      { lat: dt.latitude, lng: dt.longitude },
    );

    let strat = "";
    let conf = 0;

    if (v4AncientNorm.some((v) => v && dtAncientNorm.includes(v))) {
      strat = "ancient_exact";
      conf = d <= 0.5 ? 0.95 : 0.7;
    } else if (
      v4AncientNorm.some((v) =>
        dtAncientNorm.some((dn) => dn && v && (dn.includes(v) || v.includes(dn))),
      )
    ) {
      strat = "ancient_substr";
      conf = d <= 0.3 ? 0.85 : 0.55;
    } else if (v4ModernNorm && dtModernNorm && v4ModernNorm === dtModernNorm && d <= 0.3) {
      strat = "modern_exact";
      conf = 0.8;
    } else if (
      v4ModernNorm &&
      dtModernNorm &&
      (v4ModernNorm.includes(dtModernNorm) || dtModernNorm.includes(v4ModernNorm)) &&
      d <= 0.3
    ) {
      strat = "modern_substr";
      conf = 0.65;
    } else if (d <= 0.05) {
      strat = "coord_near";
      conf = 0.5;
    }

    if (conf > 0 && (!bestPY || conf > bestPY.conf || (conf === bestPY.conf && d < bestPY.d))) {
      bestPY = { item: dt, d, strat, conf };
    }
  }

  if (bestPY) {
    result.pinyin_id = bestPY.item.place_id;
    result.pinyin_distance = +bestPY.d.toFixed(4);
    if (bestPY.conf > result.confidence) {
      result.match_strategy = `pinyin:${bestPY.strat}`;
      result.confidence = bestPY.conf;
    } else {
      result.match_strategy = result.match_strategy + `+pinyin:${bestPY.strat}`;
    }
  }

  return result;
}

console.log("[match] 跑 ID 映射...");
const matches: MatchResult[] = v4Places.map(matchOne);

// 统计
const byStrat: Record<string, number> = {};
const byConf = { high: 0, mid: 0, low: 0, none: 0 };
const matched: MatchResult[] = [];
const unmatched: MatchResult[] = [];

for (const m of matches) {
  byStrat[m.match_strategy] = (byStrat[m.match_strategy] || 0) + 1;
  if (m.confidence >= 0.8) byConf.high++;
  else if (m.confidence >= 0.6) byConf.mid++;
  else if (m.confidence > 0) byConf.low++;
  else byConf.none++;

  if (m.confidence >= 0.6 && (m.ss_id || m.pinyin_id)) matched.push(m);
  else unmatched.push(m);
}

console.log(`[match] 匹配置信度：高 ${byConf.high} / 中 ${byConf.mid} / 低 ${byConf.low} / 无 ${byConf.none}`);

// ----- 写映射表 -----
if (!fs.existsSync(V4_META_DIR)) fs.mkdirSync(V4_META_DIR, { recursive: true });

const mapping: Record<string, any> = {};
for (const m of matches) {
  mapping[m.v4_id] = {
    ancient: m.v4_ancient,
    modern: m.v4_modern,
    ss_id: m.ss_id,
    pinyin_id: m.pinyin_id,
    match_strategy: m.match_strategy,
    confidence: m.confidence,
    ss_distance: m.ss_distance,
    pinyin_distance: m.pinyin_distance,
  };
}

fs.writeFileSync(
  path.join(V4_META_DIR, "id-mapping-v3-to-v4.json"),
  JSON.stringify(
    {
      _meta: {
        generated_at: new Date().toISOString(),
        total_v4: v4Places.length,
        matched: matched.length,
        unmatched: unmatched.length,
        confidence_dist: byConf,
        strategy_dist: byStrat,
      },
      mapping,
    },
    null,
    2,
  ),
);

fs.writeFileSync(
  path.join(V4_META_DIR, "id-mapping-unmatched.json"),
  JSON.stringify(
    {
      _meta: {
        generated_at: new Date().toISOString(),
        unmatched_count: unmatched.length,
        note: "这些 v4 节点在 v3 数据中找不到对应，多为新增小驿站/沿途景点。可人工核查或保留为只有索引数据。",
      },
      unmatched: unmatched.map((u) => ({
        v4_id: u.v4_id,
        v4_ancient: u.v4_ancient,
        v4_modern: u.v4_modern,
        v4_lat: u.v4_lat,
        v4_lng: u.v4_lng,
        nearest_ss_id: u.ss_id,
        nearest_ss_distance: u.ss_distance,
        nearest_pinyin_id: u.pinyin_id,
        nearest_pinyin_distance: u.pinyin_distance,
        confidence: u.confidence,
      })),
    },
    null,
    2,
  ),
);

console.log(`[match] 已写入 id-mapping-v3-to-v4.json + id-mapping-unmatched.json`);

// ----- 2.2 灌详情 -----
console.log("[migrate] 灌入 v3 详情...");
if (!fs.existsSync(V4_PLACES_DIR)) fs.mkdirSync(V4_PLACES_DIR, { recursive: true });

let detailWritten = 0;
const v4ById: Record<string, V4Place> = {};
for (const p of v4Places) v4ById[p.id] = p;

for (const m of matched) {
  const v4p = v4ById[m.v4_id];
  if (!v4p) continue;

  const ss = m.ss_id ? v3Core.find((c) => c.id === m.ss_id) : null;
  const ssPeriod = m.ss_id ? v3SS.get(m.ss_id) : null;
  const detail = m.pinyin_id ? v3Detail.find((d) => d.place_id === m.pinyin_id) : null;

  // 组装 v4 详情
  const out: any = {
    id: v4p.id,
    ancient_name: v4p.ancient_name,
    modern_name: v4p.modern_name,
    type: v4p.type,
    lat: v4p.lat,
    lng: v4p.lng,
    related_routes: v4p.related_routes,
    summary: detail?.summary || "",
    background: detail?.background || "",
    tags: detail?.tags || [],

    // 章节叙事（来自 SS*.json periods）
    periods: ssPeriod?.periods || [],

    // 全局事件 / 路线事件 / 作品
    global_events: detail?.global_events || [],
    global_works: detail?.global_works || [],
    route_events: detail?.route_events || {},
    route_works: detail?.route_works || {},

    // 实用信息
    memorial_sites: detail?.memorial_sites || [],
    foods: detail?.foods || [],
    transport: detail?.transport || {},
    sub_places: detail?.sub_places || [],

    // 元数据
    legacy: {
      ss_id: m.ss_id,
      pinyin_id: m.pinyin_id,
      match_strategy: m.match_strategy,
      confidence: m.confidence,
      v3_lat: ss?.lat ?? detail?.latitude ?? null,
      v3_lng: ss?.lng ?? detail?.longitude ?? null,
    },
  };

  fs.writeFileSync(
    path.join(V4_PLACES_DIR, `${v4p.id}.json`),
    JSON.stringify(out, null, 2),
  );
  detailWritten++;

  // 标记 has_detail
  v4p.has_detail = true;
}

// 回写 places-index 更新 has_detail
const newIndex = {
  ...v4IndexRaw,
  _meta: {
    ...((v4IndexRaw as any)._meta || {}),
    detail_count: detailWritten,
    detail_updated_at: new Date().toISOString(),
  },
  places: v4Places,
};
fs.writeFileSync(V4_INDEX, JSON.stringify(newIndex, null, 2));

// ----- 写迁移统计 -----
fs.writeFileSync(
  path.join(V4_META_DIR, "migration-stats.json"),
  JSON.stringify(
    {
      _meta: { generated_at: new Date().toISOString() },
      v4_total: v4Places.length,
      matched: matched.length,
      unmatched: unmatched.length,
      detail_files_written: detailWritten,
      confidence_dist: byConf,
      strategy_dist: byStrat,
      coverage: {
        with_periods: matched.filter((m) => m.ss_id && v3SS.has(m.ss_id)).length,
        with_detail: matched.filter((m) => m.pinyin_id).length,
        with_both: matched.filter((m) => m.ss_id && m.pinyin_id).length,
        with_only_ss: matched.filter((m) => m.ss_id && !m.pinyin_id).length,
        with_only_pinyin: matched.filter((m) => !m.ss_id && m.pinyin_id).length,
      },
    },
    null,
    2,
  ),
);

console.log(`[migrate] 详情写入完成：${detailWritten} 个 P*.json`);
console.log("[done] Phase 2.1 + 2.2 全部完成");
