#!/usr/bin/env node
/**
 * 234地点数据质量QA扫描（Node.js版）
 * 检查项：空内容、坐标异常、导航失效、字段缺失
 * 输出：qa-report.csv
 *
 * 用法：node scripts/qa-locations.js
 */

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'data-v4', 'places');
const OUTPUT_FILE = path.join(__dirname, '..', 'qa-report.csv');

// 中国坐标范围
const CHINA = { latMin: 3, latMax: 53, lngMin: 73, lngMax: 135 };

function haversineKm(lat1, lng1, lat2, lng2) {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.asin(Math.sqrt(a));
}

function main() {
  const files = fs.readdirSync(DATA_DIR).filter((f) => /^P\d+\.json$/.test(f));
  const issues = [];

  console.log(`扫描 ${files.length} 个地点数据...\n`);

  for (const file of files) {
    const fp = path.join(DATA_DIR, file);
    let p;
    try {
      p = JSON.parse(fs.readFileSync(fp, 'utf-8'));
    } catch (e) {
      issues.push({ id: file.replace('.json', ''), name: '', type: 'parse_error', detail: `JSON解析失败: ${e.message}`, value: '' });
      continue;
    }

    const pid = p.id || file.replace('.json', '');
    const name = p.ancient_name || p.songName || '';
    const modernName = p.modern_name || p.modernName || '';

    // 1. name 为空
    if (!name || name.trim() === '') {
      issues.push({ id: pid, name, type: 'empty_name', detail: '地点名为空', value: '' });
    }

    // 2. 坐标检测
    const lat = p.lat;
    const lng = p.lng;
    if (lat == null || lng == null) {
      issues.push({ id: pid, name, type: 'missing_coord', detail: '缺少lat/lng坐标', value: `lat=${lat}, lng=${lng}` });
    } else if (lat < CHINA.latMin || lat > CHINA.latMax || lng < CHINA.lngMin || lng > CHINA.lngMax) {
      issues.push({ id: pid, name, type: 'coord_out_of_range', detail: '坐标超出中国范围', value: `(${lat}, ${lng})` });
    }

    // 3. description/background 字符数 > 20
    const desc = p.background || p.summary || p.extended_story || '';
    if (desc.length <= 20) {
      issues.push({ id: pid, name, type: 'short_description', detail: `描述过短(${desc.length}字)`, value: desc.slice(0, 30) });
    }

    // 4. 关联诗词检测
    const works = p.global_works || p.poems || [];
    if (works.length === 0) {
      issues.push({ id: pid, name, type: 'no_poems', detail: '无关联诗词', value: '' });
    }

    // 5. 高德导航URL可构造
    const mv = p.modern_visit;
    let navLat = null;
    let navLng = null;
    let navName = '';

    if (mv && typeof mv === 'object') {
      navName = mv.amap_name || mv.name || '';

      // 从 location 字段解析（格式："lng,lat"）
      if (mv.location && typeof mv.location === 'string') {
        const parts = mv.location.split(',');
        if (parts.length === 2) {
          navLng = parseFloat(parts[0]) || null;
          navLat = parseFloat(parts[1]) || null;
        }
      }

      // fallback 到 lat/lng 字段
      if (!navLat) navLat = mv.lat || null;
      if (!navLng) navLng = mv.lng || null;
    }

    if (!mv) {
      issues.push({ id: pid, name, type: 'no_modern_visit', detail: '无文旅导航信息', value: '' });
    } else if (!navLat || !navLng) {
      issues.push({ id: pid, name, type: 'no_poi_coord', detail: '导航POI无坐标', value: `modern_visit=${JSON.stringify(mv).slice(0, 60)}` });
    } else {
      // 构造高德URL验证
      const amapUrl = `https://uri.amap.com/navigation?to=${navLng},${navLat},${encodeURIComponent(navName || name)}`;
      // 只验证URL可构造，不实际请求
      if (!navName) {
        issues.push({ id: pid, name, type: 'no_poi_name', detail: '导航POI无名称', value: amapUrl });
      }

      // POI坐标与地点坐标偏差 > 10km
      if (lat && lng && navLat && navLng) {
        const dist = haversineKm(lat, lng, navLat, navLng);
        if (dist > 10) {
          issues.push({ id: pid, name, type: 'poi_mismatch', detail: `POI偏差${dist.toFixed(1)}km`, value: `place=(${lat},${lng}) poi=(${navLat},${navLng})` });
        }
      }
    }

    // 6. 子地点坐标重复
    const subs = p.sub_places || p.memorial_sites || [];
    if (subs.length > 1) {
      const coords = subs.filter((s) => s.lat).map((s) => ({ lat: s.lat, lng: s.lng, name: s.name || '' }));
      for (let i = 0; i < coords.length; i++) {
        for (let j = i + 1; j < coords.length; j++) {
          if (coords[i].lat === coords[j].lat && coords[i].lng === coords[j].lng) {
            issues.push({ id: pid, name, type: 'sub_coord_dup', detail: '子地点坐标重复', value: `${coords[i].name}和${coords[j].name}坐标相同(${coords[i].lat},${coords[i].lng})` });
          }
        }
      }
    }

    // 7. famous_line 检测
    const fl = p.famous_line;
    if (!fl || !fl.quote) {
      issues.push({ id: pid, name, type: 'no_famous_line', detail: '无代表名句', value: '' });
    }
  }

  // 统计
  const typeCounts = {};
  for (const issue of issues) {
    typeCounts[issue.type] = (typeCounts[issue.type] || 0) + 1;
  }

  console.log('=== QA扫描结果 ===\n');
  for (const [type, count] of Object.entries(typeCounts).sort((a, b) => b[1] - a[1])) {
    console.log(`  ${type}: ${count}`);
  }
  console.log(`\n总问题数: ${issues.length}`);

  // 输出 CSV
  const header = '地点ID,地点名,问题类型,问题描述,当前值\n';
  const rows = issues.map((i) => {
    const escapeCSV = (s) => `"${String(s).replace(/"/g, '""')}"`;
    return [escapeCSV(i.id), escapeCSV(i.name), escapeCSV(i.type), escapeCSV(i.detail), escapeCSV(i.value)].join(',');
  }).join('\n');

  fs.writeFileSync(OUTPUT_FILE, header + rows, 'utf-8');
  console.log(`\n报告已输出: ${OUTPUT_FILE}`);
}

main();
