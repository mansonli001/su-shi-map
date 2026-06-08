---
name: "sxzk-gps-methodology"
description: "《苏轼行踪考》GPS精细化方法论。从行踪考提取具体子地点，按居住/游览分层，以首个居住地为主坐标，游览点为文旅推荐。适用于GPS坐标、著作、美食等所有数据提取。Invoke when processing place GPS, sub-places, works locations, or food origins from 苏轼行踪考."
---

# 《苏轼行踪考》数据精细化方法论

## 一、核心理念

**不能给一个省/市一个GPS就完事。** 苏轼在黄州住了4年，去过6个具体地点，每个地点都有不同的意义。我们的目标是：

> 从《苏轼行踪考》中提取苏轼在每个城市的**具体活动地点**，按居住/游览分层，以**第一个居住地**作为主坐标，其他地点作为文旅推荐点。

## 二、地点分层模型

每个v4地点（place）包含三层子地点（sub_places）：

### 层级1：居住地（residence）— 决定主坐标
- 苏轼在该城市的**居住场所**
- 按时间顺序排列
- **第一个居住地 = 该城市的主GPS坐标**
- 后续居住地作为次坐标

### 层级2：核心游览地（scenic/primary）— 文旅主推荐
- 苏轼创作名篇的具体地点
- 现有纪念景点/遗址（如东坡赤壁、苏堤）
- 优先使用现有纪念景点的精确坐标

### 层级3：补充游览地（scenic/secondary）— 文旅补充
- 苏轼游览但非核心的地点
- 寺庙、亭台等

## 三、GPS坐标获取优先级

```
1. 现有纪念景点/遗址坐标（最可靠）
   ↓ 找不到时
2. 《苏轼行踪考》中明确标注的"今XX省XX市XX区XX路"
   ↓ 找不到时
3. 高德POI搜索（关键词：城市名+地点名）
   ↓ 找不到时
4. 高德地理编码（省市区+地点名）
   ↓ 仍找不到
5. 标记为"待考证"，不使用模糊坐标
```

**绝对禁止**：
- 用省/市级宽泛坐标代替具体地点
- 用其他城市的同名地点坐标（如麻城定慧寺代替黄州定慧院）
- 用推断坐标填充

## 四、数据处理Pipeline

### Step 1：从《苏轼行踪考》提取子地点

从该地点的v4 JSON文件中提取：
- `global_events` → 居住地信息（"寓居XX"、"移居XX"）
- `global_works` → 创作地点（`location`字段）
- `memorial_sites` → 现有纪念景点
- `route_events` → 路线中的地点描述

输出格式：
```json
{
  "sub_places": [
    {
      "name": "定慧院",
      "ancient_name": "定慧院",
      "type": "residence",
      "period": "1080年2月-1080年冬",
      "description": "苏轼初到黄州的居所",
      "works": ["卜算子·黄州定慧院寓居作"],
      "importance": "primary",
      "lat": null,
      "lng": null,
      "modern_address": "",
      "coordinate_source": "",
      "verification_status": "pending"
    }
  ]
}
```

### Step 2：查找现代地址和GPS

对每个子地点：
1. 搜索现代是否有同名纪念景点
2. 搜索《苏轼行踪考》中是否有"今XX地址"的标注
3. 调用高德API获取坐标
4. **验证坐标是否在正确城市范围内**（经纬度偏差检查）

### Step 3：坐标验证

验证规则：
- 坐标必须在对应城市行政区范围内
- 同一城市的子地点之间距离不应超过50公里
- 如果坐标偏离城市中心超过30公里，标记为"待验证"
- 每个坐标必须有`coordinate_source`标记

### Step 4：写入数据

**仅当验证通过时**才更新v4 JSON文件：
- 主坐标（第一个居住地）→ 更新`lat`、`lng`、`coordinate_source`
- 所有子地点 → 写入`sub_places`数组
- `memorial_sites`中匹配的地点补充坐标

## 五、数据字段规范

### sub_places中每个子地点必须包含：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 现代名称 |
| ancient_name | string | 是 | 古代名称 |
| type | enum | 是 | residence/scenic/temple/office |
| period | string | 是 | 苏轼在此的时间段 |
| description | string | 是 | 该地点的说明 |
| works | array | 否 | 在此创作的作品列表 |
| importance | enum | 是 | primary/secondary |
| lat | float | 是 | 纬度（验证后填写） |
| lng | float | 是 | 经度（验证后填写） |
| modern_address | string | 是 | 现代详细地址 |
| coordinate_source | enum | 是 | memorial_site/sxzk_extracted/amap_poi/amap_geocode |
| verification_status | enum | 是 | pending/verified/rejected |

### coordinate_source枚举值说明：

| 值 | 含义 | 可信度 |
|----|------|--------|
| memorial_site | 现有纪念景点/遗址坐标 | 最高 |
| sxzk_extracted | 《苏轼行踪考》明确标注的地址 | 高 |
| amap_poi | 高德POI搜索结果 | 中 |
| amap_geocode | 高德地理编码结果 | 低 |

## 六、验证检查清单

每个地点处理完成后，必须通过以下检查：

- [ ] 主坐标是否来自第一个居住地？
- [ ] 主坐标是否在该城市行政区范围内？
- [ ] 所有子地点坐标是否在正确城市范围内？
- [ ] 是否有同名但不同城市的错误匹配？（如麻城定慧寺 vs 黄州定慧院）
- [ ] 每个坐标是否都有coordinate_source标记？
- [ ] 每个坐标是否都有verification_status标记？
- [ ] memorial_sites中的地点是否已补充坐标？

## 七、扩展应用

此方法论不仅适用于GPS坐标，还可扩展至：

### 著作定位
- 每首诗/词的创作地点 → 关联到具体sub_place
- 按时间顺序标注创作地点变化

### 美食溯源
- 每道东坡美食的发明地点 → 关联到具体sub_place
- 区分"发明地"和"传播地"

### 文旅推荐
- 基于sub_places生成游览路线
- 区分"必去"（primary）和"可选"（secondary）

## 八、黄州示范案例

### 输入：P072 黄州

从v4数据提取的子地点：

| 序号 | 名称 | 类型 | 时期 | 重要性 | 坐标来源 |
|------|------|------|------|--------|----------|
| 1 | 定慧院 | residence | 1080年2月-冬 | primary | memorial_site |
| 2 | 临皋亭 | residence | 1080年冬-1084年 | secondary | historical |
| 3 | 东坡雪堂 | residence | 1082年后 | secondary | memorial_site |
| 4 | 赤壁 | scenic | - | primary | memorial_site |
| 5 | 安国寺 | temple | - | secondary | amap_geocode |
| 6 | 承天寺 | temple | - | secondary | amap_geocode |

### 主坐标决策
- 第一个居住地 = 定慧院
- 主坐标 = 定慧院坐标 (30.4486, 114.8789)
- coordinate_source = sxzk_extracted

### 验证结果
- 所有坐标在黄冈市黄州区范围内 ✅
- 无同名异地错误 ✅
- 每个坐标有source标记 ✅
