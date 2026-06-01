/**
 * B8 place.famous_line 提取器
 *
 * 目标：每个有 global_works 或 route_works 的 place，提取一句"打开就看到"的代表名句
 *
 * 抽取规则（按优先级）：
 *   1. global_works[0].excerpt  （首选）
 *   2. global_works[0].note 中含「」「」内引号的句子
 *   3. global_works[0].title  （兜底，作为标题展示）
 *   4. route_works[*][0]       （回退到路线作品）
 *
 * 输出：写回 places/{P_id}.json 增加 famous_line 字段（结构化）
 */

import * as fs from "fs";
import * as path from "path";

const PUB = path.resolve(__dirname, "..", "..", "..", "public", "data-v4");
const INTERNAL = path.resolve(__dirname, "..", "..");

// 提取「」内或引号内的诗句
function extractQuote(text: string): string | null {
  if (!text) return null;
  // 中文引号「」 或 ""
  const m1 = text.match(/[「""]([^」""]+)[」""]/);
  if (m1 && m1[1].length >= 4) return m1[1].trim();
  // 半角双引号
  const m2 = text.match(/"([^"]+)"/);
  if (m2 && m2[1].length >= 4) return m2[1].trim();
  return null;
}

function pickFamousLine(data: any): { quote: string; source: string; from: string } | null {
  const gw = data.global_works || [];
  const rw = data.route_works || {};

  // 1) global_works[0].excerpt
  if (gw.length > 0) {
    const g0 = gw[0];
    if (g0.excerpt && typeof g0.excerpt === "string" && g0.excerpt.trim()) {
      return { quote: g0.excerpt.trim(), source: g0.title || "", from: "global_works.excerpt" };
    }
    // 2) global_works[0].note 中的引号句子
    if (g0.note) {
      const q = extractQuote(g0.note);
      if (q) return { quote: q, source: g0.title || "", from: "global_works.note" };
    }
    // 3) 兜底用标题
    if (g0.title) {
      return { quote: g0.title, source: g0.title, from: "global_works.title" };
    }
  }

  // 4) route_works
  for (const rid of Object.keys(rw)) {
    const arr = rw[rid] || [];
    if (arr.length === 0) continue;
    const w0 = arr[0];
    if (w0.excerpt) return { quote: w0.excerpt, source: w0.title || "", from: `route_works.${rid}.excerpt` };
    if (w0.note) {
      const q = extractQuote(w0.note);
      if (q) return { quote: q, source: w0.title || "", from: `route_works.${rid}.note` };
    }
    if (w0.title) return { quote: w0.title, source: w0.title, from: `route_works.${rid}.title` };
  }

  return null;
}

function processPlace(filePath: string): boolean {
  let data: any;
  try {
    data = JSON.parse(fs.readFileSync(filePath, "utf-8"));
  } catch {
    return false;
  }
  const fl = pickFamousLine(data);
  if (!fl) return false;
  data.famous_line = fl;
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), "utf-8");
  return true;
}

function main() {
  const dirs = [path.join(PUB, "places"), path.join(INTERNAL, "places")];
  let total = 0;
  let extracted = 0;
  for (const dir of dirs) {
    if (!fs.existsSync(dir)) continue;
    const files = fs.readdirSync(dir).filter((f) => f.endsWith(".json"));
    for (const f of files) {
      total++;
      if (processPlace(path.join(dir, f))) extracted++;
    }
  }
  console.log(`✅ famous_line 提取：${extracted}/${total}`);
}

main();
