# 行吟山河 v1.1 stitch 视觉升级 · 功能入口 & 文案基线（升级前快照）

> **生成时间**：2026-06-05
> **基于 commit**：`564246d`（v1.0.0 tag）
> **目的**：升级后逐项对照本基线自检——**入口 0 缺失、文案 0 改动、业务逻辑 0 偏移**。
> **配套保险**：tag `v1.0.0` + 分支 `release/v1.0` + 本文件

---

## 0. 探查关键发现（影响升级策略）

| # | 发现 | 对升级的影响 |
|---|---|---|
| ① | **首页本体在 `components/Home/HomeLanding.tsx`**，`app/page.tsx` 只是 6 行转发器 | 备份目标改为 `HomeLanding.v1.tsx.bak`，**不重写** `app/page.tsx` |
| ② | HomeLanding 文案已全是中文 + v4 真实数字（234/64/3000+/14/20/68） | 不需要改文案，只加视觉装饰类 |
| ③ | `app/routes/page.tsx` 已有 `.rb-chip / .rb-chip-act` 胶囊 chips | 不新增 chips 逻辑，仅 CSS 视觉升级 |
| ④ | `app/profile/page.tsx` 大量使用 inline style | 保留所有 inline style，外层加 stitch 装饰包裹类 |
| ⑤ | `app/explore/page.tsx` 顶栏已完整（路线/诗词/搜索/关于） | **不新增浮动搜索栏**（铁律②），只给 `.topnav-luxe` 加 glass 增强 |
| ⑥ | `BottomNav` 4 项 + inline style + active 用颜色变化 | active ::after 印章戳记必须通过新增 className + 全局 CSS 注入 |

---

## 1. 底部导航（BottomNav · 全站固定）

### 项数与跳转（4 项，**绝对禁动**）

| 序 | label | path | icon | active 态颜色 |
|---|---|---|---|---|
| 1 | 首页 | `/` | home | `#BA7517` |
| 2 | 地图 | `/explore` | map | `#BA7517` |
| 3 | 诗词 | `/poems` | book | `#BA7517` |
| 4 | 我的 | `/profile` | user | `#BA7517` |

active 判定：`pathname === path` 或 `pathname.startsWith(path + '/')`；**特例**：`/places/*` 也高亮「地图」Tab。

### 安全修改区
- ✅ 可加：朱砂红印章 `::after` 圆点（active 项 label 上方）
- ⛔ 禁动：4 项 path/label/icon、active 判定逻辑、特例规则、整体 fixed 定位与 zIndex

---

## 2. 首页（`app/page.tsx` → `components/Home/HomeLanding.tsx`）

### 路由入口（10 个 Link，**全部禁动 href**）

| 位置 | 文案 | href |
|---|---|---|
| Hero CTA 主 | 开始探索 → | `/explore` |
| Hero CTA 次 | 了解一生 | `#trajectory`（页内锚点） |
| 一生轨迹·路线入口 | 查看 20 条路线 → | `/routes` |
| 代表足迹 1 | 查看详情 → | `/explore?focus=P072`（黄州） |
| 代表足迹 2 | 查看详情 → | `/explore?focus=P024`（赤壁） |
| 代表足迹 3 | 查看详情 → | `/explore?focus=P058`（杭州） |
| 代表足迹 4 | 查看详情 → | `/explore?focus=P034`（儋州） |
| Final CTA 主 | 进入地图 → | `/explore` |
| Final CTA 次 1 | 浏览 20 条路线 | `/routes` |
| Final CTA 次 2 | 从黄州开始 | `/explore?focus=P072` |

### 关键文案（**逐字保留**）

- Hero EN：`XINGYIN SHANHE`
- Hero 主标：`行吟山河`
- Hero 副标：`追随千古诗人步履　行走华夏山河之间`
- Hero 正文 5 行：
  1. 一千年前，苏轼从眉山出发，
  2. 走过了这片土地上的两百三十四个地方。
  3. 他栖身的黄州，风骨依旧；
  4. 他疏浚的西湖，清丽如初；
  5. 他挥毫作赋的赤壁石，风华未改。
- Hero 强调：`在地图上，跟他走一遍。`
- 引言：`此心安处是吾乡` + 出处 `苏轼《定风波·南海归赠王定国侍人寓娘》`
- Footer 版权：`© 2026 · 一个慢慢做下去的项目 · 数据 v4 · 234 地点 · 68 篇代表作`

### 数字（v4 真实数据，**禁动**）

| 数字 | 含义 |
|---|---|
| 234 | 足迹点 |
| 64 | 年人生（1101 - 1037） |
| 3000+ | 苏轼总作品（chinese-poetry 3186） |
| 14 | 跨越省份 |
| 20 | 主题路线 |
| 68 | 代表作 |

### 安全修改区
- ✅ 可改：`<div className="ho-root">` 追加修饰类（如 `ho-root--stitch`）
- ✅ 可改：home.css 末尾追加新装饰类（`.ho-hero__seal` / `.ho-pgcard--stitch` 等）
- ⛔ 禁动：所有 Link 的 href、所有文案字符串、SVG `polyline` 坐标、4 张代表足迹卡的 `pid/accent/line` 字段、所有数字、`app/page.tsx` 自身

---

## 3. 探索页（`app/explore/page.tsx`）

### 顶栏入口（`topnav-luxe`，**全部禁动**）

| 入口 | 文案 | 触发 | 端 |
|---|---|---|---|
| 返回首页 | ← | 跳 `/` | 移动端 |
| 副标题 | 读苏轼 · 游神州 | 装饰，无点击 | 全端 |
| 副标章 | SU SHI · 1037–1101 / · 苏轼一生踪迹 · 数据 v4 | 装饰 | 桌面 |
| 路线 | 路线 / 📍 | 跳 `/routes` | 全端 |
| 诗词 | 诗词 / 诗 | 跳 `/poems` | 全端 |
| 搜索 | 搜索 / 🔍 | 调 `openSearch()` 弹 Search 面板 | 全端 |
| 关于 | 关于 | 跳 `/about` | 桌面 |

### 业务核心（**全部禁动**）
- `<AMap />`：地图容器，所有 marker 渲染
- `<StageTimelineBar />`：底部六阶段时间轴
- `<PlaceCard place={selectedPlace} />`：详情抽屉（90vh）
- `<Search />`：搜索面板（由 openSearch 触发）
- `<TrajectoryAnimation />`：轨迹动画
- `<LeftSidebar />`：左侧边栏（桌面）
- URL 协议：`?focus=Pxxx` / `?route=Rxx` 自动激活

### 安全修改区
- ✅ 可加：`.topnav-luxe` 增强（如 `glass-card` 类叠加、半透明深色玻璃）
- ✅ 可加：marker 涟漪动画 CSS（不动 marker 渲染逻辑）
- ⛔ 禁动：顶栏 7 个入口、URL 参数协议、AMap/StageTimelineBar/PlaceCard/Search/TrajectoryAnimation 任何 props
- ⛔ **绝不新增浮动搜索栏**（铁律②，stitch 设计稿没画的功能不主动加）

---

## 4. 路线页（`app/routes/page.tsx`）

### 入口（**禁动**）

| 入口 | 文案 | 跳转 |
|---|---|---|
| 顶栏返回 | ← 首页 | `/` |
| 顶栏 CTA | 地图 → | `/explore` |
| 路线卡 | 查看完整路线 → | `/routes/{r.id}` |
| 底部 CTA | 在地图上看完整 20 条路线 → | `/explore` |

### 已有筛选 chips（**禁动逻辑**，仅可视觉升级）

```
[全部 N] [仕途] [贬谪] [游历]
```
- state：`useState<'all' | 'office' | 'exile' | 'tour'>('all')`
- 类名：`.rb-chip` + active `.rb-chip-act`
- 类型徽章函数：`stageBadge(stageId)` — 蜕变/贬谪/仕途/终老/游历

### 数据源（**禁动**）
- `/data-v4/routes-index.json`
- `/data-v4/stages-index.json`

### 安全修改区
- ✅ 可改：`.rb-chip / .rb-chip-act` CSS 视觉升级（更胶囊化、加色块）
- ✅ 可改：`.rb-card` CSS 增强（玻璃感、引言 italic 等装饰）
- ⛔ 禁动：4 个筛选项、stageBadge 函数、路线条目数量、跳转路由格式、数据源

---

## 5. 个人中心（`app/profile/page.tsx`）

### 头部信息块（**全部禁动**）
- 头像 72×72 圆，金底白字「行」
- 标题：`行吟山河`
- 副标：`追随苏轼足迹，品读千古诗词`

### 4 项统计卡片（**全部禁动**）

| 数据字段 | label | 来源 |
|---|---|---|
| `favoritePoems.length` | 收藏诗词 | useSuShiStore |
| `checkinPlaces.length` | 打卡地点 | useSuShiStore |
| `unlockedAchievements.length` | 成就解锁 | useSuShiStore |
| `userNotes.length` | 个人笔记 | useSuShiStore |

### 打卡进度条
- `checkins / totalPlaces (XX%)` — `linear-gradient(90deg, #BA7517 0%, #FAC775 100%)`

### 3 个 Tab（**禁动顺序**）

| Tab | 内容 |
|---|---|
| 成就墙（默认） | `<SharePoster type="collection" />` + `<AchievementWall />` + 标题 `成就墙` |
| 收藏诗词 | 空态 📚 + 「去浏览」跳 `/poems`；列表态：Link → `/poems/{poemId}` |
| 我的笔记 | 空态 📝；列表态：poem/place 标签 + 时间 |

### Store hook（**单一 store**）
```ts
useSuShiStore() — favoritePoems, checkinPlaces, userNotes, places,
                   unlockedAchievements, checkAndUnlockAchievements
```
⚠️ **不存在** `usePoemFavorites / useCheckInStore / useAchievementStore`，全部走 `lib/store.ts`。

### 安全修改区
- ✅ 可加：外层 `<div>` 加 stitch 装饰类（如 `pf-stitch-bg`）
- ✅ 可加：globals.css 中给该装饰类加印章纹理 `::before`
- ⛔ 禁动：所有 inline style（保留现状，避免爆破半径过大）
- ⛔ 禁动：3 个 Tab 顺序与 label、4 个统计字段与 label、打卡进度条、AchievementWall/AchievementToast/SharePoster 组件
- ⛔ 禁动：`useSuShiStore()` 调用、`checkAndUnlockAchievements()` 副作用

---

## 6. 其他必须保留的现有功能（全站盘点）

### 路由（**全部可达**）
- `/` 首页
- `/explore` 地图
- `/poems` 诗集列表
- `/poems/[id]` 诗集详情
- `/routes` 路线列表
- `/routes/[id]` 路线详情
- `/profile` 个人中心
- `/checkin` 打卡日历
- `/checkin/[placeId]` 打卡详情
- `/about` 关于
- `/check` 检查页
- `/places/[id]` 地点详情（→ explore 高亮）

### Store 字段（**禁动**，`lib/store.ts`）
- `places / setPlaces`
- `selectedPlace / setSelectedPlace`
- `currentRoute / setCurrentRoute`
- `openSearch / closeSearch`
- `favoritePoems / addFavoritePoem / removeFavoritePoem`
- `checkinPlaces / addCheckin / removeCheckin`
- `userNotes / addNote / removeNote`
- `unlockedAchievements / checkAndUnlockAchievements`
- 持久化字段（partialize）：`favoritePoems / checkinPlaces / userNotes / unlockedAchievements`

### 关键组件（**禁删禁改 props**）
- `BottomNav`
- `LeftSidebar`
- `Search`
- `StageTimelineBar`
- `TrajectoryAnimation`
- `AMapContainer`（地图核心）
- `PlaceCard`（详情抽屉）
- `AchievementToast / AchievementWall / AchievementCardModal`
- `SharePoster`（打卡海报 / 成就海报）
- `Home/HomeLanding`

### 数据源（**禁删禁改格式**）
- `data-v4/places-index.json` + `data-v4/places/Pxxx.json`
- `data-v4/routes-index.json` + `data-v4/routes/Rxx.json`
- `data-v4/stages-index.json`
- `data-v4/poems-index.json` + `data-v4/poems/PMxx.json`

### 美食 Tab（**禁删**）
- 数据源：`data-v4/places/Pxxx.json` 中的 `food` 字段
- 渲染：`PlaceCard` 内部 Tab

---

## 7. 升级后自检 Checklist（按此对照执行）

### 入口完整性
- [ ] BottomNav 4 项可点 + 跳转正确
- [ ] 首页 10 个 Link href 与基线 100% 一致
- [ ] explore 顶栏 7 个入口 + Search 面板可弹出
- [ ] routes 顶栏 2 个入口 + 4 个 chips + 路线卡 N 张
- [ ] profile 3 个 Tab + 4 个统计 + 打卡进度条 + 成就分享按钮
- [ ] 所有 12 个路由可达

### 文案一致性（关键文案随机抽样）
- [ ] Hero `XINGYIN SHANHE` / `行吟山河` / `在地图上，跟他走一遍。`
- [ ] 引言 `此心安处是吾乡`
- [ ] BottomNav `首页 / 地图 / 诗词 / 我的`
- [ ] explore `读苏轼 · 游神州`
- [ ] routes `行旅路线`
- [ ] profile 4 个统计 label `收藏诗词 / 打卡地点 / 成就解锁 / 个人笔记`
- [ ] profile 3 个 Tab `成就墙 / 收藏诗词 / 我的笔记`

### 业务逻辑一致性
- [ ] 收藏诗词 → /profile 收藏 Tab 出现
- [ ] 地点打卡 → /profile 统计 +1 + 进度条更新
- [ ] 成就解锁 → AchievementToast 弹出
- [ ] 地图 marker 点击 → PlaceCard 弹出（90vh 高度未回退）
- [ ] explore?focus=P072 → 自动打开黄州 PlaceCard
- [ ] routes/Rxx → 路线详情页可达
- [ ] poems/PMxx → 诗集详情页可达

### 数据真实性
- [ ] 首页数字仍是 234/64/3000+/14/20/68（不被 stitch 设计稿"234/3000+/14"覆盖）
- [ ] routes 总数仍 = `routes-index.json` 实际数量

---

> **任意一项不通过 → 回滚到 v1.0.0：`git checkout main && git reset --hard v1.0.0`**
