/**
 * 数据完整度体检脚本
 *
 * 输入：data-v4/places-index.json + data-v4/places/P*.json
 * 输出：
 *   - data-v4/meta/audit-report.json（机读）
 *   - data-v4/meta/audit-report.md（人读）
 *
 * 体检字段：
 *   核心：summary / background / tags / periods / memorial_sites / global_works
 *   补充：foods / transport / route_events / sub_places / photos
 */
import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(__dirname, "..");
const PLACES_DIR = path.join(ROOT, "places");
const INDEX_FILE = path.join(ROOT, "places-index.json");
const REPORT_JSON = path.join(ROOT, "meta", "audit-report.json");
const REPORT_MD = path.join(ROOT, "meta", "audit-report.md");

interface IndexPlace {
  id: string;
  ancient_name: string;
  modern_name: string;
  type: string;
  related_routes: string[];
  has_detail?: boolean;
}

interface PlaceDetail {
  id: string;
  ancient_name: string;
  modern_name: string;
  summary?: string;
  background?: string;
  tags?: string[];
  periods?: any[];
  global_events?: any[];
  global_works?: any[];
  route_events?: Record<string, any[]>;
  route_works?: Record<string, any[]>;
  memorial_sites?: any[];
  foods?: any[];
  transport?: { train?: string; bus?: string; car?: string; airport?: string };
  sub_places?: any[];
  legacy?: { ss_id?: string; confidence?: number; match_strategy?: string };
}

const idx = JSON.parse(fs.readFileSync(INDEX_FILE, "utf-8"));
const places: IndexPlace[] = idx.places;

const FIELDS = [
  "summary",
  "background",
  "tags",
  "periods",
  "global_works",
  "memorial_sites",
  "foods",
  "transport",
  "route_events",
] as const;

type Field = (typeof FIELDS)[number];

const stats: Record<Field, { filled: number; empty: number }> = {} as any;
FIELDS.forEach((f) => (stats[f] = { filled: 0, empty: 0 }));

const perPlace: Array<{
  id: string;
  ancient: string;
  modern: string;
  type: string;
  routes: string[];
  has_detail: boolean;
  fill_score: number; // 0-100
  missing: Field[];
  legacy_confidence?: number;
}> = [];

function isFilled(field: Field, detail: PlaceDetail | null): boolean {
  if (!detail) return false;
  const v = (detail as any)[field];
  if (v == null) return false;
  if (typeof v === "string") return v.trim().length > 0;
  if (Array.isArray(v)) return v.length > 0;
  if (typeof v === "object") {
    // transport / route_events
    if (field === "transport") {
      return Object.values(v).some(
        (x) => typeof x === "string" && x.trim().length > 0,
      );
    }
    return Object.keys(v).length > 0;
  }
  return false;
}

for (const p of places) {
  const file = path.join(PLACES_DIR, `${p.id}.json`);
  const exists = fs.existsSync(file);
  let detail: PlaceDetail | null = null;
  if (exists) {
    detail = JSON.parse(fs.readFileSync(file, "utf-8"));
  }

  const missing: Field[] = [];
  let hit = 0;
  for (const f of FIELDS) {
    if (isFilled(f, detail)) {
      stats[f].filled++;
      hit++;
    } else {
      stats[f].empty++;
      missing.push(f);
    }
  }

  perPlace.push({
    id: p.id,
    ancient: p.ancient_name,
    modern: p.modern_name,
    type: p.type,
    routes: p.related_routes,
    has_detail: exists,
    fill_score: Math.round((hit / FIELDS.length) * 100),
    missing,
    legacy_confidence: detail?.legacy?.confidence,
  });
}

// 按 fill_score 升序排（最缺的排前面）
perPlace.sort((a, b) => a.fill_score - b.fill_score);

const total = places.length;
const overall = {
  total_places: total,
  has_detail_count: perPlace.filter((p) => p.has_detail).length,
  no_detail_count: perPlace.filter((p) => !p.has_detail).length,
  field_fill_rate: Object.fromEntries(
    FIELDS.map((f) => [
      f,
      `${stats[f].filled}/${total} (${Math.round((stats[f].filled / total) * 100)}%)`,
    ]),
  ),
  fill_score_dist: {
    "0%（空壳）": perPlace.filter((p) => p.fill_score === 0).length,
    "1-30%（严重缺）": perPlace.filter(
      (p) => p.fill_score > 0 && p.fill_score <= 30,
    ).length,
    "31-60%（半缺）": perPlace.filter(
      (p) => p.fill_score > 30 && p.fill_score <= 60,
    ).length,
    "61-89%（基本齐）": perPlace.filter(
      (p) => p.fill_score > 60 && p.fill_score < 90,
    ).length,
    "90-100%（完整）": perPlace.filter((p) => p.fill_score >= 90).length,
  },
};

// 按节点类型 + 路线交叉看缺口
const byType: Record<string, { total: number; filled_avg: number }> = {};
for (const p of perPlace) {
  if (!byType[p.type]) byType[p.type] = { total: 0, filled_avg: 0 };
  byType[p.type].total++;
  byType[p.type].filled_avg += p.fill_score;
}
for (const t of Object.keys(byType)) {
  byType[t].filled_avg = Math.round(byType[t].filled_avg / byType[t].total);
}

// 按路线看缺口（关键路线优先补）
const byRoute: Record<string, { total: number; no_detail: number; avg_score: number }> = {};
for (const p of perPlace) {
  for (const r of p.routes) {
    if (!byRoute[r]) byRoute[r] = { total: 0, no_detail: 0, avg_score: 0 };
    byRoute[r].total++;
    if (!p.has_detail) byRoute[r].no_detail++;
    byRoute[r].avg_score += p.fill_score;
  }
}
for (const r of Object.keys(byRoute)) {
  byRoute[r].avg_score = Math.round(byRoute[r].avg_score / byRoute[r].total);
}

// 写 JSON
fs.writeFileSync(
  REPORT_JSON,
  JSON.stringify(
    {
      _meta: {
        generated_at: new Date().toISOString(),
        schema: "audit-v1",
      },
      overall,
      by_type: byType,
      by_route: byRoute,
      worst_50: perPlace.slice(0, 50),
      all: perPlace,
    },
    null,
    2,
  ),
);

// 写 MD
const md: string[] = [];
md.push("# 苏轼地图 v4 数据完整度体检报告");
md.push("");
md.push(`生成时间：${new Date().toISOString()}`);
md.push("");
md.push("## 一、总体盘点");
md.push("");
md.push(`- 节点总数：**${total}**`);
md.push(
  `- 有详情文件：**${overall.has_detail_count}** / 无详情文件：**${overall.no_detail_count}**`,
);
md.push("");
md.push("## 二、字段填充率");
md.push("");
md.push("| 字段 | 填充情况 |");
md.push("|---|---|");
for (const [f, v] of Object.entries(overall.field_fill_rate)) {
  md.push(`| \`${f}\` | ${v} |`);
}
md.push("");
md.push("## 三、完整度分布");
md.push("");
md.push("| 区间 | 节点数 |");
md.push("|---|---|");
for (const [k, v] of Object.entries(overall.fill_score_dist)) {
  md.push(`| ${k} | ${v} |`);
}
md.push("");
md.push("## 四、按节点类型");
md.push("");
md.push("| 类型 | 节点数 | 平均完整度 |");
md.push("|---|---|---|");
for (const [t, v] of Object.entries(byType)) {
  md.push(`| ${t} | ${v.total} | ${v.filled_avg}% |`);
}
md.push("");
md.push("## 五、按路线");
md.push("");
md.push("| 路线 | 节点数 | 无详情数 | 平均完整度 |");
md.push("|---|---|---|---|");
const sortedRoutes = Object.entries(byRoute).sort(([a], [b]) =>
  a.localeCompare(b),
);
for (const [r, v] of sortedRoutes) {
  md.push(`| ${r} | ${v.total} | ${v.no_detail} | ${v.avg_score}% |`);
}
md.push("");
md.push("## 六、最缺数据的 30 个节点（重点补）");
md.push("");
md.push("| ID | 古名 | 现名 | 类型 | 路线 | 完整度 | 缺失字段 |");
md.push("|---|---|---|---|---|---|---|");
for (const p of perPlace.slice(0, 30)) {
  md.push(
    `| ${p.id} | ${p.ancient} | ${p.modern} | ${p.type} | ${p.routes.join(",")} | ${p.fill_score}% | ${p.missing.join(", ")} |`,
  );
}
md.push("");

fs.writeFileSync(REPORT_MD, md.join("\n"));

console.log("[ok] audit-report.json 已生成");
console.log("[ok] audit-report.md 已生成");
console.log("");
console.log("=== 总览 ===");
console.log(JSON.stringify(overall, null, 2));
