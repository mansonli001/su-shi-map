# 行吟山河 · XINGYIN SHANHE

> 苏轼一生 234 处足迹、20 条主题路线、68 篇代表作的交互式数字地图  
> *米白宣纸地图风，跟着东坡走一遍华夏山河*

🌐 **线上**: https://su-shi.starfluxes.com  
📦 **当前版本**: v6.0「行吟山河」  
🚀 **状态**: ✅ 已上线 · 弹性维护期

---

## 🔁 v1.0 冷启动快照与回滚

v1.1 stitch 视觉升级前已对 v1.0（commit `564246d`）做了三层快照保护，任何时候出问题都可秒回：

```bash
# 方案 A：回到 v1.0 tag（只读快照，推荐先 checkout 看效果）
git checkout v1.0.0

# 方案 B：切回 release/v1.0 分支（可继续在 v1.0 上 hotfix）
git checkout release/v1.0

# 方案 C：直接强制把 main 拉回 v1.0（核选项，慎用）
git checkout main && git reset --hard v1.0.0
```

> 备份位置：tag `v1.0.0` + 分支 `release/v1.0` + `app/page.v1.tsx.bak`（首页源码备份）

---

## 项目愿景

中国的山河，从来不只是地理。  
是千年诗文落地生根，是古人风骨留在人间。

行吟山河不止于苏轼——未来会陆续加入李白、杜甫、白居易等更多诗人的山河足迹。

## 数据规模

| 项 | 数量 | 说明 |
|---|---|---|
| 足迹点 | **234** | 苏轼一生踏过的真实地点 |
| 主题路线 | **20** | 从眉山少年到儋州终老 |
| 代表作 | **68** | 已关联到具体地点的诗词文 |
| 人生阶段 | **6** | 眉山·少年 / 汴京·宦游 / 黄州·东坡 / 元祐·还朝 / 惠儋·南贬 / 北归·终老 |
| 跨越省份 | **14** | 从四川到海南 |
| 时间跨度 | **64 年** | 1037–1101 |

## 核心特性

- 🗺️ **「行吟山河」自定义地图样式** — 米白宣纸底图 + 淡金路网 + POI 全关，跟普通导航地图完全不同
- 🎨 **设计稿 §2.4 八类 SVG marker** — 出生 / 求学 / 任职 / 居住 / 游览 / 友人 / 去世 / 坟墓 / 主线
- 🛣️ **20 条主题路线** — 一生总览 + 单路线模式，每条独立 stage 配色 + 手绘平滑路径 + 方向箭头
- 📱 **移动端底部抽屉** — 苹果地图风格，68vh 弹起，地图永远 32% 可见
- 🎵 **底部时间轴** — 横向可滑动六阶段，当前阶段自动居中放大
- 📝 **路线沉浸阅读页** — 每条路线含史诗叙事 / 关键事件 / 文学创作 / 地理脉络
- ✨ **行吟山河 LOGO 艺术字 v1.0** — 三档金色立体渐变填充
- 🔍 **全局模糊搜索** — fuse.js 本地搜索地点 / 诗词
- 🤝 **微信浏览器深度适配** — Open Graph 分享卡 + 11 条 iOS Safari/X5 内核补丁

## 视觉系统 v6.0

### 字体职能分工
| 用途 | 字体 |
|---|---|
| UI 主力（导航/卡片/列表）| **Noto Sans SC** 思源黑体 |
| 诗意锚点（Hero/品牌/诗句）| **LXGW WenKai** 霞鹜文楷 |
| 数字位（年份/时间）| **JetBrains Mono** |

### 主色板
| 色 | Hex | 用途 |
|---|---|---|
| 墨黑 | `#1A1008` | 主背景 / 顶栏 |
| 主金 | `#FAC775` | 高亮文字 / LOGO |
| 中金 | `#BA7517` | 链接 / 重点 |
| 米白 | `#FAF6F0` | 浅区背景 |
| 米白 2 | `#F0E9DF` | 卡片悬浮 |

### 4 类阶段色
| 类型 | 主色 | 浅色 |
|---|---|---|
| 出生 (birth) | `#085041` | `#5DCAA5` |
| 任职 (office) | `#0C447C` | `#85B7EB` |
| 贬谪 (exile) | `#712B13` | `#F0997B` |
| 游览 (tour) | `#633806` | `#C9975A` |

## 技术栈

- **框架**: Next.js 14 (App Router, TypeScript)
- **样式**: Tailwind CSS + @tailwindcss/typography
- **地图**: 高德 JSAPI 2.0 (@amap/amap-jsapi-loader) + 自定义样式 `amap://styles/5bcb375541c22ed25703103920a7d5e8`
- **状态管理**: Zustand
- **动画**: Framer Motion
- **搜索**: fuse.js
- **OG 图片**: @vercel/og
- **测试**: Puppeteer 自动化走查
- **部署**: Vercel + Cloudflare 橙云
- **域名**: starfluxes.com（阿里云万网）

## 快速开始

```bash
# 1. 克隆
git clone https://github.com/mansonli001/su-shi-map.git
cd su-shi-map

# 2. 安装依赖
pnpm install   # 或 npm install

# 3. 配置环境变量
cp .env.example .env.local
# 填入：
#   NEXT_PUBLIC_AMAP_KEY=...
#   AMAP_SECURITY_JS_CODE=...
#   AMAP_WEB_SERVICE_KEY=...

# 4. 跑起来
pnpm dev
# 打开 http://localhost:3000
```

## 脚本命令

| 命令 | 功能 |
|---|---|
| `pnpm dev` | 开发服务器 |
| `pnpm build` | 生产构建 |
| `pnpm start` | 启动生产 |
| `pnpm lint` | ESLint |
| `pnpm validate` | 校验数据 |
| `pnpm convert` | 坐标转换 WGS84 → GCJ-02 |
| `pnpm poems` | 提取苏轼诗词 |
| `pnpm walkthrough` | **自动化走查（本地）** Puppeteer 跑 5 条黄金路径 |
| `pnpm walkthrough:prod` | 自动化走查（线上 starfluxes）|

### 数据工程脚本（Python）

| 命令 | 功能 |
|---|---|
| `python3 scripts/extract-xingzhongkao.py` | 苏轼行踪考 Word → 简体 markdown 批量提取 |
| `python3 scripts/extract-poems-from-xingzhongkao.py` | 从行踪考提取诗词候选并对照白名单分级 |

## 数据来源（严格考据）

| 来源 | 用途 |
|---|---|
| **苏轼行踪考** | 25 篇繁→简 markdown，100 万字学术资源（在 `data-v4-source/行踪考-简体/`）|
| **《孔凡礼苏轼年谱》** | 当代最权威苏轼年谱 |
| **《苏轼全集校注》（中华书局）** | 文本校勘标准 |
| **《宋史·苏轼传》** | 官修正史 |
| **《东坡七集》《栾城集》** | 苏轼/苏辙诗文集原本 |
| **chinese-poetry**（CC0）| 诗词数据，苏轼总作品 3186 首 |
| **CHGIS 哈佛+复旦** | 北宋政区地理数据 |
| **高德地图 JSAPI 2.0** | GCJ-02 坐标系 |

## 架构与部署

### 路由

```
/                  首页 Landing（Hero + 一生轨迹 + 代表性足迹 + COMING SOON）
/explore           地图主页（marker + 底部时间轴 + 路线抽屉）
  ?focus=Pxxx      自动打开该 place 详情卡
  ?route=Rxx       自动激活该路线
/routes            20 条路线浏览列表
/routes/[id]       单条路线沉浸阅读页
/about             关于页（数据规模 / 字体方案 / 数据来源）
```

### 三层数据架构

```
data-v4/                          # 生产数据（Schema v4.0）
├── places-index.json             # 234 地点索引
├── poems-index.json              # 68 首诗词索引
├── routes-index.json             # 20 条路线索引
├── stages-index.json             # 6 阶段索引
├── places/*.json                 # 234 个地点详情
├── poems/*.json                  # 39 首已有全文 + 29 待补
└── routes/*.json                 # 20 条路线详情

data-v4-source/                   # 数据原料（不进生产）
├── R0X_xxx.md                    # 路线源数据
├── 行踪考-简体/                  # 25 篇 markdown，100 万字
└── 行踪考诗词候选/               # 提取脚本输出（待审核入库）

data/                             # 历史 v3 数据（保留备份）
└── legacy-v3-backup-2026-06-01/
```

### 部署链路

```
GitHub (mansonli001/su-shi-map)
    ↓ push main
Vercel 自动构建部署
    ↓
Cloudflare DNS (橙云代理)
    ↓
su-shi.starfluxes.com  (国内 + 海外稳定)
```

## 已知短板（正在补）

- 🟡 **实景图片** 0/234 — Phase 4 待启动，行踪考 Word 内嵌图片是来源
- 🟡 **modern_visit** 100/234 — 计划用高德 POI API 自动补全
- 🟡 **诗词扩展** 68 → 200+ — Phase 2 提取脚本已写，等白名单数据源升级
- 🟡 **A3 史实疑义裁决** — 外部专家任务清单进行中

## 开源协议

MIT License

## 贡献

欢迎 Issue / PR。  
联系方式：https://github.com/mansonli001

---

**Loading in Progress** · *Cyber Loading* 🌸
