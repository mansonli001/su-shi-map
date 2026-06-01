/**
 * B1 · .md → JSON 转换器
 * ----------------------------------------------------------
 * 把 data-v4-source/R*.md（20 条守门版路线）真实灌进 data-v4 数据系统：
 *   1. 解析 YAML，抽取 route_overview + places[]
 *   2. 更新 routes/R*.json：写入 description_long / core_essence / key_events / literary_output
 *   3. 更新 places/P*.json：按 ancient_name 匹配 P_id，灌入
 *      - background = .md 的 historical_context
 *      - extended_story = .md 的 su_shi_story
 *      - tags（合并）
 *      - route_events[route_id] = .md 的相关 key_events 抽取
 *      - global_works = .md 的 representative_works（仅当之前为空）
 *      - sources = .md 的 sources（合并去重）
 *      - verified_status = pending_dual_expert_review（如有）
 *   4. 输出未匹配点位清单 → meta/auto-fill-results/md-place-unmatched.md
 *
 * 关键：
 *   - 不破坏现有 places/P*.json 已有字段（坐标/类型/related_routes 不动）
 *   - .md 中点位匹配规则：ancient_name 完全相等 + related_routes 包含本路线
 *   - 一对多匹配（同一古名出现在多路线）→ 优先全字符串相等
 *
 * 用法：
 *   npx tsx data-v4/scripts/auto-fill/b1-md-to-json.ts
 * ----------------------------------------------------------
 */

import * as fs from "fs";
import * as path from "path";
import * as yaml from "js-yaml";

const PROJECT_ROOT = path.resolve(__dirname, "..", "..", "..");
const SOURCE_DIR = path.join(PROJECT_ROOT, "data-v4-source");
const PLACES_INDEX = path.join(PROJECT_ROOT, "public/data-v4/places-index.json");
const PLACES_DIR = path.join(PROJECT_ROOT, "public/data-v4/places");
const ROUTES_DIR = path.join(PROJECT_ROOT, "public/data-v4/routes");
const REPORT_FILE = path.join(PROJECT_ROOT, "data-v4/meta/auto-fill-results/md-to-json-report.md");
const UNMATCHED_FILE = path.join(PROJECT_ROOT, "data-v4/meta/auto-fill-results/md-place-unmatched.md");

// ============ 类型 ============
interface MdPlace {
  id: string; // R18_main_15
  name_song: string;
  name_modern?: string;
  layer: string;
  tags?: string[];
  priority?: string;
  order_in_route?: number;
  duration?: string;
  duration_years?: number[];
  historical_context?: string;
  su_shi_story?: string;
  essence?: string;
  related_works?: any[];
  sources?: string[];
}

interface MdRoute {
  route_overview: {
    route_id: string;
    route_title: string;
    route_period: string;
    route_age_range: string;
    route_color: string;
    route_position: string;
    time_range: any;
    core_essence: string;
    key_events: any[];
    key_locations_summary: string;
    literary_output: any;
  };
  places: MdPlace[];
}

interface PlaceIndexEntry {
  id: string;
  ancient_name: string;
  modern_name: string;
  type: string;
  related_routes: string[];
  has_detail: boolean;
}

// ============ 工具 ============

/** 简化古名用于匹配（去掉括号注释）*/
function simplifyName(name: string): string {
  return name
    .replace(/[（(].*?[）)]/g, "") // 去括号
    .replace(/\s+/g, "")
    .trim();
}

/** YAML 解析 .md（去掉首行 # 标题 + 尾部 markdown）*/
function parseMd(content: string): MdRoute | null {
  // 去掉首行标题
  const lines = content.split(/\r?\n/);
  const start = lines.findIndex((l) => l.trim().startsWith("route_overview"));
  if (start < 0) return null;

  // 找 yaml 结束位置（遇到 "---" 之类的元话语段）
  let end = lines.length;
  for (let i = start; i < lines.length; i++) {
    if (/^---\s*$/.test(lines[i].trim()) && i > start + 5) {
      end = i;
      break;
    }
  }
  const yamlText = lines.slice(start, end).join("\n");
  try {
    return yaml.load(yamlText) as MdRoute;
  } catch (e) {
    console.error(`YAML parse error:`, (e as Error).message);
    return null;
  }
}

// ============ 主流程 ============
async function main() {
  console.log("📥 读取 places-index.json...");
  const indexJson = JSON.parse(fs.readFileSync(PLACES_INDEX, "utf-8"));
  const placesIndex: PlaceIndexEntry[] = indexJson.places;
  console.log(`   ${placesIndex.length} 个 P 编号点位`);

  console.log("\n📥 扫描 data-v4-source/R*.md...");
  const mdFiles = fs
    .readdirSync(SOURCE_DIR)
    .filter((f) => /^R\d{2}_.*\.md$/.test(f))
    .sort();
  console.log(`   ${mdFiles.length} 篇路线 .md`);

  const stats = {
    routes_parsed: 0,
    places_total: 0,
    places_matched: 0,
    places_unmatched: 0,
    place_files_updated: 0,
    place_files_created: 0,
    route_files_updated: 0,
  };

  const unmatchedReports: string[] = [];

  for (const mdFile of mdFiles) {
    const routeId = mdFile.match(/^R(\d{2})/)?.[0];
    if (!routeId) continue;

    const content = fs.readFileSync(path.join(SOURCE_DIR, mdFile), "utf-8");
    const parsed = parseMd(content);
    if (!parsed || !parsed.route_overview) {
      console.log(`   ⚠️  ${routeId}: 解析失败，跳过`);
      continue;
    }
    stats.routes_parsed++;

    const ov = parsed.route_overview;
    const places = parsed.places || [];
    stats.places_total += places.length;

    console.log(`\n📍 ${routeId} ${ov.route_title}（${places.length} 点位）`);

    // ----- 1. 更新 routes/R*.json -----
    const routeFile = path.join(ROUTES_DIR, `${routeId}.json`);
    if (fs.existsSync(routeFile)) {
      const route = JSON.parse(fs.readFileSync(routeFile, "utf-8"));
      route.description_long = (ov.time_range?.description || "").trim();
      route.core_essence = (ov.core_essence || "").trim();
      route.key_locations_summary = (ov.key_locations_summary || "").trim();
      route.key_events = ov.key_events || [];
      route.literary_output = ov.literary_output || {};
      route.route_position = ov.route_position || "";
      route.unique_color = ov.route_color || route.unique_color;
      route.last_updated = new Date().toISOString();
      route.schema_version = "v4.1";
      route.source_md = `data-v4-source/${mdFile}`;
      fs.writeFileSync(routeFile, JSON.stringify(route, null, 2));
      stats.route_files_updated++;
    }

    // ----- 2. 更新 places/P*.json -----
    for (const mp of places) {
      const songSimple = simplifyName(mp.name_song);
      // 匹配规则：ancient_name 完全相等 + related_routes 包含本路线
      let matched = placesIndex.find(
        (p) =>
          simplifyName(p.ancient_name) === songSimple &&
          p.related_routes.includes(routeId)
      );
      // 退化：仅 ancient_name 简化匹配
      if (!matched) {
        matched = placesIndex.find((p) => simplifyName(p.ancient_name) === songSimple);
      }

      if (!matched) {
        stats.places_unmatched++;
        unmatchedReports.push(`| ${routeId} | ${mp.id} | ${mp.name_song} | ${mp.name_modern || "—"} | 未匹配 |`);
        continue;
      }

      stats.places_matched++;

      // 读 + 改 places/P*.json
      const placeFile = path.join(PLACES_DIR, `${matched.id}.json`);
      let pd: any = {};
      if (fs.existsSync(placeFile)) {
        pd = JSON.parse(fs.readFileSync(placeFile, "utf-8"));
      } else {
        pd = {
          id: matched.id,
          ancient_name: matched.ancient_name,
          modern_name: matched.modern_name,
          type: matched.type,
          related_routes: matched.related_routes,
        };
        stats.place_files_created++;
      }

      // 灌入 .md 的内容（不破坏已有字段，只填充空字段）
      if (!pd.background && mp.historical_context) {
        pd.background = mp.historical_context.trim();
      }
      if (!pd.extended_story && mp.su_shi_story) {
        pd.extended_story = mp.su_shi_story.trim();
      }
      if (!pd.essence && mp.essence) {
        pd.essence = mp.essence.trim();
      }
      // tags 合并
      if (mp.tags && mp.tags.length) {
        const oldTags: string[] = pd.tags || [];
        pd.tags = Array.from(new Set([...oldTags, ...mp.tags]));
      }
      // route_events 按路线分组
      if (!pd.route_events) pd.route_events = {};
      if (!pd.route_events[routeId]) {
        pd.route_events[routeId] = {
          duration: mp.duration || "",
          duration_years: mp.duration_years || [],
          essence: mp.essence || "",
          su_shi_story: mp.su_shi_story || "",
          historical_context: mp.historical_context || "",
          order_in_route: mp.order_in_route || 0,
          layer: mp.layer || "",
          priority: mp.priority || "",
        };
      }
      // related_works
      if (mp.related_works && mp.related_works.length) {
        const old = pd.global_works || [];
        const newWorks = mp.related_works.map((w: any) => ({
          title: w.title,
          type: w.type || "poem",
          note: w.note || "",
          source_route: routeId,
        }));
        // 去重（按 title）
        const titles = new Set(old.map((w: any) => w.title));
        for (const w of newWorks) {
          if (!titles.has(w.title)) {
            old.push(w);
            titles.add(w.title);
          }
        }
        pd.global_works = old;
      }
      // sources 合并
      if (mp.sources && mp.sources.length) {
        const oldSources: string[] = pd.source || [];
        pd.source = Array.from(new Set([...oldSources, ...mp.sources]));
      }
      pd.last_updated = new Date().toISOString();
      pd.schema_version = "v4.1";

      fs.writeFileSync(placeFile, JSON.stringify(pd, null, 2));
      stats.place_files_updated++;
    }
  }

  // ----- 3. 输出报告 -----
  console.log("\n📊 转换完成统计：");
  console.log(`   📜 路线 .md 解析    : ${stats.routes_parsed}/${mdFiles.length}`);
  console.log(`   📍 .md 中点位总数   : ${stats.places_total}`);
  console.log(`   ✅ 匹配 P 编号成功   : ${stats.places_matched}`);
  console.log(`   ⚠️  未匹配（需补编号）: ${stats.places_unmatched}`);
  console.log(`   📝 places/*.json 更新: ${stats.place_files_updated}`);
  console.log(`   ➕ places/*.json 新建: ${stats.place_files_created}`);
  console.log(`   📁 routes/*.json 更新: ${stats.route_files_updated}`);

  fs.mkdirSync(path.dirname(REPORT_FILE), { recursive: true });
  fs.writeFileSync(
    REPORT_FILE,
    `# B1 .md → JSON 转换器报告

生成时间：${new Date().toISOString()}

## 统计
- 路线 .md 解析: ${stats.routes_parsed}/${mdFiles.length}
- .md 中点位总数: ${stats.places_total}
- 匹配 P 编号成功: ${stats.places_matched}
- 未匹配: ${stats.places_unmatched}
- places/*.json 更新: ${stats.place_files_updated}
- places/*.json 新建: ${stats.place_files_created}
- routes/*.json 更新: ${stats.route_files_updated}

## 工作流
1. 读取 data-v4-source/R*.md 并 YAML 解析
2. 更新 routes/R*.json（description_long / core_essence / key_events / literary_output / route_position）
3. 按 ancient_name 匹配到 places-index.json 的 P 编号
4. 灌入 places/P*.json 的 background / extended_story / tags / route_events / global_works / source

## 未匹配清单
见 md-place-unmatched.md
`
  );

  fs.writeFileSync(
    UNMATCHED_FILE,
    `# 未匹配点位清单（${stats.places_unmatched} 条）

| 路线 | .md ID | 古名 | 现名 | 状态 |
|---|---|---|---|---|
${unmatchedReports.join("\n")}

## 后续处理
1. 检查这些点位是否需要为它们新建 P 编号
2. 或修正 .md 中的 name_song 与 places-index.json 对齐
3. 跑完后重新执行 B1 转换器
`
  );
  console.log(`\n💾 ${REPORT_FILE}`);
  console.log(`💾 ${UNMATCHED_FILE}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
