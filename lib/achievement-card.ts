/**
 * Canvas 成就卡生成器
 * 生成 750×1280 PNG 格式的成就卡图片
 * 
 * Canvas 字体降级铁律：Webfont 不能在 Canvas 中可靠渲染
 * 所有 drawText 使用系统衬线字体兜底
 */

import type { Achievement } from './achievements';

interface CardStats {
  count: number;
  placeNames: string[];
  uid: string;
  date?: string;
}

const CANVAS_WIDTH = 750;
const CANVAS_HEIGHT = 1280;

const COLORS = {
  bg: '#12090A',           // 极深棕底
  border: '#C9973A',       // 金色边框
  borderLight: '#FAC775',  // 浅金边框
  textPrimary: '#F5DFA0',  // 金色文字
  textSecondary: '#FFFFFF', // 白色文字
  textMuted: 'rgba(255, 255, 255, 0.44)', // 浅色文字
};

const FONTS = {
  // 系统衬线字体降级
  serif: '"PingFang SC", "STSong", "Songti SC", serif',
  sans: '"PingFang SC", "Helvetica Neue", Arial, sans-serif',
};

export function generateAchievementCard(
  ach: Achievement,
  stats: CardStats,
): string {
  const canvas = document.createElement('canvas');
  canvas.width = CANVAS_WIDTH;
  canvas.height = CANVAS_HEIGHT;
  const ctx = canvas.getContext('2d');
  
  if (!ctx) {
    throw new Error('Canvas context not available');
  }

  // ========== 1. 绘制背景 ==========
  drawBackground(ctx);

  // ========== 2. 绘制边框 ==========
  drawBorder(ctx);

  // ========== 3. 绘制顶部品牌区 ==========
  drawHeader(ctx);

  // ========== 4. 绘制中央 emoji 大圆 ==========
  drawEmojiCircle(ctx, ach);

  // ========== 5. 绘制成就名和打卡数 ==========
  drawAchievementInfo(ctx, ach, stats);

  // ========== 6. 绘制已打卡地点预览 ==========
  drawPlacePreview(ctx, stats.placeNames);

  // ========== 7. 绘制分隔线和诗词金句 ==========
  drawPoem(ctx, ach);

  // ========== 8. 绘制底部信息 ==========
  drawFooter(ctx, stats);

  return canvas.toDataURL('image/png');
}

function drawBackground(ctx: CanvasRenderingContext2D): void {
  // 绘制背景渐变
  const gradient = ctx.createLinearGradient(0, 0, 0, CANVAS_HEIGHT);
  gradient.addColorStop(0, '#1A1008');
  gradient.addColorStop(1, '#12090A');
  
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
}

function drawBorder(ctx: CanvasRenderingContext2D): void {
  const borderWidth = 4;
  const cornerRadius = 24;
  
  // 外层边框
  ctx.strokeStyle = COLORS.border;
  ctx.lineWidth = borderWidth;
  drawRoundedRect(ctx, borderWidth / 2, borderWidth / 2, CANVAS_WIDTH - borderWidth, CANVAS_HEIGHT - borderWidth, cornerRadius);
  ctx.stroke();
  
  // 内层边框（稍微内缩）
  ctx.strokeStyle = COLORS.borderLight;
  ctx.lineWidth = 2;
  const innerOffset = 8;
  drawRoundedRect(ctx, innerOffset, innerOffset, CANVAS_WIDTH - innerOffset * 2, CANVAS_HEIGHT - innerOffset * 2, cornerRadius - 4);
  ctx.stroke();
}

function drawRoundedRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  height: number,
  radius: number,
): void {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + height - radius);
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  ctx.lineTo(x + radius, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
}

function drawHeader(ctx: CanvasRenderingContext2D): void {
  const paddingTop = 60;
  
  // 大字「行 吟 山 河」
  ctx.font = `600 48px ${FONTS.serif}`;
  ctx.fillStyle = COLORS.textPrimary;
  ctx.textAlign = 'center';
  ctx.fillText('行 吟 山 河', CANVAS_WIDTH / 2, paddingTop);
  
  // 拼音
  ctx.font = `400 16px ${FONTS.sans}`;
  ctx.fillStyle = COLORS.textMuted;
  ctx.fillText('XINGYIN SHANHE', CANVAS_WIDTH / 2, paddingTop + 32);
}

function drawEmojiCircle(ctx: CanvasRenderingContext2D, ach: Achievement): void {
  const centerX = CANVAS_WIDTH / 2;
  const centerY = 280;
  const radius = 128;
  
  // 绘制光晕
  const glowGradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius * 1.8);
  glowGradient.addColorStop(0, ach.glow);
  glowGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
  
  ctx.fillStyle = glowGradient;
  ctx.beginPath();
  ctx.arc(centerX, centerY, radius * 1.8, 0, Math.PI * 2);
  ctx.fill();
  
  // 绘制圆形背景
  ctx.beginPath();
  ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
  
  const circleGradient = ctx.createRadialGradient(centerX - radius * 0.3, centerY - radius * 0.3, 0, centerX, centerY, radius);
  circleGradient.addColorStop(0, 'rgba(255, 255, 255, 0.1)');
  circleGradient.addColorStop(1, 'rgba(255, 255, 255, 0.02)');
  
  ctx.fillStyle = circleGradient;
  ctx.fill();
  
  // 绘制描边
  ctx.strokeStyle = ach.color;
  ctx.lineWidth = 4;
  ctx.stroke();
  
  // 绘制 emoji
  ctx.font = '140px serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(ach.emoji, centerX, centerY);
}

function drawAchievementInfo(ctx: CanvasRenderingContext2D, ach: Achievement, stats: CardStats): void {
  const y = 480;
  
  // 成就名称
  ctx.font = `600 36px ${FONTS.serif}`;
  ctx.fillStyle = ach.color;
  ctx.textAlign = 'center';
  ctx.fillText(ach.name, CANVAS_WIDTH / 2, y);
  
  // 大数字打卡数
  ctx.font = `700 72px ${FONTS.sans}`;
  ctx.fillStyle = COLORS.textSecondary;
  ctx.textAlign = 'center';
  ctx.fillText(String(stats.count), CANVAS_WIDTH / 2, y + 60);
  
  // 打卡描述
  ctx.font = `400 18px ${FONTS.sans}`;
  ctx.fillStyle = COLORS.textMuted;
  ctx.fillText('个苏轼足迹已打卡', CANVAS_WIDTH / 2, y + 100);
}

function drawPlacePreview(ctx: CanvasRenderingContext2D, placeNames: string[]): void {
  const y = 620;
  const maxPlaces = 8;
  const displayPlaces = placeNames.slice(0, maxPlaces);
  
  if (displayPlaces.length === 0) {
    return;
  }
  
  // 已打卡地点预览
  const text = displayPlaces.join(' · ');
  ctx.font = `400 16px ${FONTS.serif}`;
  ctx.fillStyle = `rgba(245, 223, 160, 0.6)`;
  ctx.textAlign = 'center';
  
  // 限制文本宽度
  const maxWidth = CANVAS_WIDTH - 80;
  const metrics = ctx.measureText(text);
  
  if (metrics.width > maxWidth) {
    // 文本过长，截断处理
    let truncated = text;
    while (ctx.measureText(truncated + '...').width > maxWidth && truncated.length > 0) {
      truncated = truncated.slice(0, -1);
    }
    ctx.fillText(truncated + '...', CANVAS_WIDTH / 2, y);
  } else {
    ctx.fillText(text, CANVAS_WIDTH / 2, y);
  }
}

function drawPoem(ctx: CanvasRenderingContext2D, ach: Achievement): void {
  const y = 720;
  
  // 分隔线
  ctx.strokeStyle = `rgba(245, 223, 160, 0.2)`;
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(80, y);
  ctx.lineTo(CANVAS_WIDTH - 80, y);
  ctx.stroke();
  
  // 诗词金句
  const poemY = y + 48;
  ctx.font = `300 italic 24px ${FONTS.serif}`;
  ctx.fillStyle = COLORS.textSecondary;
  ctx.textAlign = 'center';
  ctx.fillText(ach.poem, CANVAS_WIDTH / 2, poemY);
  
  // 出处
  const srcY = poemY + 32;
  ctx.font = `400 14px ${FONTS.sans}`;
  ctx.fillStyle = COLORS.textMuted;
  ctx.fillText(ach.poemSrc, CANVAS_WIDTH / 2, srcY);
}

function drawFooter(ctx: CanvasRenderingContext2D, stats: CardStats): void {
  const paddingBottom = 40;
  const y = CANVAS_HEIGHT - paddingBottom;
  
  // 日期
  const date = stats.date || new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
  
  ctx.font = `400 12px ${FONTS.sans}`;
  ctx.fillStyle = COLORS.textMuted;
  ctx.textAlign = 'center';
  ctx.fillText(`${date} | ${stats.uid.slice(0, 8)}...`, CANVAS_WIDTH / 2, y);
  
  // 网址
  ctx.font = `400 12px ${FONTS.sans}`;
  ctx.fillStyle = COLORS.textMuted;
  ctx.fillText('su-shi.starfluxes.com', CANVAS_WIDTH / 2, y + 20);
}