# 贺野游中国 · CHANGELOG

所有贺野模块变更记录。标记 `[主项目影响]` 的变更可能影响苏轼模块，需额外回归验证。

---

## [0.1.0] - 2026-06-13

### 开发全流程回顾

#### 项目启动与规划

1. **需求分析**：对 `HEYE-DEV-PLAN.md` 进行全面分析，拆解 7 个开发阶段，识别 5 大风险点
2. **风险逐项决策**：
   - 风险 1（苏轼回归破坏）→ 采用路由隔离 + 耦合审计 + build 验证三重保障
   - 风险 2（数据字段不匹配）→ 调整阶段顺序，类型定义先于 JSON 生成脚本
   - 风险 3（BottomNav 改动影响苏轼）→ 采用浮动切换入口方案，避免选择页对 SEO 影响
   - 风险 4（省名不一致导致地图着色失败）→ 制定省名归一映射表
   - 风险 5（AMapContainer 耦合）→ 耦合审计发现 1 处 useSuShiStore，决定新建 HeyeMapContainer
3. **阶段顺序调整**：将阶段 0 拆分为 0-A（修补 extractor）和 0-B（JSON 生成），中间插入阶段 1（类型定义），避免字段不匹配返工

#### 阶段 0-A：修补 heye_extractor.py

- 发现原始 extractor 只有 18 字段，缺少 `region`（IP 归属地标签）和 `featured`（精选标记）
- 补充后 CSV 字段从 18 → 20 字段
- `region` 字段用于 province 一致性校验，`featured` 用于首页轮播筛选

#### 阶段 1：类型 + 数据层 + 状态

- 创建 `types/heye.ts`，定义 HeyeLocation / HeyeAchievement / HeyeCheckinPlace 等 7 个核心类型
- 创建 `lib/heye-store.ts`，Zustand persist key 设为 `he-ye-user-data`，与苏轼 `su-shi-user-data` 隔离
- 创建 `lib/heye-achievements.ts`，定义 6 个成就（初行 / 行者 / 旅人 / 跨省 / 饕客 / 全精选）
- 创建 `lib/heye-loader.ts`，客户端 fetch 静态 JSON
- **Bug 修复**：heye-store 导入 HeyeAchievement 时发现 heye-achievements 只导出数组未导出类型 → 改从 @/types/heye 导入

#### 阶段 0-B：JSON 数据生成

- 创建 `scripts/csv_to_heye_json.py`，含省名归一映射表、坐标校验、density_tier 计算
- 创建 `scripts/heye_seed.csv`，手动编写 32 条种子数据（10 省 / 8 精选 / 1 trip_tag）
- 运行脚本生成 `locations.json` / `province-stats.json` / `meta.json`

#### 阶段 2：BottomNav 浮动切换入口

- 修改 `BottomNav.tsx`：4 栏 → 5 栏，第 5 栏为行者切换入口
- 按 `usePathname().startsWith('/he-ye')` 自动切换苏轼/贺野导航集
- 苏轼导航：首页 / 足迹地图 / 诗词 / 路线 / 旅人录
- 贺野导航：首页 / 足迹地图 / 文章流 / 旅人录 / 行者切换
- **决策记录**：苏轼 Home 处理采用方案 B（浮动切换入口），不新增选择页，避免 SEO 影响；添加注释说明切换逻辑

#### 阶段 3：贺野首页 /he-ye

- 创建 `app/he-ye/layout.tsx`，独立 metadata（title / description / openGraph）
- 创建 `app/he-ye/page.tsx`，6 段布局：Hero / 精选轮播 / 统计 / 最新文章 / 关于 / CTA
- 创建 `app/he-ye/HeyeHomeClient.tsx`，精选轮播客户端组件
- 创建 `app/he-ye/heye-home.css`，暖橙配色（`--he-primary: #C4612A`）+ 宣纸质感背景
- 在 `app/globals.css` 新增贺野色板 CSS 变量

#### 阶段 4：贺野地图 /he-ye/explore

- **AMapContainer 耦合审计**：发现 1 处 `useSuShiStore` 调用，决定新建独立容器
- 创建 `components/map/HeyeMapContainer.tsx`，0 处苏轼 store 引用
- 创建 `app/he-ye/explore/page.tsx`，地图页 + 省份筛选 + 地点卡片
- **Bug 修复**：addHeyeCheckin 传递了多余的 province/city 字段 → 移除，添加 checkinType 字段

#### 阶段 5：贺野文章流 /he-ye/feed

- 创建 `app/he-ye/feed/page.tsx`
- 按年份分组展示（降序），支持省份筛选
- 打卡按钮 + 打卡状态标记

#### 阶段 6：贺野旅人录 /he-ye/profile

- 创建 `app/he-ye/profile/page.tsx`
- 成就墙（6 个成就，已达成高亮）
- 打卡记录列表
- 统计概览（打卡数 / 省份数 / 小吃数）
- **Bug 修复**：calculateHeyeAchievements 函数参数错误（需 3 个参数只传了 2 个）→ 新增 checkedIds 变量

#### 阶段 7：全站回归验证

- 运行 `npx next build` → 发现 SSR 期间 heye-loader 使用相对 URL 导致 URL 解析错误
- **修复方案迭代**：
  - 第 1 次：在 heye-loader 中区分 SSR/CSR，SSR 用 fs.readFileSync → webpack 报 `Can't resolve 'fs'`（客户端组件引入了 fs）
  - 第 2 次：改用动态 `import('fs')` → webpack 仍然解析到 fs 模块
  - 第 3 次（最终方案）：拆分为两个文件
    - `lib/heye-loader.ts` — 纯客户端，仅 fetch，无 fs 引用
    - `lib/heye-loader-server.ts` — 纯服务端，fs.readFileSync，仅被 Server Component 引用
- `next build` 零错误通过，所有路由正常生成

#### 收尾工作

- **模块隔离审计**：贺野 → 苏轼 0 处引用；苏轼 → 贺野仅 2 处共享点（BottomNav + CSS 变量）
- **外部 API 依赖审计**：前端零 LLM API 调用；`heye_extractor.py` 改为两步流程（extract → IDE LLM → merge），移除 anthropic 依赖
- 创建 `app/he-ye/docs/CHANGELOG.md` 和 `app/he-ye/docs/README.md`

---

### 新增

#### 数据层
- `types/heye.ts` — 贺野类型定义（HeyeLocation / HeyeAchievement / HeyeCheckinPlace / HeyeProvinceStatsMap / HeyeMeta / CoordinateSource / HeyeCheckinType）
- `lib/heye-loader.ts` — 客户端数据加载层（fetch 静态 JSON，零 fs 依赖）
- `lib/heye-loader-server.ts` — 服务端数据加载层（fs 直接读 JSON，仅 Server Component 使用）
- `lib/heye-store.ts` — Zustand 状态管理（persist key: `he-ye-user-data`，与苏轼 store 完全隔离）
- `lib/heye-achievements.ts` — 6 个贺野成就定义 + 计算逻辑
- `scripts/csv_to_heye_json.py` — CSV → JSON 转换脚本（含省名归一映射表、坐标校验、featured 字段）
- `scripts/heye_extractor.py` — PDF 提取脚本（零外部 API 依赖版，两步流程：extract → merge）
- `scripts/heye_seed.csv` — 种子数据（32 地点 / 10 省 / 8 精选 / 1 trip_tag）
- `public/data-heye/locations.json` — 全量地点索引（32 条）
- `public/data-heye/province-stats.json` — 省份统计（10 省，density_tier 着色档）
- `public/data-heye/meta.json` — 全局元信息

#### 页面
- `app/he-ye/layout.tsx` — 贺野独立 layout + metadata（SEO）
- `app/he-ye/page.tsx` — 贺野首页（6 段：Hero / 精选轮播 / 统计 / 最新文章 / 关于 / CTA）
- `app/he-ye/HeyeHomeClient.tsx` — 精选轮播客户端组件
- `app/he-ye/heye-home.css` — 贺野全站样式（暖橙配色 + 宣纸质感）
- `app/he-ye/explore/page.tsx` — 贺野地图页
- `app/he-ye/feed/page.tsx` — 贺野文章流（按年份分组 + 省份筛选 + 打卡）
- `app/he-ye/profile/page.tsx` — 贺野旅人录（成就墙 + 打卡记录 + 统计概览）

#### 组件
- `components/map/HeyeMapContainer.tsx` — 贺野地图容器（独立于苏轼 AMapContainer，0 处苏轼 store 引用）

#### 文档
- `app/he-ye/docs/README.md` — 模块文档（目录结构 / 架构隔离 / 数据流程 / 脚本用法 / 配色方案 / 成就系统）
- `app/he-ye/docs/CHANGELOG.md` — 本文件

### 变更 `[主项目影响]`

- `components/BottomNav.tsx` — 从 4 栏改为 5 栏（+ 行者切换入口），按 pathname 自动切换苏轼/贺野导航集
- `app/globals.css` — 新增贺野色板 CSS 变量（`--he-primary` / `--he-accent` / `--he-bg` / `--he-ink` / `--he-muted` / `--he-tag-bg`）
- `app/ink-path.css` — BottomNav grid 从 `repeat(4, 1fr)` 改为 `repeat(5, 1fr)`；新增 `.heye-bottomnav` / `.ip-bottomnav-switch` 样式

### Bug 修复记录

| 问题 | 原因 | 修复 |
|---|---|---|
| heye-store 导入 HeyeAchievement 报错 | heye-achievements 只导出数组未导出类型 | 改从 @/types/heye 导入 |
| addHeyeCheckin 传递多余字段 | HeyeCheckinPlace 无 province/city | 移除多余字段，添加 checkinType |
| calculateHeyeAchievements 参数错误 | 函数需 3 参数只传了 2 个 | 新增 checkedIds 变量 |
| SSR 期间 URL 解析错误 | heye-loader 在 SSR 用相对 URL fetch | 拆分为 heye-loader（CSR）+ heye-loader-server（SSR） |
| webpack `Can't resolve 'fs'` | 客户端组件间接引用 fs 模块 | 彻底分离：客户端 loader 零 fs 引用 |

### 隔离措施

- 贺野 store persist key 为 `he-ye-user-data`，与苏轼 `su-shi-user-data` 完全隔离
- 贺野路由域 `/he-ye/*`，不触碰苏轼任何路由
- 贺野数据目录 `public/data-heye/`，与苏轼 `public/data-v4/` 独立
- 贺野 CSS 类名前缀 `he-`，与苏轼 `ho-` / `ip-` 无冲突
- HeyeMapContainer 不引用苏轼 store / types / components
- heye_extractor.py 零外部 API 依赖（移除 anthropic，改为 IDE 内置 LLM 两步流程）

### 已知限制

- 种子数据为手动创建，非 PDF 提取产出；正式数据需运行 `heye_extractor.py` + 人工校验
- 地图省份着色（GeoJSON 叠加）尚未实现，当前仅显示标记点
- 分享卡功能尚未实现
- 图片 URL 字段均为空，使用渐变占位

---

## 变更影响评估说明

| 影响级别 | 含义 | 验证要求 |
|---|---|---|
| `[主项目影响]` | 修改了苏轼模块共享的文件 | 需回归验证苏轼功能不受影响 |
| `[贺野内部]` | 仅修改贺野模块内部文件 | 仅需验证贺野功能 |
| `[数据层]` | 修改了数据脚本或 JSON 产出 | 需重新运行脚本验证产出 |
