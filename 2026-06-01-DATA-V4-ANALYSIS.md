# 苏轼地图 v4.x 数据架构分析报告
**日期**：2026-06-01
**作者**：Linus（CTO）
**目的**：在不动旧数据的前提下，对比新计划 V1.0 与现有 v3 数据，给出"新建 data-v4/ 目录"的最优数据结构建议
**铁律**：旧数据已全量备份至 `data/legacy-v3-backup-2026-06-01/`，本轮**不修改、不删除任何旧文件**。

---

## 一、事实对账：新旧数据真实差距

### 1.1 数据规模

| 维度 | 旧数据（v3，线上） | 新计划 V1.0 | 差距 |
|---|---|---|---|
| 唯一点位 | 77 个（`places-detailed-v3.json`） | 90 个 | +13 |
| 详情文件 | 120 个（`data/places/SS*.json`） | — | 旧的更多，但有重复/废 |
| `places-core.json` 行数 | 160 行 | — | 旧的是"路线-地点"组合，含重复 |
| 路线数 | 19 条（route01-route19） | **20 条**（Route0-Route19） | +1（新增 Route0「眉山故里·少年成长」） |
| 路线起点 | route01 = 第一次出蜀 | Route0 = 少年成长 | 新计划把"在眉山的少年时期"独立成 Route0 |

### 1.2 ID 体系混乱（旧数据的最大原罪）

旧数据**三套 ID 并存**：
- `places-detailed-v3.json` → 拼音 key（`meishan` / `bianjing` / `huangzhou`）
- `data/places/SS*.json` → SS001~SS160 数字编码
- 各种内部 `id` 字段 → `ms-001` / `cd-002` / `ss-s001` 等

**结果**：`routes-v3.json` 里 `place_ids` 用拼音引用 detailed-v3，但 `places-core.json` / `places-index.json` 用 SS 编号，前端要做两次映射，每次改数据都得对三个文件。

新计划 V1.0 用 **P001-P090 单一编码**，干净，但这套编码**没有给 detail 详情留扩展位**（见 2.2 节）。

### 1.3 类型体系

| 旧 v3（6 类） | 新 V1.0（8 类） | 变化 |
|---|---|---|
| birth | birth | 保留 |
| official | official | 保留 |
| exile（贬谪） | — | **删除**（合并到 official 或 stay？没说明） |
| tour | visit | 重命名 |
| friend（友人） | — | **删除**（V1.0 没这个语义） |
| grave | tomb | 重命名 |
| — | main（主线行进点） | **新增**（驿道、渡口、中转州县） |
| — | stay（普通驻留） | **新增**（别院、客舍、临时居所） |
| — | study（游学地） | **新增**（少年求学、书院研学） |
| — | death（离世地） | **新增**（终老之地，独立于 birth/tomb） |

**结论**：新类型体系**严谨度更高**，把"主线行进 vs 真正驻留 vs 游览"三者拆开，避免旧版"tour 一锅炖"。8 类正好对应 8 个 SVG 图标，前后端一致。**这是新数据的关键升级，必须保留。**

---

## 二、新计划 V1.0 的硬伤（必须补的字段）

V1.0 给的 `global_places` 节选格式：

```json
{
  "place_id": "P001",
  "type": "birth",
  "ancient_name": "眉山",
  "modern_name": "四川眉山",
  "lat": 30.0431, "lng": 103.8467,
  "svg_icon": "birth",
  "note": "苏轼出生地，少年成长与游学核心地",
  "related_poem": ""
}
```

**8 个字段，详情数据完全没考虑**。对比旧 detailed-v3 的 23 个字段：

### 2.1 V1.0 缺失但旧数据有的字段（必须迁移过来）

| 旧字段 | 旧示例 | V1.0 是否需要 | 理由 |
|---|---|---|---|
| `summary` | "苏轼出生地，在此生活约32年..." | **必须有** | 一句话概括，PlaceCard 半屏抽屉用 |
| `background` | "眉山是苏轼的出生地和故乡..." | **必须有** | 背景介绍，详情页 Hero 下方用 |
| `tags` | ["出生地","故乡","三苏祠"] | 必须有 | 详情页 chip 展示 + 搜索过滤 |
| `name_pinyin` | "Meishan" | 建议有 | 拼音搜索（虽然 Fuse.js 也能扛中文，但拼音输入法用户友好） |
| `global_events` | 数组（事件 id/date/title/desc/significance） | **必须有** | 详情页 Tabs 的「事迹」核心数据 |
| `global_works` | 数组（诗词/文章作品） | 必须有 | 详情页 Tabs 的「诗词」核心数据 |
| `route_events` | 按路线分组的事件 | **必须有** | 切换路线时显示"在这条路线里发生了什么" |
| `route_works` | 按路线分组的作品 | 建议有 | 同上 |
| `route_order` | 按路线分组的次序 | **必须有** | 路线主线绘制顺序 |
| `route_arrival` / `route_departure` | 抵达/离开时间 | 建议有 | Timeline 用、详情页时间轴用 |
| `memorial_sites` | 现代纪念地数组（祠堂/景区，含票价/开放时间/url） | **必须有** | 详情页 Tabs 的「纪念地」 |
| `foods` | 美食数组 | 建议有 | 详情页 Tabs 的「美食」 |
| `transport` | {train, bus, car, airport} | 建议有 | 详情页 Tabs 的「交通」 |
| `sub_places` | 子地点（同城多点位） | 建议有 | 处理"眉山三苏祠 vs 眉山东坡湖"这种 |
| `source` | "李常生《苏轼行踪考》" | **必须有** | 数据可追溯性 |

### 2.2 V1.0 没考虑的扩展字段（未来必踩坑，提前预留）

| 字段 | 用途 | 现在必须吗 |
|---|---|---|
| `extendedStory` | 长文叙事（旧 SS\*.json 有 markdown 长文） | 建议有，文化内容核心 |
| `poems` 完整结构 | 含 fullText/translation/analysis/sourceUrl | 必须有 |
| `attractions` | 现代景点（区别于 memorial_sites，含游玩信息） | 建议有 |
| `images` | 图片数组（首图 + 配图） | **必须有**（详情页 Hero 大图） |
| `image_blur_data` | base64 blur placeholder | 推荐有（性能优化） |
| `externalLinks` | 外部链接（古诗文网/官方景区/参考资料） | 建议有 |
| `coordinate_source` | 坐标来源（高德/百度/手测/史料推断） | **建议有**（V1.0 强调 GCJ-02 严谨度，但没标坐标如何得来） |
| `verified` | bool（是否已核校） | **建议有**（标记哪些是确证、哪些是推断） |
| `display_priority` | 渲染优先级数字 | V1.0 在 §2.1 表里有渲染优先级 8/4/5/6/3/5/2/1，**建议落到字段里**，而不是前端写死 |
| `popup_template` | 弹窗模板版本（v1/v2） | 推荐有，方便未来 A/B |

### 2.3 V1.0 路线结构的不足

V1.0 的 routes 结构：
```json
{
  "route_id": 0,
  "route_name": "眉山故里·少年成长",
  "period": "1037-1056",
  "description": "...",
  "unique_color": "#8B4513",
  "track_coords": [{"lat":30.0431,"lng":103.8467}],
  "related_place_ids": ["P001","P003","P004"]
}
```

**缺的字段**：

| 字段 | 旧 v3 是否有 | 必要性 |
|---|---|---|
| `start_date` / `end_date` | **有**（"嘉祐元年（1056年）三月" 等精确到月） | **必须有**（period 太粗，不够 timeline 用） |
| `description_short` | 无 | 建议有（卡片用） |
| `description_long` | 旧 description 较长 | 必须有 |
| `key_events` | 无 | 建议有（路线主要事件 3-5 个） |
| `key_poems` | 无 | 建议有（路线代表诗词） |
| `route_color_dim` | 无 | 推荐有（淡化态颜色，不是前端硬编码 #E0E0E0） |
| `track_segments` | V1.0 用 `track_coords` 一维数组 | **建议改为 segments**：一段一段（带每段起点/终点/距离/方式：陆路/水路） |
| `total_distance_km` | 无 | 建议有（数据展示亮点） |
| `transport_modes` | 无 | 建议有（["陆路","水路","三峡水路"]） |
| `historical_period` | 无 | 建议有（与皇帝年号对应：仁宗/英宗/神宗/哲宗/徽宗） |
| `political_context` | 无 | 建议有（一句话政治背景：变法/元祐更化/绍圣党禁） |
| `source_pages` | 无 | 建议有（《行踪考》具体页码，可追溯） |

---

## 三、推荐数据结构方案：v4.0 单一目录 + 双层文件 + 全详情

### 3.1 设计原则

1. **唯一 ID**：`P001-P0NN` 全局点位 + `R00-R19` 路线编号（V1.0 思路）
2. **双层存储**：
   - 索引层 `places-index.json`（轻量，列表/搜索/地图标记用，单文件）
   - 详情层 `places/P001.json`（厚重，详情页用，按需 lazy load）
3. **路线主线坐标独立**：`routes/R00.json` 单条独立，方便编辑
4. **保留扩展位**：所有「非核心」字段都用可选字段，初期可空，后续渐进填充
5. **新建目录 `data-v4/`**：和旧 v3 完全隔离，前端通过 feature flag 切换

### 3.2 推荐目录结构

```
data-v4/
├── README.md                 # 数据规范、字段说明、ID 编码规则
├── map-config.json           # 全局配置（坐标系/默认视图/线宽/类型枚举/颜色板）
├── places-index.json         # 90 条点位索引（轻量，~30KB）
├── places/                   # 详情层
│   ├── P001.json             # 单点完整详情（事迹/诗词/纪念地/美食/交通/图片）
│   └── ...
├── routes-index.json         # 20 条路线索引（轻量）
├── routes/                   # 路线详情
│   ├── R00.json              # 单路线（含 track_segments、key_events、source_pages）
│   └── ...
├── icons/                    # 8 个 SVG 图标
│   ├── marker-main.svg
│   └── ...
└── meta/
    ├── id-mapping-v3-to-v4.json  # 旧拼音/SS ID → 新 P 编号映射，迁移用
    ├── poems-master.json          # 全部诗词（去重，被 places 引用）
    └── verified-status.json       # 哪些点已核校、哪些待核校
```

### 3.3 关键 schema（建议版，可改）

#### 3.3.1 `places-index.json` 单条（索引层，轻）

```typescript
interface PlaceIndex {
  id: string;                  // "P001"
  type: PlaceType;             // 8 类枚举
  song_name: string;           // 古名
  modern_name: string;         // 现代名
  pinyin: string;              // 搜索用
  lat: number;                 // GCJ-02
  lng: number;
  coordinate_source: 'amap' | 'inferred' | 'historical';
  importance: 1 | 2 | 3;       // 渲染分层
  display_priority: number;    // 1-8（V1.0 表里的优先级）
  tags: string[];              // ["出生地","三苏祠"]
  summary: string;             // 一句话（≤50字）
  related_routes: string[];    // ["R00","R02","R04"]
  has_detail: boolean;         // 是否有 places/P001.json
  verified: boolean;           // 是否已核校
}
```

#### 3.3.2 `places/P001.json` 单点详情（厚重，按需 load）

```typescript
interface PlaceDetail {
  id: string;
  // 1. 基本（与 index 重复，便于单文件可用）
  type: PlaceType;
  song_name: string;
  modern_name: string;
  lat: number; lng: number;

  // 2. 描述
  background: string;          // 背景（2-3句）
  extended_story: string;      // markdown 长文（可选）

  // 3. 时间事件（关键改进：拆 global / route）
  global_events: Event[];      // 全局事件（不分路线）
  route_events: Record<string, Event[]>;  // {"R02":[...]} 按路线分组

  // 4. 文学作品
  poems: Poem[];               // 关联诗词（含 fullText/translation/analysis）
  prose: Prose[];              // 关联文章

  // 5. 路线参与（每条路线在此地停留的元数据）
  route_participations: {
    [routeId: string]: {
      order: number;            // 在该路线中的次序
      arrival: string;          // "嘉祐元年（1056年）三月"
      departure: string;
      duration_days?: number;
      role: 'origin' | 'transit' | 'destination' | 'side_trip';
    }
  };

  // 6. 现代信息
  memorial_sites: MemorialSite[];   // 纪念地（祠堂/博物馆）
  attractions: Attraction[];        // 旅游景点
  foods: Food[];                    // 当地美食
  transport: Transport;             // 交通信息
  sub_places: SubPlace[];           // 子点位（同城多点）

  // 7. 媒体
  images: Image[];                  // {url, blur_data, alt, source}
  external_links: Link[];

  // 8. 元数据
  source: string[];                 // ["李常生《苏轼行踪考》P38-P52"]
  verified: boolean;
  last_updated: string;             // ISO date
  schema_version: 'v4.0';
}
```

#### 3.3.3 `routes/R00.json` 路线详情

```typescript
interface RouteDetail {
  id: string;                       // "R00"
  index: number;                    // 0
  name: string;
  period: string;                   // "1037-1056"
  start_date: string;               // "景祐三年（1037年）十二月"
  end_date: string;                 // "嘉祐元年（1056年）三月"
  historical_period: string;        // "仁宗朝"
  political_context: string;        // 一句话政治背景

  description_short: string;        // 卡片用 ≤50 字
  description_long: string;         // 详情页用

  unique_color: string;             // #8B4513
  unique_color_dim: string;         // #C8B294（淡化态）

  // 主线 segments（一段一段，比 V1.0 的 coords 一维数组更可扩展）
  track_segments: {
    from_place_id: string;
    to_place_id: string;
    coords: { lat: number; lng: number }[];
    transport_mode: 'land' | 'water' | 'mixed';
    distance_km?: number;
    duration_days?: number;
  }[];

  // 索引/关联
  related_place_ids: string[];      // 该路线涉及的所有点位
  key_events: Event[];              // 路线主要事件 3-5 个
  key_poems: string[];              // 路线代表诗词 id

  // 统计
  total_distance_km?: number;
  total_duration_days?: number;
  transport_modes: ('land' | 'water')[];

  // 元数据
  source: string[];
  source_pages?: string;            // 《行踪考》P38-P52
  verified: boolean;
  schema_version: 'v4.0';
}
```

---

## 四、新旧路线编号对照（关键）

V1.0 的 Route0-19 与旧 route01-19 不是简单平移：

| V1.0 | V1.0 名称 | 旧 v3 | 旧 v3 名称 | 关系 |
|---|---|---|---|---|
| **Route0** | 眉山故里·少年成长 | 无 | — | **新增** |
| Route1 | 首次出蜀·京城赶考 | route01 | 第一次出蜀赴京 | 对应 |
| Route2 | 高中进士·丁忧返乡 | route02 | 第二次出蜀与三苏《南行集》 | **可能错位**（需考证） |
| Route3 | 二次出蜀·南行漫游 | route02 | 第二次出蜀 | **重叠**（V1.0 把 02 拆成 02+03？） |
| Route4 | 凤翔任官·初入仕途 | route03 | 第二次进京与凤翔签判 | 对应 |
| Route5 | 父丧归蜀·往返京蜀 | route04 | 第三次入京与父丧返乡 | 对应 |
| Route6 | 杭州通判·西湖初筑 | route06 | 任杭州倅 | 对应 |
| Route7 | 密州知州·超然台上 | route07 | 知密州 | 对应 |
| Route8 | 徐州治水·黄楼铭记 | route08 | 知徐州 | 对应 |
| Route9 | 乌台诗案·贬谪黄州 | route09+route10 | 知湖+贬谪黄州 | **V1.0 把两条合并成一条** |
| Route10 | 量移汝州·庐山问道 | route11 | 量移汝州与庐山之游 | 对应 |
| Route11 | 登州五日·短期入朝 | route12 | 万里来去知登州 | 对应 |
| Route12 | 礼部尚书·元祐在京 | route13 | 第六次入京 | 对应 |
| Route13 | 再知杭州·苏堤春晓 | route14 | 再知杭州 | 对应 |
| Route14 | 定州太守·河北戍边 | route17? | 知定州 | 需对照 |
| Route15 | 南迁惠州·远赴岭南 | route18? | 贬谪惠州 | 需对照 |
| Route16 | 再贬儋州·海外孤臣 | route19? | 贬谪儋州 | 需对照 |
| Route17 | 遇赦北归·万里返程 | — | — | 新增独立 |
| Route18 | 常州病逝·人生终点 | — | — | 新增独立 |
| Route19 | 苏轼遗迹·后世巡礼 | — | — | **后世巡礼，非苏轼本人路线** |

**关键问题（需要你回答）**：
- Q1：V1.0 Route2 和 Route3 是不是同一段被拆了？还是真有两次南行？
- Q2：V1.0 Route9 把"知湖州+乌台诗案+贬黄州"合并对吗？还是其实是 3 段？
- Q3：V1.0 Route19 是"后世巡礼"（不是苏轼本人路线），需要在数据结构里加 `is_meta: true` 标记，前端**默认隐藏**，避免和真实路线混展。

---

## 五、关键设计决策（建议你拍板）

### 决策 1：用 V1.0 的 8 类还是旧 6 类？
**推荐**：用 V1.0 的 8 类（main / visit / stay / study / birth / official / death / tomb）。理由：拆得更细、对应 8 个 SVG、人生节点突出。

### 决策 2：用 P001 还是保留拼音 ID？
**推荐**：用 V1.0 的 `P001-P0NN`，但额外存 `legacy_pinyin_id` 和 `legacy_ss_id` 在 meta 里方便迁移。

### 决策 3：路线坐标用 `track_coords`（V1.0 一维）还是 `track_segments`（推荐二维）？
**推荐**：`track_segments`。理由：未来要加"陆路/水路/三峡水路"模式区分、距离统计、动画分段播放，一维数组撑不起来。

### 决策 4：详情数据怎么从旧数据迁移？
**推荐**三步：
1. 用 V1.0 的 90 个点位 ID + 坐标作为基线（结构骨架）
2. 写一份 `meta/id-mapping-v3-to-v4.json`：每个 P 编号 → 旧 SS\* / 旧拼音 ID（人工对一遍，或者 AI 跑相似度）
3. 跑一次脚本：依据映射，把旧 detailed-v3 + SS\*.json 的内容**自动迁移**到新 places/P\*.json。新数据没有的字段保留为空，慢慢补。

### 决策 5：前端怎么切换？
**推荐**：
- 加 `NEXT_PUBLIC_DATA_VERSION` 环境变量（`v3` / `v4`）
- 默认 `v3`（线上不动）
- dev 跑 `v4` 验证
- 验证 OK 后 push v4 上线，v3 文件保留 1 个月作为回滚位

### 决策 6：V1.0 提到的"复合点位"（一地多属性，主图标 + 角标）数据怎么存？
**推荐**：在 PlaceDetail 加 `secondary_types: PlaceType[]` 字段，例：眉山是 `birth`（主），但同时有 `stay`（家宅）、`tomb`（程夫人墓）属性。前端遇到 `secondary_types.length > 0` 就渲染右下角角标。

### 决策 7：路线 Route19「后世巡礼」要不要进数据？
**两条路**：
- A：进数据，加 `is_meta: true`，前端默认隐藏，"现代旅游模式"里出现
- B：不进数据，等"现代旅游模式"产品做出来再说

**建议 A**，结构留好，未来不用动数据架构。

---

## 六、迁移成本估算

| 任务 | 工作量 | 谁做 |
|---|---|---|
| 1. 写 `data-v4/README.md` + 全部 schema 类型定义 | 0.5d | AI |
| 2. 把 V1.0 的 90 点位 + 20 路线 + 8 SVG 录入到 `data-v4/`（**只录基础字段**） | 1d | 你给数据，AI 录入 |
| 3. 写 `id-mapping-v3-to-v4.json`（人工对照） | 0.5d | **你做**（AI 没有考证能力，对不准） |
| 4. 写迁移脚本 `scripts/migrate-v3-to-v4.ts`（自动把旧详情塞进新 P 文件） | 0.5d | AI |
| 5. 跑迁移脚本，人工抽查 10 个点位 | 0.5d | AI 跑 + 你抽查 |
| 6. 前端加 `NEXT_PUBLIC_DATA_VERSION` 切换 + lib/data-loader.ts 抽象层 | 0.5d | AI |
| 7. dev 验证 + 三大冒烟用例（地图/路线/marker） | 0.5d | AI + 你确认 |
| 8. 上线 v4，v3 备份 | 0.25d | AI |

**合计：约 4.25 天**，分 2-3 轮交付。

---

## 七、最终建议（一句话）

**采用 V1.0 的 ID/类型/路线设计骨架 + 旧 v3 的详情字段厚度 + 我给的 schema 扩展位**，新建 `data-v4/` 目录，旧 v3 完全冻结。**第一步只录 90 点位 + 20 路线的基础字段（纯骨架）让前端先跑起来，详情数据按页迁移，慢慢喂。**

---

## 八、等你拍板的事

请回复以下 7 个决策：

1. ✅ 8 类 type 拍板？（推荐 V1.0 的）
2. ✅ ID 用 P001-P0NN？（推荐）
3. ✅ 路线坐标用 segments 而不是一维 coords？（推荐）
4. ✅ 新建 `data-v4/` 目录？（推荐）
5. ❓ Route2/3 是真两条还是一条拆开？
6. ❓ Route9 是真合并还是分 3 段？
7. ❓ Route19「后世巡礼」是否进数据（建议加 `is_meta` 标记）？

回复后我开始按计划落地。
