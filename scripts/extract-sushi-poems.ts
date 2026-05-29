/**
 * 从 chinese-poetry 提取苏轼诗词 → Poem 结构
 * 输出: data/poems-sushi.json
 *
 * 用法: pnpm poems
 */

import * as fs from 'fs';
import * as path from 'path';
import { Poem } from '@/types';

const CHINESE_POETRY_ROOT = path.resolve('./temp-poetry');
const OUTPUT_PATH = path.resolve('./data/poems-sushi.json');

// 苏轼别名（chinese-poetry 中用这些名字）
const SUSHI_AUTHORS = ['苏轼', '苏东坡', '苏子瞻', '苏和仲'];

// 需要扫描的子目录
const TARGET_DIRS = ['宋词', '全唐诗', '御定全唐詩'];

/**
 * 递归扫描所有 JSON 文件
 */
function walkDir(dir: string): string[] {
  let results: string[] = [];
  const list = fs.readdirSync(dir);
  for (const file of list) {
    const full = path.join(dir, file);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) {
      results = results.concat(walkDir(full));
    } else if (file.endsWith('.json')) {
      results.push(full);
    }
  }
  return results;
}

/**
 * 尝试从内容中推断写作地点（简单启发式，后期人工标注）
 */
function inferLocation(content: string): string | undefined {
  const locationKeywords: Record<string, string> = {
    '黄州': 'SS021',
    '惠州': 'SS073',
    '儋州': 'SS091',
    '杭州': 'SS119',
    '密州': 'SS015',
    '徐州': 'SS016',
    '湖州': 'SS118',
    '颍州': 'SS050',
    '扬州': 'SS051',
    '定州': 'SS066',
    '眉山': 'SS001',
    '汴京': 'SS004',
    '开封': 'SS004',
    '海南': 'SS091',
    '岭南': 'SS073',
  };

  for (const [keyword, placeId] of Object.entries(locationKeywords)) {
    if (content.includes(keyword)) {
      return placeId;
    }
  }
  return undefined;
}

/**
 * 清洗诗词内容
 */
function cleanContent(raw: string): string {
  return raw
    .replace(/[\r\n]+/g, '\n')
    .replace(/\s{2,}/g, ' ')
    .trim();
}

async function extractPoems(): Promise<Poem[]> {
  const poems: Poem[] = [];

  console.log('📖 开始提取苏轼诗词...');

  const allFiles: string[] = [];

  // 扫描目标子目录
  for (const dir of TARGET_DIRS) {
    const fullDir = path.join(CHINESE_POETRY_ROOT, dir);
    if (!fs.existsSync(fullDir)) {
      console.log(`⚠️  目录不存在: ${dir}`);
      continue;
    }
    const files = walkDir(fullDir);
    allFiles.push(...files);
    console.log(`📂 ${dir}: 找到 ${files.length} 个 JSON 文件`);
  }

  console.log(`📊 共扫描 ${allFiles.length} 个文件\n`);

  let processed = 0;

  for (const filePath of allFiles) {
    processed++;
    if (processed % 100 === 0) {
      process.stdout.write(`\r⏳ 处理中: ${processed}/${allFiles.length}`);
    }

    let data: any[] = [];
    try {
      const raw = fs.readFileSync(filePath, 'utf-8');
      data = JSON.parse(raw);
    } catch (e) {
      continue;
    }

    if (!Array.isArray(data)) continue;

    for (const item of data) {
      const author: string = item.author || item.writer || item.artist || '';

      // 匹配苏轼（含别名）
      const isSushi = SUSHI_AUTHORS.some(
        (name) => author.includes(name)
      );
      if (!isSushi) continue;

      const title = item.title || item.name || '无题';
      const content = cleanContent(
        item.content || item.content_s || item.paragraphs?.join('\n') || ''
      );

      if (!content) continue;

      const poem: Poem = {
        id: `poem-${poems.length + 1}`,
        title,
        content,
        year: item.year ? parseInt(item.year) : undefined,
        locationId: inferLocation(content) || undefined,
      };

      poems.push(poem);
    }
  }

  console.log(`\n✅ 提取完成，共 ${poems.length} 首诗词`);
  return poems;
}

async function main() {
  const poems = await extractPoems();

  // 去重（按 title + content 前50字）
  const seen = new Set<string>();
  const unique: Poem[] = [];
  for (const p of poems) {
    const key = `${p.title}::${p.content.slice(0, 50)}`;
    if (seen.has(key)) continue;
    seen.add(key);
    unique.push(p);
  }

  console.log(`🧹 去重后: ${unique.length} 首`);

  // 重新编号
  unique.forEach((p, i) => {
    p.id = `poem-${i + 1}`;
  });

  fs.writeFileSync(
    OUTPUT_PATH,
    JSON.stringify(unique, null, 2),
    'utf-8'
  );

  console.log(`💾 已保存到 ${OUTPUT_PATH}`);
}

main().catch(console.error);
