# 苏轼地图项目变更日志

## 2026-06-04

---

### 24. BUG-NAV-002 v2 真修复 — 移动端抽屉滚动失效根因定位

**问题描述**：
6/4 上午做过 BUG-NAV-002 第一次修复（外层+内层 maxHeight 双层 calc），用户实测仍然在常州故居等长内容详情页**滑不动**，验收失败。

**真实根因（v1 没修对的原因）**：

| # | 错误点 | 后果 |
|---|--------|------|
| 1 | 抽屉外层用 `maxHeight: calc(100vh - 60 - 70 - safe)` ≈ 全屏 92vh，但 `motion.div` 在 collapsed 状态 `y: '38%'` 是相对自身高度的 transform，把卡片向下推 35vh | **collapsed 状态卡片实际可见 ≈ 57vh，但内层滚动容器仍按近全屏 maxHeight 渲染 → 浏览器判定"未溢出" → 滑不动** |
| 2 | 外层未声明 `flex flex-col`，内层手动写 maxHeight 而非 `flex-1 min-h-0` | 浏览器无法基于父容器实际高度推算可滚动空间，两层 calc 互相打架 |
| 3 | 用 `100vh` 而非 `100dvh` | iOS Safari 地址栏弹收时视口高度跳变，maxHeight 计算瞬间失准 |
| 4 | 缺 `overscroll-behavior: contain` | 滚到底部时事件穿透到 body，体感上像"滑不动" |

**v2 修复方案**：

| 修改项 | 文件 | 说明 |
|--------|------|------|
| 外层固定高度 + flex 布局 | `components/place/PlaceCard.tsx` | `height: calc(92dvh - safe-top - safe-bottom)` + `maxHeight: calc(100dvh - safe-top - safe-bottom)` 兜底 + `flex flex-col`，translateY 不再影响 layout 高度 |
| 内层让浏览器自动算 | `components/place/PlaceCard.tsx` | `flex-1 min-h-0 overflow-y-auto sheet-scroll`，删除原 maxHeight calc，浏览器自动 = 92dvh - 拖拽手柄 ≈ 88dvh |
| 100vh → 100dvh | `components/place/PlaceCard.tsx` | 动态视口单位适配移动端浏览器地址栏弹收 |
| 新增 `.sheet-scroll` utility | `app/globals.css` §12 | `-webkit-overflow-scrolling: touch` (iOS 顺滑) + `overscroll-behavior: contain` (阻止滚动穿透到 body) |

**为什么 v2 一定能修好**：
- v1 错把 `maxHeight` 当 `height` 用 → translateY 动一动，可视高度和滚动容器高度立刻脱节
- v2 用 `height` 锁死 layout 高度 → translateY 只改视觉位置，layout 高度不变 → flex-1 min-h-0 准确算出滚动空间
- 不再做"扣掉标题60+Tab70"的硬编码减法（项目暂无固定 60px 标题栏，原计算本就和实际不符）

**验证记录**：
```
✓ Compiled successfully
✓ Generating static pages (11/11)
✓ next build 11/11 静态页通过，0 TS 错误，0 ESLint 警告
✓ next dev Ready in 2.4s @ http://localhost:3000
```

**自测路径**：
1. 移动端打开 `/explore`
2. 点击常州故居（P010）/ 黄州东坡雪堂（P053）/ 任意贬谪长内容地点
3. 抽屉弹出后内容区可上下顺滑滚动到底，末尾文字完整显示
4. 切换 collapsed（38%）↔ expanded（8%）两种状态都可滚
5. iOS Safari 地址栏弹收时高度无跳动

---

### 23. BUG-FOOD-001 美食模块假数据修复 + 成就系统数据源去重

**问题描述**：
6/3 落地的美食模块存在 P0 级数据真实性事故，并伴随成就系统数据漂移风险，需要在合并到主分支前修复。

**故障根因**：

| # | 严重度 | 问题 | 后果 |
|---|--------|------|------|
| 1 | 🚨 P0 | `lib/food-search.ts` 的 `searchNearbyFood` 是 mock 实现，无论用户在哪个地点（黄州/眉山/惠州/儋州）永远返回同样的 5 家硬编码杭州餐厅（东坡酒楼/楼外楼/知味观/奎元馆/杭帮菜博物馆） | 上线后用户在儋州看到楼外楼，立刻信任崩塌 |
| 2 | 🟡 P1 | `lib/store.ts` 的 `checkAndUnlockAchievements` 内硬编码了一份完整的 6 枚成就数据，与 `lib/achievements.ts` 单一数据源完全重复 | 未来改金句/emoji/名称两边漂移 |
| 3 | 🟡 P1 | `lib/amap-loader.ts` 的 plugins 列表缺 `AMap.PlaceSearch` | PlaceSearch 调用直接 undefined |

**修复方案**：

| 修改项 | 文件 | 说明 |
|--------|------|------|
| 真接入高德 PlaceSearch | `lib/food-search.ts` | 用 `AMap.PlaceSearch` + `searchNearBy` 真调用，type=050000 餐饮服务大类，半径 2000m，返回前 20 条；映射 POI 到 `AMapPOIResult` schema 保持 PlaceCard 向后兼容 |
| 失败兜底 | `lib/food-search.ts` | SDK 加载失败 / 插件超时（5s）/ status≠complete / 异常一律返回 `[]`，UI 显示「附近暂无推荐」不阻塞苏轼特供 |
| SSR 防护 | `lib/food-search.ts` | `typeof window === 'undefined'` 直接返回 `[]`，避免误调爆炸 |
| 苏轼特供加单 Promise 缓存 | `lib/food-search.ts` | `_sushiFoodsPromise` 单例，避免切换地点时反复 fetch JSON |
| PlaceSearch 插件按需加载 | `lib/food-search.ts` | `AMap.plugin(['AMap.PlaceSearch'], cb)` 动态加载，不污染初始 SDK 体积 |
| 基础 plugins 补 PlaceSearch | `lib/amap-loader.ts` | plugins 列表追加 `AMap.PlaceSearch` 双保险 |
| 删除重复的 achievementMap | `lib/store.ts` | 6 枚成就硬编码（35 行）整体删除，改为 `import { getAchievement }` + `getAchievement(latestId)`，单一数据源即 `lib/achievements.ts` |

**修复效果**：
- ✅ 用户在任意地点点「附近推荐」拿到的是真实高德 POI（餐饮店名/距离/评分/类别）
- ✅ 高德 SDK / 插件 / API 任意环节失败一律静默兜底，不影响苏轼特供与打卡主流程
- ✅ 成就金句 / emoji / 名称只在 `lib/achievements.ts` 维护一份，store 不再持有副本
- ✅ `npx next build` 通过，0 TypeScript 错误，0 ESLint 警告

**验证记录**：
```
✓ Compiled successfully
✓ Generating static pages (11/11)
○ (Static)  / /about /checkin /explore /poems /profile /routes /_not-found
ƒ (Dynamic) /api/* /poems/[id] /routes/[id]
```

---

### 22. BUG-NAV-003 移动端 Header 图标重复与布局挤压修复

**问题描述**：
- 视觉重复冗余：路线筛选和全局搜索共用放大镜图标，用户无法区分功能
- 移动端布局挤压：窄屏环境下右侧图标被压缩变形、间距拥挤、显示裁切

**故障根因**：
- 图标复用错误：路线筛选、全局搜索共用放大镜Search图标
- 布局缺少弹性约束：Header容器未使用flex:1自适应分配空间
- 图标无最小尺寸：窄屏自动挤压变形

**修复方案**：

| 修改项 | 文件 | 说明 |
|--------|------|------|
| 图标差异化 | `app/explore/page.tsx` | 路线列表改用📍地图标记图标，搜索保留🔍放大镜 |
| 布局弹性约束 | `app/explore/page.tsx` | Header容器改为 `justify-between`，标题区域 `flex-1` |
| 图标最小尺寸 | `app/explore/page.tsx` | 所有按钮添加 `min-w-[44px] min-h-[44px]`（全局触控规范） |
| 间距统一 | `app/explore/page.tsx` | 右侧图标组使用 `gap-1 md:gap-2` |
| 移动端左侧按钮 | `app/explore/page.tsx` | 首页按钮移到左侧，避免右侧拥挤 |

**修复效果**：
- ✅ 图标语义清晰：📍路线列表 vs 🔍全局搜索，用户可快速区分
- ✅ 移动端布局稳定：按钮固定44px最小尺寸，不会被挤压变形
- ✅ 间距均匀：右侧图标组有合理间距，不紧贴
- ✅ 桌面端不变：原有布局和交互逻辑保持不变

---

### 21. BUG-NAV-002 地点详情抽屉移动端滚动修复

**问题描述**：
- PC桌面端：地点详情抽屉弹窗可正常滚动浏览
- 移动端：长内容详情抽屉高度被截断，内部无法滚动，底部内容被遮挡

**故障根因**：
- CSS布局定位错误：移动端BottomSheet缺少高度约束
- 滚动层级溢出：弹窗父容器未添加`overflow-y: auto`
- PWA安全区适配缺失：未适配`env(safe-area-inset-bottom)`底部安全边距

**修复方案**：

| 修改项 | 文件 | 说明 |
|--------|------|------|
| 外层容器高度约束 | `components/place/PlaceCard.tsx` | 设置 `maxHeight: calc(100vh - env(safe-area-inset-top) - 60px - 70px - env(safe-area-inset-bottom))` |
| 内容区独立滚动 | `components/place/PlaceCard.tsx` | 添加 `overflow-y: auto` + `WebkitOverflowScrolling: touch` |
| 拖拽手柄固定 | `components/place/PlaceCard.tsx` | 添加 `shrink-0` 防止被压缩 |

**修复效果**：
- ✅ 移动端长内容详情抽屉可正常滚动，末尾文字完整展示
- ✅ iPhone全面屏机型避开顶部刘海、底部手势条、全局Tab，无遮挡
- ✅ PC桌面端原有逻辑不变，保持正常滚动效果
- ✅ 兼容即将上线的全局底部Tab导航（预留70px高度）

---

### 20. BUG-NAV-001 全页面统一底部导航修复

**问题描述**：
- 一级页面（首页/地图/诗词/我的）显示自研水墨风格4项Tab导航
- 二级详情页（诗词详情`/poems/[id]`、地点详情）仅显示浏览器原生控件，无项目统一导航
- UI不一致、交互路径冗余、PWA体验破损

**修复方案**：

| 修改项 | 文件 | 说明 |
|--------|------|------|
| 根布局全局挂载 | `app/layout.tsx` | 添加全局底部安全边距 `pb-[calc(70px+env(safe-area-inset-bottom))]`，全局挂载 `<BottomNav />` |
| 路由高亮增强 | `components/BottomNav.tsx` | 新增 `/places/*` 路径匹配「地图」Tab高亮 |
| PWA配置检查 | `public/manifest.json` | 已配置 `"display": "standalone"` |

**修复效果**：
- ✅ 全站点统一：所有页面（含动态详情页）固定显示同款底部4项Tab导航
- ✅ 高亮规则正确：诗词列表/详情页 →「诗词」高亮；地图/地点详情 →「地图」高亮  
- ✅ PWA原生体验：隐藏浏览器原生导航控件，实现APP级沉浸式浏览
- ✅ 交互逻辑一致：详情页可一键跳转任意一级页面，无需逐级返回

---

### 19. ESLint 代码质量修复

**目标**：修复项目中的 ESLint 代码质量问题，包括未使用变量、`any` 类型、`prefer-const` 等。

**修复内容**：

| 文件 | 修复项 |
|------|--------|
| `app/api/og/route.tsx` | 删除未使用变量 `placeName`、`summary`，添加类型定义 |
| `app/api/route/route.ts` | 添加 `AMapPathStep`、`AMapPath` 接口，移除 `error: any` |
| `app/checkin/page.tsx` | 移除未使用的 `useEffect` 导入 |
| `app/explore/page.tsx` | 修复 `any` 类型，移除 `error: any` |
| `app/poems/[id]/page.tsx` | 移除未使用的 `RouteIdx` 类型和 `favoritePoems` 变量，优化 `let` → `const` |
| `app/poems/page.tsx` | 移除未使用的 `setSearchQuery` |
| `app/routes/page.tsx` | 修复类型转换问题 |
| `components/LeftSidebar.tsx` | 修复 `any` 类型 |
| `components/Search.tsx` | 修复类型转换问题 |
| `components/StageTimelineBar.tsx` | 修复 `any` 类型 |
| `components/TrajectoryAnimation.tsx` | 移除未使用的 `PlaceCore` 导入和 `STAGE_COLORS` 常量 |
| `data-v4/scripts/audit-completeness.ts` | 将 `any[]` 改为 `unknown[]` |

**验证**：`npx next build` ✓ 编译成功，无 TypeScript 错误。

---

## 2026-06-03

---

### 18. Phase 5 - 打卡/成就/美食功能开发

**目标**：实现完整的用户成就系统和美食推荐功能，提升用户互动体验。

**核心亮点**：
- 零技术债起步：清理无人调用的老打卡代码（`lib/idb.ts` + `components/Checkin.tsx`）
- 复用现有 zustand store：直接在 `addCheckin()` 中集成成就解锁判定
- Canvas 成就卡 1:1 复刻设计稿：750×1280 / 6枚成就 / 金句+出处 / 系统衬线字体降级
- 美食模块深嵌 PlaceCard：travel Tab 加3档sub-tab（全部/苏轼特供/附近推荐）
- 高德POI 1分钟同地点缓存避免重复请求

**新增文件**：
| 文件 | 说明 |
|------|------|
| `lib/uid.ts` | 匿名UUID生成器（localStorage存储） |
| `lib/achievements.ts` | 成就系统核心模块（6枚成就定义+解锁逻辑） |
| `lib/achievement-card.ts` | Canvas成就卡生成器（750×1280 PNG） |
| `lib/food-search.ts` | 美食搜索模块（AMap POI封装+1分钟缓存） |
| `data-v4/foods-sushi.json` | 苏轼特供美食数据（15种特色美食） |
| `components/AchievementWall.tsx` | 成就墙组件 |
| `components/AchievementCardModal.tsx` | 成就卡预览弹窗 |
| `components/AchievementToast.tsx` | 成就解锁Toast提示 |

**修改文件**：
| 文件 | 修改内容 |
|------|----------|
| `lib/store.ts` | 添加成就状态（unlockedAchievements、checkAndUnlockAchievements） |
| `app/profile/page.tsx` | 新增成就墙Tab、统计卡片升级、打卡进度条 |
| `components/place/PlaceCard.tsx` | Travel Tab加美食sub-tab（全部/苏轼特供/附近推荐） |

**6枚成就定义**：
| 成就ID | 名称 | 解锁条件 | 金句 |
|--------|------|----------|------|
| bronze | 苏轼青铜爱好者 | 打卡5个地点 | 人生到处知何似，应似飞鸿踏雪泥 |
| silver | 苏轼白银探索者 | 打卡20个地点 | 竹外桃花三两枝，春江水暖鸭先知 |
| gold | 苏轼黄金追寻者 | 打卡50个地点 | 明月几时有，把酒问青天 |
| exile | 贬谪三地行者 | 打卡黄州、惠州、儋州 | 一蓑烟雨任平生 |
| westlake | 西湖苏堤漫步 | 打卡杭州系列地点 | 欲把西湖比西子，淡妆浓抹总相宜 |
| full | 集大成者 | 打卡全部120个地点 | 大江东去，浪淘尽，千古风流人物 |

**苏轼特供美食（15种）**：
- 东坡肉、东坡羹、东坡饼、东坡肘子
- 西湖醋鱼、龙井虾仁、葱包桧
- 惠州梅菜扣肉、儋州粽子、儋州海鲜
- 蜜酒、荔枝、莼菜羹、蟹、河豚

**删除文件**：
- `lib/idb.ts` - 老打卡代码，无人调用
- `components/Checkin.tsx` - 老打卡组件，无人调用

---

### 0. v6.1 工程化加固（quick-win patch）

**目标**：评审报告 P0 修复一刀切，根治"数据双写漂移 + XSS 隐患 + 文案过期 + 大量事件去重 O(n²) + fetch 竞态"五个潜在线上事故源。

**变更要点**：

| # | 修复 | 原因 |
|---|---|---|
| 1 | 新增 `scripts/lib_sync.py` 单向同步工具（rsync + atomic + 排除 scripts/icons） | 13 个旧脚本各自手写 `public/data-v4` 双写代码，已踩坑过一次（#9） |
| 2 | 11 个数据脚本全部删除 `public/data-v4` 双写代码，统一末尾调 `sync_public()` | 唯一权威源是 `data-v4/`，public 只是部署副本 |
| 3 | `scripts/renumber-by-type.py` 加原子写入（写 `*.tmp` 后 `os.replace`） | 中途崩溃不再留下半新半旧无法回滚的 poems |
| 4 | `app/routes/[id]/page.tsx` 删除 2 处 `dangerouslySetInnerHTML`，改纯 React 节点解析 `**bold**` | 数据源被污染时的 XSS 隐患（违反安全 RULE 8） |
| 5 | `components/place/PlaceCard.tsx` fetch 加 `AbortController`、去掉 `?t=${Date.now()}` | 快速切换地点的请求竞态、Vercel CDN 缓存被穿透 |
| 6 | `PlaceCard.tsx` 事件去重 O(n²) 改 Map → O(n)，并切换地点时清掉旧详情 | 路由事件多时卡顿 + 切换瞬间错位 |
| 7 | `PlaceCard.tsx` 文案修正：「68 首代表作（39 首全文）」→「326 首代表作（全部含全文与赏析）」 | 与最新数据现状一致 |

**涉及文件**：
- `scripts/lib_sync.py`（新增）
- `scripts/renumber-by-type.py`（重写：原子 + 删 public 双写）
- `scripts/match-works-to-poems.py` `scripts/fix-poem-consistency.py` `scripts/add-poem-content.py` `scripts/poem_data_enhancer.py` `scripts/add-missing-poems.py` `scripts/clean-route-desc.py` `scripts/convert-markdown.py` `scripts/add-more-poem-content.py` `scripts/clean-all-markdown.py` `scripts/update-poem-ids.py`（删 public 双写 + 末尾调 sync_public）
- `app/routes/[id]/page.tsx`（XSS 加固）
- `components/place/PlaceCard.tsx`（fetch + dedup + 文案）
- `public/data-v4/`（rsync 全量重建，删除多余的 scripts/ icons/，与 data-v4 内容完全一致）

**验证**：`npx next build` ✓ 编译 11/11 静态页全部通过，无 TypeScript 错误。

---

### 9. 诗词列表页显示修复（68首→321首）

**变更内容**：修复诗词列表页只显示68首的问题，现在正确显示全部321首诗词。

**问题原因**：`public/data-v4/poems/` 目录下缺少诗词文件，只有1个文件，导致前端无法加载完整数据。

**修复方案**：将 `data-v4/poems/` 目录下的321个诗词文件同步到 `public/data-v4/poems/` 目录。

**涉及文件**：
- `/public/data-v4/poems/*.json` - 321个诗词详情文件
- `/public/data-v4/poems-index.json` - 诗词索引文件

---

### 10. 诗词全文内容补充

**变更内容**：为10首缺少全文的诗词补充 `paragraphs` 字段内容。

**涉及文件**：
- `/scripts/add-poem-content.py` - 诗词内容补充脚本
- `/data-v4/poems/W014.json` - 江城子·密州出猎
- `/data-v4/poems/W031.json` - 题西林壁
- `/data-v4/poems/W029.json` - 卜算子·黄州定慧院寓居作
- `/data-v4/poems/W011.json` - 有美堂暴雨
- `/data-v4/poems/W056.json` - 食荔枝
- `/data-v4/poems/W067.json` - 自题金山画像
- `/data-v4/poems/W046.json` - 临江仙·送钱穆父
- `/data-v4/poems/W058.json` - 纵笔三首
- `/data-v4/poems/W002.json` - 初发嘉州
- `/data-v4/poems/W036.json` - 蓬莱阁记所见

---

### 11. 作品跳转逻辑优化

**变更内容**：优化地点详情页作品卡片的交互逻辑：
- **诗词（诗、词）**：保留"展开全文"按钮，支持在卡片内查看全文；同时标题支持跳转至诗词详情页
- **文章（文、赋、策等）**：只显示跳转链接，不显示展开全文按钮

**涉及文件**：
- `/components/place/PlaceCard.tsx` - 地点卡片组件（WorkCard函数）

**详细变更**：
- 添加诗词类型判断：`['诗', '词']` 为诗词，其他为文章
- 诗词类型：显示"展开全文"按钮 + 标题跳转链接
- 文章类型：只显示"查看全文"跳转链接

---

### 12. 常州事件数据完善

**变更内容**：完善常州（苏轼终老之地）的事件数据，补充"归眠地"相关重要事件。

**涉及文件**：
- `/data-v4/places/P017.json` - 常州地点详情

**事件补充**：
- **卒于常州**：建中靖国元年（1101年）七月二十八日，苏轼在常州孙氏公馆病逝，享年六十五岁
- **买田宜兴**：元丰七年（1084年），苏轼在宜兴买田，计划归隐
- **定居常州**：建中靖国元年（1101年）六月，苏轼北归抵达常州，租屋居住

---

### 13. 路线详述Markdown格式转换

**变更内容**：将20条路线详述中的Markdown加粗格式（`**内容**`）转换为HTML `<strong>` 标签，确保前端渲染时正确显示加粗效果。

**涉及文件**：
- `/data-v4/routes/R00.json ~ R19.json` - 20条路线详情文件
- `/scripts/convert-markdown.py` - Markdown转换脚本

**详细变更**：
- 将所有 `**内容**` 转换为 `<strong>内容</strong>`
- 将所有 `*内容*` 转换为 `<em>内容</em>`
- 同步更新到 `public/data-v4/routes/` 目录

---

### 14. 诗词数据一致性检查与修复

**变更内容**：检查并修复诗词索引与详情数据的不一致问题。

**发现问题**：
- 标题不匹配：5处（如W005、W006、W009、W010）
- 年份不匹配：12处（如W007、W011、W017等）

**修复结果**：所有328首诗词数据完全一致

**涉及文件**：
- `/data-v4/poems-index.json` - 诗词索引文件
- `/scripts/check-poem-consistency.py` - 一致性检查脚本
- `/scripts/fix-poem-consistency.py` - 修复脚本

---

### 15. 作品类型编号体系重新设计

**变更内容**：为作品实现按类型编号的体系，便于数据管理和检索。

**新编号规则**：
| 类型 | 前缀 | 数量 | 示例 |
|------|------|------|------|
| 诗 | S | 180 | S001-S180 |
| 词 | C | 120 | C001-C120 |
| 文 | W | 18 | W001-W018 |
| 赋 | F | 5 | F001-F005 |
| 策 | Z | 4 | Z001-Z004 |
| 题画 | T | 1 | T001 |

**涉及文件**：
- `/data-v4/poems/*.json` - 328个诗词详情文件
- `/data-v4/poems-index.json` - 诗词索引文件
- `/data-v4/places/*.json` - 所有地点数据中的poem_id引用
- `/scripts/renumber-by-type.py` - 编号重命名脚本

**详细变更**：
- 原编号 W001-W328 → 按类型重新编号
- 更新所有地点数据中的poem_id引用
- 同步更新到 public 目录

---

### 16. 补充缺失诗词数据

**变更内容**：为7首未匹配到的诗词作品添加完整数据。

**新增诗词**：
- W322/S108：《初入庐山》
- W323/S109：《泊船瓜洲》
- W324/S162：《别子由三首》
- W325/S170：《留题仙游潭中兴寺》
- W326/S131：《定州中山怀古》
- W327/S130：《平山堂怀古》
- W328/S163：《海南日记》

**涉及文件**：
- `/data-v4/poems/W322-W328.json` - 新增诗词详情文件
- `/data-v4/poems-index.json` - 更新索引
- `/scripts/add-missing-poems.py` - 添加脚本
- `/scripts/update-poem-ids.py` - 更新地点作品引用

---

### 17. 地点作品与诗词关联优化

**变更内容**：优化地点作品与诗词数据的关联匹配，提升关联成功率。

**统计数据**：
- 作品总数：136个
- 有有效poem_id：125个（91.9%）
- 无poem_id：11个（均为文章类型，无需匹配）

**涉及文件**：
- `/data-v4/places/*.json` - 更新poem_id引用
- `/scripts/match-works-to-poems.py` - 匹配脚本

---

## 2026-06-03（原变更）

---

### 1. 诗词数据大规模补充（111首→321首）

**变更内容**：批量补充苏轼耳熟能详、名句经典的诗词数据，从111首扩展至321首，超过300+目标。

**涉及文件**：
- `/scripts/add_new_poems.py` - 第一批诗词补充脚本（88首）
- `/scripts/add_new_poems_batch2.py` - 第二批诗词补充脚本（40首）
- `/scripts/add_new_poems_batch3.py` - 第三批诗词补充脚本（57首）
- `/scripts/add_new_poems_batch4.py` - 第四批诗词补充脚本（25首）
- `/data-v4/poems-index.json` - 诗词索引文件更新
- `/data-v4/poems/W112.json ~ W321.json` - 新增210首诗词详情文件

**详细变更**：
- 第一批：添加88首新诗词（111→199首）
- 第二批：添加40首经典名篇（199→239首）
- 第三批：添加57首补充诗词（239→296首）
- 第四批：添加25首最终补充（296→321首）

**补充重点**：
- 早年及第期：《和子由渑池怀旧》《次韵子由除日元日省宿》等
- 杭州通判期：《惠崇春江晚景》《吉祥寺赏牡丹》《冬至日独游吉祥寺》等
- 密州知州期：《水龙吟·似花还似非花》《蝶恋花·花褪残红青杏小》等
- 徐州时期：《浣溪沙·徐州石潭谢雨》《永遇乐·彭城夜宿燕子楼》等
- 黄州时期：《念奴娇·大江东去》《定风波·一蓑烟雨任平生》《临江仙·小舟从此逝》等
- 庐山时期：《题西林壁》《庐山二胜》《开先漱玉亭》等
- 惠州时期：《食荔枝》《试茶》《和陶归园田居六首》等
- 儋州时期：《六月二十日夜渡海》《别海南黎民表》《在儋耳书》等
- 北归时期：《自题金山画像》《次韵法芝举旧诗》等

**名句覆盖**：
- "人生到处知何似，应似飞鸿踏雪泥"
- "竹外桃花三两枝，春江水暖鸭先知"
- "可使食无肉，不可居无竹"
- "春宵一刻值千金"
- "只恐夜深花睡去，更烧高烛照红妆"
- "一年好景君须记，最是橙黄橘绿时"
- "大江东去，浪淘尽，千古风流人物"
- "一蓑烟雨任平生"
- "小舟从此逝，江海寄余生"
- "谁道人生无再少，门前流水尚能西"
- "不识庐山真面目，只缘身在此山中"
- "日啖荔枝三百颗，不辞长作岭南人"
- "九死南荒吾不恨，兹游奇绝冠平生"
- "问汝平生功业，黄州惠州儋州"
- "人间有味是清欢"
- "此心安处是吾乡"

---

### 2. Phase 4 - 行踪考 docx 内嵌图片提取

**变更内容**：成功从26个docx文件中提取1572张图片，为地点详情页准备实景图片资源。

**涉及文件**：
- `/scripts/extract_images_from_docx.py` - 图片提取脚本
- `/data-v4-source/行踪考图片/` - 图片输出目录
- `/data-v4-source/行踪考图片/image_records.json` - 图片记录

**详细变更**：
- 从26个docx文件（封面至结论）提取图片
- 按章节组织：每章一个子目录
- 生成图片记录JSON文件，包含章节、原图名、保存路径、文件大小等信息

**统计数据**：
- 处理docx文件：26个
- 提取图片：1572张
- 失败文件：0个
- 输出目录：`/data-v4-source/行踪考图片/`

---

### 3. P0-3 modern_visit POI 批量补全

**变更内容**：使用高德地图API批量补全234个地点的现代旅游信息（地址、门票、开放时间等）。

**涉及文件**：
- `/scripts/auto-fill-poi.py` - POI批量补全脚本（优化版）
- `/data-v4/places/P001.json ~ P234.json` - 233个地点详情文件
- `/data-v4-source/amap-poi-cache.json` - POI搜索缓存

**详细变更**：
- 优化搜索策略，提高匹配成功率
- 支持多种关键词组合搜索（地名+景区/景点/公园/故居等）
- 优先匹配苏轼相关景点（含"苏轼"、"东坡"关键词）

**统计数据**：
- 总地点数：234个
- 成功补全：233个（99.6%）
- 未补全：1个（P149 三峡全程 - 路线类型无具体POI）
- 缓存条目：73条

---

### 4. P1-1 Phase 3 global_events 批量补全

**变更内容**：为地点数据批量补充历史事件（global_events），提升地点详情页的史实丰富度。

**涉及文件**：
- `/scripts/fill-global-events.py` - 事件补全脚本
- `/scripts/fill-global-events-enhanced.py` - 增强版事件补全脚本
- `/data-v4/places/*.json` - 123个地点详情文件

**详细变更**：
- 创建事件数据库，涵盖苏轼一生重要节点
- 支持模糊匹配，自动为地点添加相关历史事件
- 包含出生、教育、仕途、贬谪、文学创作等各类事件

**事件覆盖时期**：
- 眉山时期（1036-1056）：出生、启蒙、成婚、出蜀
- 凤翔时期（1061-1064）：第一任官职、凤翔签判
- 杭州时期（1071-1074, 1089-1091）：通判、知州、疏浚西湖
- 密州时期（1074-1076）：知州、超然台、中秋词
- 徐州时期（1077-1079）：抗洪、黄楼
- 黄州时期（1080-1084）：贬谪、赤壁怀古、东坡雪堂
- 惠州时期（1094-1097）：贬谪、白鹤峰新居
- 儋州时期（1097-1100）：贬谪、载酒堂、遇赦北归
- 北归时期（1100-1101）：廉州、广州、常州病逝

**统计数据**：
- 总地点数：234个
- 有global_events：123个（52.6%）
- 无global_events：111个
- 事件总数：228条

---

### 5. P1-2 OG 分享图制作

**变更内容**：更新OG分享图API以支持v4数据结构，生成精美的分享预览图。

**涉及文件**：
- `/app/api/og/route.tsx` - OG分享图API路由（v5.0）

**详细变更**：
- 重写支持v4 places-index.json数据结构
- 支持地点详情页分享（显示地点名、现代地名、诗句）
- 首页分享默认展示品牌信息
- 优化视觉设计：渐变背景、金色装饰线、诗句展示区

**分享图片内容**：
- 主标题：行吟山河 · 苏轼足迹地图
- 地点名：古地名大字展示
- 现代地名：现代地址信息
- 诗句：经典名句+作者署名
- 底部：网站域名+扫码提示

---

### 6. P1-3 PWA Icon 完整化

**变更内容**：生成完整的PWA图标集，包括标准图标和maskable图标。

**涉及文件**：
- `/scripts/generate-pwa-icons.py` - PWA图标生成脚本
- `/public/icons/pwa-192.png` - 192px标准图标
- `/public/icons/pwa-512.png` - 512px标准图标
- `/public/icons/pwa-maskable-512.png` - 512px maskable图标
- `/public/manifest.json` - PWA清单文件

**详细变更**：
- 使用Python Pillow库生成图标
- 金色渐变背景（#FAC775 → #BA7517）
- 墨黑色背景底色（#1A1008）
- 居中显示"山"字艺术字
- 圆角矩形设计

**生成图标**：
- pwa-192.png (192x192)
- pwa-512.png (512x512)
- pwa-maskable-512.png (512x512, 用于Android启动画面)

---

### 7. P2-2 用户打卡/收藏/笔记功能

**变更内容**：实现完整的用户数据功能，包括诗词收藏、地点打卡和个人笔记。

**涉及文件**：
- `/lib/store.ts` - Zustand状态管理（添加持久化用户数据）
- `/components/place/PlaceCard.tsx` - 地点卡片添加打卡按钮
- `/app/poems/[id]/page.tsx` - 诗词详情页添加收藏按钮
- `/app/checkin/page.tsx` - 打卡足迹页面
- `/app/profile/page.tsx` - 个人中心页面

**详细变更**：
- **数据层**：使用Zustand + persist中间件实现localStorage持久化
- **收藏诗词**：诗词详情页心形收藏按钮，金色激活态
- **打卡地点**：地点卡片底部打卡按钮，支持添加个人笔记
- **个人笔记**：支持为诗词和地点添加文字笔记

**数据结构**：
- `favoritePoems`: [{ poemId, title, addedAt }]
- `checkinPlaces`: [{ placeId, placeName, checkinAt, note }]
- `userNotes`: [{ id, targetId, targetType, content, createdAt, updatedAt }]

---

### 8. P2-3 底部Tab菜单（4栏）

**变更内容**：实现4栏底部导航菜单，完全按照设计稿样式实现。

**涉及文件**：
- `/components/BottomNav.tsx` - 底部导航组件（v2.0）
- `/src/app/layout.tsx` - 根布局引入底部导航

**详细变更**：
- 4栏设计：首页 / 地图 / 诗词 / 我的
- 使用Tabler Icons风格SVG图标
- 白色背景 + 浅灰色边框（#E5E7EB）
- 激活态金色（#BA7517），未激活灰色（#9CA3AF）
- 移除数字角标设计

**Tab配置**：
| 位置 | 名称 | 路由 | 图标 |
|------|------|------|------|
| 1 | 首页 | `/` | home |
| 2 | 地图 | `/explore` | map |
| 3 | 诗词 | `/poems` | book |
| 4 | 我的 | `/profile` | user |

---

## 2026-06-02 至 2026-06-03