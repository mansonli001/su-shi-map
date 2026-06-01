# data-v4 数据规范

> **版本**：v4.0.0-phase1
> **生成日期**：2026-06-01
> **作用**：苏轼地图全节点数据层。**不替代旧 v3，并行存在**，前端通过 `NEXT_PUBLIC_DATA_VERSION` env 切换。
> **规模**：20 路线 / 233 唯一节点 / 8 类型

---

## 一、目录结构

```
data-v4/
├── README.md                         # 本文档
├── map-config.json                   # 全局配置（坐标系/类型枚举/颜色板）
├── places-index.json                 # 233 节点索引（轻量，前端首屏拉取）
├── places/                           # 详情层（按需 lazy load）
│   └── P001.json ~ P233.json         # Phase 2 由迁移脚本生成
├── routes-index.json                 # 20 路线索引
├── routes/                           # 路线详情
│   └── R00.json ~ R19.json
├── icons/                            # SVG 图标（10 种 type）
├── meta/                             # 工程元数据（gitignore 由 .gitignore 决定）
│   ├── places-master-raw.json        # Step 2 原始解析产物
│   ├── routes-parsed-raw.json        # Step 2 路线分块产物
│   ├── id-mapping-v3-to-v4.json      # Phase 2 旧 ID → P 编号映射
│   └── coordinate-whitelist.json     # 核心州府人工核校坐标白名单
└── scripts/                          # 数据建设脚本
    ├── extract-nodes-from-routes.ts  # Step 2 节点提取
    ├── build-coordinates.ts          # Step 4 补坐标
    ├── build-places-index.ts         # Step 5 生成索引
    └── build-routes.ts               # Step 5 生成路线骨架
```

---

## 二、ID 编码规范

| 实体 | 格式 | 范围 | 备注 |
|---|---|---|---|
| 节点 | `P001` ~ `P999` | 当前 P001-P233 | 按古名拼音排序分配，恒定不变 |
| 路线 | `R00` ~ `R19` | 当前 20 条 | 与订正版 V1 编号严格对齐 |
| 诗词 | `POEM_XXX` | Phase 2 引入 | 跨节点复用 |
| 事件 | `EV_XXX` | Phase 2 引入 | 跨节点复用 |

**铁律**：P 编号一旦分配，永不重用；新增节点用未占用最小编号。

---

## 三、节点类型（10 类，扩展自旧 6 类）

| type | 中文 | 用途 | priority | 示例 |
|---|---|---|---|---|
| `birth` | 出生地 | 一生独一 | 8 | 眉山 |
| `death` | 终老地 | 一生独一 | 7 | 常州 |
| `tomb` | 墓葬地 | 一生独一 | 7 | 郏县（小峨眉山） |
| `official` | 为官地 | 仕途节点 | 6 | 杭州、徐州、密州 |
| `main` | 主线行进 | 路线轨迹连点（驿道、渡口、中转州） | 5 | 利州、潼关、楚州 |
| `stay` | 驻留地 | 较长居住 | 5 | 黄州雪堂、惠州合江楼 |
| `study` | 游学地 | 少年求学 | 4 | 中岩寺 |
| `sight` | 沿途名胜 | 路过观赏（不在主线轨迹上） | 3 | 庐山、金山寺 |
| `visit` | 游览地 | 专程造访 | 3 | 鄱阳湖 |
| `around` | 驻留打卡 | 围绕驻留地的小点 | 2 | 沙湖、岐亭、白鹤峰 |

**渲染分层**：低 zoom 只显示 priority ≥ 6；高 zoom 显示全部。详见 `map-config.json#render_priority`。

---

## 四、坐标来源（coordinate_source 字段必填）

| 值 | 含义 | 精度 | trustworthy |
|---|---|---|---|
| `amap` | 高德地理编码反查 | ★★★★★ | true |
| `amap_corrected` | 高德 + 历史考证修正 | ★★★★★ | true |
| `chgis` | CHGIS V6 治所坐标 | ★★★★★ | true |
| `core_curated` | 核心州府人工核校（白名单） | ★★★★ | true |
| `inferred` | 现代名推断 / LLM 辅助 | ★★★ | false |
| `approximate` | 近似坐标（古址不存） | ★★ | false |
| `chgis_pending` | 待 Phase 2 用 CHGIS 校准 | ★★ | false |

**注**：`trustworthy: false` 的节点前端默认显示「考证中」icon，提示用户该坐标为示意。

---

## 五、places-index.json schema

```typescript
interface PlaceIndex {
  id: string;                    // "P001"
  ancient_name: string;          // "眉山"
  modern_name: string;           // "四川眉山"
  pinyin: string;                // "Meishan"
  type: PlaceType;               // 10 类之一
  layer: 'main' | 'sight' | 'around' | 'special';  // 'special' = birth/death/tomb 等人生节点
  lat: number;                   // GCJ-02
  lng: number;
  coordinate_source: CoordinateSource;
  trustworthy: boolean;
  importance: 1 | 2 | 3;         // 1=核心 / 2=次要 / 3=点缀
  display_priority: number;      // 1-8（来自 map-config.place_types[type].priority）
  tags: string[];                // ["北宋路：京西北路", "出生地", "三苏祠"]
  summary: string;               // 一句话 ≤50 字
  related_routes: string[];      // ["R00","R01","R04"]
  route_layers: { route_id: string; layer: 'main'|'sight'|'around'; order: number }[];
  has_detail: boolean;           // 是否存在 places/P001.json（Phase 2 起 true）
  verified: boolean;             // 是否已人工核校
  legacy: {
    ss_id?: string;              // 旧 SS001-SS160
    pinyin_id?: string;          // 旧 meishan / bianjing
  };
}
```

---

## 六、routes/R00.json schema

```typescript
interface RouteDetail {
  id: string;                    // "R00"
  index: number;                 // 0
  name: string;                  // "眉山故里 · 少年成长"
  period: string;                // "1037-1056"
  start_year: number;            // 1037
  end_year: number;              // 1056
  unique_color: string;          // 调色盘 #8B4513
  unique_color_dim: string;      // 淡化态 #C8B294

  description_short: string;     // ≤50 字（卡片用）
  description_long: string;      // 详情用

  // 主线 segments（可能多段，如出蜀+返程）
  track_segments: {
    segment_id: string;          // "R00-S01"
    label: string;               // "出蜀进京" / "母丧返程"
    place_ids: string[];         // ["P001","P012",...] 顺序连点
    transport_mode: 'land' | 'water' | 'mixed';
    distance_km?: number;        // Phase 2 计算
    duration_days?: number;
  }[];

  // 沿途 / 驻留（不在主线轨迹）
  sight_place_ids: string[];     // 标记不连线
  around_place_ids: string[];    // 标记不连线

  // 索引
  related_place_ids: string[];   // 全部涉及节点

  // 元数据
  source: string[];              // ["李常生《苏轼行踪考》", "网络公开资料整理"]
  schema_version: 'v4.0';
}
```

---

## 七、Phase 1 / Phase 2 边界

### Phase 1（当天交付，本轮）

- ✅ 233 节点 + 20 路线骨架
- ✅ `places-index.json` 含坐标（核心州府人工核校 + 推断 + 待 CHGIS 校准）
- ✅ `routes/R00-R19.json` 含 track_segments 占位
- ✅ schema 与 README 完整
- ⏳ 详情数据 `places/P*.json` **暂留空**

### Phase 2（后续迭代）

1. **详情迁移脚本**：旧 `places-detailed-v3.json` + `data/places/SS*.json` → 新 `places/P*.json`
   - 字段：background / extended_story / global_events / poems / memorial_sites / foods / transport
2. **CHGIS 真数据接入**：
   - 下载 V6 北宋时间切片
   - 用治所坐标批量校准 Phase 1 inferred 节点
   - 北宋路边界 GeoJSON 接入地图水墨化底图
3. **前端切换**：`NEXT_PUBLIC_DATA_VERSION=v4` env 灰度

---

## 八、构建命令速查

```bash
# Step 2：节点提取（已运行）
pnpm tsx data-v4/scripts/extract-nodes-from-routes.ts

# Step 4：补坐标（接核心白名单 + 推断）
pnpm tsx data-v4/scripts/build-coordinates.ts

# Step 5：生成最终 places-index.json + routes/R*.json
pnpm tsx data-v4/scripts/build-places-index.ts
pnpm tsx data-v4/scripts/build-routes.ts

# Phase 2：详情迁移
pnpm tsx data-v4/scripts/migrate-v3-detail.ts
```

---

## 九、数据来源声明

```
本项目所用苏轼路线、地点、诗词等数据，整理自互联网公开资料，
仅供个人学习与文化爱好者交流之用，不作为学术引用依据。
坐标与路线为示意性还原，如有错漏欢迎指正。
```

CHGIS 政区底图（Phase 2 接入后）将单独署名：
```
Data: CHGIS V6, © Fairbank Center for Chinese Studies, Harvard University
& 复旦大学历史地理研究所, licensed under CC-BY 4.0.
```
