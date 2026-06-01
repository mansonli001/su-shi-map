/**
 * 路径完整度体检：
 * 1. 每条路线 track_segments[].place_ids 是否都在 places 索引里
 * 2. 找到的点是否都有合法经纬度
 * 3. 相邻两点的地理距离是否过大（疑似断点/跳跃）
 * 4. order 字段一致性
 */
import * as fs from 'fs';
import * as path from 'path';

const ROOT = path.resolve(__dirname, '..');
const PLACES_INDEX = path.join(ROOT, 'places-index.json');
const ROUTES_DIR = path.join(ROOT, 'routes');

type Place = {
  id: string;
  ancient_name: string;
  modern_name: string;
  lat?: number;
  lng?: number;
  coordinate_source?: string;
};

const placesIndex = JSON.parse(fs.readFileSync(PLACES_INDEX, 'utf-8'));
const placesMap = new Map<string, Place>();
for (const p of placesIndex.places) placesMap.set(p.id, p);

// Haversine 距离 (km)
function haversine(a: Place, b: Place): number {
  if (a.lat == null || a.lng == null || b.lat == null || b.lng == null) return -1;
  const R = 6371;
  const toRad = (d: number) => (d * Math.PI) / 180;
  const dLat = toRad(b.lat - a.lat);
  const dLng = toRad(b.lng - a.lng);
  const lat1 = toRad(a.lat);
  const lat2 = toRad(b.lat);
  const x =
    Math.sin(dLat / 2) ** 2 + Math.sin(dLng / 2) ** 2 * Math.cos(lat1) * Math.cos(lat2);
  return 2 * R * Math.asin(Math.sqrt(x));
}

const JUMP_THRESHOLD_KM = 500; // 相邻两点 > 500km 标记为疑似跳跃

const routeFiles = fs
  .readdirSync(ROUTES_DIR)
  .filter((f) => f.match(/^R\d+\.json$/))
  .sort();

type Issue =
  | { kind: 'missing_place'; place_id: string }
  | { kind: 'no_coord'; place_id: string; ancient: string }
  | { kind: 'invalid_coord'; place_id: string; lat: any; lng: any }
  | { kind: 'jump'; from: string; to: string; km: number };

const report: any = {
  generated_at: new Date().toISOString(),
  routes: [] as any[],
};

for (const file of routeFiles) {
  const route = JSON.parse(fs.readFileSync(path.join(ROUTES_DIR, file), 'utf-8'));
  const issues: Issue[] = [];
  let mainCount = 0;
  let foundCount = 0;
  let coordOkCount = 0;

  const segments = route.track_segments || [];
  for (const seg of segments) {
    const ids: string[] = seg.place_ids || [];
    mainCount += ids.length;

    const resolved: Place[] = [];
    for (const id of ids) {
      const p = placesMap.get(id);
      if (!p) {
        issues.push({ kind: 'missing_place', place_id: id });
        continue;
      }
      foundCount++;
      const lat = p.lat;
      const lng = p.lng;
      if (lat == null || lng == null) {
        issues.push({ kind: 'no_coord', place_id: id, ancient: p.ancient_name });
        continue;
      }
      if (
        typeof lat !== 'number' ||
        typeof lng !== 'number' ||
        isNaN(lat) ||
        isNaN(lng) ||
        lat < -90 ||
        lat > 90 ||
        lng < -180 ||
        lng > 180
      ) {
        issues.push({ kind: 'invalid_coord', place_id: id, lat, lng });
        continue;
      }
      coordOkCount++;
      resolved.push(p);
    }

    // 相邻跳跃检测
    for (let i = 1; i < resolved.length; i++) {
      const km = haversine(resolved[i - 1], resolved[i]);
      if (km > JUMP_THRESHOLD_KM) {
        issues.push({
          kind: 'jump',
          from: `${resolved[i - 1].id}(${resolved[i - 1].ancient_name})`,
          to: `${resolved[i].id}(${resolved[i].ancient_name})`,
          km: Math.round(km),
        });
      }
    }
  }

  // 综合评分
  const completeRate = mainCount === 0 ? 0 : Math.round((coordOkCount / mainCount) * 100);
  const jumpCount = issues.filter((i) => i.kind === 'jump').length;
  const status =
    completeRate === 100 && jumpCount === 0
      ? '✅ OK'
      : completeRate < 100
        ? '🚨 缺点'
        : '⚠️ 有跳跃';

  report.routes.push({
    id: route.id,
    name: route.name,
    period: route.period,
    main_count: mainCount,
    found_count: foundCount,
    coord_ok_count: coordOkCount,
    complete_rate: completeRate,
    jump_count: jumpCount,
    status,
    issues,
  });
}

// 汇总
const summary = {
  total_routes: report.routes.length,
  perfect: report.routes.filter((r: any) => r.status === '✅ OK').length,
  missing_or_no_coord: report.routes.filter((r: any) => r.complete_rate < 100).length,
  has_jumps: report.routes.filter((r: any) => r.jump_count > 0).length,
};

report.summary = summary;

// 输出
const outPath = path.join(ROOT, 'meta', 'route-audit-report.json');
fs.writeFileSync(outPath, JSON.stringify(report, null, 2), 'utf-8');

console.log('\n=== 路径完整度体检 ===\n');
console.log(`总路线: ${summary.total_routes}`);
console.log(`✅ 完美: ${summary.perfect}`);
console.log(`🚨 有缺点/无坐标: ${summary.missing_or_no_coord}`);
console.log(`⚠️ 有大跳跃 (>${JUMP_THRESHOLD_KM}km): ${summary.has_jumps}`);
console.log('\n--- 各路线明细 ---');
for (const r of report.routes) {
  console.log(
    `${r.id} ${r.status}  ${r.complete_rate}%  主线点=${r.main_count} 坐标OK=${r.coord_ok_count} 跳跃=${r.jump_count}  「${r.name}」`,
  );
}

// 重点问题清单
console.log('\n--- 缺点/无坐标 详情（前 30 条）---');
let n = 0;
for (const r of report.routes) {
  for (const i of r.issues) {
    if (i.kind === 'missing_place' || i.kind === 'no_coord' || i.kind === 'invalid_coord') {
      if (n++ < 30) {
        console.log(`  ${r.id} ${i.kind} ${JSON.stringify(i)}`);
      }
    }
  }
}

console.log('\n--- 跳跃 详情（前 20 条）---');
n = 0;
for (const r of report.routes) {
  for (const i of r.issues) {
    if (i.kind === 'jump') {
      if (n++ < 20) {
        const j = i as any;
        console.log(`  ${r.id} ${j.from} → ${j.to} = ${j.km}km`);
      }
    }
  }
}

console.log(`\n报告已写入: ${outPath}\n`);
