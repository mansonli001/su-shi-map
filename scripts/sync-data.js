#!/usr/bin/env node
/**
 * 同步 data-v4 → public/data-v4
 * 确保前端读取的数据与源数据一致
 *
 * 用法：node scripts/sync-data.js [--check]
 *   --check  仅检查不一致，不同步
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const SRC = path.join(ROOT, 'data-v4');
const DST = path.join(ROOT, 'public', 'data-v4');

const checkOnly = process.argv.includes('--check');

// 需要同步的目录和文件
const DIRS = ['places', 'routes', 'poems', 'meta', 'icons'];
const FILES = [
  'places-index.json',
  'routes-index.json',
  'poems-index.json',
  'stages-index.json',
  'map-config.json',
  'foods-by-place.json',
  'foods-sushi.json',
];

let synced = 0;
let mismatched = 0;
let missing = 0;

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function syncFile(src, dst) {
  if (!fs.existsSync(src)) return;

  if (!fs.existsSync(dst)) {
    if (checkOnly) {
      console.log(`  MISSING: ${path.relative(ROOT, dst)}`);
      missing++;
      return;
    }
    ensureDir(path.dirname(dst));
    fs.copyFileSync(src, dst);
    synced++;
    return;
  }

  const h1 = fs.readFileSync(src).toString();
  const h2 = fs.readFileSync(dst).toString();
  if (h1 !== h2) {
    if (checkOnly) {
      console.log(`  MISMATCH: ${path.relative(ROOT, dst)}`);
      mismatched++;
      return;
    }
    fs.copyFileSync(src, dst);
    synced++;
  }
}

function syncDir(subDir) {
  const srcDir = path.join(SRC, subDir);
  const dstDir = path.join(DST, subDir);

  if (!fs.existsSync(srcDir)) return;

  ensureDir(dstDir);

  const files = fs.readdirSync(srcDir).filter((f) => f.endsWith('.json'));
  for (const f of files) {
    syncFile(path.join(srcDir, f), path.join(dstDir, f));
  }
}

console.log(checkOnly ? '检查数据一致性...' : '同步 data-v4 → public/data-v4...');

// 同步目录
for (const dir of DIRS) {
  syncDir(dir);
}

// 同步顶层文件
for (const file of FILES) {
  syncFile(path.join(SRC, file), path.join(DST, file));
}

if (checkOnly) {
  if (mismatched === 0 && missing === 0) {
    console.log('✅ 所有数据一致');
  } else {
    console.log(`❌ ${mismatched} 个不一致, ${missing} 个缺失`);
    process.exit(1);
  }
} else {
  console.log(`✅ 同步完成: ${synced} 个文件已更新`);
}
