#!/usr/bin/env node
/**
 * 自动化走查脚本 v1.0 · 5 条黄金路径
 *
 * 用 Puppeteer 模拟 iPhone 14 Pro 视口，自动跑 5 条核心用户路径，
 * 截图保存 + 收集 console error/warning + 检查关键 DOM 元素是否渲染。
 *
 * 用法：
 *   node scripts/auto-walkthrough.mjs                # 默认 localhost:3000
 *   node scripts/auto-walkthrough.mjs --prod         # 跑线上 su-shi.starfluxes.com
 *
 * 输出：
 *   walkthrough-report/
 *     ├─ 01-home.png
 *     ├─ 02-explore.png
 *     ├─ 03-place-card.png
 *     ├─ 04-routes-list.png
 *     ├─ 05-route-detail.png
 *     └─ report.md
 */

import puppeteer from 'puppeteer';
import fs from 'node:fs/promises';
import path from 'node:path';

const isProd = process.argv.includes('--prod');
const BASE = isProd ? 'https://su-shi.starfluxes.com' : 'http://localhost:3000';
const OUT_DIR = path.join(process.cwd(), 'walkthrough-report');

// iPhone 14 Pro 视口（实际 393x852 + DPR 3）
const VIEWPORT = { width: 393, height: 852, deviceScaleFactor: 2, isMobile: true, hasTouch: true };
const UA_IOS = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1';

const results = [];
const consoleLogs = [];

function logResult(step, status, details = '') {
  const icon = status === 'pass' ? '✅' : status === 'warn' ? '⚠️' : '❌';
  console.log(`${icon} ${step}${details ? ` · ${details}` : ''}`);
  results.push({ step, status, details });
}

async function checkElement(page, selector, name, optional = false) {
  try {
    await page.waitForSelector(selector, { timeout: 8000 });
    const visible = await page.$eval(selector, (el) => {
      const style = window.getComputedStyle(el);
      return style.display !== 'none' && style.visibility !== 'hidden';
    }).catch(() => false);
    if (visible) {
      logResult(`  → ${name}`, 'pass');
      return true;
    }
    logResult(`  → ${name}`, optional ? 'warn' : 'fail', '元素存在但不可见');
    return false;
  } catch (err) {
    logResult(`  → ${name}`, optional ? 'warn' : 'fail', '找不到元素');
    return false;
  }
}

async function shoot(page, filename) {
  const fullPath = path.join(OUT_DIR, filename);
  await page.screenshot({ path: fullPath, fullPage: false });
  return filename;
}

async function main() {
  console.log(`\n🚀 行吟山河 · 自动化走查 v1.0`);
  console.log(`   目标：${BASE}`);
  console.log(`   视口：iPhone 14 Pro (393x852)`);
  console.log(`   ────────────────────────────\n`);

  await fs.mkdir(OUT_DIR, { recursive: true });

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  try {
    const page = await browser.newPage();
    await page.setViewport(VIEWPORT);
    await page.setUserAgent(UA_IOS);

    // 收集 console
    page.on('console', (msg) => {
      const t = msg.type();
      if (t === 'error' || t === 'warning') {
        consoleLogs.push({ type: t, text: msg.text(), location: msg.location() });
      }
    });
    page.on('pageerror', (err) => {
      consoleLogs.push({ type: 'pageerror', text: err.message });
    });
    // 抓 404 / 5xx 网络错误
    page.on('response', (res) => {
      const status = res.status();
      if (status >= 400) {
        consoleLogs.push({
          type: 'network',
          text: `${status} ${res.url()}`,
        });
      }
    });

    // ─── Path 1: 首页 Landing ─────────────────────
    console.log(`📍 Path 1: 首页 Landing /`);
    await page.goto(BASE, { waitUntil: 'networkidle2', timeout: 30000 });
    await new Promise((r) => setTimeout(r, 1500));
    await checkElement(page, '.logo-brand-lg', '行吟山河 LOGO 大字');
    await checkElement(page, '.ho-body', 'Hero 5 行排比正文');
    await checkElement(page, '.ho-btns a', 'Hero 按钮（开始探索/了解一生）');
    await checkElement(page, '.ho-pg-grid .ho-pgcard', '代表性足迹卡片');
    await checkElement(page, '.ho-ft-grid', 'COMING SOON 4 诗人');
    await checkElement(page, '.ho-cta-btns', 'Final CTA 三按钮');
    const homeShot = await shoot(page, '01-home.png');
    logResult(`  📸 截图保存 ${homeShot}`, 'pass');

    // ─── Path 2: 进探索页 ─────────────────────────
    console.log(`\n📍 Path 2: 探索页 /explore`);
    await page.goto(`${BASE}/explore`, { waitUntil: 'networkidle2', timeout: 30000 });
    await new Promise((r) => setTimeout(r, 3000)); // 等地图加载
    await checkElement(page, '.topnav-luxe', '顶栏（深色）');
    await checkElement(page, '.amap-container, [class*="amap"]', '高德地图容器');
    await checkElement(page, 'button[aria-label="打开路线菜单"]', '左上汉堡按钮');
    // 时间轴（移动端在底部）
    const hasTimeline = await page.evaluate(() => {
      return !!document.querySelector('[class*="bottom-0"]') || !!document.querySelector('.scrollbar-none');
    });
    logResult(`  → 底部时间轴`, hasTimeline ? 'pass' : 'fail');
    const exploreShot = await shoot(page, '02-explore.png');
    logResult(`  📸 截图保存 ${exploreShot}`, 'pass');

    // ─── Path 3: 打开 PlaceCard 详情卡 ────────────
    console.log(`\n📍 Path 3: 打开地点详情卡（焦点黄州 P072）`);
    await page.goto(`${BASE}/explore?focus=P072`, { waitUntil: 'networkidle2', timeout: 30000 });
    await new Promise((r) => setTimeout(r, 4000)); // 等 marker 触发
    const cardShot = await shoot(page, '03-place-card.png');
    logResult(`  📸 截图保存 ${cardShot}`, 'pass');

    // ─── Path 4: 路线列表 ─────────────────────────
    console.log(`\n📍 Path 4: 路线列表 /routes`);
    await page.goto(`${BASE}/routes`, { waitUntil: 'networkidle2', timeout: 30000 });
    await new Promise((r) => setTimeout(r, 1500));
    await checkElement(page, '.rb-root', '路线列表根容器');
    await checkElement(page, '.rb-header', '路线列表标题区');
    const routeCount = await page.$$eval('.rb-card', (cards) => cards.length).catch(() => 0);
    logResult(`  → 路线卡片数量: ${routeCount} 张`, routeCount >= 18 ? 'pass' : 'warn', `期望 ≥18`);
    const routesShot = await shoot(page, '04-routes-list.png');
    logResult(`  📸 截图保存 ${routesShot}`, 'pass');

    // ─── Path 5: 单条路线详情 ─────────────────────
    console.log(`\n📍 Path 5: 单条路线详情 /routes/R10（贬谪黄州）`);
    await page.goto(`${BASE}/routes/R10`, { waitUntil: 'networkidle2', timeout: 30000 });
    await new Promise((r) => setTimeout(r, 1500));
    await checkElement(page, '.rd-root', '路线详情根容器');
    await checkElement(page, '.rd-hero', 'Hero 区');
    await checkElement(page, '.rd-section', 'Section 区块', true);
    const detailShot = await shoot(page, '05-route-detail.png');
    logResult(`  📸 截图保存 ${detailShot}`, 'pass');

    // ─── 控制台错误汇总 ──────────────────────────
    console.log(`\n📊 控制台日志统计`);
    const errs = consoleLogs.filter((l) => l.type === 'error' || l.type === 'pageerror');
    const warns = consoleLogs.filter((l) => l.type === 'warning');
    if (errs.length === 0 && warns.length === 0) {
      logResult(`  → 0 errors, 0 warnings`, 'pass');
    } else {
      logResult(`  → ${errs.length} errors, ${warns.length} warnings`, errs.length > 0 ? 'fail' : 'warn');
    }

    // ─── 写报告 ──────────────────────────────────
    const passCount = results.filter((r) => r.status === 'pass').length;
    const warnCount = results.filter((r) => r.status === 'warn').length;
    const failCount = results.filter((r) => r.status === 'fail').length;

    let report = `# 行吟山河 · 自动化走查报告\n\n`;
    report += `- **目标**: ${BASE}\n`;
    report += `- **视口**: iPhone 14 Pro (393x852, DPR 2)\n`;
    report += `- **时间**: ${new Date().toLocaleString('zh-CN')}\n`;
    report += `- **结果**: ✅ ${passCount} pass / ⚠️ ${warnCount} warn / ❌ ${failCount} fail\n\n`;

    report += `## 检查项\n\n`;
    for (const r of results) {
      const icon = r.status === 'pass' ? '✅' : r.status === 'warn' ? '⚠️' : '❌';
      report += `${icon} ${r.step}${r.details ? ` · ${r.details}` : ''}\n`;
    }

    report += `\n## 截图\n\n`;
    report += `1. ![首页](./01-home.png)\n`;
    report += `2. ![探索页](./02-explore.png)\n`;
    report += `3. ![地点详情](./03-place-card.png)\n`;
    report += `4. ![路线列表](./04-routes-list.png)\n`;
    report += `5. ![路线详情](./05-route-detail.png)\n\n`;

    if (consoleLogs.length > 0) {
      report += `## 控制台日志\n\n`;
      for (const log of consoleLogs) {
        report += `- **[${log.type}]** ${log.text}\n`;
      }
    } else {
      report += `## 控制台日志\n\n无任何 error/warning ✨\n`;
    }

    await fs.writeFile(path.join(OUT_DIR, 'report.md'), report, 'utf-8');

    console.log(`\n✨ 走查完成`);
    console.log(`   ✅ pass: ${passCount}`);
    console.log(`   ⚠️ warn: ${warnCount}`);
    console.log(`   ❌ fail: ${failCount}`);
    console.log(`\n📂 报告: ${OUT_DIR}/report.md`);
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error('💥 走查异常:', err);
  process.exit(1);
});
