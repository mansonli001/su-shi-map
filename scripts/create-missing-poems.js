#!/usr/bin/env node
/**
 * 为缺少 poem_id 的作品批量创建 poem 详情文件并回填 poem_id
 *
 * 用法：node scripts/create-missing-poems.js [--dry-run]
 *   --dry-run  仅输出计划，不实际创建文件
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const PLACES_DIR = path.join(ROOT, 'data-v4', 'places');
const POEMS_DIR = path.join(ROOT, 'data-v4', 'poems');

const dryRun = process.argv.includes('--dry-run');

// 读取现有 poems
const poemFiles = fs.readdirSync(POEMS_DIR).filter(f => f.endsWith('.json'));
const poemByTitle = new Map();
const existingIds = new Set();
for (const f of poemFiles) {
  try {
    const p = JSON.parse(fs.readFileSync(path.join(POEMS_DIR, f), 'utf-8'));
    poemByTitle.set(p.title, p.id);
    existingIds.add(p.id);
  } catch {}
}

// 收集所有无 poem_id 的 works
const needCreate = new Map(); // title -> {title, type, place, placeId, description, excerpt}
const placeUpdates = []; // {file, workIndex, poemId}

for (const f of fs.readdirSync(PLACES_DIR).filter(f => f.endsWith('.json'))) {
  const fp = path.join(PLACES_DIR, f);
  const p = JSON.parse(fs.readFileSync(fp, 'utf-8'));
  const gw = p.global_works || [];

  for (let i = 0; i < gw.length; i++) {
    const w = gw[i];
    if (!w.poem_id) {
      // 先检查是否已有同名 poem
      const existingId = poemByTitle.get(w.title);
      if (existingId) {
        placeUpdates.push({ file: fp, placeId: p.id, workIndex: i, poemId: existingId, title: w.title });
      } else if (!needCreate.has(w.title)) {
        needCreate.set(w.title, {
          title: w.title,
          type: w.type || '诗',
          place: p.ancient_name,
          placeId: p.id,
          description: w.description || '',
          excerpt: w.excerpt || w.coreVerse || '',
        });
      }
    }
  }
}

// 生成新 ID
let nextNum = 200; // 从 S200 开始，避免与现有 ID 冲突
function generateId(type) {
  const prefix = type === '词' ? 'C' : type === '文' || type === '策' ? 'W' : type === '赋' ? 'F' : 'S';
  let id;
  do {
    id = `${prefix}${String(nextNum).padStart(3, '0')}`;
    nextNum++;
  } while (existingIds.has(id));
  existingIds.add(id);
  return id;
}

// 创建 poem 文件
const newPoems = [];
for (const [title, info] of needCreate) {
  const id = generateId(info.type);
  const poem = {
    id,
    title: info.title,
    author: '苏轼',
    type: info.type,
    location: info.place,
    paragraphs: [],
    background: info.description || `${info.title}，苏轼作于${info.place}。`,
    famousQuotes: info.excerpt ? [info.excerpt] : [],
  };

  newPoems.push({ id, title, poem, placeId: info.placeId });
  poemByTitle.set(title, id);

  if (!dryRun) {
    fs.writeFileSync(path.join(POEMS_DIR, `${id}.json`), JSON.stringify(poem, null, 2) + '\n');
  }
}

// 回填 poem_id 到 places
for (const f of fs.readdirSync(PLACES_DIR).filter(f => f.endsWith('.json'))) {
  const fp = path.join(PLACES_DIR, f);
  const p = JSON.parse(fs.readFileSync(fp, 'utf-8'));
  const gw = p.global_works || [];
  let modified = false;

  for (const w of gw) {
    if (!w.poem_id) {
      const matchId = poemByTitle.get(w.title);
      if (matchId) {
        w.poem_id = matchId;
        modified = true;
      }
    }
  }

  if (modified && !dryRun) {
    fs.writeFileSync(fp, JSON.stringify(p, null, 2) + '\n');
  }
}

console.log(`=== ${dryRun ? '[DRY RUN] ' : ''}结果 ===`);
console.log(`已有poem可匹配: ${placeUpdates.length}`);
console.log(`新建poem文件: ${newPoems.length}`);
console.log(`总计补全poem_id: ${placeUpdates.length + newPoems.length}`);

if (dryRun) {
  console.log('\n新建文件预览:');
  newPoems.slice(0, 10).forEach(p => console.log(`  ${p.id} | ${p.title} | ${p.poem.location}`));
  if (newPoems.length > 10) console.log(`  ... 还有 ${newPoems.length - 10} 个`);
}
