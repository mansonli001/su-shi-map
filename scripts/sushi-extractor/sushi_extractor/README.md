# 《苏轼行踪考》智能提取流水线

## 安装依赖
```bash
pip install anthropic python-docx pdfplumber tqdm requests supabase
```

## 使用流程

### 第一步：测试切分效果（不花 API 费用）
```bash
python extract_pipeline.py --file 苏轼行踪考.docx --dry-run
```
看一下章节切分是否合理，如果章节标题格式不对，
调整 extract_pipeline.py 里 `is_heading` 的正则规则。

### 第二步：提取结构化数据
```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxx

python extract_pipeline.py \
  --file 苏轼行踪考.docx \
  --output output/
```
中途可以 Ctrl+C 中断，下次用 --resume 继续：
```bash
python extract_pipeline.py \
  --file 苏轼行踪考.docx \
  --output output/ \
  --resume output/checkpoint.json
```

### 第三步：与现有数据库匹配（可选）
先把 Supabase 里现有数据导出为 JSON，再：
```bash
python extract_pipeline.py \
  --file 苏轼行踪考.docx \
  --output output/ \
  --existing existing_db.json
```
会生成 `output/match_result.json`，包含：
- matched：书中记录与库中记录的匹配对（用于更新坐标和描述）
- unmatched_new：书中有但库中没有的新地点
- unmatched_existing：库中有但书中没提到的地点

### 第四步：转换 + 自动坐标 + 推送 Supabase
```bash
export AMAP_KEY=你的高德Key

python to_supabase.py \
  --input output/locations.json \
  --amap-key $AMAP_KEY \
  --supabase-url https://xxx.supabase.co \
  --supabase-key your-service-role-key
```

只想本地看结果，不推送：
```bash
python to_supabase.py \
  --input output/locations.json \
  --amap-key $AMAP_KEY \
  --no-push \
  --output output/supabase_rows.json
```

---

## 输出文件说明

| 文件 | 内容 |
|------|------|
| `output/locations.json` | 提取的地点记录（主要结果） |
| `output/locations.csv` | 同上，CSV 格式，方便 Excel 查看 |
| `output/match_result.json` | 与现有库的匹配分析 |
| `output/supabase_rows.json` | 转换后的 Supabase 行格式（含坐标） |
| `output/checkpoint.json` | 断点续传文件（完成后自动删除） |

---

## Supabase locations 表需要新增的字段

```sql
ALTER TABLE locations ADD COLUMN IF NOT EXISTS modern_name text;
ALTER TABLE locations ADD COLUMN IF NOT EXISTS modern_address text;
ALTER TABLE locations ADD COLUMN IF NOT EXISTS coord_quality text DEFAULT 'city';
ALTER TABLE locations ADD COLUMN IF NOT EXISTS verified_lat float8;
ALTER TABLE locations ADD COLUMN IF NOT EXISTS verified_lng float8;
ALTER TABLE locations ADD COLUMN IF NOT EXISTS su_poi_name text;
ALTER TABLE locations ADD COLUMN IF NOT EXISTS su_poi_id text;
ALTER TABLE locations ADD COLUMN IF NOT EXISTS visit_period text;
ALTER TABLE locations ADD COLUMN IF NOT EXISTS su_quote text;
ALTER TABLE locations ADD COLUMN IF NOT EXISTS author_note text;
ALTER TABLE locations ADD COLUMN IF NOT EXISTS current_status text;
ALTER TABLE locations ADD COLUMN IF NOT EXISTS has_memorial boolean DEFAULT false;
ALTER TABLE locations ADD COLUMN IF NOT EXISTS source text;
ALTER TABLE locations ADD COLUMN IF NOT EXISTS data_quality char(1) DEFAULT 'C';
ALTER TABLE locations ADD COLUMN IF NOT EXISTS search_radius int DEFAULT 2000;
```

---

## 版权说明

- 苏轼原文诗词：公有领域，可自由使用
- 李常生先生的考察文字：有著作权，`author_note` 字段只供内部参考，
  前端展示时需改写为自己的描述语言，不能原文搬运
- 书中照片：不在提取范围内，仅提取文字信息

---

## 费用估算

全书约 20~30 章，每章约 3000~5000 字：
- Claude Sonnet 输入：~50万 token ≈ $1.5
- Claude Sonnet 输出：~10万 token ≈ $1.5
- **合计约 $3~5 完成全书提取**
