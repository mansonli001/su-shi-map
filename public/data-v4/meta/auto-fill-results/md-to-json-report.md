# B1 .md → JSON 转换器报告

生成时间：2026-06-01T10:22:05.268Z

## 统计
- 路线 .md 解析: 19/20
- .md 中点位总数: 343
- 匹配 P 编号成功: 276
- 未匹配: 67
- places/*.json 更新: 276
- places/*.json 新建: 0
- routes/*.json 更新: 19

## 工作流
1. 读取 data-v4-source/R*.md 并 YAML 解析
2. 更新 routes/R*.json（description_long / core_essence / key_events / literary_output / route_position）
3. 按 ancient_name 匹配到 places-index.json 的 P 编号
4. 灌入 places/P*.json 的 background / extended_story / tags / route_events / global_works / source

## 未匹配清单
见 md-place-unmatched.md
