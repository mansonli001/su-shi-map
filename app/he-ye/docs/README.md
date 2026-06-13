# 贺野游中国 · 模块文档

> 公众号「有生余年」贺野的旅行足迹地图，独立于苏轼模块运行。

## 目录结构

```
app/he-ye/                  # 贺野路由域
├── layout.tsx              # 独立 layout + SEO metadata
├── page.tsx                # 首页（6 段：Hero / 精选 / 统计 / 最新 / 关于 / CTA）
├── HeyeHomeClient.tsx      # 精选轮播客户端组件
├── heye-home.css           # 全站样式（暖橙配色）
├── explore/page.tsx        # 足迹地图
├── feed/page.tsx           # 文章流（按年份 + 省份筛选）
├── profile/page.tsx        # 旅人录（成就墙 + 打卡记录）
└── docs/                   # 模块文档
    ├── README.md           # 本文件
    └── CHANGELOG.md        # 变更记录

components/map/
└── HeyeMapContainer.tsx    # 贺野地图容器（独立于苏轼 AMapContainer）

lib/
├── heye-loader.ts          # 客户端数据加载（fetch JSON）
├── heye-loader-server.ts   # 服务端数据加载（fs 读取，仅 Server Component）
├── heye-store.ts           # Zustand 状态管理（persist key: he-ye-user-data）
└── heye-achievements.ts    # 成就系统（6 个成就 + 计算逻辑）

types/
└── heye.ts                 # TypeScript 类型定义

public/data-heye/           # 静态数据
├── locations.json          # 全量地点索引
├── province-stats.json     # 省份统计（着色用）
└── meta.json               # 全局元信息

scripts/
├── heye_extractor.py       # PDF 提取脚本（零外部 API 依赖版）
├── csv_to_heye_json.py     # CSV → JSON 转换
└── heye_seed.csv           # 种子数据（32 地点 / 10 省）
```

## 架构隔离

| 维度 | 苏轼 | 贺野 |
|---|---|---|
| 路由域 | `/` `/explore` `/checkin` 等 | `/he-ye` `/he-ye/explore` `/he-ye/feed` `/he-ye/profile` |
| 数据目录 | `public/data-v4/` | `public/data-heye/` |
| Store persist key | `su-shi-user-data` | `he-ye-user-data` |
| CSS 类名前缀 | `ho-` `ip-` | `he-` |
| 色板 | 水墨风（`--ink-*`） | 暖橙风（`--he-*`） |
| 地图容器 | `AMapContainer` | `HeyeMapContainer` |
| 数据加载 | `lib/data-loader.ts` | `lib/heye-loader.ts` / `heye-loader-server.ts` |

**共享点**（合理共用，不影响功能）：
- `BottomNav.tsx` — 按 pathname 自动切换苏轼/贺野导航
- `lib/amap-loader.ts` — AMap SDK 单例加载器
- `app/globals.css` — 贺野色板 CSS 变量（仅新增，不修改苏轼变量）
- `app/ink-path.css` — 底栏样式扩展

## 数据流程

```
PDF 文章
  ↓ heye_extractor.py extract（步骤 1）
prompt JSON + 文本文件
  ↓ IDE 内置 LLM 处理
LLM 结果 JSON（*_result.json）
  ↓ heye_extractor.py merge（步骤 2）
CSV（heye_locations.csv）
  ↓ csv_to_heye_json.py
locations.json + province-stats.json + meta.json
  ↓ heye-loader / heye-loader-server
前端页面
```

## 脚本使用

### 提取 PDF 文本（步骤 1）

```bash
# 批量处理
python scripts/heye_extractor.py extract --dir /path/to/pdfs --out-dir ./prompts

# 单文件
python scripts/heye_extractor.py extract --file 某篇文章.pdf --out-dir ./prompts
```

### 合并 LLM 结果（步骤 2）

```bash
# 批量合并
python scripts/heye_extractor.py merge --json-dir ./prompts --out heye_locations.csv

# 单文件
python scripts/heye_extractor.py merge --json ./prompts/HY001_result.json --out heye_locations.csv
```

### 生成 JSON 数据

```bash
python scripts/csv_to_heye_json.py --csv heye_locations.csv --out-dir public/data-heye --validate
```

## 配色方案

```css
--he-primary: #C4612A;   /* 主色：赤陶橙 */
--he-accent:  #E8854A;   /* 辅色：琥珀橙 */
--he-bg:      #FDF8F3;   /* 背景：宣纸白 */
--he-ink:     #2D1810;   /* 墨色：深褐 */
--he-muted:   #8B7355;   /* 辅助：褐灰 */
--he-tag-bg:  #F5E6D3;   /* 标签：浅杏 */
```

## 成就系统

| ID | 名称 | 条件 |
|---|---|---|
| first_step | 初行 | 打卡 1 个地点 |
| explorer_5 | 行者 | 打卡 5 个地点 |
| explorer_15 | 旅人 | 打卡 15 个地点 |
| province_3 | 跨省 | 打卡 3 个省份 |
| snack_5 | 饕客 | 打卡 5 种小吃 |
| all_featured | 全精选 | 打卡所有精选地点 |

## 已知限制

- 种子数据为手动创建，正式数据需运行 `heye_extractor.py` + 人工校验
- 地图省份着色（GeoJSON 叠加）尚未实现
- 分享卡功能尚未实现
- 图片 URL 字段均为空，使用渐变占位
