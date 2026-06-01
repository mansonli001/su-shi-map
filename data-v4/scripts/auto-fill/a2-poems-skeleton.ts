/**
 * A2 诗词索引层构建器
 *
 * 输入：
 *   data-v4/meta/auto-fill-results/a2-poem-tasks.json (68 首作品任务)
 *
 * 输出：
 *   public/data-v4/poems-index.json  轻量索引
 *   public/data-v4/poems/W{nnn}.json 单首骨架（含外链跳转兜底）
 *
 * 策略：
 *   - 第一步（本脚本）：建 W001-W068 骨架 + 古诗文网/ctext 搜索链接
 *   - 第二步（A2.2）：爬全文逐步填 fullText（可手动或脚本）
 */

import * as fs from "fs";
import * as path from "path";

const PUB = path.resolve(__dirname, "..", "..", "..", "public", "data-v4");
const INTERNAL = path.resolve(__dirname, "..", "..");

interface Task {
  route_id: string;
  title: string;
  category: string;
  note: string;
  year: number | string | "";
  verification_status: string;
}

interface PoemSkeleton {
  id: string;
  title: string;
  category: string;
  type: "诗" | "词" | "文" | "赋" | "策" | "铭" | "碑" | "题画" | "其他";
  year_estimate?: number;
  route_id: string;
  related_route_ids: string[];
  note: string;
  verification_status?: string;
  // 全文/创作背景（待爬）
  fullText?: string;
  background?: string;
  excerpt?: string;
  coreVerse?: string;
  // 外链跳转兜底
  external_links: {
    gushiwen_search: string; // 古诗文网搜索
    ctext_search: string; // ctext 搜索
    sou_yun_search: string; // 搜韵
  };
  // 元数据
  source_chain: string[];
  has_full_text: boolean;
}

// 类型推断（基于 category 关键词）
function inferType(category: string): PoemSkeleton["type"] {
  const c = category.toLowerCase();
  if (c.includes("词")) return "词";
  if (c.includes("赋")) return "赋";
  if (c.includes("文") || c.includes("散文") || c.includes("题跋") || c.includes("记")) return "文";
  if (c.includes("策") || c.includes("奏") || c.includes("表")) return "策";
  if (c.includes("铭")) return "铭";
  if (c.includes("碑")) return "碑";
  if (c.includes("题画")) return "题画";
  return "诗";
}

// 标题清洗（去括号注释）
function cleanTitle(title: string): string {
  return title
    .replace(/[（(].*?[)）]/g, "") // 去括号
    .replace(/[、，,].*$/, "") // 去顿号后内容
    .trim();
}

function buildSkeleton(task: Task, idx: number): PoemSkeleton {
  const id = `W${String(idx + 1).padStart(3, "0")}`;
  const cleanT = cleanTitle(task.title);
  const enc = encodeURIComponent(cleanT);

  return {
    id,
    title: task.title,
    category: task.category,
    type: inferType(task.category),
    year_estimate: typeof task.year === "number" ? task.year : undefined,
    route_id: task.route_id,
    related_route_ids: [task.route_id],
    note: task.note,
    verification_status: task.verification_status || undefined,
    external_links: {
      gushiwen_search: `https://www.gushiwen.cn/search.aspx?value=${enc}`,
      ctext_search: `https://ctext.org/searchbooks.pl?if=gb&searchu=${enc}&author=苏轼`,
      sou_yun_search: `https://sou-yun.cn/QueryPoem.aspx?key=${enc}&author=苏轼`,
    },
    source_chain: ["李常生苏轼行踪考", "孔凡礼苏轼年谱"],
    has_full_text: false,
  };
}

function writeBoth(rel: string, json: any) {
  const data = JSON.stringify(json, null, 2);
  const pubPath = path.join(PUB, rel);
  const intPath = path.join(INTERNAL, rel);
  fs.mkdirSync(path.dirname(pubPath), { recursive: true });
  fs.mkdirSync(path.dirname(intPath), { recursive: true });
  fs.writeFileSync(pubPath, data, "utf-8");
  fs.writeFileSync(intPath, data, "utf-8");
}

function main() {
  const tasksPath = path.join(INTERNAL, "meta", "auto-fill-results", "a2-poem-tasks.json");
  const tasksData = JSON.parse(fs.readFileSync(tasksPath, "utf-8"));
  const tasks: Task[] = tasksData.tasks || [];
  console.log(`📚 加载 ${tasks.length} 首作品任务`);

  // 合并同名作品（不同路线的同名诗合并 related_route_ids）
  const skeletonMap = new Map<string, PoemSkeleton>();
  tasks.forEach((task, idx) => {
    const cleanT = cleanTitle(task.title);
    if (skeletonMap.has(cleanT)) {
      const existing = skeletonMap.get(cleanT)!;
      if (!existing.related_route_ids.includes(task.route_id)) {
        existing.related_route_ids.push(task.route_id);
      }
    } else {
      const sk = buildSkeleton(task, skeletonMap.size);
      skeletonMap.set(cleanT, sk);
    }
  });

  const skeletons = Array.from(skeletonMap.values());

  // 写单首
  for (const sk of skeletons) {
    writeBoth(`poems/${sk.id}.json`, sk);
  }
  console.log(`✅ 写出 ${skeletons.length} 首诗词骨架到 poems/`);

  // 写索引
  const index = {
    schema_version: "v4.1",
    generated_at: new Date().toISOString(),
    total: skeletons.length,
    has_full_text: 0,
    pending_full_text: skeletons.length,
    poems: skeletons.map((s) => ({
      id: s.id,
      title: s.title,
      type: s.type,
      year: s.year_estimate,
      route_id: s.route_id,
      related_route_ids: s.related_route_ids,
      has_full_text: s.has_full_text,
    })),
  };
  writeBoth("poems-index.json", index);
  console.log(`✅ 写出 poems-index.json: ${skeletons.length} 首`);

  // 类型分布
  const typeCount: Record<string, number> = {};
  for (const s of skeletons) {
    typeCount[s.type] = (typeCount[s.type] || 0) + 1;
  }
  console.log("\n📊 类型分布:");
  for (const [t, c] of Object.entries(typeCount).sort((a, b) => b[1] - a[1])) {
    console.log(`  ${t}: ${c}`);
  }
}

main();
