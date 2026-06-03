# 苏轼地图 v4 数据完整度体检报告

生成时间：2026-06-01T10:18:02.314Z

## 一、总体盘点

- 节点总数：**234**
- 有详情文件：**207** / 无详情文件：**27**

## 二、字段填充率

| 字段 | 填充情况 |
|---|---|
| `summary` | 103/234 (44%) |
| `background` | 197/234 (84%) |
| `tags` | 197/234 (84%) |
| `periods` | 69/234 (29%) |
| `global_works` | 53/234 (23%) |
| `memorial_sites` | 100/234 (43%) |
| `foods` | 3/234 (1%) |
| `transport` | 103/234 (44%) |
| `route_events` | 196/234 (84%) |

## 三、完整度分布

| 区间 | 节点数 |
|---|---|
| 0%（空壳） | 30 |
| 1-30%（严重缺） | 7 |
| 31-60%（半缺） | 98 |
| 61-89%（基本齐） | 98 |
| 90-100%（完整） | 1 |

## 四、按节点类型

| 类型 | 节点数 | 平均完整度 |
|---|---|---|
| sight | 57 | 30% |
| main | 98 | 49% |
| around | 61 | 54% |
| study | 1 | 11% |
| death | 1 | 78% |
| official | 11 | 88% |
| birth | 2 | 78% |
| stay | 3 | 89% |

## 五、按路线

| 路线 | 节点数 | 无详情数 | 平均完整度 |
|---|---|---|---|
| R00 | 13 | 1 | 47% |
| R01 | 27 | 2 | 47% |
| R02 | 18 | 3 | 34% |
| R03 | 22 | 2 | 44% |
| R04 | 24 | 1 | 53% |
| R05 | 14 | 3 | 47% |
| R06 | 22 | 0 | 70% |
| R07 | 15 | 0 | 64% |
| R08 | 14 | 3 | 51% |
| R09 | 17 | 0 | 63% |
| R10 | 14 | 2 | 53% |
| R11 | 14 | 0 | 66% |
| R12 | 10 | 2 | 44% |
| R13 | 12 | 1 | 48% |
| R14 | 14 | 2 | 64% |
| R15 | 11 | 2 | 60% |
| R16 | 11 | 0 | 66% |
| R17 | 13 | 1 | 49% |
| R18 | 28 | 1 | 63% |
| R19 | 26 | 1 | 60% |

## 六、最缺数据的 30 个节点（重点补）

| ID | 古名 | 现名 | 类型 | 路线 | 完整度 | 缺失字段 |
|---|---|---|---|---|---|---|
| P029 | 大别山边缘古道 | 大别山北缘古道 | sight | R10 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P043 | 凤县 | 陕西凤县 | main | R01 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P047 | 赣江古道 | 江西赣江古道 | sight | R19 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P057 | 汉中栈道 | 陕西汉中古栈道 | sight | R05 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P063 | 洪泽湖沿岸 | 江苏洪泽湖沿岸 | sight | R15 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P067 | 华山远眺 | 陕西华阴华山 | sight | R03 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P070 | 淮河南岸古驿 | 淮河南岸驿道 | sight | R10 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P082 | 江淮水乡驿道 | 江淮水乡古驿 | sight | R14 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P085 | 江南运河 | 江南运河（苏州段） | sight | R14 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P088 | 胶东半岛古道 | 山东胶东半岛古道 | sight | R12 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P093 | 夔门三峡 | 长江三峡（瞿塘峡） | sight | R02 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P096 | 乐山大佛 | 四川乐山大佛 | sight | R02 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P102 | 临沂 | 山东临沂 | main | R08 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P114 | 洛阳龙门 | 河南洛阳龙门石窟 | sight | R01 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P130 | 彭山江口 | 四川彭山江口 | sight | R00 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P137 | 秦岭古驿 | 陕西秦岭古驿 | sight | R05 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P149 | 三峡全程 |  | sight | R04 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P157 | 泗水古道 | 山东泗水古道 | sight | R08 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P160 | 苏北沿海驿道 | 江苏苏北沿海 | sight | R12 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P167 | 太学 | 河南开封太学旧址 | around | R15 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P172 | 潼关渡口 | 陕西潼关渡口 | sight | R01 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P183 | 西江山水 | 广东西江山水 | sight | R18 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P184 | 相国寺 | 河南开封大相国寺 | around | R05 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P189 | 崤山二陵 | 河南三门峡崤山二陵 | sight | R01 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P190 | 崤山古道 | 河南三门峡崤山古道 | sight | R03 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P202 | 沂蒙山 | 山东沂蒙山 | sight | R08 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P204 | 宜宾锁江楼 | 四川宜宾锁江楼 | sight | R02 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P218 | 漳河渡口 | 河北漳河渡口 | sight | R17 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P225 | 长江沿岸渡口 | 长江中游渡口 | around | R02 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
| P231 | 资善堂 | 河南开封资善堂旧址 | around | R13 | 0% | summary, background, tags, periods, global_works, memorial_sites, foods, transport, route_events |
