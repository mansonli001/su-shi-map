"""
《苏轼行踪考》智能提取流水线
用法:
  1. pip install python-docx pdfplumber anthropic tqdm
  2. 把书放到 input/ 目录下
  3. python extract_pipeline.py --file input/苏轼行踪考.docx
  4. 结果在 output/locations.json 和 output/locations.csv
"""

import os
import json
import time
import argparse
import re
import csv
from pathlib import Path
from typing import Optional

# ── 依赖检查 ─────────────────────────────────────────────────
try:
    import anthropic
except ImportError:
    raise SystemExit("请先安装: pip install anthropic")

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda x, **kw: x  # fallback: 无进度条


# ══════════════════════════════════════════════════════════════
# Step 1: 书籍切分（Word / PDF）
# ══════════════════════════════════════════════════════════════

def load_docx(path: str) -> list[dict]:
    """从 Word 文件按标题切章节，返回 [{title, content}, ...]"""
    from docx import Document
    doc = Document(path)
    chapters = []
    current = {"title": "前言", "content": ""}

    for para in doc.paragraphs:
        style = para.style.name.lower()
        text  = para.text.strip()
        if not text:
            continue

        # 标题段落 or 明显章节标记（调整正则适配书的实际格式）
        is_heading = (
            "heading" in style
            or re.match(r'^第[一二三四五六七八九十百\d]+[站章节]', text)
            or re.match(r'^\d+[\.\、]\s*\S{2,10}(市|县|州|府|路|镇)?$', text)
        )

        if is_heading and len(current["content"]) > 50:
            chapters.append(current)
            current = {"title": text, "content": ""}
        else:
            current["content"] += text + "\n"

    if current["content"].strip():
        chapters.append(current)

    print(f"[切分] 共切出 {len(chapters)} 章节（来源: Word）")
    return chapters


def load_pdf(path: str) -> list[dict]:
    """从 PDF 文件提取文字并按页分组，每 N 页一块"""
    import pdfplumber
    PAGES_PER_CHUNK = 8  # 每块页数，可调整

    chapters = []
    with pdfplumber.open(path) as pdf:
        total = len(pdf.pages)
        for i in range(0, total, PAGES_PER_CHUNK):
            chunk_pages = pdf.pages[i:i+PAGES_PER_CHUNK]
            text = "\n".join(
                p.extract_text() or "" for p in chunk_pages
            ).strip()
            if text:
                chapters.append({
                    "title": f"第{i+1}~{min(i+PAGES_PER_CHUNK, total)}页",
                    "content": text
                })

    print(f"[切分] 共切出 {len(chapters)} 块（来源: PDF，每块{PAGES_PER_CHUNK}页）")
    return chapters


def split_book(file_path: str) -> list[dict]:
    ext = Path(file_path).suffix.lower()
    if ext in (".docx", ".doc"):
        return load_docx(file_path)
    elif ext == ".pdf":
        return load_pdf(file_path)
    else:
        raise ValueError(f"不支持的格式: {ext}，请使用 .docx 或 .pdf")


# ══════════════════════════════════════════════════════════════
# Step 2: Claude API 提取结构化数据
# ══════════════════════════════════════════════════════════════

EXTRACTION_PROMPT = """你是一个文献整理助手，正在处理李常生先生《苏轼行踪考》的章节内容。

请从以下章节中提取所有苏轼相关地点记录，输出严格的 JSON 数组。

## 提取规则
- 每个地点一条记录，同一地点多次提及只记一次
- 区分"苏轼诗文原文"和"作者考察描述"，分别放入对应字段
- 若某字段在章节中无信息，填 null
- 只提取有实质内容的地点，不要提取泛指地名（如"四川"这样的省份）

## 输出格式（严格 JSON 数组，不要任何解释文字）
[
  {
    "location_name": "地点原名（书中称呼）",
    "modern_name": "现代景区/地点名称",
    "modern_address": "现代详细地址（作者实地考察所得，越详细越好）",
    "province": "省份",
    "city": "地级市",
    "district": "区县",
    "visit_year": 1080,
    "visit_period": "元丰三年",
    "su_works": ["赤壁赋", "念奴娇·赤壁怀古"],
    "su_quote": "苏轼原文关键引用（简短，控制在100字内）",
    "author_note": "作者实地考察的核心发现（不超过150字的摘要）",
    "current_status": "有遗址可参观|已不存仅有标记|待考|民间说法",
    "has_memorial": true,
    "has_photo_in_book": true,
    "coord_quality_estimate": "precise|district|city",
    "tags": ["谪居地", "创作地", "贬谪途中"]
  }
]

## 章节内容
---
{chapter_content}
---"""


def extract_chapter(client: anthropic.Anthropic, chapter: dict, retry: int = 3) -> list[dict]:
    """调用 Claude API 提取单章节，返回地点列表"""
    content = f"## {chapter['title']}\n\n{chapter['content']}"

    # 限制单次输入长度（约 6000 字，防止超 token）
    if len(content) > 8000:
        content = content[:8000] + "\n\n[内容截断]"

    prompt = EXTRACTION_PROMPT.format(chapter_content=content)

    for attempt in range(retry):
        try:
            resp = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = resp.content[0].text.strip()

            # 清理 markdown 代码块
            raw = re.sub(r'^```(?:json)?\s*', '', raw)
            raw = re.sub(r'\s*```$', '', raw)
            raw = raw.strip()

            records = json.loads(raw)
            if isinstance(records, list):
                return records
            elif isinstance(records, dict):
                return [records]  # 单条记录

        except json.JSONDecodeError as e:
            print(f"  [警告] JSON 解析失败 (尝试{attempt+1}/{retry}): {e}")
            if attempt < retry - 1:
                time.sleep(2)
        except anthropic.RateLimitError:
            wait = (attempt + 1) * 10
            print(f"  [限速] 等待 {wait}s...")
            time.sleep(wait)
        except Exception as e:
            print(f"  [错误] {type(e).__name__}: {e}")
            if attempt < retry - 1:
                time.sleep(3)

    print(f"  [跳过] 章节《{chapter['title']}》提取失败")
    return []


# ══════════════════════════════════════════════════════════════
# Step 3: 合并去重
# ══════════════════════════════════════════════════════════════

def deduplicate(records: list[dict]) -> list[dict]:
    """按 location_name + visit_year 去重，合并信息"""
    seen = {}
    for rec in records:
        key = f"{rec.get('location_name', '')}_{rec.get('visit_year', '')}"
        if key not in seen:
            seen[key] = rec
        else:
            # 合并：用非 null 值填充已有记录的空字段
            existing = seen[key]
            for field, val in rec.items():
                if val is not None and existing.get(field) is None:
                    existing[field] = val
                elif field == "su_works" and val:
                    existing_works = existing.get("su_works") or []
                    existing["su_works"] = list(set(existing_works + val))
                elif field == "tags" and val:
                    existing_tags = existing.get("tags") or []
                    existing["tags"] = list(set(existing_tags + val))

    result = list(seen.values())
    print(f"[去重] {len(records)} 条 → {len(result)} 条（去重后）")
    return result


def save_outputs(records: list[dict], output_dir: str):
    """保存 JSON 和 CSV 两种格式"""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # JSON
    json_path = out / "locations.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"[输出] JSON → {json_path}")

    # CSV（扁平化数组字段）
    csv_path = out / "locations.csv"
    flat_records = []
    for r in records:
        flat = dict(r)
        flat["su_works"] = "、".join(r.get("su_works") or [])
        flat["tags"]     = "、".join(r.get("tags") or [])
        flat_records.append(flat)

    if flat_records:
        fields = list(flat_records[0].keys())
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(flat_records)
    print(f"[输出] CSV  → {csv_path}")

    # 失败章节摘要
    print(f"\n✅ 提取完成：共 {len(records)} 条地点记录")


# ══════════════════════════════════════════════════════════════
# Step 4: 与现有 Supabase 数据做匹配（可选）
# ══════════════════════════════════════════════════════════════

def match_with_existing(
    new_records: list[dict],
    existing_json_path: Optional[str]
) -> dict:
    """
    将提取结果与已有数据库匹配
    返回: {matched: [...], unmatched_new: [...], unmatched_existing: [...]}
    """
    if not existing_json_path or not Path(existing_json_path).exists():
        return {"matched": [], "unmatched_new": new_records, "unmatched_existing": []}

    with open(existing_json_path, encoding="utf-8") as f:
        existing = json.load(f)

    # 简单字符串匹配（可换成更复杂的模糊匹配）
    existing_names = {
        r.get("name", "").replace(" ", ""): r
        for r in existing
    }

    matched, unmatched_new = [], []
    matched_keys = set()

    for rec in new_records:
        name = rec.get("location_name", "").replace(" ", "")
        modern = rec.get("modern_name", "").replace(" ", "")

        hit = existing_names.get(name) or existing_names.get(modern)
        if hit:
            matched.append({"book_record": rec, "db_record": hit})
            matched_keys.add(name)
            matched_keys.add(modern)
        else:
            unmatched_new.append(rec)

    unmatched_existing = [
        r for r in existing
        if r.get("name", "").replace(" ", "") not in matched_keys
    ]

    print(f"\n[匹配] 命中: {len(matched)} | 书中新增: {len(unmatched_new)} | 库中未覆盖: {len(unmatched_existing)}")
    return {
        "matched": matched,
        "unmatched_new": unmatched_new,
        "unmatched_existing": unmatched_existing
    }


# ══════════════════════════════════════════════════════════════
# 主流程
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="《苏轼行踪考》智能提取工具")
    parser.add_argument("--file",     required=True,  help="书籍路径（.docx 或 .pdf）")
    parser.add_argument("--output",   default="output", help="输出目录")
    parser.add_argument("--existing", default=None,   help="现有数据库 JSON 路径（可选，用于匹配）")
    parser.add_argument("--api-key",  default=None,   help="Anthropic API Key（或设环境变量 ANTHROPIC_API_KEY）")
    parser.add_argument("--resume",   default=None,   help="断点续传：已有的中间 JSON 路径")
    parser.add_argument("--dry-run",  action="store_true", help="只切分章节，不调用 API")
    args = parser.parse_args()

    # API 客户端
    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key and not args.dry_run:
        raise SystemExit("请设置 ANTHROPIC_API_KEY 环境变量，或用 --api-key 参数传入")
    client = anthropic.Anthropic(api_key=api_key) if not args.dry_run else None

    # Step 1: 切分
    print(f"\n📖 加载书籍: {args.file}")
    chapters = split_book(args.file)

    if args.dry_run:
        print("\n[dry-run] 章节预览:")
        for i, ch in enumerate(chapters[:5]):
            print(f"  [{i+1}] {ch['title']} ({len(ch['content'])} 字)")
        print(f"  ... 共 {len(chapters)} 章")
        return

    # Step 2: 断点续传
    all_records = []
    start_idx = 0

    if args.resume and Path(args.resume).exists():
        with open(args.resume, encoding="utf-8") as f:
            checkpoint = json.load(f)
        all_records = checkpoint.get("records", [])
        start_idx   = checkpoint.get("last_chapter", 0) + 1
        print(f"[续传] 从第 {start_idx+1} 章继续，已有 {len(all_records)} 条记录")

    # Step 3: 逐章提取
    cache_path = Path(args.output) / "checkpoint.json"
    Path(args.output).mkdir(parents=True, exist_ok=True)

    print(f"\n🤖 开始提取（共 {len(chapters)} 章，从第 {start_idx+1} 章）\n")

    for i, chapter in enumerate(tqdm(chapters[start_idx:], desc="提取进度"), start=start_idx):
        print(f"\n  → [{i+1}/{len(chapters)}] {chapter['title'][:40]}")
        records = extract_chapter(client, chapter)
        print(f"     提取到 {len(records)} 条地点")
        all_records.extend(records)

        # 每章保存断点
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"last_chapter": i, "records": all_records}, f, ensure_ascii=False)

        # 限速：避免 API 频率限制
        if i < len(chapters) - 1:
            time.sleep(1.5)

    # Step 4: 去重
    print(f"\n📊 原始提取: {len(all_records)} 条")
    final_records = deduplicate(all_records)

    # Step 5: 与已有库匹配
    if args.existing:
        match_result = match_with_existing(final_records, args.existing)
        match_out = Path(args.output) / "match_result.json"
        with open(match_out, "w", encoding="utf-8") as f:
            json.dump(match_result, f, ensure_ascii=False, indent=2)
        print(f"[匹配结果] → {match_out}")

    # Step 6: 输出
    save_outputs(final_records, args.output)

    # 清理断点文件
    if cache_path.exists():
        cache_path.unlink()
        print("[清理] 删除断点文件")


if __name__ == "__main__":
    main()
