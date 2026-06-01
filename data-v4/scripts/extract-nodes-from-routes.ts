/**
 * data-v4 Phase 1 / Step 2
 * ----------------------------------------------------------
 * 解析 data-v4-source/2026-06-01-ROUTES-CORRECTED-V1.md
 * 抽取 20 条路线的全部节点（主线 / 沿途 / 驻留），去重
 * 输出 data-v4/meta/places-master-raw.json
 * ----------------------------------------------------------
 * 使用：pnpm tsx data-v4/scripts/extract-nodes-from-routes.ts
 *
 * 设计要点：
 * - 节点层级 (layer)：'main' | 'sight' | 'around'
 *   main   = 主线行进节点（连成路线轨迹）
 *   sight  = 沿途游览（地图标记，非路径上）
 *   around = 驻留周边打卡点（点位弹窗）
 * - 跨路线复用：一个古名同时出现在多条路线 → 合并 routes 数组
 * - 现代名解析：括号内即为现代名，例如 "汴京（开封）" → ancient="汴京", modern="开封"
 *   无括号 → modern 暂为空字符串，留 Step 4 高德反查时补
 * - 同名歧义（如出现在两条路线含义不同）由人工 review 阶段订正
 */

import * as fs from "fs";
import * as path from "path";

// ======================================================
// 类型定义（与最终 places-index 对齐的最小子集）
// ======================================================
type Layer = "main" | "sight" | "around";

interface RawNode {
  ancient_name: string; // 古名（去括号后）
  modern_name: string; // 括号内现代名，可能为空
  routes: { route_id: string; layer: Layer; order_in_route: number }[];
  occurrences: number; // 跨路线累计出现次数
}

interface ParsedRoute {
  route_id: string;
  route_index: number;
  route_title_raw: string; // 原始 markdown 标题
  main: string[][]; // 主线，可能多段（出蜀 + 返程）
  sight: string[];
  around: string[];
}

// ======================================================
// 工具函数
// ======================================================
function splitNodeChain(line: string): string[] {
  // 主线行进里节点用 → 或 -> 分隔
  return line
    .split(/→|->/g)
    .map((s) => s.trim())
    .filter(Boolean);
}

function splitCommaList(line: string): string[] {
  // 沿途游览 / 驻留周边用 中文/英文逗号、顿号、分号分隔
  return line
    .split(/[、，,；;]/g)
    .map((s) => s.trim())
    .filter(Boolean);
}

function parseAncientModern(token: string): { ancient: string; modern: string } {
  // 例 "汴京（开封）" / "汴京(开封)"
  const m = token.match(/^([^（(]+)[（(]([^）)]+)[）)]$/);
  if (m) return { ancient: m[1].trim(), modern: m[2].trim() };
  return { ancient: token.trim(), modern: "" };
}

// ======================================================
// 主解析逻辑
// ======================================================
function parseMarkdown(md: string): ParsedRoute[] {
  // 按 "## Route X" 切块
  const blocks = md.split(/^##\s+Route\s+/m).slice(1); // 第 0 块是文件头
  const routes: ParsedRoute[] = [];

  for (const block of blocks) {
    // 块开头形如 "0 ｜ 眉山故里 · 少年成长（1037–1056）未出蜀\n**主线行进**：..."
    const headerMatch = block.match(/^(\d+)\s*[｜|]\s*([^\n]+)/);
    if (!headerMatch) continue;
    const idx = parseInt(headerMatch[1], 10);
    if (Number.isNaN(idx)) continue;

    const route: ParsedRoute = {
      route_id: `R${String(idx).padStart(2, "0")}`,
      route_index: idx,
      route_title_raw: headerMatch[2].trim(),
      main: [],
      sight: [],
      around: [],
    };

    // 抓 **主线行进** 段（可能多段，如"出蜀进京"+"母丧返程"）
    const mainRegex = /\*\*主线行进[^*]*\*\*[：:]\s*\n?([^\n*]+(?:\n[^\n*]+)*?)(?=\n\*\*|\n---|$)/g;
    let m: RegExpExecArray | null;
    while ((m = mainRegex.exec(block)) !== null) {
      const chain = splitNodeChain(m[1]);
      if (chain.length > 0) route.main.push(chain);
    }

    // **沿途游览**：xxx、yyy
    const sightMatch = block.match(/\*\*沿途游览\*\*[：:]\s*([^\n]+)/);
    if (sightMatch) route.sight = splitCommaList(sightMatch[1]);

    // **驻留周边**：xxx、yyy
    const aroundMatch = block.match(/\*\*驻留周边\*\*[：:]\s*([^\n]+)/);
    if (aroundMatch) route.around = splitCommaList(aroundMatch[1]);

    routes.push(route);
  }

  return routes;
}

// ======================================================
// 节点去重 & 跨路线合并
// ======================================================
function aggregateNodes(routes: ParsedRoute[]): Map<string, RawNode> {
  const map = new Map<string, RawNode>();

  function addNode(token: string, route_id: string, layer: Layer, order: number) {
    const { ancient, modern } = parseAncientModern(token);
    if (!ancient) return;
    const key = ancient; // 以古名作主键，去重
    let node = map.get(key);
    if (!node) {
      node = {
        ancient_name: ancient,
        modern_name: modern,
        routes: [],
        occurrences: 0,
      };
      map.set(key, node);
    } else if (!node.modern_name && modern) {
      // 早出现没带括号、晚出现带括号 → 补上现代名
      node.modern_name = modern;
    }
    node.occurrences++;
    node.routes.push({ route_id, layer, order_in_route: order });
  }

  for (const r of routes) {
    // 主线（多段合并编号；段内顺序）
    let mainOrder = 0;
    for (const chain of r.main) {
      for (const t of chain) {
        addNode(t, r.route_id, "main", mainOrder++);
      }
    }
    r.sight.forEach((t, i) => addNode(t, r.route_id, "sight", i));
    r.around.forEach((t, i) => addNode(t, r.route_id, "around", i));
  }

  return map;
}

// ======================================================
// 入口
// ======================================================
function main() {
  const projectRoot = path.resolve(__dirname, "..", "..");
  const mdPath = path.join(
    projectRoot,
    "data-v4-source",
    "2026-06-01-ROUTES-CORRECTED-V1.md"
  );
  const md = fs.readFileSync(mdPath, "utf-8");
  const routes = parseMarkdown(md);

  console.log(`[parse] 解析路线数：${routes.length}（期望 20）`);
  for (const r of routes) {
    const mainCount = r.main.reduce((s, c) => s + c.length, 0);
    console.log(
      `  ${r.route_id}: 主线 ${mainCount}（${r.main.length}段） / 沿途 ${r.sight.length} / 驻留 ${r.around.length}`
    );
  }

  const nodeMap = aggregateNodes(routes);
  const nodes = Array.from(nodeMap.values()).sort((a, b) =>
    a.ancient_name.localeCompare(b.ancient_name, "zh-Hans-CN")
  );

  console.log(`\n[aggregate] 唯一节点总数：${nodes.length}`);
  const byLayer = { main: 0, sight: 0, around: 0 };
  for (const n of nodes) {
    const layers = new Set(n.routes.map((r) => r.layer));
    if (layers.has("main")) byLayer.main++;
    else if (layers.has("sight")) byLayer.sight++;
    else byLayer.around++;
  }
  console.log(
    `  主线节点：${byLayer.main} / 沿途独占：${byLayer.sight} / 驻留独占：${byLayer.around}`
  );

  const noModern = nodes.filter((n) => !n.modern_name).length;
  console.log(`  待补现代名（Step 4 高德反查）：${noModern}`);

  // 输出
  const outDir = path.join(projectRoot, "data-v4", "meta");
  fs.mkdirSync(outDir, { recursive: true });

  fs.writeFileSync(
    path.join(outDir, "places-master-raw.json"),
    JSON.stringify(
      {
        _meta: {
          generated_at: new Date().toISOString(),
          source: "data-v4-source/2026-06-01-ROUTES-CORRECTED-V1.md",
          total_routes: routes.length,
          total_nodes: nodes.length,
          by_primary_layer: byLayer,
          modern_name_pending: noModern,
        },
        nodes,
      },
      null,
      2
    ),
    "utf-8"
  );

  fs.writeFileSync(
    path.join(outDir, "routes-parsed-raw.json"),
    JSON.stringify(
      {
        _meta: {
          generated_at: new Date().toISOString(),
          source: "data-v4-source/2026-06-01-ROUTES-CORRECTED-V1.md",
          total_routes: routes.length,
        },
        routes,
      },
      null,
      2
    ),
    "utf-8"
  );

  console.log(`\n[write] data-v4/meta/places-master-raw.json`);
  console.log(`[write] data-v4/meta/routes-parsed-raw.json`);
  console.log(`\n✅ Step 2 完成。下一步：Step 3 建 data-v4 schema + Step 4 补坐标`);
}

main();
