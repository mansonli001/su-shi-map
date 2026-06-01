# CHGIS（中国历史地理信息系统）数据接入说明

## 数据来源

- **项目**：CHGIS — China Historical GIS
- **机构**：哈佛费正清中心（Fairbank Center for Chinese Studies, Harvard University）& 复旦大学历史地理研究所
- **版本**：CHGIS V6（推荐使用）
- **协议**：CC-BY 4.0（**必须署名引用**，不能模糊处理）
- **下载入口**：
  - 哈佛 Dataverse：https://dataverse.harvard.edu/dataverse/chgis
  - 复旦镜像：http://yugong.fudan.edu.cn/chgis/

## 引用规范（README 致谢段必须出现）

```
Data: CHGIS V6, © Fairbank Center for Chinese Studies, Harvard University
& 复旦大学历史地理研究所, licensed under CC-BY 4.0.
https://sites.fas.harvard.edu/~chgis/
```

## 本项目用途

| 用途 | 数据文件 | 状态 |
|---|---|---|
| 北宋路（一级行政区）边界水墨化叠加 | `song-routes.geojson`（裁剪版） | Phase 2 待接入 |
| 北宋州/府/县治所点坐标参考 | `song-prefectures.geojson`（裁剪版） | Phase 2 校准用 |
| 古址不存节点（如徐闻递角场、岐亭、兴廉村净行院）坐标推断 | 手工查表 | Phase 2 |

## 目录结构

```
data-v4-source/chgis/
├── README.md                    # 本说明（git tracked）
├── raw/                         # 原始 V6 shapefile + zip（gitignore，不入库）
│   ├── v6_1820_pref_pgn.shp
│   └── ...
├── v6/                          # 解压中间产物（gitignore）
├── song-prefectures.geojson     # 加工后的北宋治所点（git tracked，预估 < 200KB）
└── song-routes.geojson          # 加工后的北宋路边界（git tracked，预估 < 500KB）
```

## Phase 1 与 CHGIS 的关系

**Phase 1 不依赖 CHGIS**。Phase 1 节点坐标主要来源：
1. 现代州县同名 → 走高德地理编码（约 80% 节点覆盖）
2. 古址不存的小驿站/渡口/古寺 → LLM 推断 + 标注 `coordinate_source: "inferred"`

**Phase 2 才接入 CHGIS**：
- 用治所坐标校准 Phase 1 的高德结果（精度提升）
- 用政区边界画一层水墨化北宋"路"图层
- 用 CHGIS 反查 inferred 节点的精确坐标

## 下载步骤（Phase 2 时执行）

```bash
# 哈佛 Dataverse 需要一个简单的署名表单（学术免费），下载 CHGIS V6 全量包
# 推荐只取北宋（960-1279）时间切片：1080年与1100年两个 timestamp
# 关键文件：v6_1820CE_pref_pgn.shp（实际取 1080CE/1100CE 切片）

# 解压到 raw/，再用 ogr2ogr 转 GeoJSON 并按 dynasty="北宋" 裁剪
ogr2ogr -f GeoJSON song-prefectures.geojson \
  raw/v6_pref_pts_utf.shp \
  -where "BEG_YR <= 1101 AND END_YR >= 1037 AND DYN_CH LIKE '宋%'"
```

> 实操由 Phase 2 单独 issue 跟进。Phase 1 不阻塞。
