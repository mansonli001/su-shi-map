/**
 * B7 place.duration_summary 聚合器
 *
 * 目标：每个 place 给出"在苏轼一生中的时间区间"概览
 *   - first_year / last_year（在所有 related_routes 中的最早/最晚年份）
 *   - duration_label（如 "1080-1084 · 4年2个月" 或 "1080.2-1084.4"）
 *   - related_route_count
 *
 * 数据源：
 *   public/data-v4/places/{P_id}.json   读取 related_routes
 *   public/data-v4/routes-index.json    读 start_year/end_year
 *
 * 输出：写回 places/{P_id}.json 增加 duration_summary 字段
 */

import * as fs from "fs";
import * as path from "path";

type RouteIdx = {
  id: string;
  start_year: number;
  end_year: number;
  name: string;
  stage_id?: string;
};

const PUB = path.resolve(__dirname, "..", "..", "..", "public", "data-v4");
const INTERNAL = path.resolve(__dirname, "..", "..");

function loadRoutesIdx(): Map<string, RouteIdx> {
  const data = JSON.parse(
    fs.readFileSync(path.join(PUB, "routes-index.json"), "utf-8"),
  );
  const m = new Map<string, RouteIdx>();
  for (const r of data.routes || []) m.set(r.id, r);
  return m;
}

function buildDurationLabel(start: number, end: number): string {
  if (start === end) return `${start}`;
  const yrs = end - start;
  return `${start}-${end} · ${yrs}年`;
}

function processPlace(filePath: string, routesIdx: Map<string, RouteIdx>): boolean {
  let data: any;
  try {
    data = JSON.parse(fs.readFileSync(filePath, "utf-8"));
  } catch {
    return false;
  }
  const related: string[] = data.related_routes || [];
  if (related.length === 0) return false;

  let minY = Infinity;
  let maxY = -Infinity;
  const stageSet = new Set<string>();
  const validRoutes: string[] = [];
  for (const rid of related) {
    const r = routesIdx.get(rid);
    if (!r) continue;
    validRoutes.push(rid);
    if (r.start_year < minY) minY = r.start_year;
    if (r.end_year > maxY) maxY = r.end_year;
    if (r.stage_id) stageSet.add(r.stage_id);
  }
  if (!isFinite(minY)) return false;

  data.duration_summary = {
    first_year: minY,
    last_year: maxY,
    span_years: maxY - minY,
    duration_label: buildDurationLabel(minY, maxY),
    related_route_count: validRoutes.length,
    stage_ids: Array.from(stageSet).sort(),
  };

  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), "utf-8");
  return true;
}

function main() {
  const routesIdx = loadRoutesIdx();
  console.log(`📊 加载 ${routesIdx.size} 条路线索引`);

  const dirs = [path.join(PUB, "places"), path.join(INTERNAL, "places")];
  let total = 0;
  let updated = 0;
  for (const dir of dirs) {
    if (!fs.existsSync(dir)) continue;
    const files = fs.readdirSync(dir).filter((f) => f.endsWith(".json"));
    for (const f of files) {
      total++;
      if (processPlace(path.join(dir, f), routesIdx)) updated++;
    }
  }
  console.log(`✅ duration_summary 注入：${updated}/${total}`);
}

main();
