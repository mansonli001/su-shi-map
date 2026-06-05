# 苏轼地图项目变更日志

## 2026-06-05

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