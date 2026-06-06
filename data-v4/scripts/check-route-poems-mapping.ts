/**
 * 检查路线作品与诗词库的映射关系
 * 1. 提取所有路线中的作品信息
 * 2. 匹配诗词库中的作品ID
 * 3. 输出缺失的作品和匹配结果
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROUTES_DIR = path.join(__dirname, '../routes');
const POEMS_INDEX = path.join(__dirname, '../poems-index.json');

interface RouteWork {
  title: string;
  category?: string;
  note?: string;
  year_estimate?: number | string;
}

interface RouteData {
  id: string;
  name: string;
  literary_output?: {
    representative_works?: RouteWork[];
  };
}

interface PoemIndex {
  id: string;
  title: string;
  type: string;
  year?: number;
}

// 读取诗词库索引
const poemsIndex: PoemIndex[] = JSON.parse(fs.readFileSync(POEMS_INDEX, 'utf-8')).poems;

// 创建标题到ID的映射
const titleToId: Map<string, string> = new Map();
poemsIndex.forEach(p => {
  titleToId.set(p.title, p.id);
});

// 提取所有路线中的作品
const routeFiles = fs.readdirSync(ROUTES_DIR).filter(f => f.endsWith('.json') && f.startsWith('R'));
const allRouteWorks: Array<{ routeId: string; routeName: string; work: RouteWork }> = [];

routeFiles.forEach(file => {
  const routeData: RouteData = JSON.parse(fs.readFileSync(path.join(ROUTES_DIR, file), 'utf-8'));
  if (routeData.literary_output?.representative_works) {
    routeData.literary_output.representative_works.forEach(work => {
      allRouteWorks.push({
        routeId: routeData.id,
        routeName: routeData.name,
        work: work
      });
    });
  }
});

// 匹配作品ID
const matchedWorks: Array<{ routeId: string; routeName: string; work: RouteWork; poemId: string }> = [];
const unmatchedWorks: Array<{ routeId: string; routeName: string; work: RouteWork }> = [];

allRouteWorks.forEach(item => {
  const poemId = titleToId.get(item.work.title);
  if (poemId) {
    matchedWorks.push({
      ...item,
      poemId: poemId
    });
  } else {
    unmatchedWorks.push(item);
  }
});

// 输出结果
console.log('=== 路线作品与诗词库映射检查 ===\n');
console.log(`总路线数: ${routeFiles.length}`);
console.log(`总作品数: ${allRouteWorks.length}`);
console.log(`已匹配: ${matchedWorks.length}`);
console.log(`未匹配: ${unmatchedWorks.length}\n`);

if (unmatchedWorks.length > 0) {
  console.log('=== 未匹配的作品（需要补充到诗词库） ===\n');
  unmatchedWorks.forEach(item => {
    console.log(`路线: ${item.routeId} - ${item.routeName}`);
    console.log(`作品: ${item.work.title}`);
    console.log(`分类: ${item.work.category || '未知'}`);
    console.log(`年份: ${item.work.year_estimate || '未知'}`);
    console.log(`备注: ${item.work.note || '无'}`);
    console.log('---');
  });
}

// 输出匹配结果（用于更新路线数据）
console.log('\n=== 匹配结果（用于更新路线数据） ===\n');
matchedWorks.forEach(item => {
  console.log(`${item.routeId} | ${item.work.title} | ${item.poemId}`);
});

// 输出JSON格式的匹配结果
const mappingResult = {
  matched: matchedWorks.map(m => ({
    routeId: m.routeId,
    routeName: m.routeName,
    workTitle: m.work.title,
    poemId: m.poemId
  })),
  unmatched: unmatchedWorks.map(u => ({
    routeId: u.routeId,
    routeName: u.routeName,
    work: u.work
  }))
};

fs.writeFileSync(
  path.join(__dirname, '../meta/route-poems-mapping.json'),
  JSON.stringify(mappingResult, null, 2)
);

console.log('\n匹配结果已保存到: data-v4/meta/route-poems-mapping.json');