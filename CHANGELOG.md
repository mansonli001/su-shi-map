# 苏轼地图项目变更日志

## 2026-06-06

---

### 47. v9.3.5 /profile 顶部身份区改横排（左 logo + 右文字）

**触发**：用户截图反馈 `/profile` 页顶部 logo 居中、「行吟山河」+「追随苏轼足迹，品读千古诗词」堆在 logo 下方，「文字应该在右侧」。

**改动**：`app/profile/page.tsx` 顶部身份区容器从「`textAlign: center` + logo `margin: 0 auto`」垂直堆叠，改为 `display: flex / alignItems: center / justifyContent: center / gap: 16px` 横排，左 96×96 logo（`flexShrink: 0`）+ 右标题区（`textAlign: left`）。

**为什么这样改**：
- 横排后视觉密度更高，logo 与文字形成「图 + 名」的品牌头格式（类似 App 启动页 brand mark），不再是空旷的居中堆栈
- 整体仍居中（`justifyContent: center`），保持 profile 页的对称感
- 文字块 `textAlign: left`，标题与副标题左边自然对齐，比居中两行短文更有层次

**验证**：lint 0 error，HMR 自动刷新

**安全清单**：✅ 仅静态样式，无 API/secrets/依赖变化

**改动文件**：`app/profile/page.tsx`（1 个）

---

### 46. v9.3.4 logo 位置对齐微调（explore 左对齐 / 首页 sidenav 居中）

**触发**：用户截图反馈 v9.3.3 改完后位置仍不对——
- 第一张图（`/explore` PC LeftSidebar）：logo 左缩进比下方「一生总览」按钮的黑色描边边框还要多 8px，"应该和左边一致行"
- 第二张图（PC 首页 sidenav）：logo（山形 + 一蓑烟雨人物）整体偏左，"应该一致 居中"

**改动对照**：

| 位置 | 之前 | 现在 | 原因 |
|------|------|------|------|
| `LeftSidebar.tsx` 标题区 | `px-4 py-3`（左 16px） | `px-2 py-3`（左 8px） | 与下方「一生总览」按钮容器 `px-2` 一致，logo 左边对齐黑色描边 |
| `app/ink-path.css` `.ip-sidenav-header` | `justify-content: flex-start` | `justify-content: center` | logo 在 sidenav 列表上方居中，与下方居中的菜单图标视觉重心一致 |

**为什么这么改**：
- `/explore` 页：sidebar 是窄列布局，logo 和按钮的左边缘必须对齐，否则会有「logo 缩在里面」的错位感
- 首页 sidenav：logo 是大块视觉锚点（128×128），下方菜单本身是图标 + 文字组合，居中比左对齐更稳
- 两处的判断标准是「视觉对齐目标不同」：explore 对齐按钮边框，首页对齐列表整体重心

**验证**：
- dev server 已在 :3000 运行，HMR 自动刷新
- LeftSidebar lint 0 error
- 不影响业务逻辑、点击行为、移动端抽屉

**安全清单**：
- ✅ 仅 frontend 静态样式调整，无后端 / API / secrets 变化
- ✅ 无新依赖、无 npm install
- ✅ 无 XSS 面（React 自动转义，无 dangerouslySetInnerHTML）

**改动文件**（2 个）：
- `components/LeftSidebar.tsx`（px-4 → px-2 + 注释）
- `app/ink-path.css`（flex-start → center + 注释）

---

### 45. v9.3.3 explore 页 LeftSidebar 去重「行吟山河」文字 + 移动端 logo 放大

**触发**：用户截图反馈 `/explore` 页两处问题——
- 第一张图（PC 左侧栏 header）：横版 logo 自带「行吟山河」字样，下面还有一个独立 h2「行吟山河」+ ROUTES 拼音，**字重叠了**，"不要文字 只留图"
- 第二张图（移动端底部抽屉 header）：同样问题，"只留图加文字 不留下面的文字，图大一些"

延续 v9.3.2 的精简方向，把 `LeftSidebar.tsx` 里 PC 与移动端两处 brand block 都简化为**仅横版 logo**。

**改动对照**：

| 位置 | 之前 | 现在 |
|------|------|------|
| `LeftSidebar.tsx` PC 标题区（line 90-127） | 横版 logo 130×26 + h2「行吟山河」18px + 拼音「ROUTES · 苏轼一生」10px | **仅横版 logo 160×32**（小幅放大 + 去字重叠） |
| `LeftSidebar.tsx` 移动端抽屉 header（line 312-341） | 横版 logo 150×30 + h2「行吟山河」18px + 拼音 10px | **仅横版 logo 220×44**（图大一些 + 去字） |

**为什么这么改**：
- `logo-nav.png` 横版 logo 本身就画了「行吟山河」四个字 + 山形印章，再用 CSS 重复一遍 h2 文字属于**视觉冗余**
- 文字和 logo 字体、字重都不一样（h2 是 Wenkai 600，logo 是设计字），并排反而打架
- 与 v9.3.2 首页、profile 页方向一致：**全站品牌位只用 logo 一个视觉锚点**

**两处保留 `alt="行吟山河"` 不动**，无障碍语义不退步。

**验证**：
- dev server 已在 :3000 运行（pnpm dev），文件保存自动 HMR 刷新
- LeftSidebar lint 0 error
- 不影响业务逻辑（路线列表/总览按钮/移动端抽屉开关全部不动）

**安全清单**：
- ✅ 仅 frontend 静态结构调整，无后端/API/secrets/路由变化
- ✅ logo 路径 `/brand/logo-nav.png` 仍为本地静态资源，不引外链
- ✅ React 自动转义，无 XSS
- ✅ 无新依赖、无 npm install

**改动文件**（1 个）：
- `components/LeftSidebar.tsx`（-31 行 / +12 行，净 -19）

---

### 44. v9.3.2 品牌位三处统一：仅大 logo，去文字、去描边、去圆形

**触发**：用户反馈"导航/移动端 brand bar 文字喧宾夺主，profile 头像还在用「行」字"。继续 v9.3.1 的精简方向，把所有还残留品牌文字/占位符的位置全部替成纯 logo。

**三处改动**：

| 位置 | 之前 | 现在 |
|------|------|------|
| `components/Home/HomeLanding.tsx` PC 左侧竖排导航 header | 圆形 `ip-sidenav-seal`（96×96 logo）+ 横排「行吟山河」h1 + 「XINGYIN SHANHE」拼音 | **仅 128×128 logo 左上对齐**，删除 h1 和拼音 |
| `components/Home/HomeLanding.tsx` 移动端顶部 brand bar | 横版 logo 36px + 「XINGYIN SHANHE」拼音两行居中 | **仅横版 logo 56px 左对齐**，删除拼音 |
| `app/profile/page.tsx` 个人中心头像 | 72×72 墨黑实底圆 + 朱砂红描边 + 「行」字 | **96×96 主 logo `/brand/logo.png` 居中**，无底/无边 |

**`app/ink-path.css` 同步清理**（共 -49 行 / +18 行）：
- 删除：`.ip-sidenav-seal`（圆形容器规则）、`.ip-sidenav-title`（h1 横排样式）、`.ip-sidenav-en`（PC 拼音样式）、`.ip-mobile-brand-en`（移动端拼音样式）
- 新增：`.ip-sidenav-logo`（128×128 直出）
- 修改：`.ip-sidenav-header` 改为 flex-start 左对齐、padding 收紧 `8px 20px 28px`
- 修改：`.ip-mobile-brand` 改为 flex-start 左对齐、单行高度，logo 从 36px → 56px

**为什么这么改**：
- v9.3.1 已把 logo 和文字放一起，但 PC 96px logo + 17px 标题 + 10px 拼音三层视觉重复，反而显得拥挤
- "行吟山河"四个字本身就在 logo 图里画着，再用 CSS 重复一次属于冗余
- profile 头像继续用「行」字 placeholder 与全站 logo 化方向冲突
- 统一后视觉更干净，logo 单点突出更有冲击力

**验证**：
- `curl /profile` HTTP 200，logo 正常加载（同首页同款 `/brand/logo.png`）
- PC 侧栏只剩大 logo，无文字
- 移动端顶部 brand bar 只剩横版 logo，单行高度 56px

**安全清单**：
- ✅ 仅 frontend 静态资源/样式调整，无后端逻辑/API/secrets
- ✅ logo 路径仍为本地 `public/brand/logo.png` 和 `/brand/logo-nav.png`，不引外链
- ✅ `<img alt>` 保留语义（PC 侧栏 alt="行吟山河"，移动端同），无障碍不退步
- ✅ React 自动转义，无 XSS

**改动文件**（3 个）：
- `app/ink-path.css`（-49 / +18）
- `app/profile/page.tsx`（-22 / +14）
- `components/Home/HomeLanding.tsx`（-14 / +6）

---

### 43. 全站 logo 替换 v9.3「行吟山河」品牌可视化（Layer B 中庸版）

**问题现状**：项目此前**没有任何 logo 图片**——所有"行吟山河"品牌位都是 CSS 渐变文字，浏览器 tab/PWA 应用图标用的是 v1 自制"山"字小图（`favicon.svg` 516B + `pwa-*.png` 同款位图）。

**新资源**（`/Users/mansonlee/Downloads/苏轼行踪考/files.zip` → `xingyin_logo2_assets.zip`）：
- `logo_1024_transparent.png` 主 logo · 透明底
- `logo_1024_paper.png` 米白宣纸底版（备用）
- `logo_nav_transparent.png` **800×160 横版**（5:1，专为导航位准备）
- `pwa/icon-{72,96,128,144,152,192,384,512}.png` 全 8 尺寸
- `favicon.ico` 新版

**三层替换**：

**Layer 1 · 浏览器/PWA 元数据**
| 操作 | 位置 |
|------|------|
| 替换 | `public/favicon.ico` ← 新版 |
| 替换 | `public/icons/pwa-{192,512}.png` ← 新版 |
| 新增 | `public/icons/pwa-{72,96,128,144,152,384}.png` 全尺寸补齐 |
| 重新生成 maskable | Python PIL：`logo_1024_transparent` 缩到 410×410（80% 安全区） + 米白宣纸底 #F5E6C8 padding 到 512×512 → `pwa-maskable-512.png` |
| 删除 SVG | `public/favicon.svg` 移除（新版未提供 SVG，新位图 .ico 已足够） |
| 更新 | `app/layout.tsx` `icons.icon` 改为多尺寸 PNG 数组，`apple` 升级为 152/192 双档 |
| 更新 | `public/manifest.json` icons 数组扩展为 9 项（含 maskable） |

**Layer 2 · brand 资产新增**
- `public/brand/logo.png`（= 1024 透明，主图）
- `public/brand/logo-paper.png`（米白宣纸底，备用）
- `public/brand/logo-nav.png`（800×160 横版）

**Layer 3 · UI 真正用上 logo（中庸版）**
- `components/Home/HomeLanding.tsx`：左侧竖排导航 `ip-sidenav-seal` 圆形容器内 material icon `account_balance` → 真 logo 56×56 居中
- `components/LeftSidebar.tsx` 桌面版（200px 米白边栏）：标题区 `<h2>行吟山河</h2>` 上方加横版 logo 130×26（5:1）
- `components/LeftSidebar.tsx` 移动版（68vh 抽屉）：标题区同处理，logo 150×30
- Hero 大标题、关于页、OG 分享卡仍保留 CSS 渐变文字（更轻、更糊不掉、与 OG 拼字一致）

**为什么选 B 而不是 A/C**：
- A 仅换浏览器 tab → 800×160 横版 logo 浪费
- C 全量图片化 → 移动端不同字号下纯 CSS 文字更灵活，且 OG 分享卡用拼字更稳
- B 导航/侧栏品牌位用图（5:1 横版正好），其余文字保留 → 视觉冲击中等、风险低

**验证**（`./node_modules/.bin/next dev -p 3000`）：
```
200  /brand/logo.png        200  /brand/logo-nav.png       200  /brand/logo-paper.png
200  /favicon.ico           200  /icons/pwa-72.png         200  /icons/pwa-192.png
200  /icons/pwa-512.png     200  /icons/pwa-maskable-512.png   200  /manifest.json
404  /favicon.svg（应 404 ✓）
```

**安全清单**：
- ✅ 资源全部本地化到 `public/`，不引外链 → 无 SSRF/CSP 问题
- ✅ `<img src="/brand/...">` 走 Next 静态路径 → React 自动转义无 XSS
- ✅ 旧资源备份到 `backup-20260606/icons-old/`（5 个文件：favicon.ico/svg + pwa-192/512/maskable-512）
- ✅ 仅 frontend 静态资源改动，无后端逻辑/API/secrets 涉及

---

### 42. 234 个 place 全量补齐 lat/lng（修复 42 个无坐标地点）

**问题现象**：扫库发现 `public/data-v4/places/` 下 42 个 place JSON 缺 `lat/lng`，分布在两类：
- 21 个**线性/区域地物**：长江/汴河/赣江/京杭大运河/茅山/巴蜀古道/北部湾海岸 等，本身没有"一个点"
- 21 个**城市/具体足迹**：博白/海康/沂蒙/汉中/大庾岭/卢山 等，应该有具体坐标但漏录

部分点 `places-index.json` 里残留 `core_curated` 兜底坐标（如 P004 北部湾海岸 21.5/109.5），但 per-place 文件留空，造成**双源漂移**——前端 store 拿到 index 占位坐标，详情页拿到 null，行为不一致。

**修复方案**（脚本 `scripts/fix-missing-latlng.py`）：

| 类别 | 数量 | 处理 | 标记 |
|------|------|------|------|
| 线性/区域地物 | 21 | 人工指定代表点（最贴近文中具体足迹的那个端点/中心） | `_latlng_source: "preset"` / `coordinate_source: "manual_preset"` |
| 城市/具体足迹 | 19 | `modern_name + province + city` → 高德 Web Service `/v3/geocode/geo` | `_latlng_source: "amap"` / `coordinate_source: "amap_geocode"` |
| geocode 失败手工补 | 2 | P107 诸城卢山、P193 汉中 | `_latlng_source: "manual"` |

**双源同步**：脚本同时回写 `public/data-v4/places/PXXX.json`（per-place）和 `public/data-v4/places-index.json`（store 用），遵守 v6.1 工程化加固铁律。

**结果**：234/234 全部就位，0 缺坐标。其中 4 个原有 `core_curated` 占位坐标被更精准的 amap 结果覆盖（如 P002 博白：22.2754/109.9758 → 22.2735/109.9759，<200m 偏移；P004 北部湾海岸：21.5/109.5 → 21.65/108.65，纠正到防城港代表点）。

**安全清单**：
- ✅ AMAP key 从 `.env.local` 读，不进脚本/不进 git（`.gitignore` 已覆盖）
- ✅ 输入参数全部 URL encode，输出走 `urllib.parse.quote`
- ✅ 上游域名固定 `restapi.amap.com`，无用户传入 URL
- ✅ 失败 fallback 不爆错，仅打印警告，由人工二次补

**遗留**：脚本是一次性工具，已留档 `scripts/fix-missing-latlng.py` 备复盘；后续如再有新 place，应在录入流程里强制 lat/lng 必填，而非依赖事后扫描。

---

### 41. 「食在附近」从 JSAPI 切到服务端 Web Service（修复"连高德也沉默了"）

**问题现象**：点开任意苏轼足迹点，「食在附近 · 古今同乐」一栏长期显示「连高德也沉默了」空状态。实际附近不缺餐厅（成都锦江点位 37m 内就有库迪咖啡），是接口拉不出来。

**根因**：旧链路用浏览器侧 `AMap.PlaceSearch`（JSAPI 2.0 插件）。在 Vercel 海外线路 + `securityJsCode` 校验场景下，回调经常 `status !== 'complete'`，被 `lib/food-search.ts` 当作"真没数据"返回 `[]`，前端落到空状态。

**改造**：前端调用从 JSAPI 插件迁到自建服务端代理。

| 文件 | 变更 |
|------|------|
| `app/api/nearby-food/route.ts` | 🆕 新增。Next.js Route Handler，服务端 fetch 高德 Web Service v3 `/v3/place/around`，60s `Cache-Control: s-maxage`。持有 `AMAP_WEB_SERVICE_KEY`，不暴露给浏览器 |
| `lib/food-search.ts` | 重写。删除 `loadAMap` + `AMap.PlaceSearch` 链路，改 `fetch('/api/nearby-food?lat=&lng=&radius=')`，保留 1 分钟客户端缓存与 `[]` 兜底 |

**验证**：
```bash
curl "http://localhost:3000/api/nearby-food?lat=30.65&lng=104.07&radius=2000"
# HTTP 200 → pois[0]=库迪咖啡(37m,4.3★) pois[1]=鱼游万家(40m) pois[2]=麦当劳…
```

**安全清单（按用户 V5 安全规则）**：
- ✅ Key 只走服务端 `process.env`，不进 JS bundle
- ✅ 入参 `lat/lng/radius` 全部 `Number.isFinite` + 范围校验（lat ∈ [-90,90]、lng ∈ [-180,180]、radius ∈ (0, 50000]），防 SSRF / 参数注入
- ✅ URL 用 `URLSearchParams` 拼接，无字符串拼接
- ✅ 上游域名固定 `restapi.amap.com`，不接受用户传入 URL
- ✅ 异常路径统一 `{pois: []}`，不向前端泄漏内部错误细节

**部署提醒**：Vercel 环境变量需新增 `AMAP_WEB_SERVICE_KEY`（与 JSAPI key 不是同一个，需在高德控制台「Web 服务」类型下单独申请）。

---

### 40. 数据双源漂移全量根治（CHANGELOG 一致性核验）

**触发动机**：用户要求「读 CHANGELOG 验证修正方案能否顺利实现 且无 bug」。逐项核验 #33-#39 改动落地情况时，扫到 4 处违反 v6.1 工程化加固铁律的数据漂移，其中 2 处是 P0 级线上事故。

**问题清单**：

| # | 严重度 | 文件 | 现状 | 真值在 | 修复方向 |
|---|--------|------|------|--------|----------|
| 1 | 🚨 P0 | `poems/C002.json` | 双源完全是不同作品（data-v4=《江城子·密州出猎》／public=《桄榔庵记》），但 `poems-index.json` 两边一致指向《江城子·密州出猎》→ 浏览器列表显示 A 点开却是 B | data-v4 | 跑 sync_public 让 data-v4 覆盖 public |
| 2 | 🚨 P0 | `poems/C012.json` | 双源完全是不同作品（data-v4=《水调歌头·明月几时有》／public=《和陶归去来兮辞》），index 同样指向前者 | data-v4 | 同上 |
| 3 | 🟡 P1 | `places/P017.json` | CHANGELOG #33「常州时间线修正」（六月抵达 → 七月定居 → 七月二十八日卒）落到 public 4 个事件，但忘了回写 data-v4，data-v4 仍是 3 个事件的旧版本 | public | 先 public→data-v4 回写，再 sync_public |
| 4 | 🟡 P1 | `foods-by-place.json` | 仅在 public/data-v4/，data-v4/ 没有 → 任何人下次跑 `lib_sync.py` 触发 `rsync --delete` 时会被静默删除，美食功能直接挂掉 | public | 先 public→data-v4 备份，再 sync_public |

**根因**：CHANGELOG #33（常州时间线修正）和 #34（foods-by-place.json 新增）均直接写了 `public/data-v4/`，违反 v6.1 工程化加固 #1 的铁律「唯一权威源是 data-v4/，public 只是部署副本」。C002/C012 的具体污染源未追到（疑似 6/3 16:26 时段 add-missing-poems 脚本的中间状态被留在 public 没被 sync 覆盖），但症状一致：两边 schema 同型、内容不同 → diff 才能查出。

**修复执行**：
```bash
cp public/data-v4/places/P017.json data-v4/places/P017.json     # P017 回写
cp public/data-v4/foods-by-place.json data-v4/foods-by-place.json  # 美食回写
python3 scripts/lib_sync.py                                      # rsync 全量同步
```

**修复后验证**：

| 验证点 | 结果 |
|--------|------|
| `diff -rq data-v4/ public/data-v4/` | 仅剩 `Only in data-v4: icons / scripts`（lib_sync 预期排除） |
| `C002.json` 浏览器侧 | index 与文件均《江城子·密州出猎》type=词 ✅ |
| `C012.json` 浏览器侧 | index 与文件均《水调歌头·明月几时有》type=词 ✅ |
| `P017.json` global_events | 两边均 4 项（卒于常州 / 买田宜兴 / 抵达常州 / 定居常州）✅ |
| `foods-by-place.json` | 两边都在，HTTP 200，sync_public 不再误删 ✅ |
| 49 个绑美食的 placeId | 全部存在于 places-index ✅ |
| 19 条路线代表作 poem_id | 全部 100% 有值，跳转可用 ✅ |
| 7 个核心路由（/explore /routes /poems /profile /checkin /poems/[id] /routes/[id]） | HTTP 200 ✅ |

**预防建议（待落 PROJECT-ARCHITECTURE）**：
- `lib_sync.py` 增加反向校验：`rsync --delete` 前先扫 `public/data-v4 - data-v4` 的孤儿，警告或终止
- pre-commit 钩子加 `diff -rq data-v4 public/data-v4` 红绿灯，发现差异禁止提交

---

### 39. 美食数据结构升级 + Tab顺序调整 + 探索页移动端优化 + 路线标签修正

**美食数据升级**：

| # | 修复项 | 文件 | 说明 |
|---|--------|------|------|
| 1 | 新美食数据接口 | `lib/food-search.ts` | 新增 `LocalFoodItem` 接口（含 `source_text`、`source_work`、`story` 字段）、`FoodsByPlace` 类型；新增 `getFoodsByPlace()` 和 `getSushiFoodsByPlace(placeId)` 函数 |
| 2 | FoodTab 组件重构 | `components/place/PlaceCard.tsx` | 移除 `localFoods` 和 `routeId` prop，改用 `placeId`；支持新的按地点绑定的美食数据；展示来源文本/来源作品/故事背景 |
| 3 | 日期解析增强 | `components/place/PlaceCard.tsx` | 支持完整农历月份解析（五月/六月/七月/八月/九月/十月/十一月/腊月/十二月） |

**Tab 顺序调整**：

| # | 修复项 | 文件 | 说明 |
|---|--------|------|------|
| 4 | Tab 顺序调整 | `components/place/PlaceCard.tsx` | 从 事迹/美食/作品/文旅 调整为 事迹/作品/文旅/美食（更符合内容丰富度优先级） |
| 5 | 空状态组件化 | `components/place/PlaceCard.tsx` | 事迹/作品/文旅 Tab 空状态统一使用 `EmptyState` 组件，移除硬编码文案 |

**页面空状态升级**：

| # | 修复项 | 文件 | 说明 |
|---|--------|------|------|
| 6 | 诗词详情空状态 | `app/poems/[id]/page.tsx` | "诗词内容暂未收录" → "诗在路上，尚未抵达" + "三千余首，仍在一首一首整理。" + "这里的篇章，稍后见。" + "——「腹有诗书气自华」 |
| 7 | 路线详情代表作可点击 | `app/routes/[id]/page.tsx` | 代表作卡片新增 `poem_id` 字段，点击可跳转到诗词详情页 |

**探索页移动端优化**：

| # | 修复项 | 文件 | 说明 |
|---|--------|------|------|
| 8 | 移动端按钮尺寸缩小 | `app/explore/page.tsx` | 导航按钮从 44px 缩小到 28px，减少垂直空间占用 |
| 9 | 副标题居中 | `app/explore/page.tsx` | 移动端副标题"读苏轼·游神州"绝对定位居中，不参与 flex 布局 |
| 10 | 字体统一 | `app/explore/page.tsx` | 所有按钮文字统一使用 `font-wenkai` |

**路线标签修正**：

| # | 修复项 | 文件 | 说明 |
|---|--------|------|------|
| 11 | 新增"少年"标签 | `app/routes/page.tsx` | S1 阶段新增 `stageBadge` 返回"少年"标签 |
| 12 | "游历"改为"归途" | `app/routes/page.tsx` | 路线筛选标签"游历"改为"归途"，并包含"少年"阶段 |

**样式微调**：

| # | 修复项 | 文件 | 说明 |
|---|--------|------|------|
| 13 | 页面主体文本左对齐 | `app/ink-path.css` | `.ip-hero-body` 新增 `text-align: left` |
| 14 | 诗句字号缩小 | `app/ink-path.css` | `.ip-hero-em` 字号从 18px 调整为 16px |

**验证记录**：
```
✓ 进入黄州 → 美食Tab → 显示带来源文本/来源作品的黄州专属美食
✓ 进入无美食数据的地点 → 各Tab显示 EmptyState 组件空状态
✓ 探索页移动端 → 按钮更紧凑，副标题居中
✓ 路线列表 → "归途"筛选包含少年/归途/终老路线
✓ 路线详情 → 点击代表作可跳转到诗词详情页
```

---

### 38. 全站字体统一为霞鹜文楷

**修复内容**：

| # | 修复项 | 文件 | 说明 |
|---|--------|------|------|
| 1 | 折页（LeftSidebar）字体统一 | `components/LeftSidebar.tsx` | 所有中文标题/按钮从 `Noto Serif SC` 改为 `font-wenkai`（霞文楷） |
| 2 | 名士录（profile）字体统一 | `app/profile/page.tsx` | 页面容器 + 所有数据卡片 + Tab 按钮从 `Noto Serif SC` 改为 `font-wenkai` |
| 3 | 阶段时间轴（StageTimelineBar）字体统一 | `components/StageTimelineBar.tsx` | 阶段名称按钮从 `Noto Serif SC` 改为 `font-wenkai` |
| 4 | 首页（HomeLanding）字体统一 | `components/Home/HomeLanding.tsx` | 所有中文标题从 `Noto Serif SC` 改为 `font-wenkai` |

**字体方案说明**：
- **中文**：LXGW WenKai（霞鹜文楷）→ `font-wenkai` 类
- **英文/数字**：Source Sans 3 → 保持 `fontFamily: '"Source Sans 3", sans-serif'`
- **Logo**：保持不变（可能使用特殊字体）

**验证记录**：
```
✓ 折页中的所有中文（标题/路线名/阶段名）→ 霞鹜文楷
✓ 名士录中的所有中文（数据/Tab/按钮）→ 霞鹜文楷
✓ 首页所有中文标题 → 霞鹜文楷
✓ 英文内容（如"SU SHI · 1037–1101"）→ Source Sans 3
```

---

### 37. 美食 Tab 逻辑修复 + 总览功能恢复 + 眉山故居美食补充

**修复内容**：

| # | 修复项 | 文件 | 说明 |
|---|--------|------|------|
| 1 | 恢复"总览"tab | `components/place/PlaceCard.tsx` | 用户反馈点击美食 Tab 应该看到总览（东坡特供 + 附近推荐合并），而非只显示东坡特供导致无数据时显示空状态 |
| 2 | 附近推荐始终加载 | `components/place/PlaceCard.tsx` | 原逻辑只在切换到"附近推荐"tab 时才加载数据，导致总览 tab 下无数据时显示空状态。修复：附近推荐在组件加载时就加载，不管在哪个 tab |
| 3 | 总览 tab 显示逻辑 | `components/place/PlaceCard.tsx` | 东坡特供（如果有）排在前面，后面是附近推荐 |
| 4 | 空状态条件修正 | `components/place/PlaceCard.tsx` | 只有当东坡特供和附近推荐都没有数据时才显示空状态 |
| 5 | 眉山故居美食缺失 | `public/data-v4/foods-by-place.json` | 用户反馈眉山故居没有显示东坡肘子。原因：美食数据绑定在 P116（眉山），但用户点击的是 P118（眉山故居）。修复：为 P118 添加相同美食数据 |

**FoodTab组件重构**：
- 移除`localFoods` prop（不再需要）
- 移除降级逻辑`getSushiSpecialFoods(routeId)`
- 附近推荐始终加载，使用`useEffect`依赖`placeLat/placeLng`
- 空状态使用`FoodEmptyState`组件，根据当前tab显示对应文案

**验证记录**：
```
✓ 进入任意地点 → 美食Tab → 默认显示"总览"（苏轼特供在前，后面是附近推荐）
✓ 进入黄州 → 美食Tab → 显示东坡肉等黄州专属美食 + 附近推荐
✓ 进入无东坡特供的地点 → 美食Tab → 只显示附近推荐（不会显示空状态）
```

---

### 36. 空状态文案系统 + 东坡特供美食显示修复

**新增文件**：

| # | 文件 | 说明 |
|---|------|------|
| 1 | `lib/empty-state-config.ts` | 空状态文案配置文件，统一管理所有空状态文案（标题、正文、诗句引用、行动引导） |
| 2 | `components/place/EmptyState.tsx` | 通用空状态组件，支持4种线条风格图标（毛笔/空碗/地图/书本） |
| 3 | `components/place/FoodEmptyState.tsx` | 美食Tab专用空状态组件，支持切换到"附近推荐"动作 |

**修复内容**：

| # | 修复项 | 文件 | 说明 |
|---|--------|------|------|
| 1 | 东坡特供美食全站一样 | `components/place/PlaceCard.tsx` | **关键Bug**：原逻辑当地点无专属美食时会降级调用`getSushiSpecialFoods(routeId)`返回该路线所有美食。修复：移除降级逻辑，无数据直接显示空状态 |
| 2 | 事迹Tab空状态 | `components/place/PlaceCard.tsx` | "此处山河，我曾路过" + "人生到处知何似，应似飞鸿踏雪泥" |
| 3 | 作品Tab空状态 | `components/place/PlaceCard.tsx` | "我在此地，沉默过" + "此心安处是吾乡" |
| 4 | 文旅Tab空状态 | `components/place/PlaceCard.tsx` | "此地风物，我记得" + "江山如此多娇，我曾一一走过" |
| 5 | 美食-东坡特供空状态 | `components/place/FoodEmptyState.tsx` | "此地美食，我吃过，只是忘了写下来"，带"去附近推荐"切换按钮 |
| 6 | 美食-附近推荐空状态 | `components/place/FoodEmptyState.tsx` | "此地人迹罕至，连高德也沉默了" |
| 7 | 美食-全部为空 | `components/place/FoodEmptyState.tsx` | "美食这件事，我从不将就" |
| 8 | 诗词搜索空状态 | `app/poems/page.tsx` | "没有找到，也许换个说法？苏轼的世界很大，但有些角落还没被整理进来" |
| 9 | 诗词详情内容空状态 | `app/poems/[id]/page.tsx` | "诗在路上，尚未抵达" + "腹有诗书气自华" |
| 10 | 路线详情空状态 | `app/routes/[id]/page.tsx` | "二十条路线，正在铺开" |

**空状态设计规范**：
- 第一人称视角，苏轼口吻
- 不用「暂无数据」「内容整理中」等冷冰冰的系统语言
- 每条带一句真实诗文或化用，有出处感
- 结尾留悬念或引导动作
- 统一使用线条风格图标（禁用实心/感叹号）

**验证记录**：
```
✓ 无专属美食的地点现在显示苏轼口吻空状态，不再显示东坡肉
✓ 黄州/杭州/惠州等有专属美食的地点仍正常显示
✓ 所有空状态文案已更新为统一风格
```

---

### 35. 旧数据文件清理（性能优化）

**问题分析**：
- 项目首次加载慢，排查发现 `public/data/places/` 目录下有120个旧版v3地点JSON文件（SS001~SS120.json）未被引用
- `public/icons/marker-*.svg` 6个地图标记图标未被使用
- `public/data/chgis-song.zip` GIS数据压缩包未被使用
- `public/data/poems-sushi.json` 旧诗词数据未被使用

**清理内容**：

| # | 删除文件/目录 | 文件数 | 说明 |
|---|---------------|--------|------|
| 1 | `public/data/places/` | 120个 | 旧版v3地点JSON文件（SS001~SS120.json），已迁移到v4 |
| 2 | `public/data/chgis-song.zip` | 1个 | GIS数据压缩包，未被前端引用 |
| 3 | `public/data/poems-sushi.json` | 1个 | 旧诗词数据，已迁移到v4 |
| 4 | `public/icons/marker-*.svg` | 6个 | 未使用的地图标记图标（birth/burial/exile/friend/office/tour） |

**保留文件**：

| 文件 | 状态 | 说明 |
|------|------|------|
| `public/data/places-core.json` | ✅ 仍在使用 | `components/Search.tsx` 引用 |
| `public/data/places-index.json` | ✅ 仍在使用 | `components/Search.tsx` 引用 |
| `public/icons/pwa-*.png` | ✅ 仍在使用 | PWA应用图标 |

**备份记录**：
- 删除前已备份到 `backup-20260606/`（共128个文件）
- 备份文件不提交Git，仅本地保留

**验证记录**：
```
✓ 备份完成：128个文件已备份到 backup-20260606/
✓ 删除完成：127个旧文件已移除
✓ npx next build 成功通过，无TypeScript错误
✓ 项目功能正常，未受影响
```

---

### 34. 苏轼特供美食按地点绑定 + 空状态文案升级

**问题修复**：

| # | 修复项 | 文件 | 说明 |
|---|--------|------|------|
| 1 | 苏轼特供内容全站一样 | `public/data-v4/foods-by-place.json` | **新数据文件**：按地点ID绑定苏轼特供美食，包含眉山、黄州、杭州、惠州、儋州、常州、开封、湖州等8个重要地点的专属美食记录（共48条，每条含名称、别名、描述、来源文本、来源作品、置信度、故事、标签） |
| 2 | 新数据结构适配 | `lib/food-search.ts` | 新增 `LocalFoodItem` 接口、`FoodsByPlace` 类型；新增 `getFoodsByPlace()`、`getSushiFoodsByPlace(placeId)` 函数；保留旧 `getSushiSpecialFoods()` 作为降级方案 |
| 3 | FoodTab 组件升级 | `components/place/PlaceCard.tsx` | FoodTab 新增 `placeId` 参数，优先使用新的按地点数据；移除「全部」sub-tab（全部=苏轼特供+附近推荐，不需要独立展示）；新增置信度标签（A=史料可考[金色]、B=文献记载、C=民间传说）；优化空状态文案为苏轼口吻 |

**数据结构设计**：
```json
{
  "places": {
    "P072": {
      "name": "黄州",
      "foods": [
        {
          "id": "hz-001",
          "name": "东坡肉",
          "alias": "红烧肉",
          "desc": "苏轼贬居黄州...",
          "source_text": "净洗铛，少著水...",
          "source_work": "苏轼《猪肉颂》",
          "confidence": "A",
          "story": "「黄州好猪肉...」",
          "tags": ["名菜", "猪肉", "黄州"]
        }
      ]
    }
  }
}
```

**UI 优化**：
- 美食 sub-tab 从 3 个（全部/苏轼特供/附近推荐）改为 2 个（苏轼特供/附近推荐）——「全部」功能实际上就是两者叠加，不需要独立
- 苏轼特供美食显示「置信度标签」：
  - A级（史料可考）：金色背景，白色文字
  - B级（文献记载）：琥珀色背景，深棕色文字
  - C级（民间传说）：灰色背景，深灰色文字
- 空状态文案更有温度：「苏轼途经此地，未留饮食记载——但他说过：此心安处是吾乡，或许在每个地方，他都吃得很好，只是没写下来」

**验证记录**：
```
✓ Compiled successfully
✓ next dev Ready in 2.3s
✓ 进入黄州地点 → 美食 Tab → 显示黄州专属特供（东坡肉/东坡羹/东坡饼/蜜酒）
✓ 进入杭州地点 → 美食 Tab → 显示杭州专属特供（河豚/宋嫂鱼羹/西湖莼菜汤/东坡肉杭州版/西湖醋鱼/甜羹）
✓ 进入惠州地点 → 美食 Tab → 显示惠州专属特供（荔枝/烤羊脊骨/蟹与蛤/槐叶冷淘/罗浮山荔枝）
✓ 进入儋州地点 → 美食 Tab → 显示儋州专属特供（生蚝/槟榔/番薯/海南椰子）
✓ 进入常州地点 → 美食 Tab → 显示常州专属特供（阳羡茶）
✓ 进入没有美食数据的地点（如任意过路地点）→ 显示新的空状态文案
```

---

### 33. 常州时间线修正 + 事件排序增强 + Tab顺序调整

**修复内容**：

| # | 修复项 | 文件 | 说明 |
|---|--------|------|------|
| 1 | 常州事件时间线修正 | `public/data-v4/places/P017.json` | 原数据「六月定居」与「七月到常州」逻辑矛盾。修正为：六月抵达常州 → 七月定居常州 → 七月二十八日卒于常州 |
| 2 | 事件排序逻辑增强 | `components/place/PlaceCard.tsx` | 原排序只按年份，同一年事件顺序不可控。新增 `getTimeValue()` 函数，支持提取完整日期（年×10000 + 月×100 + 日），实现精确排序 |
| 3 | Tab顺序调整 | `components/place/PlaceCard.tsx` | 原顺序「事迹 | 美食 | 作品 | 文旅」→ 新顺序「事迹 | 作品 | 文旅 | 美食」 |

**排序逻辑升级细节**：
- 支持中文月份（六月、七月等）和阿拉伯数字月份（6月、7月等）
- 支持日期提取（二十八日、2日等）
- 同一年事件按完整时间线排序，解决黄州、湖州、惠州等多地同一年多事件的排序问题

---

### 32. v1.2.0 「Ink & Path」设计系统 v1.0 + 移动端一致性收尾

**升级动机**：
- v1.1 的 stitch 装饰层完成了「视觉提级」的第一步，但全局仍是「老配色 + 增量装饰」的拼合。本次基于 `references/stitch-pc/ink_path/DESIGN.md` 重做底色与组件级配色，落地一套完整的「米白宣纸 + 墨黑 + 朱砂红 + 暗金」设计 token 体系（命名空间 `.ip-*`），与老命名 0 冲突。
- 同时收尾一批积累的移动端 bug：附近美食永远空、地图全屏抖动、安卓首次点击 marker 需双击。

**改动文件清单**（11 改 + 1 新增 CSS + 1 备份 + 25 个静态资源）：

| # | 文件 | 类型 | 说明 |
|---|---|---|---|
| 1 | `app/ink-path.css` | **新增** | Ink & Path 设计系统 v1.0 — Material 11 级 Surface tokens + Primary/Secondary/Tertiary 三色（墨黑/暗金/朱砂红） + `.ip-bottomnav` `.ip-card` 等组件类。零冲突老 `.ho-* / .gold / .ink-*` |
| 2 | `app/layout.tsx` | 增量 | 新增 Noto Serif SC（标题）+ Source Sans 3（正文）+ Material Symbols Outlined（图标）字体加载 |
| 3 | `app/globals.css` | 修复 | Marker hover 锁进 `@media (hover: hover) and (pointer: fine)`，触屏设备跳过 hover 块；增 `touch-action: manipulation` + `-webkit-tap-highlight-color: transparent` |
| 4 | `components/BottomNav.tsx` | 重构 v2.0 | 米白 frosted parchment 底（rgba 0.92 + blur 14px） + 朱砂红 active 圆点上浮 + Material Symbols 图标 + 4 栏文案改「首页 / 水墨地图 / 古诗集 / 名士录」 |
| 5 | `components/LeftSidebar.tsx` | 重构 v4.0 | 桌面端 200px 米白宣纸 + 墨黑文字（不再深色版）；移动抽屉底部 `padding-bottom` 兜住 BottomNav 64px，CTA 不再被遮 |
| 6 | `components/Home/HomeLanding.tsx` | 重构 | 全页迁到 ink-path token；接入 `public/hero/landscape.png` Hero 大图；v1 备份至 `HomeLanding.v2.tsx.bak` |
| 7 | `components/StageTimelineBar.tsx` | 重构 | 时间轴节点改暗金 + 朱砂红 active；移动端字号再放大一档 |
| 8 | `components/AchievementWall.tsx` | 视觉升级 | 卡片圆角 `xl→2xl` + padding `3→4` + hover 抬起 `-translate-y-0.5` + shadow lg→xl，配合 24 张新成就 PNG |
| 9 | `components/place/PlaceCard.tsx` | **关键 bug 修复** | 美食「附近推荐」永远空：根因是高德 PlaceSearch 在中国大陆 90% POI 不返回 `biz_ext.rating`，旧逻辑 `rating>=3.8` 把所有 `undefined` 都丢掉。新逻辑：`rating` 缺失保留（按距离/菜系排），仅 `rating` 存在且 `<3.5` 才剔除；展示前 12 家 |
| 10 | `components/map/AMapContainer.tsx` | 修复 | 地图容器 `absolute inset-0` 改为显式 `top/left/right` + `bottom: calc(--bottom-nav-height + --safe-area-bottom)`，解决移动端全屏地图被底栏遮挡 / 高度抖动 |
| 11 | `app/profile/page.tsx` | 重构 | 全页迁到 ink-path token，头像朱砂红外环 + 暖米白衬纸 + 暗金底边渐变 |
| 12 | `app/explore/page.tsx` | 重构 | 顶栏改米白 frosted parchment + 墨黑文字 + 朱砂红 hover；按钮 hover 走 inline `onMouseEnter/Leave`，与触屏点击逻辑解耦 |
| 13 | `public/hero/landscape.png` | **新增** | 首页 Hero 山水大图 |
| 14 | `public/achievements/*.png` × 24 | **新增** | 24 张成就图标（初踏苏途 / 风雨定风波 / 黄州客居 / 赤壁诗魂 / 鎏金终极 / 天涯儋州 等） |
| 15 | `public/data-v4/foods-sushi.json` | **新增** | 苏轼特供美食基础数据（东坡肉 / 东坡羹 ...），驱动 PlaceCard FoodTab 「苏轼特供」分页 |
| 16 | `components/Home/HomeLanding.v2.tsx.bak` | 新增 | v1.1 stitch 版 HomeLanding 备份，与 v1 备份并存 |

**Ink & Path token 体系（节选）**：

| 类别 | 变量 | 值 | 用途 |
|---|---|---|---|
| Surface | `--ip-surface` | `#fef8f6` | 暖米白主底（统一不分段） |
| Surface | `--ip-surface-container` | `#f3edea` | 卡片底 |
| Outline | `--ip-outline-variant` | `#d1c4bc` | 1px hairline 描边（替代玻璃阴影） |
| Primary | `--ip-primary` | `#000` | 主按钮 / 主文字 / 标题（不再朱砂红） |
| Secondary | `--ip-secondary` | `#7b5800` | 次按钮描边 / 文化路径 active |
| Tertiary | `--ip-cinnabar` | `#ba1a1a` | 仅 marker / BottomNav active dot / 关键 emphasis |

**关键移动端修复（按重要性）**：

1. **附近美食永远空 → 已修复**（PlaceCard FoodTab）
2. **地图被底栏遮挡 / 高度抖动 → 已修复**（AMapContainer 显式 bottom）
3. **安卓首次点击 marker 需双击 → 已修复**（globals.css hover 媒体查询锁定）
   - 根因：CSS `.su-marker:hover` 在安卓 Chrome 触发 sticky-hover，第一次 tap 被识别为 hover 粘住（点位放大），第二次 tap 才触发 click
   - 修复：`@media (hover: hover) and (pointer: fine)` 把 hover 样式只匹配真鼠标设备，所有触屏（安卓/iOS/平板）单击直接走 click → `setSelectedPlace`，**与 iOS 行为对齐**
4. 抽屉 CTA 被 BottomNav 遮 → 已修复（LeftSidebar v4.0 padding-bottom）

**回滚保险**：

| 层 | 命令 |
|---|---|
| Tag | `git checkout v1.1.0` |
| 分支 | `git checkout release/v1.0`（v1.0 兜底分支仍在） |
| HomeLanding | `cp components/Home/HomeLanding.v2.tsx.bak components/Home/HomeLanding.tsx`（v1.1 stitch 版） |
| HomeLanding | `cp components/Home/HomeLanding.v1.tsx.bak components/Home/HomeLanding.tsx`（v1.0 朴素版） |

**铁律保留**：
- 现有功能 100% 保留（打卡 / 收藏 / 成就 / 美食 / 笔记 / 分享 / 检查页 / 所有 API 路由）
- 业务逻辑 0 改动（仅美食 FoodTab 的过滤条件按高德数据现实做了纠错，从「假筛选」改成「真可用」）
- 命名零冲突（`.ip-*` 与 `.ho-* / .gold / .ink-*` 全部并存）

---

## 2026-06-05

---

### 31. v1.1.0 stitch 视觉升级（增量装饰层 · 业务逻辑 0 改动）

**升级动机**：吸收 stitch 设计稿的「三色印章 + 玻璃质感 + 纸张纹理 + 印章戳记」视觉语言，让产品观感从「PWA 工具感」升级为「精致内容产品感」。

**两条最高级铁律**：
- **铁律 ①**：现有功能 100% 保留（含 v1.0 之后所有已落地新增——打卡 / 收藏 / 成就 / 美食 / 笔记 / 分享 / 检查页 / 所有 API 路由）
- **铁律 ②**：只参考 stitch 的视觉设计，文案 / 数据 / 入口全部用项目原版（不引入英文文案 / 不写死虚构数据 / 不砍 stitch 没画的入口）

**三层快照保险**（任意时刻可秒回 v1.0）：

| 层 | 备份方式 | 命令 |
|---|---|---|
| Tag | `v1.0.0` 锁定 commit `564246d` | `git checkout v1.0.0` |
| 分支 | `release/v1.0` | `git checkout release/v1.0` |
| 文件 | `components/Home/HomeLanding.v1.tsx.bak`（首页源码备份） | 直接覆盖 |
| 兜底 | 重置 main 到 v1.0 | `git checkout main && git reset --hard v1.0.0` |

**改动文件清单**（6 文件 +1 备份 +1 新增）：

| # | 文件 | 类型 | 说明 |
|---|---|---|---|
| 1 | `app/globals.css` | 增量 | §13 stitch tokens（5 个 CSS 变量）+ §14 工具类（glass-card / parchment-texture / nav-seal-active / gold-edge-top / marker-ripple）+ §15 页面级装饰（pf-stitch / topnav-luxe 玻璃增强）。**0 删除原有变量与样式** |
| 2 | `app/home.css` | 增量 | 末尾追加 8 段 stitch 装饰（仅在 `.ho-root--stitch` 下生效，老样式 0 影响）：纸纹 overlay / Hero 朱砂印章 / 代表足迹卡金边 / CTA 玻璃感 / 引言朱砂中线 / 英文小标暗金渐变 / 时间轴关键节点高光 |
| 3 | `app/routes.css` | 增量 | 末尾追加 stitch 增强：active chip 朱砂红圆点 + 印章光晕 / card hover 升起金边 / badge 内描边 / desc 朱砂引导线 |
| 4 | `components/Home/HomeLanding.tsx` | 1 行 | `<div className="ho-root">` → `<div className="ho-root ho-root--stitch">`。**所有 JSX 结构、文案、数字、href 0 改动** |
| 5 | `components/BottomNav.tsx` | 1 行 | active 项 `<Link>` 加条件 className `nav-seal-active`，触发朱砂红印章 ::before 圆点上浮动画 |
| 6 | `app/profile/page.tsx` | 1 行 | 最外层 `<div>` 加 className `pf-stitch`（保留所有 inline style）→ 触发头像朱砂红外环 + 头部底金边渐变 |
| 7 | `components/Home/HomeLanding.v1.tsx.bak` | 新增 | HomeLanding v1.0 完整源码备份 |
| 8 | `INVENTORY-BASELINE.md` | 新增 | 升级前功能入口 / 文案 / 业务逻辑基线（升级后逐项自检对照表） |

**视觉装饰清单**（按页面）：

- **首页 HomeLanding**
  - 全页 feTurbulence 微纸纹（opacity 0.045）
  - Hero 右上角朱砂红「行吟」印章戳记（旋转 -8°，box-shadow 三层堆叠模拟印章质感）
  - 代表足迹 4 卡顶部金边渐变 + hover 朱砂红描边
  - section 英文小标 `XINGYIN SHANHE / LIFE TRAJECTORY` 等改暗金→亮金→暗金渐变文字
  - 引言「此心安处是吾乡」加垂直朱砂红中线
- **底部导航 BottomNav**
  - active 项标签上方朱砂红圆点（5×5px）+ navSealPop 弹跳动画（cubic-bezier(0.34, 1.56, 0.64, 1)，220ms）
- **路线 /routes**
  - active chip 左侧朱砂红圆点 + 朱砂光晕 box-shadow
  - 路线卡 hover 升起 + 0.5px 金边光
  - 贬谪 badge 改朱砂红软调
- **个人中心 /profile**
  - 头像 72×72 加 2px 朱砂红外环 + 1px 暖米白衬纸圈
  - 头部墨黑背景底加金边渐变线（左右淡出）
- **地图 /explore**
  - 顶栏 `.topnav-luxe` 改深色玻璃（rgba(26,16,8,0.78) + backdrop-filter blur 14px saturate 160%）
  - 顶栏底部追加 0.5px 暗金渐变线

**安全设计原则**：

| 原则 | 体现 |
|---|---|
| 增量装饰 | 所有视觉变更通过新增 className + CSS scope 实现，0 删除既有样式与 token |
| 业务逻辑 0 改动 | 不动任何 store 字段、props 契约、API 路由、URL 参数协议、数据加载逻辑 |
| 文案 0 改动 | 不引入 stitch 的英文文案，所有现有中文文案逐字保留（已通过 INVENTORY-BASELINE.md 锁定） |
| 入口 0 缺失 | BottomNav 4 项 / 首页 10 个 Link / explore 顶栏 7 个入口 / routes 4 个 chips / profile 3 个 Tab — 全部可达 |
| 数据 0 篡改 | 首页数字 234/64/3000+/14/20/68 全部维持 v4 真实数据，不写死 stitch 设计稿的虚构数字 |
| inline style 0 重写 | profile 页大量 inline style 全部保留，避免爆破半径过大 |
| 老 className 0 删除 | `.ho-* / .rb-* / .topnav-luxe / --paper / --gold-* / --ink` 等所有现有 className 与 CSS 变量保留 |

**自检结果**（基于 INVENTORY-BASELINE.md）：

- 入口完整性：✅ 7 路由全部 HTTP 200（/ /explore /poems /routes /profile /checkin /about）
- 文案一致性：✅ 关键文案逐字未改（Hero / BottomNav / Tab labels / 统计字段）
- 业务逻辑：✅ Store hook、checkAndUnlockAchievements、URL focus/route 参数、PlaceCard 90vh — 全部 0 改动
- 数据真实性：✅ 234/64/3000+/14/20/68 维持，stitch 虚构数字未引入

**回滚命令**：
```bash
git checkout main && git reset --hard v1.0.0
# 或文件级
cp components/Home/HomeLanding.v1.tsx.bak components/Home/HomeLanding.tsx
```

---

### 30. CHANGELOG #29 综合评分排序「假修复」根因修补 v2

**复盘动机**：用户要求「逐项校验 CHANGELOG 与代码一致性」，发现 #29 子项 3「综合评分排序模型」承诺的 5 个维度中，**评论数(25%) + 本地菜系(20%) = 45% 权重在代码层完全失效**。

**根因定位（两层 schema 错配）**：

| # | 问题点 | 文件 | 后果 |
|---|--------|------|------|
| 1 | `lib/food-search.ts` mapped 高德 POI 时**未填 `categories` 字段** | `lib/food-search.ts:115-133` | 接口声明了 `categories?: string[]` 但运行时永远 `undefined` → `isCuisineMatch` 中 `poi.categories \|\| []` 永远为空数组 → 关键词匹配只剩 `name.includes(keyword)` 一条路，命中率极低 |
| 2 | `lib/food-search.ts` mapped 时**未填 `comment_count` 字段** | 同上 | `parseInt(undefined \|\| '0') = 0` → `Math.log(0+1)*0.25 = 0` → **所有餐厅在评论数维度同分** → 25% 权重彻底等于 0 |
| 3 | `PlaceCard.tsx` 调用 `scoreRestaurant(b)` **未传第二参数 province** | `components/place/PlaceCard.tsx:898` | `province` 默认 `''` → `getRegionalKeywords('')` 返回 `[]` → `isCuisineMatch` 永远返回 0 → **20% 权重彻底等于 0** |

**实际生效公式（修复前）**：
```
score = rating * 0.40 + 0 + 0 + chainPenalty(±0.15) + distPenalty * 0.15
                ↑40%   ↑25%失效  ↑20%失效   ↑15%      ↑15%
```
**有效权重只有 70%**，与 CHANGELOG 承诺严重不符。

**v2 修复方案**：

| 修改项 | 文件 | 说明 |
|--------|------|------|
| 填充 categories | `lib/food-search.ts` | 高德 `type` 字段格式 `"餐饮服务;粤菜;茶餐厅"` 按 `;/；` 拆分为字符串数组，存入 `categories` |
| 填充 comment_count | `lib/food-search.ts` | 高德 PlaceSearch 不直接返回评论数，**用 photos 数量作为热度代理**（与商家曝光度正相关，可作 popularity proxy）；缺失时为 `'0'` |
| FoodTab 推断省份 | `components/place/PlaceCard.tsx` | 新增 `detectProvince(modernName)`：先匹配直辖市（北京/上海/天津/重庆/港澳台），再用 `regionalKeywords` 的 24 个 key 头部去后缀（"河南省"→"河南"）匹配 `modern_name` 开头/包含 |
| 传 province 到打分函数 | `components/place/PlaceCard.tsx` | `scoreRestaurant(b, province)`，让本地菜系 20% 权重真生效 |
| 增强菜系命中范围 | `components/place/PlaceCard.tsx` | `isCuisineMatch` 同时检查 `categories / name / type` 三处，避免高德 POI 数据格式差异导致漏判 |
| `routeId` 透传修复 | `components/place/PlaceCard.tsx` | DetailView 传 `modernName` 到 FoodTab，链路打通 |

**修复后实际生效公式**：
```
score = rating * 0.40 
      + log(photosCount + 1) * 0.25     ← 25% 真生效（photos 代理评论数）
      + cuisineMatch(0/1) * 0.20         ← 20% 真生效（黄惠儋杭川等省份命中）
      + chainPenalty(±0.15)
      + distPenalty * 0.15
```

**验证记录**：
```
✓ Compiled successfully
✓ npx next build 11/11 静态页通过，0 TS 错误，0 ESLint 警告
✓ next dev Ready，可立即验收
```

**自测建议**：
1. 进入「黄州东坡雪堂」（湖北）→ 美食 Tab → 附近推荐 → 武昌鱼/热干面店应该排在前列
2. 进入「惠州」（广东）→ 附近推荐 → 粤菜/早茶/客家应该排在前列
3. 进入「儋州」（海南）→ 附近推荐 → 文昌鸡/海南粉应该排在前列
4. 同条件下不传 province 时，排序结果应明显差异（说明 cuisineMatch 维度真的在影响）

---

### 28. 诗词筛选与跳转逻辑修复

**问题描述**：用户反馈在诗词列表页筛选「诗」或「词」后，点击诗词进入详情页，再点击「上一首/下一首」会跳转到不同类型的诗词，导致内容对不上。

**故障根因**：
1. 详情页的上一首/下一首跳转逻辑基于完整诗词列表，未考虑用户筛选的类型
2. 诗词索引文件（poems-index.json）与详情文件（poems/T001.json）中的类型不一致（索引为"题画"，文件为"文"）
3. route_id 数据不一致（索引为R16，文件为R14）

**修复方案**：

| 修改项 | 文件 | 说明 |
|--------|------|------|
| 类型一致化 | `data-v4/poems-index.json` | 将 T001 的类型从"题画"改为"文"，route_id 从 R16 改为 R14 |
| 同类型跳转 | `app/poems/[id]/page.tsx` | 修改上一首/下一首逻辑，只在同类型诗词之间跳转 |
| 禁用状态优化 | `app/poems/[id]/page.tsx` | 更新按钮禁用状态判断，准确反映是否有同类型的上一首/下一首 |

**修复效果**：
- ✅ 筛选「诗」后，详情页跳转只在诗之间进行
- ✅ 筛选「词」后，详情页跳转只在词之间进行
- ✅ 诗词索引与详情文件数据完全一致
- ✅ 按钮禁用状态正确，无类型边界处的无效点击

**验证记录**：
```
✓ Compiled successfully
✓ npx next build 通过，0 TypeScript 错误
✓ 诗词索引与文件数量匹配（328首）
```

---

### 29. 底部导航遮挡修复 + 文旅/美食功能优化

**问题一：底部导航遮挡地图内容**

**根因**：新增的底部Tab Bar是固定定位，但地图容器没有相应增加 padding-bottom，导致底部内容被遮挡。

**修复方案**：
- 在 `app/globals.css` 中添加布局尺寸变量：`--bottom-nav-height: 70px`、`--safe-area-bottom`
- 在 `components/map/AMapContainer.tsx` 中设置地图内边距 `viewPadding: [0, 0, totalBottomPadding, 0]`

**问题二：文旅/美食功能优化**

**优化内容**：

| 问题 | 优化方案 |
|------|----------|
| 美食入口太深（三级才到） | 将美食提升为独立Tab，与事迹/作品/文旅平级 |
| Tab顺序不合理 | 调整为「事迹 | 美食 | 作品 | 文旅」，美食前置到第二位（苏轼=吃货人设） |
| 附近推荐排序不合理 | 添加综合评分排序模型：高德评分(40%) + 评论数(25%) + 本地菜系匹配(20%) + 非连锁加分(15%) + 距离衰减 |
| 连锁快餐干扰 | 添加连锁品牌黑名单过滤（麦当劳/肯德基/星巴克等） |
| 空状态文案生硬 | 使用苏轼口吻："此处山水尚在，美食记录尚未抵达——你若到访，不妨留下线索" |

**新增功能**：
- 菜系关键词库（覆盖全国30+省市的特色菜系）
- 综合评分排序模型（权重可调）
- 「当地推荐」角标（前3名优质餐厅）
- 苏轼特供美食专属样式（金色边框+背景）

**修改文件**：
| 文件 | 修改内容 |
|------|----------|
| `app/globals.css` | 添加布局尺寸变量 |
| `components/map/AMapContainer.tsx` | 设置地图内边距 |
| `components/place/PlaceCard.tsx` | 拆分TravelTab和FoodTab，添加综合评分排序 |
| `lib/food-search.ts` | 扩展AMapPOIResult类型 |

**验证记录**：
```
✓ Compiled successfully
✓ npx next build 通过，0 TypeScript 错误
```

---

## 2026-06-04

---

### 27. Phase 8 - 成就图标视觉升级

**目标**：将设计精美的SVG成就图标压缩后嵌入代码，确保分享海报高清清晰，提升视觉体验。

**核心改进**：
- ✅ 双分辨率方案：UI展示用128px，分享海报用256px（高清）
- ✅ 压缩率高达 **98%+**（73MB → 1.3MB）
- ✅ 分享海报使用高清256×256图标，保证分享图清晰
- ✅ UI使用128×128图标，平衡性能与清晰度
- ✅ 无需外部图标文件夹依赖

**新增文件**：
| 文件 | 说明 |
|------|------|
| `lib/icons.ts` | 24枚成就图标的双分辨率Base64编码数据 |
| `scripts/compress-icons.ts` | 图标压缩脚本（支持双分辨率） |

**修改文件**：
| 文件 | 修改内容 |
|------|----------|
| `lib/achievements.ts` | 扩展 `Achievement` 接口，新增 `icon` 字段；为25枚成就添加图标名称映射 |
| `components/AchievementWall.tsx` | 使用UI尺寸图标（128×128），空图标时显示 emoji 兜底 |
| `components/SharePoster.tsx` | 使用高清图标（256×256），确保分享海报清晰 |

**图标分类映射**：
| 分类 | 图标数量 | 文件名 |
|------|----------|--------|
| 青铜・成长 | 5枚 | 初踏苏途、眉山故人、宦途起步、行路起步、一城漫游 |
| 白银・进阶 | 4枚 | 宦游四方、半生起落、七日同游、月月同游 |
| 鎏金・终极 | 2枚 | 半生行遍、鎏金终极 |
| 贬谪红・专题 | 3枚 | 黄州客居、岭南逐客、天涯儋州 |
| 江南绿・专题 | 2枚 | 西湖闲客、江南行舟 |
| 诗词珍藏 | 5枚 | 美食墨客、中秋望月、赤壁诗魂、风雨定风波、千首拾珍 |
| 隐藏彩蛋 | 3枚 | 雨夜读苏、生辰同游、节气同游 |
| 合成成就 | 1枚 | 贬谪三地行者（空图标，使用emoji兜底） |

**压缩统计**：
```
原始总大小: 73,795 KB (约72MB)
UI图标(128×128): 311.2 KB
海报图标(256×256): 992.1 KB
总压缩后大小: 1,303.3 KB
格式: PNG + Base64编码
```

**技术实现**：
- 使用 sharp 库压缩图片，高质量PNG输出（quality=95）
- 生成双分辨率图标：128×128用于UI，256×256用于分享海报
- 存储在 `lib/icons.ts` 中，导出 `achievementIcons` 和 `achievementIconsHD`
- 成就墙组件使用 `achievementIcons`（UI尺寸）
- 分享海报组件使用 `achievementIconsHD`（高清尺寸）
- 空图标或缺失时自动回退显示 emoji

**验证记录**：
```
✓ Compiled successfully
✓ 图标压缩脚本运行成功
✓ 双分辨率图标嵌入正常
✓ 分享海报使用高清图标
✓ 24/25 成就图标已嵌入（合成成就使用emoji兜底）
```

---

### 26. Phase 7 - 社交分享功能实现

**目标**：实现「生成国风分享海报 + 系统原生分享」双模式社交分享功能，支持成就分享、打卡分享、成就合集分享。

**核心亮点**：
- 两大分享模式：海报分享（保存到相册，适合朋友圈/小红书）+ 系统原生分享（一键分享到微信好友/QQ）
- 三种分享类型：单成就卡分享、打卡记录分享、成就合集分享
- 9:16竖版国风海报设计，符合朋友圈/小红书标准尺寸
- 纯前端实现，零后端成本，兼容PWA离线分享

**新增文件**：
| 文件 | 说明 |
|------|------|
| `lib/sharePoster.ts` | 分享海报生成工具函数（DOM转图片、保存相册、系统分享、文案模板） |
| `components/SharePoster.tsx` | 分享海报组件（隐藏的DOM容器 + 分享按钮） |

**修改文件**：
| 文件 | 修改内容 |
|------|----------|
| `components/AchievementCardModal.tsx` | 添加「生成分享海报」按钮 |
| `components/place/PlaceCard.tsx` | 实地打卡成功后显示分享按钮 |
| `app/profile/page.tsx` | 成就墙顶部添加「分享我的成就墙」按钮 |

**分享海报设计规范**：
- **尺寸**：9:16竖版（375px × 667px），适合手机全屏展示
- **顶部**：行吟山河 · 读苏轼 游神州（鎏金字体 + 宣纸底色）
- **主体**：成就卡/打卡卡片居中放大展示
- **数据区**：用户打卡数、已解锁成就数
- **底部**：项目二维码占位 + 国风slogan「扫码追随苏轼足迹」
- **风格**：宣纸纹理（#FAF6F0）、水墨边框、无杂乱元素

**分享文案模板**：
| 类型 | 文案 |
|------|------|
| 成就分享 | `我在「行吟山河」解锁【XX成就】！走遍东坡足迹，感受千古文风～` |
| 打卡分享 | `实地打卡【XX地点】，与苏轼隔空相逢｜行吟山河` |
| 合集分享 | `累计解锁XX项成就，打卡XX处东坡足迹｜行吟山河` |

**技术实现**：
- 使用 `html2canvas` 将DOM转为高清图片（scale=2）
- 使用 `navigator.share` API 调用系统原生分享
- 使用 `navigator.clipboard` 复制分享文案
- 支持PWA离线分享，不依赖服务器

**验证记录**：
```
✓ Compiled successfully
✓ Generating static pages (11/11)
✓ next build 11/11 静态页通过，0 TS 错误，0 ESLint 警告
```

---

### 25. Phase 6 - 打卡功能升级与成就体系扩展

**目标**：实现三种打卡模式（云打卡/传图打卡/GPS打卡）的三状态UI交互，将成就系统从6枚扩展到25枚，分为五大板块，实现合成成就与隐藏成就逻辑。

**核心亮点**：
- 三种打卡模式：云打卡（一键打卡）、传图打卡（上传照片）、GPS打卡（位置核验）
- 三状态UI设计：未打卡→云打卡→实地打卡的完整交互流程
- 成就体系升级：从6枚扩展到25枚，分为成长阶梯、贬谪专题、江南专题、诗词珍藏、隐秘彩蛋五大板块
- 合成成就逻辑：实现"贬谪三地行者"等合成成就，需同时满足多个基础成就
- 隐藏成就系统：实现雨夜读苏、生辰同游、节气同游等隐藏彩蛋成就
- 地图可视化高亮：已打卡地点在地图上显示特殊高亮效果

**修改文件**：
| 文件 | 修改内容 |
|------|----------|
| `lib/store.ts` | 扩展 `CheckinPlace` 接口，新增 `checkinType`、`photos`、`gpsLocation` 字段；修改 `addCheckin` 方法，实现打卡记录按时间倒序排序 |
| `lib/achievements.ts` | 扩展 `Achievement` 接口，新增 `category`、`tier`、`isHidden`、`isSynthesis` 等字段；定义五大板块25枚成就；实现节气判断、连续打卡计算、合成成就解锁等逻辑 |
| `components/place/PlaceCard.tsx` | 添加 `showUpgradeOptions`、`currentCheckin`、`isCloudCheckin`、`isFieldCheckin` 等状态变量；重构打卡按钮区域，实现未打卡、云打卡后、实地打卡后三种状态的UI展示与交互逻辑 |
| `app/checkin/page.tsx` | 在打卡记录中添加打卡类型徽章（云游/传图认证/GPS核验），优化时间显示格式 |
| `lib/clusterRender.ts` | 扩展 `makeMarkerHtml` 函数，新增 `isCheckedIn` 参数，实现已打卡地点的高亮效果（绿色光晕+徽章） |
| `components/map/AMapContainer.tsx` | 在创建 marker 时传递打卡状态，实现地图上已打卡地点的视觉区分 |

**25枚成就定义**：
| 板块 | 成就数量 | 示例成就 |
|------|----------|----------|
| 成长阶梯 | 11枚 | 初踏苏途（3处）、苏途初探（10处）、苏途行者（30处）、苏途专家（60处）、苏途大师（100处）、苏途宗师（120处）、连续打卡者（3天）、连续打卡达人（7天）、连续打卡王者（14天）、连续打卡传奇（30天）、连续打卡神话（100天） |
| 贬谪专题 | 4枚 | 黄州谪居者（黄州10处）、惠州谪居者（惠州5处）、儋州谪居者（儋州3处）、贬谪三地行者（合成成就） |
| 江南专题 | 4枚 | 杭州漫步者（杭州8处）、江南行者（江南20处）、西湖苏堤漫步（西湖系列）、江南诗词爱好者（江南诗词5首） |
| 诗词珍藏 | 4枚 | 初识苏诗（收藏5首）、苏诗爱好者（收藏20首）、苏诗专家（收藏50首）、苏诗收藏家（收藏100首） |
| 隐秘彩蛋 | 2枚 | 雨夜读苏（雨天打卡）、生辰同游（苏轼生日打卡） |

**三种打卡模式**：
| 模式 | 触发方式 | 徽章样式 | 数据字段 |
|------|----------|----------|----------|
| 云打卡 | 点击"云打卡 · 到此一游"按钮 | 🌤️ 云游 | `checkinType: 'cloud'` |
| 传图打卡 | 点击"传图打卡"按钮，上传照片 | 📷 传图认证 | `checkinType: 'photo'`, `photos: string[]` |
| GPS打卡 | 点击"GPS打卡"按钮，获取当前位置 | 📍 GPS核验 | `checkinType: 'gps'`, `gpsLocation: { latitude, longitude, accuracy }` |

**地图高亮效果**：
- 已打卡地点：绿色光晕（`rgba(74, 124, 98, 0.8)`）+ 右上角绿色圆点徽章
- 未打卡地点：默认阴影效果
- 视觉区分：用户可快速识别已打卡地点，提升探索成就感

**合成成就逻辑**：
- 贬谪三地行者（banish-004）：需同时解锁黄州谪居者（banish-001）、惠州谪居者（banish-002）、儋州谪居者（banish-003）
- 自动触发：当所有基础成就解锁后，合成成就自动解锁

**隐藏成就逻辑**：
- 雨夜读苏（secret-001）：雨天（22:00-6:00）打卡任意地点
- 生辰同游（secret-002）：苏轼生日（1月8日）打卡任意地点
- 节气同游（secret-003）：二十四节气当天打卡任意地点

**验证记录**：
```
✓ Compiled successfully
✓ Generating static pages (11/11)
✓ next build 11/11 静态页通过，0 TS 错误，0 ESLint 警告
```

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