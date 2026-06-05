/**
 * 图标压缩脚本
 * 将成就图标压缩并转为Base64编码，嵌入代码中
 * 双分辨率方案：UI展示用128px，分享海报用256px保证高清
 */

import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';
import sharp from 'sharp';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const inputDir = '/Users/mansonlee/Downloads/SVG';
const outputFile = path.join(__dirname, '../lib/icons.ts');

// 双分辨率方案
const UI_SIZE = 128;      // UI展示用
const POSTER_SIZE = 256;  // 分享海报用（保证高清）

async function compressAndEncode(inputPath: string, fileName: string, size: number): Promise<{ base64: string; size: number }> {
  const buffer = await fs.promises.readFile(inputPath);
  const originalSize = buffer.length;
  
  // 压缩图片
  const compressedBuffer = await sharp(buffer)
    .resize(size, size, {
      fit: sharp.fit.contain,
      background: { r: 0, g: 0, b: 0, alpha: 0 }
    })
    .png({
      quality: 95,  // 高质量压缩
      compressionLevel: 6  // 适中压缩级别，平衡质量和大小
    })
    .toBuffer();
  
  const base64 = compressedBuffer.toString('base64');
  const compressedSize = compressedBuffer.length;
  
  console.log(`  ${fileName}: ${(originalSize/1024).toFixed(1)}KB -> ${(compressedSize/1024).toFixed(1)}KB (${((1-compressedSize/originalSize)*100).toFixed(0)}% reduction)`);
  
  return { base64, size: compressedSize };
}

async function main() {
  console.log('=== 成就图标压缩脚本（双分辨率方案）===\n');
  
  const categories = fs.readdirSync(inputDir).filter(item => 
    fs.statSync(path.join(inputDir, item)).isDirectory()
  );
  
  const uiIcons: Record<string, string> = {};
  const posterIcons: Record<string, string> = {};
  let totalOriginal = 0;
  let totalUiCompressed = 0;
  let totalPosterCompressed = 0;
  
  for (const category of categories) {
    console.log(`处理分类: ${category}`);
    
    const categoryDir = path.join(inputDir, category);
    const files = fs.readdirSync(categoryDir).filter(file => file.endsWith('.png'));
    
    for (const file of files) {
      const inputPath = path.join(categoryDir, file);
      const stat = fs.statSync(inputPath);
      totalOriginal += stat.size;
      
      const name = file.replace('.png', '');
      
      // 生成UI尺寸图标
      const { base64: uiBase64, size: uiSize } = await compressAndEncode(inputPath, file, UI_SIZE);
      totalUiCompressed += uiSize;
      uiIcons[name] = uiBase64;
      
      // 生成海报尺寸图标（高清）
      const { base64: posterBase64, size: posterSize } = await compressAndEncode(inputPath, file, POSTER_SIZE);
      totalPosterCompressed += posterSize;
      posterIcons[name] = posterBase64;
    }
    console.log('');
  }
  
  // 生成图标数据文件
  const outputContent = `/**
 * 成就图标数据（Base64编码）
 * 自动生成，请勿手动修改
 * 
 * 双分辨率方案：
 * - UI展示: ${UI_SIZE}x${UI_SIZE}像素
 * - 分享海报: ${POSTER_SIZE}x${POSTER_SIZE}像素（高清）
 */

/**
 * UI展示用图标（${UI_SIZE}x${UI_SIZE}）
 */
export const achievementIcons: Record<string, string> = {
${Object.entries(uiIcons).map(([name, base64]) => `  '${name}': 'data:image/png;base64,${base64}',`).join('\n')}
};

/**
 * 分享海报用图标（${POSTER_SIZE}x${POSTER_SIZE}，高清）
 */
export const achievementIconsHD: Record<string, string> = {
${Object.entries(posterIcons).map(([name, base64]) => `  '${name}': 'data:image/png;base64,${base64}',`).join('\n')}
};

/**
 * 获取UI图标
 */
export const getIconByName = (name: string): string | undefined => {
  return achievementIcons[name];
};

/**
 * 获取高清海报图标
 */
export const getIconByNameHD = (name: string): string | undefined => {
  return achievementIconsHD[name];
};
`;
  
  await fs.promises.writeFile(outputFile, outputContent);
  
  console.log('=== 压缩完成 ===');
  console.log(`原始总大小: ${(totalOriginal/1024).toFixed(1)} KB`);
  console.log(`UI图标总大小: ${(totalUiCompressed/1024).toFixed(1)} KB`);
  console.log(`海报图标总大小: ${(totalPosterCompressed/1024).toFixed(1)} KB`);
  console.log(`总压缩后大小: ${((totalUiCompressed + totalPosterCompressed)/1024).toFixed(1)} KB`);
  console.log(`\n输出文件: ${outputFile}`);
}

main().catch(console.error);
