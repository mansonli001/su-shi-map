# 贺野游中国 · 扩展开发计划

> 基于 `heye_spec_v2.md`（用户 v2 初步想法）分析、修正后产出的可执行开发计划。
> 编写日期：2026-06-13　|　目标项目：su-shi-map（行吟山河，su-shi.starfluxes.com）

---

## 〇、一句话结论

v2 的**产品方向完全正确**（双行者、`/he-ye/*` 独立域、复用地图/打卡/成就/分享），但它建立在一个**错误的技术前提**上——v2 假设项目是「Next.js + Supabase 后端」，而真实的 su-shi-map 是**零后端**（静态 JSON + localStorage）。

因此本计划做了三处结构性修正（均已与你确认）：

| v2 原方案 | 本计划修正 | 原因 |
|---|---|---|
| 阶段一：Supabase 建表 + SQL + Python 入库 | **静态 JSON + localStorage(zustand)** | 真实项目无 Supabase 依赖，零后端 |
| 阶段三：苏轼路由平移到 `/su-shi/*` + 301 重定向 | **苏轼路由完全不动**，只改 `/` 为选择页 | 平移回归风险最高，收益低 |
| 每个行者独立 layout + 底栏 | **BottomNav 单组件按路径前缀切换** | root 单例 + SEO/metadata 不动，改动最小 |

---

## 一、v2 假设 vs 真实架构（逐项验证）

| 维度 | v2 假设（❌ 错误） | 真实代码（✅ 已读码验证） | 涉及文件 |
|---|---|---|---|
| 数据层 | Supabase 建表 + SQL + Python 入库 | 静态 JSON，`fetch('/data-v4/places/{id}.json')`，服务端 `readPlaceDetailServer` 读 `public/data-v4/` | `lib/data-loader.ts` |
| 打卡/成就 | `heye_checkins` 表 + `user_id` | localStorage(zustand)，persist key=`su-shi-user-data`，持久化 favoritePoems / checkinPlaces / userNotes / unlockedAchievements；打卡类型 cloud/photo/gps | `lib/store.ts` |
| 成就计算 | `heye_achievements` 表 | 纯函数 `evaluateAchievements(checkedIds, places, favoritePoemIds, checkinDates)`，store 内计算并 toast | `lib/achievements.ts` |
| 地图 | 可注入 props 的 `<MapExplorer>` | 高德 AMap，与苏轼 store 深度耦合 | `components/map/AMapContainer.tsx` |
| 底栏 | 每行者独立 layout+底栏 | 全局单例，root layout 渲染，`NAV_ITEMS` 硬编码 4 项（`/` `/explore` `/poems` `/profile`） | `components/BottomNav.tsx`、`app/layout.tsx` |
| 路由盘点 | 只提 explore/poems/routes/profile | 还有 `app/about`、`app/checkin`、`app/api`、`app/places/*` | `app/*` |
| 后端依赖 | 假设有 supabase-js | **package.json 无任何 supabase 依赖**；有 zustand / swr | `package.json` |

---

## 二、最终架构决策（已确认）

### 2.1 路由树（苏轼零改动，贺野新增）

```
/                  → 行者选择页（改写现有 app/page.tsx；带 localStorage 记忆直跳）

# 苏轼（全部保持现状，一行不改）
/explore /poems /routes /profile /about /checkin /places/* /api/*

# 贺野（全部新增）
/he-ye             → 贺野 Home
/he-ye/explore     → 贺野地图
/he-ye/feed        → 贺野文章流（替代诗词页）
/he-ye/profile     → 贺野旅人录
```

> ⚠️ 不做路由平移、不加 `next.config.js` 重定向、不动 PWA manifest/SW。零回归。

### 2.2 数据与状态（零后端）

- **贺野地点数据** → 静态 JSON，放 `public/data-heye/`（与 `public/data-v4/` 对齐），用 fetch 读取。
- **贺野打卡/成就** → 独立 zustand persist，**新建 key `he-ye-user-data`**（不复用 `su-shi-user-data`，避免污染苏轼数据、便于各自清理）。
- **行者记忆** → `localStorage.last_character`（`su-shi` | `he-ye`），选择页据此直跳。

### 2.3 底栏（单组件双套切换）

`components/BottomNav.tsx` 内维护两套 `NAV_ITEMS`，按 `usePathname()` 是否以 `/he-ye` 开头切换：

```
苏轼: 首页/ · 水墨地图/explore · 古诗集/poems · 名士录/profile
贺野: 首页/he-ye · 足迹地图/he-ye/explore · 文章流/he-ye/feed · 旅人录/he-ye/profile
```

选择页 `/` 本身不显示底栏（或显示中性态）。

### 2.4 配色 token（globals.css 新增，苏轼不动）

```css
--color-he-primary: #C4612A;  --color-he-accent: #E8854A;
--color-he-bg: #FBF7F4;       --color-he-ink: #1A0E08;
--color-he-muted: #8C6A58;    --color-he-tag-bg: #FDE8DC;
```

---

## 二·五、数据字段核心规划（唯一权威定义）

> ⚠️ **本章节取代 `heye_feature_spec.md` 中的旧 Supabase 数据库章节**，自此为贺野数据字段的**唯一权威定义**。旧方案假设 Supabase 建表，真实项目零后端——所有字段以静态 JSON（对齐 `data-v4`）落地。
> 本章节直接驱动两个脚本：`heye_extractor.py` 的 `CSV_FIELDS` 修补、新增脚本 `scripts/csv_to_heye_json.py` 的 JSON 产出。

### 0. 三层数据架构（为什么要分三层）

PDF 提取实战暴露一个核心事实：**「给人工校验的中间产物」和「上线渲染的数据」不是同一套字段**。强行用一套 schema，会让上线 JSON 背上 `search_term`/`extractor_notes`/`human_reviewed` 这类流程字段，也会让校验 CSV 缺少派生统计。因此拆三层：

```
┌─ 第一层 · 提取层（CSV 中间产物）──────────────┐
│  heye_extractor.py 产出 → 人工逐行校验          │
│  含 AI 提取字段 + 流程控制字段（搜索词/校验标记） │
└───────────────────┬───────────────────────────┘
                     │ csv_to_heye_json.py（剥离流程字段 + 派生）
                     ▼
┌─ 第二层 · 展示层（上线 JSON）────────────────┐
│  public/data-heye/locations.json + places/{id} │
│  HeyeLocation，对齐 data-v4 的 place schema     │
└───────────────────┬───────────────────────────┘
                     │ 同脚本聚合
                     ▼
┌─ 第三层 · 聚合层（统计/着色）─────────────────┐
│  province-stats.json（省份点亮着色）            │
│  meta.json（首页统计 + schema 元信息）          │
└─────────────────────────────────────────────────┘
```

**数据流向**：`PDF → CSV(19字段) → 人工校验(填坐标/改 human_reviewed=Y) → csv_to_heye_json.py → locations.json + province-stats.json + meta.json`。只有 `human_reviewed=Y` 的行才进入展示层。

**命名规范（全层统一）**：
- JSON / CSV 字段一律 **snake_case**（`place_name`/`visit_date`/`coordinate_source`），与 `data-v4`、原始贺野样本完全对称。
- TypeScript 接口用 **camelCase**，loader 层做映射（见 §4 映射表）。
- ID 规范：地点 `HY001` 起递增，零填充 3 位；一篇文章产出多条时连续编号（`HY012`/`HY013`…）。

---

### 1. 第一层 · 提取层 schema（CSV，19 字段）

`heye_extractor.py` 的 `CSV_FIELDS` 当前为 18 字段，**缺 `region`**——脚本 `extract_text()` 已从 PDF 第二行元数据解析出地区（`原创 贺野 有生余年 2024-07-27 21:27:51 内蒙古` → `内蒙古`），但写 CSV 时丢弃了。「区域为主」方向必须捡回。修补后为 **19 字段**：

| # | 字段 | 类型 | 必填 | 来源 | 说明 | 示例 |
|---|---|---|---|---|---|---|
| 1 | `id` | string | ✅ | 派生 | `HY` + 3 位序号，一篇多点连续编号 | `HY001` |
| 2 | `province` | string | ✅ | AI 提取 | 省级行政区（标准名，不带"省/市"后缀可，与 `region` 做一致性校验） | `福建` |
| 3 | `city` | string | ✅ | AI 提取 | 地级市/区县 | `武夷山市` |
| 4 | `place_name` | string | ✅ | AI 提取 | 具体地点名 | `武夷山` |
| 5 | `full_name` | string | ✅ | AI 提取 | `城市·地点名` 展示用全称 | `福建·武夷山` |
| 6 | **`region`** | string | ⬜ | **PDF 元数据**（新捡回） | PDF 发布时的 IP 归属地标签，做 `province` 一致性校验、补救 AI 漏判 | `内蒙古` |
| 7 | `visit_date` | string\|null | ⬜ | AI 提取 | 模糊到月 `YYYY年M月`，不确定填 null | `2022年12月` |
| 8 | `trip_tag` | string\|null | ⬜ | AI 提取 | 弱标签，同次出行软关联，不确定填 null | `2022福建行` |
| 9 | `excerpt` | string | ✅ | AI 提取 | **原文原话**，允许相邻 2-3 句拼接、不跨段、50-150 字 | `昨天爬山…今天漂流…` |
| 10 | `snacks` | string(JSON) | ⬜ | AI 提取 | JSON 字符串数组，仅"明确吃过/买过"，空则 `[]` | `["扁肉","拌粉"]` |
| 11 | `search_term` | string | ⬜ | AI 提取 | **高德搜索词**（省市+地名），供人工核坐标，AI 不给经纬度 | `福建武夷山九曲溪` |
| 12 | `lat` | string→float | ⬜ | **人工填** | GCJ-02 纬度，AI 留空，人工据 `search_term` 核实 | `27.7547` |
| 13 | `lng` | string→float | ⬜ | **人工填** | GCJ-02 经度，同上 | `118.0353` |
| 14 | `image_url` | string | ⬜ | 人工/后补 | 配图，留空则渐变占位 | `` |
| 15 | `article_url` | string | ⬜ | 人工/后补 | 公众号原文外链，空则隐藏「读原文」 | `` |
| 16 | `source_file` | string | ✅ | 派生 | 来源 PDF 文件名，溯源用 | `2024-07-27_…达里湖….pdf` |
| 17 | `source_title` | string | ✅ | PDF 元数据 | 来源文章标题，溯源 + 可作"读原文"标题 | `父子暑假北上之旅（3）…` |
| 18 | `extractor_notes` | string | ⬜ | AI 提取 | AI 自标不确定处，有内容的行优先人工看 | `坐标为河谷酒店附近，需核实` |
| 19 | `human_reviewed` | enum | ✅ | **人工卡口** | `N` 默认 / `Y` 校验通过可上线 / `X` 有问题需重提取 | `N` |

**字段角色分类**（决定是否进展示层）：
- **核心内容字段**（进展示层）：`id` `province` `city` `place_name` `full_name` `region` `visit_date` `trip_tag` `excerpt` `snacks` `lat` `lng` `image_url` `article_url`
- **流程/中间字段**（不进展示层，仅校验用）：`search_term` `extractor_notes` `human_reviewed`
- **溯源字段**（择一进展示层）：`source_file`（仅留 CSV）、`source_title`（可进展示层做"读原文"标题）

> 🔧 **脚本修补点**：`CSV_FIELDS` 在 `full_name` 后插入 `"region"`；`process_pdf()` 组装 row 时加 `"region": article["region"]`。其余不动。

---

### 2. 第二层 · 展示层 schema（`HeyeLocation`，上线 JSON）

对齐 `data-v4` 的 place schema（GCJ-02 坐标 + `coordinate_source`、snake_case、元字段齐全）。落地两处：
- `public/data-heye/locations.json`：全量轻索引（首屏拉取，含坐标 + 卡片必需字段）。
- `public/data-heye/places/{id}.json`：单点详情（可选，第一版数据量小可只用 locations.json，预留按需加载）。

**单条 `HeyeLocation` 字段**：

| 字段 | 类型 | 必填 | 来源 | 说明 |
|---|---|---|---|---|
| `id` | string | ✅ | CSV | `HY001` |
| `province` | string | ✅ | CSV | 省份（聚合/着色主键） |
| `city` | string | ✅ | CSV | 城市 |
| `place_name` | string | ✅ | CSV | 地点名 |
| `full_name` | string | ✅ | CSV | 展示全称 |
| `region` | string | ⬜ | CSV | PDF 原始地区标签，已与 province 校验后保留（多用于异常追踪，前端一般不展示） |
| `lat` | number | ✅ | CSV（人工） | GCJ-02 纬度，**对齐高德/苏轼** |
| `lng` | number | ✅ | CSV（人工） | GCJ-02 经度 |
| `coordinate_source` | enum | ✅ | 派生 | 坐标来源标记：`amap_search`（高德搜索词核实，贺野默认）/ `manual`（人工直填）/ `inferred`（推断，需谨慎上线）。对齐 `data-v4` 的 `coordinate_source` 设计 |
| `visit_date` | string\|null | ⬜ | CSV | `YYYY年M月` |
| `visit_year` | number\|null | ⬜ | **派生** | 从 `visit_date` 抽取的年份（number），供排序/时间筛选；无则 null |
| `excerpt` | string | ✅ | CSV | 原文原话 |
| `snacks` | string[] | ⬜ | CSV（解析 JSON） | 数组，空 `[]` 则不渲染"他吃的" |
| `image_url` | string | ⬜ | CSV | 空则渐变占位 |
| `article_url` | string | ⬜ | CSV | 空则隐藏外链 |
| `source_title` | string | ⬜ | CSV | "读原文"标题/溯源 |
| `trip_tag` | string\|null | ⬜ | CSV | **弱标签**，同次出行软关联（筛选 chips / 首页时间轴），非组织主轴 |
| `featured` | boolean | ✅ | **人工运营** | 首页精选轮播，默认 false，人工挑 ≥6 条 true |

**剥离字段**（CSV 有但不进展示层）：`search_term`、`extractor_notes`、`human_reviewed`、`source_file`。

**派生关系（运行时算，不入库）**：
- "同省/同市其他地点"、"同 `trip_tag` 其他地点" → loader 层按 `province`/`city`/`trip_tag` 分组得出，不冗余存储。

**`locations.json` 顶层结构**（对齐 `data-v4` 的 `_meta` + 数组）：

```jsonc
{
  "_meta": {
    "schema_version": "heye-v1.0",
    "data_source": "公众号「有生余年」· 贺野原创",
    "disclaimer": "地点坐标经人工校验，excerpt 为原文原话引用，版权归原作者所有。",
    "generated_at": "2026-06-13T00:00:00.000Z",
    "total_locations": 32
  },
  "locations": [ /* HeyeLocation[] */ ]
}
```

---

### 3. 第三层 · 聚合层 schema

由 `csv_to_heye_json.py` 在生成 `locations.json` 时一并算出，避免前端重复遍历。

#### 3.1 `public/data-heye/province-stats.json`（省份点亮着色）

```jsonc
{
  "_meta": { "generated_at": "...", "schema_version": "heye-v1.0" },
  "provinces": {
    "福建": {
      "place_count": 3,           // 该省地点数
      "city_count": 2,            // 去重城市数
      "place_ids": ["HY001","HY004","HY007"],
      "density_tier": 2           // 着色档：0 无 / 1=(1-2) / 2=(3-5) / 3=(6+)
    },
    "内蒙古": { "place_count": 6, "city_count": 3, "place_ids": ["..."], "density_tier": 3 }
  }
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `place_count` | number | 该省已上线地点数 |
| `city_count` | number | 该省去重城市数 |
| `place_ids` | string[] | 该省地点 id 列表（点击省份下钻用） |
| `density_tier` | 0\|1\|2\|3 | 四档着色：`0`无 / `1`=1-2 / `2`=3-5 / `3`=6+，地图按此填橙色透明度 |

> ⚠️ 着色档与 GeoJSON 省份名匹配：`china-provinces.geojson` 的省份命名（如"内蒙古自治区"）与 `province`（"内蒙古"）可能不一致，脚本需维护一张**省名归一映射表**（`内蒙古↔内蒙古自治区`、`广西↔广西壮族自治区` 等）。

#### 3.2 `public/data-heye/meta.json`（首页统计 + 全局元信息）

```jsonc
{
  "schema_version": "heye-v1.0",
  "generated_at": "2026-06-13T00:00:00.000Z",
  "data_source": "公众号「有生余年」· 贺野原创",
  "disclaimer": "...",
  "stats": {
    "total_places": 32,        // 上线地点总数
    "province_count": 11,      // 点亮省份数（成就/首页"全国点亮"）
    "city_count": 24,          // 去重城市数
    "snack_variety": 47,       // 去重小吃种数（成就 snack_variety）
    "article_count": 28,       // 去重源文章数（source_title 去重）
    "trip_count": 5,           // 去重 trip_tag 数（null 不计）
    "featured_count": 6        // featured=true 数
  }
}
```

> 这些聚合量直接喂：首页 `HeyeStatsBanner`（城市/省份/小吃/篇数）、成就系统（`province_count`/`snack_variety`/`percent`）、省份着色覆盖率。

---

### 4. CSV ↔ JSON ↔ TypeScript 映射表

| CSV（提取层） | JSON（展示层 snake_case） | TS（`types/heye.ts` camelCase） | 转换 |
|---|---|---|---|
| `id` | `id` | `id` | 透传 |
| `province` | `province` | `province` | 透传 |
| `city` | `city` | `city` | 透传 |
| `place_name` | `place_name` | `placeName` | snake→camel |
| `full_name` | `full_name` | `fullName` | |
| `region` | `region` | `region` | 校验后保留 |
| `visit_date` | `visit_date` | `visitDate` | |
| —（派生） | `visit_year` | `visitYear` | 从 visit_date 抽年份 |
| `trip_tag` | `trip_tag` | `tripTag` | 空串→null |
| `excerpt` | `excerpt` | `excerpt` | |
| `snacks` | `snacks` | `snacks` | JSON 字符串→string[] |
| `lat` | `lat` | `lat` | str→number |
| `lng` | `lng` | `lng` | str→number |
| —（派生） | `coordinate_source` | `coordinateSource` | 据来源标记 |
| `image_url` | `image_url` | `imageUrl` | |
| `article_url` | `article_url` | `articleUrl` | |
| `source_title` | `source_title` | `sourceTitle` | |
| —（人工） | `featured` | `featured` | 默认 false |
| `search_term` | ✂️ 剥离 | — | 不进展示层 |
| `extractor_notes` | ✂️ 剥离 | — | 不进展示层 |
| `human_reviewed` | ✂️ 剥离（作为过滤条件） | — | 仅 `Y` 进 JSON |
| `source_file` | ✂️ 剥离 | — | 仅 CSV 溯源 |

> `types/heye.ts` 中阶段 1 已列的 `HeyeLocation` 需据此补齐 `region`/`visitYear`/`coordinateSource`/`sourceTitle` 四个字段。

---

### 5. 一致性与异常处理规则

| 场景 | 规则 |
|---|---|
| **`province` ↔ `region` 冲突** | 以 AI 提取的 `province` 为展示主键（更细更准）；`region` 是 IP 归属地（可能是出发地而非到达地），仅作交叉校验与漏判补救。冲突时在 `extractor_notes` 标记，人工裁决，**不自动覆盖** |
| **一篇文章多地点** | 按 `id` 连续编号，全部带同一 `source_file`/`source_title`/可同享 `trip_tag`；拆分上限 5 个，"有独立 GPS + 有实质描述"才单独建条目，过路顺带归并主地点（武夷山一线天/九曲溪/大红袍 → 合并为 1 个武夷山） |
| **坐标缺失** | `human_reviewed != Y` 或 `lat/lng` 为空的条目**一律不进 `locations.json`**，由脚本过滤 |
| **`snacks` 空** | 输出 `[]`，前端"他吃的"区块整块不渲染 |
| **`trip_tag` null** | 不进入 trip 筛选 chips / 时间轴，地点仍正常展示在地图与文章流 |
| **`image_url` 空** | 卡片用 16:9 暖橙渐变占位（贺野色 token） |
| **`article_url` 空** | 隐藏"读原文 →"按钮，不显示空链接 |
| **省名归一** | `province` 与 GeoJSON 省名通过映射表对齐后才能着色，未命中的省记入脚本告警日志 |
| **`visit_date` 模糊/缺失** | 允许 null；`visit_year` 抽不出年份时也为 null，排序时 null 沉底 |

---

### 6. 对脚本的回填核对清单（执行阶段 0 时照此改）

- [ ] `heye_extractor.py`：`CSV_FIELDS` 在 `full_name` 后加 `"region"`（→19 字段）；`process_pdf()` row 加 `"region": article["region"]`。
- [ ] 新增 `scripts/csv_to_heye_json.py`：读 CSV → 过滤 `human_reviewed=='Y'` → 剥离流程字段 → 派生 `visit_year`/`coordinate_source` → 解析 `snacks` JSON → 输出 `locations.json` + `province-stats.json`（含省名归一映射 + density_tier）+ `meta.json`（含 7 项 stats）。
- [ ] `types/heye.ts`：`HeyeLocation` 补 `region`/`visitYear`/`coordinateSource`/`sourceTitle`；新增 `ProvinceStats`、`HeyeMeta` 接口。

---

## 三、分阶段开发计划

> 每阶段可独立验收，完成后**必须本地回归测试苏轼原有功能**再进下一阶段。

### 阶段 0 · 数据管线（PDF → 静态 JSON）

**目标**：把 `/Users/mansonlee/Downloads/heye/有生余年/`（1380 PDF）跑成可上线的贺野 JSON。

1. 复用 `heye_extractor.py`（PDF→pdfplumber→Claude API→CSV），**第一版只跑足够覆盖 ≥30 地点 / ≥10 省份的子集**，不必全量 1380 篇。
2. 人工校验 CSV：填 `lat/lng`（按 `search_term` 高德核实）、`human_reviewed=Y`、挑 ≥6 条 `featured=true`、整理 2-3 个 `trip_tag` 组。
3. **新增脚本 `scripts/csv_to_heye_json.py`**（替代 v2 的 `seed_heye.py`）：CSV → 静态 JSON，产出：
   - `public/data-heye/locations.json`（全部地点索引）
   - `public/data-heye/province-stats.json`（各省地点数，供着色）
   - `public/data-heye/meta.json`（城市数/省份数/小吃种数/篇数，供首页统计）
4. `public/china-provinces.geojson`（省级 GeoJSON，省份着色用，缺则下载）。

**验收**：JSON 文件生成、字段完整、坐标非空、≥30 地点 ≥10 省。

---

### 阶段 1 · 类型 + 数据层 + 状态

**新增**
- `types/heye.ts`：`HeyeLocation`（id/province/city/place_name/full_name/lat/lng/visit_date/trip_tag/excerpt/snacks[]/image_url/article_url/featured）、`HeyeAchievement`、`ProvinceStats`、`CharacterId='su-shi'|'he-ye'`。
- `lib/heye-loader.ts`：`getHeyeLocations()` / `getHeyeLocation(id)` / `getHeyeProvinceStats()` / `getHeyeMeta()` / `getFeaturedHeyeLocations()` / `getHeyeLocationsByTrip(tag)`——全部 fetch 静态 JSON。
- `lib/heye-store.ts`：独立 zustand persist（key `he-ye-user-data`），`heyeCheckins / addHeyeCheckin / removeHeyeCheckin / isCheckedIn / unlockedAchievements / checkAndUnlock`，结构对齐 `lib/store.ts`。
- `lib/heye-achievements.ts`：`calculateHeyeAchievements(achievements, allLocations, checkedIds)`，实现 6 类条件（checkin_count / snack_location / province_count / snack_variety / percent / checkin_all），返回带 `progress/total/unlocked`。

**验收**：`tsc` 无报错；浏览器 console 调用 loader 能拿到数据；localStorage 读写 `he-ye-user-data` 正常。

---

### 阶段 2 · 行者选择页 `/`

**改写** `app/page.tsx`：
- 进入时读 `localStorage.last_character`，有记录直跳对应 Home（`/` 或 `/he-ye`）。
- 无记录 → 渲染选择页：品牌名 + 两张人物卡（苏轼水墨棕 / 贺野暖橙），点卡片写记忆并跳转。

**新增** `components/CharacterCard.tsx`（接收 character 配置 + onSelect）。

**底栏** `components/BottomNav.tsx`：实现双套切换 + `/` 不显示底栏。

**验收**：首次进显示选择页；选苏轼跳 `/` 并显示苏轼站点正常；选贺野跳 `/he-ye`；刷新后直跳记忆行者；**苏轼所有页面底栏与功能无回归**。

---

### 阶段 3 · 贺野 Home `/he-ye`

**新增**
- `app/he-ye/layout.tsx`：注入贺野色彩 token（容器 class），metadata。
- `app/he-ye/page.tsx`：6 段滚动长页。
- `components/heye/HeyeHeroSection.tsx`（英雄区 + 公路大地底图占位）
- `components/heye/HeyeStatsBanner.tsx`（城市/省份/小吃/篇数，读 meta.json）
- `components/heye/HeyeFeaturedCarousel.tsx`（featured 横滑卡）
- `components/heye/HeyeTripTimeline.tsx`（按 trip_tag 出行轨迹，点击跳 `/he-ye/explore?trip=xxx`）
- 引流公众号"有生余年"外链段 + 入口段。

**验收**：6 段渲染正常，统计数字来自 JSON，横滑/外链/跳转可用。

---

### 阶段 4 · 贺野地图 `/he-ye/explore`

**复用策略**：先评估 `AMapContainer` 能否参数化（markerColor / locations / 卡片组件）。
- 若可参数化 → 直接传 props。
- 若与苏轼 store 强耦合 → 抽 `hooks/useHeyeMap.ts` 承接贺野数据逻辑，地图容器复用渲染层。

**新增**
- `app/he-ye/explore/page.tsx`
- `components/heye/HeyeLocationCard.tsx`：图 16:9（无图渐变占位）/ full_name / visit_date + trip_tag chip / excerpt（引号 + 衬线体）/ 「他吃的」snacks 标签（空则不渲染）/「这次出行」同 trip_tag 其他地点 / 导航 + 原文（article_url 空则隐藏）+ 打卡按钮（接 heye-store）。
- `components/heye/HeyeMapFilters.tsx`：trip_tag 筛选 chips（读 URL `?trip=` 自动激活）。
- 省份着色层：读 province-stats.json，按 0 / 1-2 / 3-5 / 6+ 四档橙色透明度填 `china-provinces.geojson`；**仅贺野地图启用**。

**验收**：markers 橙色、点击出卡、打卡切换并触发成就、省份着色正确、trip 筛选可用、苏轼地图不受影响。

---

### 阶段 5 · 贺野文章流 `/he-ye/feed`

**新增**
- `app/he-ye/feed/page.tsx`：excerpt 卡片列表，visit_date 倒序，trip_tag 分组筛选。
- `components/heye/HeyeFeedCard.tsx`：地点名 + visit_date + excerpt + snacks + 「在地图上看 →」（跳 explore focus 该点）+「读原文 →」（外链公众号，空则隐藏）。

**验收**：列表渲染、排序、筛选、两个跳转均可用。

---

### 阶段 6 · 贺野旅人录 `/he-ye/profile`

**新增**
- `app/he-ye/profile/page.tsx`
- `components/heye/HeyeAchievementWall.tsx`：6 成就，复用苏轼 `AchievementCard` 四状态（unlocked / near≥70% / in-progress / locked），传贺野配色。
- `components/heye/HeyeUserMap.tsx`：用户已打卡省份点亮小地图（只读）。
- `components/heye/HeyeShareCard.tsx`：复用 html2canvas，橙渐变 `#FDE8DC→#F5C5A3`，水印「贺野游中国 · 有生余年」，9:16 2x 导出。
- 「← 切换到苏轼线路」入口：清 `last_character`，跳 `/`。

**验收**：贺野总量 + 用户打卡数 + 进度条 + 成就墙 + 小地图 + 分享卡导出无截断 + 切换入口可用。

---

### 阶段 7 · 数据扩充 + 上线

- 把阶段 0 的种子数据补到上线标准（≥30 / ≥10 省 / ≥6 featured / 2-3 trip_tag）。
- 全站回归：苏轼线路逐页验、贺野线路逐页验、PWA 安装/缓存正常。
- 本地 `pnpm dev`（PORT=3000）自检 → 部署。

---

## 四、完整文件清单

### 新增
```
public/data-heye/locations.json
public/data-heye/province-stats.json
public/data-heye/meta.json
public/china-provinces.geojson
scripts/csv_to_heye_json.py

types/heye.ts
lib/heye-loader.ts
lib/heye-store.ts
lib/heye-achievements.ts
hooks/useHeyeMap.ts                  (视地图耦合程度决定是否需要)

components/CharacterCard.tsx
components/heye/HeyeHeroSection.tsx
components/heye/HeyeStatsBanner.tsx
components/heye/HeyeFeaturedCarousel.tsx
components/heye/HeyeTripTimeline.tsx
components/heye/HeyeLocationCard.tsx
components/heye/HeyeMapFilters.tsx
components/heye/HeyeFeedCard.tsx
components/heye/HeyeAchievementWall.tsx
components/heye/HeyeUserMap.tsx
components/heye/HeyeShareCard.tsx

app/he-ye/layout.tsx
app/he-ye/page.tsx
app/he-ye/explore/page.tsx
app/he-ye/feed/page.tsx
app/he-ye/profile/page.tsx
```

### 改动（最小化）
```
app/page.tsx              → 改写为行者选择页 + 记忆直跳
components/BottomNav.tsx   → 双套导航按路径前缀切换
app/globals.css            → 新增贺野色彩 token
components/map/AMapContainer.tsx → 仅在需参数化时改（优先抽 hook，不破坏苏轼）
```

### 不动（明确不碰）
```
苏轼所有页面 app/explore /poems /routes /profile /about /checkin /places /api
lib/store.ts  lib/data-loader.ts  lib/achievements.ts
next.config.js（不加重定向）  PWA manifest / service worker
```

---

## 五、回归风险控制

| 风险点 | 控制措施 |
|---|---|
| 改 `app/page.tsx` 影响苏轼首页 | 苏轼 Home 内容若需保留，拆为 `components/Home/` 复用；选择页只做路由分流 |
| 改 BottomNav 影响苏轼底栏 | 默认套=苏轼原 4 项，仅 `/he-ye` 前缀切贺野套；先验苏轼各页底栏 active 态 |
| 贺野 localStorage 污染苏轼数据 | 独立 persist key `he-ye-user-data`，两套互不读写 |
| 地图组件耦合 | 优先抽 hook 不改苏轼调用；改 AMapContainer 前先备份并验苏轼地图 |
| 省份着色误开到苏轼地图 | 着色层用 `character==='he-ye'` 守卫，苏轼地图不挂载 |

---

## 六、第一版边界（不做）

- 贺野成就 Midjourney 插画（emoji 占位）
- 贺野全文搜索
- 贺野单独 `/routes` 页（trip_tag 已承担路线）
- 公众号正文在 app 内全文展示（外链引流即可）
- 用户间社交功能 / 多语言 / PWA service worker 升级

---

## 七、执行顺序速览

```
0 数据管线(PDF→JSON) → 1 类型/数据层/状态 → 2 选择页/ → 3 贺野Home
→ 4 贺野地图 → 5 文章流 → 6 旅人录 → 7 数据扩充+上线
每阶段后：本地回归苏轼功能 → 通过再进下一阶段
```
