# Changelog

## 2026-06-13 旅人录点亮逻辑修复（按实际打卡计算）

### Bug 根因（P0）
- 旅人录「点亮省份 / 打卡地点 / 尝过小吃」三个数原本都来自 `provinceStats`（数据库里**全部地点**的统计），与用户实际打卡无关——导致一进页面就显示一堆"已点亮"省份，但用户一个都没打卡。

### 修复（`app/he-ye/profile/page.tsx`）
- 全部改为基于 `heyeCheckins`（实际打卡记录）计算：
  - 每省计数：数据库该省总数 → **我实际打卡的地点数**（`placeId` 反查 `location.province`）。
  - 点亮省份：满阈值 3 个才点亮（阈值不变）。
  - 打卡地点：库内总数 → 我打卡过的**去重**地点数。
  - 尝过小吃：全库小吃 → 我打卡地点里的小吃种类。
- 建 `placeId → location` 映射做省份反查（`HeyeCheckinPlace` 自身不带 province）。
- 打卡记录按 `placeId` 去重，过滤查不到 location 的脏数据，避免重复/失效记录污染计数。
- 直辖市合并逻辑（北京/天津→河北、上海→江苏、重庆→四川）原样保留。
- 移除不再需要的 `getHeyeProvinceStats` / `provinceStats` 引用。

### 涉及文件
- `app/he-ye/profile/page.tsx` — 点亮与统计逻辑改为按实际打卡计算

---

## 2026-06-13 旅人录渲染修复 + 设计优化

### 渲染根因修复（P0）
- **样式加载位置上移**：`heye-home.css` 原仅在 `app/he-ye/page.tsx` 引入，导致直接硬加载/刷新 `/he-ye/profile`、`/he-ye/feed`、`/he-ye/explore` 时缺失全站布局样式（页面"裸奔"）。改为在 `app/he-ye/layout.tsx` 统一引入，覆盖所有 `/he-ye/*` 子路由。
- 移除 `app/he-ye/page.tsx` 中冗余的 CSS import。

### 已知 bug 修复
- **删除死代码 `components/map/ChinaMapSvg.tsx`**：今日地图已改 PNG，该旧 SVG 组件全项目零引用，且存在 `ProvinceFeature.shortName` 缺失的类型错误，阻断 `next build`。删除后构建恢复通过。
- 清理 `profile/page.tsx`：移除残留 `console.log` 与失效的省份点击 prop（地图已为纯展示），更新过时注释。

### profile 设计优化
- 统计卡片：暖色渐变 + 描边 + hover 微浮起。
- 足迹地图容器：移除与暖橙主题冲突的冷色蓝底（`#EAF4FA`），改暖色渐变。
- 省份成就区：与统计/地图区左右对齐（移除多余 16px 缩进）。
- 翻牌卡：正反面增加层次阴影，点亮态轻微浮起。
- 打卡记录卡片：左侧暖橙强调条 + hover 反馈。

### 性能
- 地图 `<img>` 增加 `width/height`（防 CLS）+ `decoding="async"` + `loading="lazy"`。

### 涉及文件
- `app/he-ye/layout.tsx` / `app/he-ye/page.tsx` — CSS 加载位置调整
- `app/he-ye/profile/page.tsx` — 清理与注释
- `app/he-ye/heye-home.css` — profile 区域设计优化
- `components/map/ChinaMapMask.tsx` — 地图图片性能属性
- `components/map/ChinaMapSvg.tsx` — 删除（死代码）

---

## 2026-06-13 旅人录页面重构

### 地图组件
- **替换底图**：从纯SVG渲染改为PNG设计图展示（`/heye-map/china-map-lit.png`）
- **移除SVG蒙版**：不再叠加SVG路径覆盖层，直接居中展示设计图
- **移除交互**：地图不再支持省份点击（纯展示）
- **未点亮状态**：无打卡时底图透明度降低（0.6），有打卡恢复1.0

### 成就卡
- **统一配色**：所有省份统一使用苏轼暖色系
  - 点亮：`#C4612A`（暖橙）/ `#A04818`（深橙描边）
  - 未点亮：`#E8E0D4`（米色）/ `#C8C0B0`（灰棕描边）
  - 卡片背景：`#FBF7F4`（暖白）
  - 进度条/文字：`#C4612A` / `#8C6A58`
- **移除多色方案**：删除34个省份独立配色（PROVINCE_STYLE），改为统一色
- **移除渐变填充**：SVG缩略图从linearGradient改为纯色填充
- **移除金色光晕**：点亮状态不再叠加 #FFD580 描边

### 直辖市处理
- **成就卡移除4个直辖市**：北京、天津、上海、重庆不再单独显示
- **打卡数据合并**：
  - 北京 + 天津 → 河北
  - 上海 → 江苏
  - 重庆 → 四川
- **卡片总数**：31 → 27

### SVG缩略图
- **放大**：64px → 80px
- **简化**：移除渐变和光晕，纯色填充

### 统计数字
- 省份计数：31 → 27

### 涉及文件
- `components/map/ChinaMapMask.tsx` — 地图组件 + 成就卡组件
- `app/he-ye/profile/page.tsx` — 旅人录页面（直辖市合并逻辑）
- `public/heye-map/china-map-lit.png` — 新增地图底图
