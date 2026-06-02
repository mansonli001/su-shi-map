# 行吟山河 · 项目架构与技术说明

> **当前版本**: v6.0「行吟山河」  
> **创建时间**: 2026-05-29  
> **当前状态**: ✅ v1.0 已上线弹性维护期 + 数据补全持续推进  
> **线上地址**: https://su-shi.starfluxes.com

---

## 一、项目定位

**行吟山河（XINGYIN SHANHE）** 是一个交互式数字地图，把苏轼一生 234 处足迹、20 条主题路线、68 篇代表作放回它们真实发生的土地上。

**核心理念**：中国的山河，从来不只是地理。是千年诗文落地生根。

**远期愿景**：行吟山河不止于苏轼——李白、杜甫、白居易等历代诗人将逐步加入。

---

## 二、技术架构

### 2.1 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户界面层 (UI)                          │
├─────────────────────────────────────────────────────────────────┤
│  / Landing  │  /explore  │  /routes  │  /routes/[id]  │  /about │
│  (Hero +    │  (地图主页)│ (路线列表)│ (沉浸阅读页)   │  (关于) │
│   4 卡片)   │            │           │                │         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        组件层 (Components)                        │
├─────────────────────────────────────────────────────────────────┤
│  HomeLanding   AMapContainer   PlaceCard   LeftSidebar          │
│  (首页)         (地图核心)      (详情卡)    (路线抽屉)           │
│                                                                  │
│  StageTimelineBar   Search   TrajectoryAnimation   AMapScript   │
│  (底部时间轴)        (搜索)   (轨迹动画)            (脚本加载)   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        状态与工具层 (Lib)                        │
├─────────────────────────────────────────────────────────────────┤
│  Zustand store   v4-adapter   route19-config   navigate         │
│  (全局状态)       (数据加载)   (路线配置)        (URL 跳转)      │
│                                                                  │
│  clusterRender   handDrawnPath   logger                          │
│  (Marker SVG)     (手绘平滑)      (日志)                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        API路由层 (API Routes)                   │
├─────────────────────────────────────────────────────────────────┤
│  /api/_AMapService/security_js_code  (高德密钥代理)              │
│  /api/checkin                          (打卡)                    │
│  /api/og                               (OG 图片)                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        数据层 (Data)                            │
├─────────────────────────────────────────────────────────────────┤
│  data-v4/                                                        │
│    ├─ places-index.json (234)   ├─ poems-index.json (68)        │
│    ├─ routes-index.json (20)    ├─ stages-index.json (6)        │
│    ├─ places/*.json (234)       ├─ poems/*.json                 │
│    └─ routes/*.json (20)                                         │
│                                                                  │
│  data-v4-source/  (数据原料)                                     │
│    └─ 行踪考-简体/ (25 篇 markdown / 100 万字)                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        外部服务层 (Services)                     │
├─────────────────────────────────────────────────────────────────┤
│  高德 JSAPI 2.0  + 自定义样式 amap://styles/5bcb3755...          │
│  Vercel OG (分享卡)                                              │
│  Cloudflare CDN (橙云代理)                                       │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 目录结构

```
su-shi-map/
├── app/                                  # Next.js App Router
│   ├── page.tsx                          # 首页（→ HomeLanding）
│   ├── home.css                          # Landing 专属样式
│   ├── explore/page.tsx                  # 地图主页 /explore
│   ├── routes/
│   │   ├── page.tsx                      # 路线列表 /routes
│   │   └── [id]/page.tsx                 # 单条路线详情 /routes/[id]
│   ├── routes.css                        # 路线浏览/详情样式
│   ├── about/page.tsx                    # 关于页 v5.0
│   ├── api/
│   │   ├── _AMapService/security_js_code/route.ts
│   │   ├── checkin/route.ts
│   │   └── og/route.tsx
│   ├── globals.css                       # 全局样式 + 字体 + 微信适配
│   └── layout.tsx                        # Root layout（OG 元数据）
│
├── components/
│   ├── Home/HomeLanding.tsx              # 首页 Landing
│   ├── map/AMapContainer.tsx             # 地图核心
│   ├── place/PlaceCard.tsx               # 地点详情卡
│   ├── LeftSidebar.tsx                   # 路线抽屉（移动底部 / 桌面左侧）
│   ├── StageTimelineBar.tsx              # 底部时间轴（横向滑动）
│   ├── Search.tsx                        # 全局搜索
│   ├── TrajectoryAnimation.tsx           # 轨迹动画
│   └── AMapScript.tsx                    # 高德脚本加载
│
├── lib/
│   ├── store.ts                          # Zustand 全局状态
│   ├── v4-adapter.ts                     # v4 数据加载/转换
│   ├── route19-config.ts                 # 路线运行时配置
│   ├── clusterRender.ts                  # Marker SVG 渲染
│   ├── handDrawnPath.ts                  # 手绘平滑路径算法
│   ├── navigate.ts                       # URL 跳转工具
│   └── logger.ts                         # 日志工具
│
├── types/
│   └── index.ts                          # TypeScript 全局类型
│
├── data-v4/                              # 生产数据 Schema v4.0
│   ├── places-index.json                 # 234 地点索引
│   ├── poems-index.json                  # 68 首诗词索引
│   ├── routes-index.json                 # 20 条路线索引
│   ├── stages-index.json                 # 6 阶段索引
│   ├── map-config.json                   # 地图全局配置
│   ├── places/P001~P234.json             # 234 个 place 详情
│   ├── poems/W001~W068.json              # 39 已有全文 + 29 待补
│   └── routes/R00~R19.json               # 20 条路线详情
│
├── data-v4-source/                       # 数据原料（不进生产）
│   ├── R0X_xxx.md                        # 20 条路线源数据 markdown
│   ├── 行踪考-简体/                      # 25 篇繁→简 markdown · 100 万字
│   ├── 行踪考诗词候选/                   # Phase 2 提取脚本输出
│   └── 外部专家任务清单/                 # A3 史实疑义裁决等
│
├── data/                                 # 历史 v3 + 备份
│   └── legacy-v3-backup-2026-06-01/
│
├── public/
│   ├── markers/marker-{type}.svg         # 8 类设计稿 SVG marker
│   ├── icons/pwa-{192,512}.png           # PWA 图标（占位）
│   ├── favicon.svg                       # 行吟山河"山"金色渐变 SVG
│   ├── favicon.ico                       # PWA 占位
│   └── manifest.json                     # PWA 清单
│
├── scripts/
│   ├── extract-xingzhongkao.py           # 行踪考 Word → 简体 md
│   ├── extract-poems-from-xingzhongkao.py # 诗词候选提取
│   ├── auto-walkthrough.mjs              # Puppeteer 自动化走查
│   ├── validate-data.ts                  # 数据校验
│   ├── convert-geojson.ts                # 坐标转换
│   └── extract-sushi-poems.ts            # 苏轼诗词提取
│
├── tailwind.config.ts                    # Tailwind 配置
├── next.config.js                        # Next.js 配置
├── package.json                          # 依赖
├── tsconfig.json                         # TypeScript 配置
├── vercel.json                           # Vercel 部署配置
├── README.md                             # 项目说明
└── PROJECT-ARCHITECTURE.md               # 本文档
```

---

## 三、视觉系统 v6.0

### 3.1 字体职能分工

| 用途 | 字体 | CSS 类 |
|---|---|---|
| UI 主力（导航/卡片/列表）| Noto Sans SC 思源黑体 | `var(--font-sans)` 默认 |
| 诗意锚点（Hero/品牌/诗句）| LXGW WenKai 霞鹜文楷 | `font-wenkai` |
| 数字位（年份/时间）| JetBrains Mono | `font-mono` |

### 3.2 行吟山河 LOGO 艺术字（3 档）

| 档位 | 用在哪 | CSS 类 |
|---|---|---|
| lg | Hero 大字 56-110px | `.logo-brand-lg` |
| md | Section 标题 28-38px | `.logo-brand-md` |
| sm | 顶栏小 logo 17px | `.logo-brand-sm` |

### 3.3 主色板

| 色 | Hex | CSS 变量 |
|---|---|---|
| 墨黑 | #1A1008 | `--ink` |
| 主金 | #FAC775 | `--gold` |
| 中金 | #BA7517 | `--gold-m` |
| 深金 | #EF9F27 | `--gold-d` |
| 米白 1 | #FAF6F0 | `--paper` |
| 米白 2 | #F0E9DF | `--paper2` |

### 3.4 4 类阶段色

| 类型 | 主色 | 浅色 |
|---|---|---|
| birth 出生 | #085041 | #5DCAA5 |
| office 任职 | #0C447C | #85B7EB |
| exile 贬谪 | #712B13 | #F0997B |
| tour 游览 | #633806 | #C9975A |

### 3.5 地图样式

- **样式 ID**: `amap://styles/5bcb375541c22ed25703103920a7d5e8`
- **基调**: 暖米白宣纸底图 #F4EEDD
- **路网**: 淡金主干道（高速 #C4A96A）+ 全部小路关闭
- **POI**: 全部关闭（餐饮/景区/医疗/商业等）
- **行政区界**: 淡赭石细线 #B0A080

---

## 四、关键交互设计

### 4.1 路线模式切换

```
总览模式（currentRoute === null/overview）：
- 所有 234 marker 显示
- 所有 20 条 polyline 显示（细虚线 strokeWeight 2）
- setFitView 自适应中国全图

单路线模式（currentRoute === 'Rxx'）：
- 仅显示该路线相关 marker
- 仅画该路线 polyline（中虚线 strokeWeight 3 + 方向箭头）
- 自动 setFitView 到该路线范围
```

### 4.2 移动端底部抽屉（v3.1）

苹果地图风格，68vh 弹起，地图永远 32% 可见。

```
┌────────────────────┐
│   [地图 32%]        │
├────────────────────┤
│   ━━━ 把手          │
│   行吟山河          │
│   ROUTES · 苏轼一生 │
│  ─────────────────  │
│   ● 一生总览         │
│  ─────────────────  │
│   ● 眉山·少年        │
│     眉山故里·少年... │
│   ● 汴京·宦游        │
│     ...              │
│  ─────────────────  │
│  ┌──────────────┐   │
│  │浏览全部 20 条→│   │ ← 主入口大按钮
│  └──────────────┘   │
└────────────────────┘
```

### 4.3 底部时间轴（v2.0）

横向可滑动 6 阶段，当前阶段自动居中放大（scale 1.05 + 金色背景）。

```
[眉山·少年] [汴京·宦游] [黄州·东坡] ◀ [元祐·还朝] [惠儋·南贬] [北归·终老]
   1037        1056        1080         1085         1094         1100
```

### 4.4 PlaceCard 详情卡

Framer Motion 三档拖动：折叠（38%）/ 展开（8%），底部留 144px 安全区防止 Safari 浏览器栏遮挡。

---

## 五、数据架构

### 5.1 v4 Schema 概览

每个 place 含以下字段：

```typescript
type PlaceCore = {
  id: string;                    // P001-P234
  ancient_name: string;          // 古地名（如"黄州"）
  modern_name: string;           // 今地名（如"湖北黄冈"）
  type: 'main' | 'visit' | 'stay' | 'study' | 'birth' | 'official' | 'death' | 'tomb';
  designType: DesignPlaceType;   // 设计稿 8 类
  lat: number;                   // GCJ-02 纬度
  lng: number;                   // GCJ-02 经度
  related_routes: string[];      // R00-R19
  summary: string;               // 一句话简介（100% 覆盖）
  background: string;            // 背景介绍 30-100 字（100% 覆盖）
  global_events: Array<{         // 史实事件（平均 5-8 条）
    id, date, title, description, significance
  }>;
  modern_visit?: {                // 旅游信息（57% 覆盖）
    address, ticket, hours, transport, tips
  };
  importance: 1 | 2 | 3;         // 重要度
  tags: string[];                // 标签
};
```

### 5.2 数据补全 Phase 路径

| Phase | 状态 | 内容 |
|---|---|---|
| Phase 1 | ✅ 完成 | 苏轼行踪考 26 docx → 25 简体 md（100 万字）|
| Phase 2 | 🟡 进行中 | 诗词关联 68 → 200+（卡在白名单数据源升级）|
| Phase 3 | ⏳ 计划中 | global_events 史实补全（最重）|
| Phase 4 | ⏳ 计划中 | 实景图片提取 + place 关联 |
| modern_visit | ⏳ 计划中 | 高德 POI API 批量补全 134 个 |
| A3 裁决 | 🟡 进行中 | 外部专家史实疑义清单 |

---

## 六、部署链路

```
开发环境
    ↓ git push origin main
GitHub (mansonli001/su-shi-map · Public)
    ↓ webhook
Vercel (Hobby 免费版)
    ↓ next build → Edge Functions
Cloudflare (橙云代理)
    ↓ CDN 分发
su-shi.starfluxes.com（国内+海外稳定）
```

### 域名架构

- **主域** `starfluxes.com` — 阿里云万网注册，Cloudflare DNS
- **当前子域** `su-shi.starfluxes.com` — 苏轼地图专用
- **未来子域**（规划中）`xingxing.starfluxes.com` — 醒醒攻 / `toxic-pm.starfluxes.com` — 产品抬杠大师等

### 环境变量（生产）

```bash
NEXT_PUBLIC_AMAP_KEY=...          # 高德 JS API（白名单含 starfluxes）
AMAP_SECURITY_JS_CODE=...          # 安全密钥（保密）
AMAP_WEB_SERVICE_KEY=...          # POI Web Service（开发数据补全用）
```

---

## 七、自动化质量保证

### 7.1 自动化走查脚本

`scripts/auto-walkthrough.mjs`：

- Puppeteer 模拟 iPhone 14 Pro（393x852, DPR 2）
- 5 条黄金路径 22 项断言
- 截图 + console 日志 + 网络 4xx/5xx 抓取
- 输出 `walkthrough-report/{01-05}.png + report.md`

```bash
pnpm walkthrough          # 跑本地 dev server
pnpm walkthrough:prod     # 跑线上 starfluxes
```

最近一次走查：**22 pass / 0 warn / 0 fail · 0 console error**

### 7.2 数据完整性

| 字段 | 覆盖率 |
|---|---|
| summary | ✅ 234/234 (100%) |
| background | ✅ 234/234 (100%) |
| global_events | ✅ 234/234（平均 5-8 条）|
| modern_visit | 🟡 100/234 (43%) |
| 实景图片 | ❌ 0/234 |
| 诗词关联 | 🟡 68 首已关联 |

---

## 八、版本历史

| 版本 | 日期 | 主要变更 |
|---|---|---|
| v6.0 | 2026-06-02 | 自定义地图样式 + LOGO 艺术字 + 微信适配 + 数据补全 Phase 1 |
| v5.0 | 2026-06-01 | v3→v4 数据切换 + Landing 首页 + Routes 详情页 + GitHub/Vercel 上线 |
| v4.0 | 2026-05-29 | 项目启动，120 地点骨架 |

---

## 九、重要原则

### 不做（v1.0 弹性维护期）

- ❌ 试探性新功能（推荐算法 / 用户系统 / 多语言等）
- ❌ 没有用户反馈支持的优化
- ❌ 锦上添花的视觉调整

### 永远做

- ✅ Bug 修复
- ✅ 性能优化
- ✅ 安全加固
- ✅ 用户反馈调优
- ✅ 数据补全（核心内涵）

---

**Loading in Progress** · *Cyber Loading* 🌸
