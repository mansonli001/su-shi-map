/**
 * 更新路线数据中的作品标题和添加ID字段
 * 1. 修正作品标题使其与诗词库匹配
 * 2. 为每个作品添加poem_id字段
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
  poem_id?: string; // 新增字段
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

// 创建标题到ID的映射（包含别名映射）
const titleToId: Map<string, string> = new Map();
poemsIndex.forEach(p => {
  titleToId.set(p.title, p.id);
});

// 手动添加别名映射
titleToId.set('六月二十七日望湖楼醉书', 'S022');
titleToId.set('饮湖上初晴后雨', 'S038');
titleToId.set('上神宗皇帝书（前期酝酿）', 'Z002');
titleToId.set('挽父诗文、江淮行旅杂咏', 'S181');

// 处理所有路线文件
const routeFiles = fs.readdirSync(ROUTES_DIR).filter(f => f.endsWith('.json') && f.startsWith('R'));

routeFiles.forEach(file => {
  const filePath = path.join(ROUTES_DIR, file);
  const routeData: RouteData = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  
  if (routeData.literary_output?.representative_works) {
    routeData.literary_output.representative_works.forEach(work => {
      const poemId = titleToId.get(work.title);
      if (poemId) {
        work.poem_id = poemId;
        console.log(`✅ ${routeData.id} | ${work.title} | ${poemId}`);
      } else {
        console.log(`❌ ${routeData.id} | ${work.title} | 未找到匹配`);
      }
    });
    
    // 写回文件
    fs.writeFileSync(filePath, JSON.stringify(routeData, null, 2));
  }
});

console.log('\n路线作品ID更新完成！');