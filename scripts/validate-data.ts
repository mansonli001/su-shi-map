/**
 * 数据校验脚本
 * 校验 core / index / detail 三份数据的 id 一致性
 *
 * 用法: npx tsx scripts/validate-data.ts
 */

import * as fs from 'fs';
import * as path from 'path';
import json5 from 'json5';
import { PlaceCore, PlaceIndex, PlaceDetail } from '@/types';

const DATA_DIR = path.resolve('./data');

function loadJSON<T>(filename: string): T {
  const filepath = path.join(DATA_DIR, filename);
  if (!fs.existsSync(filepath)) {
    console.error(`❌ 文件不存在: ${filepath}`);
    process.exit(1);
  }
  const raw = fs.readFileSync(filepath, 'utf-8');
  try {
    return json5.parse(raw) as T;
  } catch (e) {
    console.error(`❌ JSON 解析失败: ${filepath}`);
    console.error((e as Error).message);
    process.exit(1);
  }
}

function validate(): void {
  console.log('🔍 校验地点数据...\n');

  const core: PlaceCore[] = loadJSON<PlaceCore[]>('places-core.json');
  const index: PlaceIndex[] = loadJSON<PlaceIndex[]>('places-index.json');

  // 1. 校验 core.id 唯一性
  const coreIds = new Set(core.map((p) => p.id));
  if (core.length !== coreIds.size) {
    console.error('❌ core: 存在重复 id');
    process.exit(1);
  }
  console.log(`✅ core: ${core.length} 个地点，id 唯一`);

  // 2. 校验 index.id 唯一性
  const indexIds = new Set(index.map((p) => p.id));
  if (index.length !== indexIds.size) {
    console.error('❌ index: 存在重复 id');
    process.exit(1);
  }
  console.log(`✅ index: ${index.length} 个地点，id 唯一`);

  // 3. 校验 core ↔ index id 一致
  const missingInIndex = coreIds.size > indexIds.size ? [...coreIds].filter((id) => !indexIds.has(id)) : [];
  const missingInCore = indexIds.size > coreIds.size ? [...indexIds].filter((id) => !coreIds.has(id)) : [];

  if (missingInIndex.length > 0) {
    console.error(`❌ core 有 ${missingInIndex.length} 个 id 在 index 中缺失: ${missingInIndex.join(', ')}`);
    process.exit(1);
  }
  if (missingInCore.length > 0) {
    console.error(`❌ index 有 ${missingInCore.length} 个 id 在 core 中缺失: ${missingInCore.join(', ')}`);
    process.exit(1);
  }
  console.log('✅ core ↔ index: id 完全一致');

  // 4. 校验详情页文件
  const detailIds = new Set<string>();
  const detailsDir = path.join(DATA_DIR, 'places');
  if (!fs.existsSync(detailsDir)) {
    console.log('⚠️  places/ 目录不存在，跳过详情页校验');
  } else {
    const files = fs.readdirSync(detailsDir).filter((f) => f.endsWith('.json'));
    for (const file of files) {
      const filepath = path.join(detailsDir, file);
      try {
        const raw = fs.readFileSync(filepath, 'utf-8');
        const detail: PlaceDetail = json5.parse(raw);
        detailIds.add(detail.id);
      } catch (e) {
        console.error(`❌ 详情文件解析失败: ${file}`);
        console.error((e as Error).message);
        process.exit(1);
      }
    }
    console.log(`✅ details: ${detailIds.size} 个详情文件`);

    const missingInDetails = [...coreIds].filter((id) => !detailIds.has(id));
    if (missingInDetails.length > 0) {
      console.warn(`⚠️  ${missingInDetails.length} 个地点缺少详情文件: ${missingInDetails.slice(0, 5).join(', ')}${missingInDetails.length > 5 ? '...' : ''}`);
    }
  }

  // 5. 校验 type 枚举
  const validTypes = ['birth', 'office', 'exile', 'tour', 'friend', 'burial'];
  const invalidTypes = core.filter((p) => !validTypes.includes(p.type));
  if (invalidTypes.length > 0) {
    console.error(`❌ 无效的 type: ${invalidTypes.map((p) => `${p.id}=${p.type}`).join(', ')}`);
    process.exit(1);
  }
  console.log('✅ type: 枚举校验通过');

  // 6. 校验 stage 枚举
  const validStages = ['youth', 'early_career', 'first_exile', 'middle_career', 'second_exile', 'third_exile', 'final_journey'];
  const invalidStages = core.filter((p) => !validStages.includes(p.stage));
  if (invalidStages.length > 0) {
    console.error(`❌ 无效的 stage: ${invalidStages.map((p) => `${p.id}=${p.stage}`).join(', ')}`);
    process.exit(1);
  }
  console.log('✅ stage: 枚举校验通过');

  // 7. 校验坐标范围（GCJ-02 中国范围）
  const chinaLng = core.filter((p) => p.lng < 72 || p.lng > 135);
  const chinaLat = core.filter((p) => p.lat < 3 || p.lat > 53);
  if (chinaLng.length > 0 || chinaLat.length > 0) {
    console.warn(`⚠️  坐标可能超出中国范围: ${chinaLng.map((p) => p.id).concat(chinaLat.map((p) => p.id)).join(', ')}`);
  }

  console.log('\n🎉 全部校验通过！');
}

validate();
